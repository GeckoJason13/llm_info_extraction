# 日志记录
import logging
import os
from datetime import datetime

# 创建logs目录
os.makedirs('logs', exist_ok=True)

# 配置日志记录器
logger = logging.getLogger('llm_doc_system')
logger.setLevel(logging.INFO)

# 日志文件格式：logs/年月日.log
log_file = os.path.join('logs', f"{datetime.now().strftime('%Y%m%d')}.log")

# 文件处理器
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 定义输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加处理器到日志记录器
logger.addHandler(file_handler)
logger.addHandler(console_handler)
