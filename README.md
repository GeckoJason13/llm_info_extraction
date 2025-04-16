# 基于LLM的长文档信息提取与分析系统

## 项目简介

本系统基于大型语言模型(LLM)实现了长文档的信息提取和分析功能，包括关键词提取、摘要生成和情感分析等核心功能。系统采用了高效的文档处理方法，能够处理多种格式的长文档，并提供友好的Web界面，使非技术用户也能轻松使用。

## 系统架构

系统采用前后端分离架构:
- 后端: Flask API服务
- 前端: HTML/CSS/JavaScript
- 模型: DeepSeek-R1-Distill-Qwen-1.5B本地部署

## 功能特点

1. **文档处理**
   - 支持多种格式: TXT, PDF, DOCX, MD, JSON
   - 大文档自动分块处理
   - 文档缓存管理

2. **信息提取**
   - 关键词提取与权重分析
   - 智能摘要生成(支持多种长度)
   - 情感分析与可视化

3. **交互界面**
   - 文件上传与管理
   - 分析结果可视化
   - 响应式设计

## 安装与使用

### 环境要求
- Python 3.8+
- GPU支持(推荐NVIDIA显卡，CUDA 11.7+)
- 至少8GB内存

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/yourusername/llm_info_extraction.git
cd llm_info_extraction
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行系统
```bash
python app.py
```

4. 打开浏览器访问
```
http://localhost:5000
```

## 系统使用流程

1. 打开Web界面，上传文档
2. 在文档列表中选择已上传的文档
3. 选择需要的分析功能:
   - 关键词提取
   - 摘要生成
   - 情感分析
4. 查看分析结果和可视化图表

## 文件结构

```
llm_info_extraction/
├── app.py                          # 启动入口，Flask 路由注册
├── routes/                         # 路由文件夹，存放各接口
│   ├── __init__.py
│   ├── upload.py                   # 文件上传接口
│   ├── keywords.py                 # 关键词提取接口
│   ├── summary.py                  # 摘要生成接口
│   ├── sentiment.py                # 情感分析接口
├── services/                       # 模型相关服务（模型加载、推理）
│   ├── __init__.py
│   ├── llm_client.py               # 用于加载和运行 LLM 模型
│   ├── document_processor.py       # 处理长文档分块等操作
├── utils/                          # 辅助功能
│   ├── logger.py                   # 日志记录
│   ├── config.py                   # 配置文件
├── data/                           # 存放上传的文档、预处理数据
├── experiments/                    # 实验结果与数据存储
│   ├── test_cases/                 # 测试用例文件
│   ├── results/                    # 实验结果文件
├── static/                         # 静态资源文件
├── templates/                      # HTML模板
├── requirements.txt                # 项目依赖包
├── README.md                       # 项目说明文档
```

## 扩展与优化方向

1. 支持更多文档格式(EPUB, HTML等)
2. 增加更多分析功能(实体识别、文档分类等)
3. 优化模型推理性能
4. 添加批处理模式
5. 支持多语言文档分析