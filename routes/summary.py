# 摘要生成接口
from flask import Blueprint, request, jsonify
from services.llm_client import LLMClient
from services.document_processor import DocumentProcessor
from utils.logger import logger
import os

summary_bp = Blueprint('summary', __name__, url_prefix='/api/summary')


@summary_bp.route('/generate', methods=['POST'])
def generate_summary():
    data = request.json
    file_path = data.get('file_path')
    summary_length = data.get('length', 'medium')  # short, medium, long

    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': '文件不存在'}), 400

    # 根据长度设置摘要字数
    length_map = {
        'short': 150,
        'medium': 300,
        'long': 500
    }
    word_count = length_map.get(summary_length, 300)

    try:
        # 处理文档
        doc_processor = DocumentProcessor()
        chunks = doc_processor.process_document(file_path)

        # 初始化LLM客户端
        llm_client = LLMClient()

        # 为每个块生成摘要
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            logger.info(f"正在为第 {i + 1}/{len(chunks)} 个文档块生成摘要...")

            prompt = f"""
            请为以下文本生成一个简洁的摘要：

            {chunk}

            摘要：
            """

            summary = llm_client.generate(prompt)
            chunk_summaries.append(summary)

        # 合并所有块的摘要
        combined_summaries = " ".join(chunk_summaries)

        # 生成最终摘要
        final_prompt = f"""
        请根据以下文本生成一个约{word_count}字的摘要，捕捉最重要的信息和观点：

        {combined_summaries}

        摘要：
        """

        final_summary = llm_client.generate(final_prompt)

        result = {
            'filename': os.path.basename(file_path),
            'summary': final_summary
        }

        return jsonify(result)
    except Exception as e:
        logger.error(f"生成摘要时出错: {str(e)}")
        return jsonify({'error': f'生成摘要时出错: {str(e)}'}), 500
