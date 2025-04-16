# 情感分析接口
from flask import Blueprint, request, jsonify
from services.llm_client import LLMClient
from services.document_processor import DocumentProcessor
from utils.logger import logger
import os
import json

sentiment_bp = Blueprint('sentiment', __name__, url_prefix='/api/sentiment')


@sentiment_bp.route('/analyze', methods=['POST'])
def analyze_sentiment():
    data = request.json
    file_path = data.get('file_path')

    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': '文件不存在'}), 400

    try:
        # 处理文档
        doc_processor = DocumentProcessor()
        chunks = doc_processor.process_document(file_path)

        # 初始化LLM客户端
        llm_client = LLMClient()

        # 情感分析结果
        chunk_sentiments = []
        overall_positive = 0
        overall_negative = 0
        overall_neutral = 0

        for i, chunk in enumerate(chunks):
            logger.info(f"正在分析第 {i + 1}/{len(chunks)} 个文档块的情感...")

            prompt = f"""
            请分析以下文本的情感倾向，并以JSON格式返回结果，包括以下字段：
            1. positive_score: 正面情感分数（0-1之间）
            2. negative_score: 负面情感分数（0-1之间）
            3. neutral_score: 中性情感分数（0-1之间）
            4. dominant_sentiment: 主导情感（"positive"、"negative"或"neutral"）
            5. key_phrases: 包含3个关键情感短语的数组

            分析的文本：
            {chunk}

            JSON格式的情感分析结果：
            """

            response = llm_client.generate(prompt)

            # 解析JSON响应
            try:
                # 提取JSON部分
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    sentiment_data = json.loads(json_str)
                else:
                    # 如果无法找到JSON，创建默认结构
                    sentiment_data = {
                        "positive_score": 0.33,
                        "negative_score": 0.33,
                        "neutral_score": 0.34,
                        "dominant_sentiment": "neutral",
                        "key_phrases": ["无法解析情感短语"]
                    }

                chunk_sentiments.append(sentiment_data)

                # 累计总体情感分数
                overall_positive += sentiment_data["positive_score"]
                overall_negative += sentiment_data["negative_score"]
                overall_neutral += sentiment_data["neutral_score"]

            except json.JSONDecodeError:
                logger.error(f"无法解析情感分析的JSON响应: {response}")
                chunk_sentiments.append({
                    "positive_score": 0.33,
                    "negative_score": 0.33,
                    "neutral_score": 0.34,
                    "dominant_sentiment": "neutral",
                    "key_phrases": ["无法解析情感短语"]
                })

        # 计算平均情感分数
        chunk_count = len(chunks)
        if chunk_count > 0:
            avg_positive = overall_positive / chunk_count
            avg_negative = overall_negative / chunk_count
            avg_neutral = overall_neutral / chunk_count

            # 确定主导情感
            max_score = max(avg_positive, avg_negative, avg_neutral)
            if max_score == avg_positive:
                dominant_sentiment = "positive"
            elif max_score == avg_negative:
                dominant_sentiment = "negative"
            else:
                dominant_sentiment = "neutral"
        else:
            avg_positive = avg_negative = avg_neutral = 0.33
            dominant_sentiment = "neutral"

        # 提取所有关键情感短语
        all_phrases = []
        for sentiment in chunk_sentiments:
            all_phrases.extend(sentiment.get("key_phrases", []))

        # 获取最频繁的短语（去重）
        unique_phrases = list(set(all_phrases))
        top_phrases = unique_phrases[:min(len(unique_phrases), 10)]

        result = {
            'filename': os.path.basename(file_path),
            'overall_sentiment': {
                'positive_score': avg_positive,
                'negative_score': avg_negative,
                'neutral_score': avg_neutral,
                'dominant_sentiment': dominant_sentiment
            },
            'key_phrases': top_phrases,
            'chunk_sentiments': chunk_sentiments
        }

        return jsonify(result)
    except Exception as e:
        logger.error(f"情感分析时出错: {str(e)}")
        return jsonify({'error': f'情感分析时出错: {str(e)}'}), 500
