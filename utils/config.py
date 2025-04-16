# 配置文件
import os

# 基础配置
config = {
    "model_dir": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models"),
    "data_dir": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"),
    "experiments_dir": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "experiments"),
    "chunk_size": 2000,
    "chunk_overlap": 200,
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "supported_formats": ["txt", "pdf", "docx", "md", "json"]
}

# 创建必要的目录
for directory in ["model_dir", "data_dir", "experiments_dir"]:
    os.makedirs(config[directory], exist_ok=True)

# 创建实验相关目录
os.makedirs(os.path.join(config["experiments_dir"], "test_cases"), exist_ok=True)
os.makedirs(os.path.join(config["experiments_dir"], "results"), exist_ok=True)
