# 处理长文档分块等操作
import os
from PyPDF2 import PdfReader
import docx
import json
from utils.logger import logger
from utils.config import config


class DocumentProcessor:
    def __init__(self, chunk_size=2000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_document(self, file_path):
        """
        处理文档，支持txt、pdf、docx、md和json格式，并返回分块后的文本
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower()

            # 提取文本
            if file_extension == '.txt' or file_extension == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            elif file_extension == '.pdf':
                text = self._extract_text_from_pdf(file_path)
            elif file_extension == '.docx':
                text = self._extract_text_from_docx(file_path)
            elif file_extension == '.json':
                text = self._extract_text_from_json(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {file_extension}")

            # 分块处理
            chunks = self._split_text(text)

            # 保存分块结果
            self._save_chunks(file_path, chunks)

            return chunks

        except Exception as e:
            logger.error(f"处理文档时出错: {str(e)}")
            raise

    def _extract_text_from_pdf(self, file_path):
        """从PDF文件中提取文本"""
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _extract_text_from_docx(self, file_path):
        """从DOCX文件中提取文本"""
        doc = docx.Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text

    def _extract_text_from_json(self, file_path):
        """从JSON文件中提取文本"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 如果是字符串，直接返回
        if isinstance(data, str):
            return data

        # 如果是字典或列表，转换为字符串
        return json.dumps(data, ensure_ascii=False, indent=2)

    def _split_text(self, text):
        """
        将文本分割成固定大小的块，支持重叠
        """
        if not text:
            return []

        # 按段落分割
        paragraphs = text.split('\n')
        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            # 如果添加当前段落会超过块大小，则保存当前块并开始新块
            if len(current_chunk) + len(paragraph) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())

                # 如果段落本身就超过块大小，则直接分割段落
                if len(paragraph) > self.chunk_size:
                    for i in range(0, len(paragraph), self.chunk_size - self.chunk_overlap):
                        chunks.append(paragraph[i:i + self.chunk_size].strip())
                    current_chunk = paragraph[-(self.chunk_overlap):]
                else:
                    current_chunk = paragraph
            else:
                current_chunk += "\n" + paragraph if current_chunk else paragraph

        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _save_chunks(self, file_path, chunks):
        """保存分块结果到文件"""
        basename = os.path.basename(file_path)
        name, _ = os.path.splitext(basename)

        chunks_dir = os.path.join(config["data_dir"], "chunks")
        os.makedirs(chunks_dir, exist_ok=True)

        output_path = os.path.join(chunks_dir, f"{name}_chunks.json")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "original_file": basename,
                "chunks": chunks,
                "chunk_count": len(chunks)
            }, f, ensure_ascii=False, indent=2)

        logger.info(f"文档分块保存到: {output_path}")
