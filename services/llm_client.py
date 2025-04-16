# 用于加载和运行 LLM 模型
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from utils.logger import logger
from utils.config import config
import os


class LLMClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True

        # 设置设备
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"使用设备: {self.device}")

        # 加载模型
        self.model_path = "D:/code/model/deepseek/DeepSeek-R1-Distill-Qwen-1.5B"

        try:
            logger.info(f"正在从 {self.model_path} 加载模型...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)

            # 根据可用内存确定是否使用FP16
            if torch.cuda.is_available():
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    trust_remote_code=True
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    device_map="auto",
                    trust_remote_code=True
                )

            logger.info("模型加载完成")
        except Exception as e:
            logger.error(f"加载模型时出错: {str(e)}")
            raise

    def generate(self, prompt, max_length=2048, temperature=0.7):
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    do_sample=True,
                    temperature=temperature,
                    top_p=0.9,
                    eos_token_id=self.tokenizer.eos_token_id
                )

            response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
            return response.strip()
        except Exception as e:
            logger.error(f"生成文本时出错: {str(e)}")
            raise

    def fine_tune(self, train_data, epochs=1, batch_size=4, learning_rate=5e-5):
        """
        使用训练数据微调模型

        Parameters:
        - train_data: 训练数据列表，每项包含 {"prompt": "...", "completion": "..."}
        - epochs: 训练轮数
        - batch_size: 批处理大小
        - learning_rate: 学习率
        """
        try:
            # 准备训练数据
            train_encodings = []
            for item in train_data:
                prompt = item["prompt"]
                completion = item["completion"]
                full_text = f"{prompt}{completion}"

                encoded = self.tokenizer(full_text, return_tensors="pt", truncation=True, max_length=1024)
                train_encodings.append(encoded)

            # 设置模型为训练模式
            self.model.train()

            # 使用AdamW优化器
            optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)

            # 训练循环
            for epoch in range(epochs):
                logger.info(f"Epoch {epoch + 1}/{epochs}")
                total_loss = 0

                # 批处理训练
                for i in range(0, len(train_encodings), batch_size):
                    batch = train_encodings[i:i + batch_size]

                    # 将输入移到GPU
                    input_ids = torch.cat([item.input_ids for item in batch], dim=0).to(self.device)
                    attention_mask = torch.cat([item.attention_mask for item in batch], dim=0).to(self.device)

                    # 计算损失
                    outputs = self.model(input_ids=input_ids, attention_mask=attention_mask, labels=input_ids)
                    loss = outputs.loss

                    # 反向传播
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()

                    total_loss += loss.item()

                    if (i // batch_size) % 10 == 0:
                        logger.info(f"Batch {i // batch_size}, Loss: {loss.item()}")

                logger.info(
                    f"Epoch {epoch + 1} completed. Average loss: {total_loss / (len(train_encodings) / batch_size)}")

            # 保存微调模型
            finetuned_path = os.path.join(config['model_dir'], "finetuned_model")
            os.makedirs(finetuned_path, exist_ok=True)

            logger.info(f"正在保存微调后的模型到 {finetuned_path}")
            self.model.save_pretrained(finetuned_path)
            self.tokenizer.save_pretrained(finetuned_path)

            logger.info("微调完成，模型已保存")

            # 恢复为评估模式
            self.model.eval()

            return {"status": "success", "saved_path": finetuned_path}

        except Exception as e:
            logger.error(f"微调模型时出错: {str(e)}")
            raise
