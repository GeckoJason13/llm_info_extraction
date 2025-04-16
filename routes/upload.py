# 文件上传接口
from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from services.document_processor import DocumentProcessor
from utils.logger import logger

upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')

# 允许上传的文件扩展名
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'md', 'json'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route('', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '未找到文件'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # 处理文档
        try:
            doc_processor = DocumentProcessor()
            chunks = doc_processor.process_document(file_path)

            return jsonify({
                'success': True,
                'filename': filename,
                'chunks_count': len(chunks),
                'file_path': file_path
            })
        except Exception as e:
            logger.error(f"处理文件时出错: {str(e)}")
            return jsonify({'error': f'处理文件时出错: {str(e)}'}), 500

    return jsonify({'error': '不支持的文件类型'}), 400


@upload_bp.route('/list', methods=['GET'])
def list_files():
    files = []
    upload_folder = current_app.config['UPLOAD_FOLDER']

    if os.path.exists(upload_folder):
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path) and allowed_file(filename):
                files.append({
                    'name': filename,
                    'path': file_path,
                    'size': os.path.getsize(file_path)
                })

    return jsonify({'files': files})
