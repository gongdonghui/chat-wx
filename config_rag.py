# RAG相关配置
VLLM_SERVER_URL = 'http://your-vllm-server-address/generate'  # VLLM推理服务地址
EMBEDDING_MODEL = 'paraphrase-multilingual-MiniLM-L12-v2'  # 嵌入模型
CHUNK_SIZE = 512  # 文本分块大小
CHUNK_OVERLAP = 50  # 文本分块重叠
RRF_K = 60  # RRF融合参数
TOP_K = 10  # 检索Top K结果
TOP_N = 5  # 最终返回Top N结果