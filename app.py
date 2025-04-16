# 启动入口，Flask 路由注册
from flask import Flask, render_template
from routes.upload import upload_bp
from routes.keywords import keywords_bp
from routes.summary import summary_bp
from routes.sentiment import sentiment_bp
from utils.config import config
import os

# 创建Flask应用
app = Flask(__name__,
            static_folder="static",
            template_folder="templates")

# 设置上传文件的目录
app.config['UPLOAD_FOLDER'] = config['data_dir']
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 最大上传文件大小: 50MB
app.secret_key = 'llm_document_analysis_secret_key'

# 注册路由蓝图
app.register_blueprint(upload_bp)
app.register_blueprint(keywords_bp)
app.register_blueprint(summary_bp)
app.register_blueprint(sentiment_bp)

# 确保文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
