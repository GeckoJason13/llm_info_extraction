# 关键词提取接口
from flask import Blueprint, request, jsonify
from services.llm_client import LLMClient
from services.document_processor import DocumentProcessor
from utils.logger import logger
import os

keywords_bp = Blueprint('keywords', __name__, url_prefix='/api/keywords')


@keywords_bp.route('/extract', methods=['POST'])
def extract_keywords():
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

        # 提取关键词
        all_keywords = []
        for i, chunk in enumerate(chunks):
            logger.info(f"正在处理第 {i + 1}/{len(chunks)} 个文档块...")

            prompt = f"""
            请从以下文本中提取10个最重要的关键词，以逗号分隔：

            {chunk}

            关键词：
            """

            response = llm_client.generate(prompt)

            # 处理响应，提取关键词
            keywords = [kw.strip() for kw in response.split(',')]
            all_keywords.extend(keywords)

        # 统计关键词频率
        keyword_freq = {}
        for kw in all_keywords:
            if kw in keyword_freq:
                keyword_freq[kw] += 1
            else:
                keyword_freq[kw] = 1

        # 按频率排序
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        top_keywords = sorted_keywords[:20]  # 取前20个最频繁的关键词

        result = {
            'filename': os.path.basename(file_path),
            'keywords': [{'text': k, 'weight': v} for k, v in top_keywords]
        }

        return jsonify(result)
    except Exception as e:
        logger.error(f"提取关键词时出错: {str(e)}")
        return jsonify({'error': f'提取关键词时出错: {str(e)}'}), 500
