from app.api import *
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import faiss
import numpy as np
import re
import requests
import json
import configparser

rag = Blueprint('rag', __name__)

# 加载配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 加载配置
VLLM_SERVER_URL = config.get('vllm', 'server_url', fallback='http://your-vllm-server-address/generate')
EMBEDDING_MODEL = 'paraphrase-multilingual-MiniLM-L12-v2'
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
RRF_K = 60
TOP_K = 10
TOP_N = 5

# 初始化模型和存储
model = SentenceTransformer(EMBEDDING_MODEL)

documents = []
embeddings = []
bm25 = None
index = None

# 文本分块函数
def split_text(text, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, mode='fixed'):
    """
    将长文本分割成块
    :param text: 输入文本
    :param chunk_size: 块大小（仅在fixed模式下有效）
    :param chunk_overlap: 滑动窗口重叠大小
    :param mode: 分割模式，可选值：'fixed'（固定长度）, 'paragraph'（按段分割）
    :return: 分块后的文本列表
    """
    if mode == 'paragraph':
        # 按段分割，保留段落结构
        chunks = re.split(r'(\n\n+)', text.strip())
        # 合并段落分隔符到前一个块
        merged_chunks = []
        for i in range(0, len(chunks), 2):
            chunk = chunks[i].strip()
            if i + 1 < len(chunks):
                chunk += chunks[i+1]  # 保留段落分隔符
            if chunk:
                merged_chunks.append(chunk)
        return merged_chunks
    
    # 默认固定长度分割，带滑动窗口，保留标点符号
    # 使用正则分割并保留分隔符
    sentences = re.split(r'([。！？\n])', text)
    chunks = []
    current_chunk = []
    current_length = 0
    
    # 将分割后的句子和标点符号重新组合
    combined_sentences = []
    for i in range(0, len(sentences), 2):
        if i + 1 < len(sentences):
            combined_sentences.append(sentences[i] + sentences[i+1])
        else:
            combined_sentences.append(sentences[i])
    
    for sentence in combined_sentences:
        if not sentence:
            continue
        sentence_length = len(sentence)
        
        if current_length + sentence_length > chunk_size and current_chunk:
            chunks.append(''.join(current_chunk))
            
            # 实现滑动窗口：保留最后chunk_overlap个字符
            window_text = ''.join(current_chunk)
            if len(window_text) <= chunk_overlap:
                # 如果当前块长度小于等于重叠大小，则保留整个块
                current_chunk = [s for s in current_chunk if s]
            else:
                # 保留最后chunk_overlap个字符作为重叠
                overlap_part = window_text[-chunk_overlap:]
                # 确保重叠部分是完整的句子
                new_current_chunk = []
                temp_text = ''
                for sent in reversed(current_chunk):
                    temp_text = sent + temp_text
                    if temp_text in overlap_part or not new_current_chunk:  # 至少保留一个句子
                        new_current_chunk.insert(0, sent)
                    else:
                        break
                current_chunk = new_current_chunk if new_current_chunk else []
            
            current_length = sum(len(s) for s in current_chunk)
        
        current_chunk.append(sentence)
        current_length += sentence_length
    
    if current_chunk:
        chunks.append(''.join(current_chunk))
    
    # 移除空块
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    return chunks

# RRF融合排序
def rrf_fusion(results1, results2, k=60):
    """
    逆序位融合
    :param results1: 第一个检索结果列表 [(doc_id, score), ...]
    :param results2: 第二个检索结果列表 [(doc_id, score), ...]
    :param k: RRF参数
    :return: 融合后的结果列表 [(doc_id, score), ...]
    """
    rrf_scores = {}
    
    for rank, (doc_id, score) in enumerate(results1):
        if doc_id not in rrf_scores:
            rrf_scores[doc_id] = 0
        rrf_scores[doc_id] += 1 / (rank + k)
    
    for rank, (doc_id, score) in enumerate(results2):
        if doc_id not in rrf_scores:
            rrf_scores[doc_id] = 0
        rrf_scores[doc_id] += 1 / (rank + k)
    
    # 按得分降序排序
    fused_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return fused_results

@rag.route('/rag/upload', methods=['POST'])
def upload_text():
    """
    上传文本并进行分块、索引
    """
    global documents, embeddings, bm25, index
    
    text = request.form.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    # 获取分块参数
    mode = request.form.get('mode', 'fixed')  # 默认为固定长度模式
    chunk_size = int(request.form.get('chunk_size', CHUNK_SIZE))  # 块大小
    chunk_overlap = int(request.form.get('chunk_overlap', CHUNK_OVERLAP))  # 滑动窗口重叠大小
    
    # 验证模式
    if mode not in ['fixed', 'paragraph']:
        return jsonify({'error': 'Invalid mode. Supported modes: fixed, paragraph'}), 400
    
    # 文本分块
    chunks = split_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap, mode=mode)
    if not chunks:
        return jsonify({'error': 'Text is too short or empty'}), 400
    
    # 更新文档列表
    documents.extend(chunks)
    
    # 生成向量嵌入
    new_embeddings = model.encode(chunks)
    embeddings.extend(new_embeddings.tolist())
    
    # 构建BM25索引
    tokenized_docs = [doc.split() for doc in documents]
    bm25 = BM25Okapi(tokenized_docs)
    
    # 构建FAISS向量索引
    embeddings_np = np.array(embeddings, dtype='float32')
    dimension = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)
    
    return jsonify({
        'message': 'Text uploaded and indexed successfully',
        'num_chunks': len(chunks),
        'total_docs': len(documents)
    })

@rag.route('/rag/query', methods=['POST'])
def rag_query():
    """
    执行RAG查询，融合向量检索和BM25
    """
    global documents, embeddings, bm25, index
    
    query = request.form.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    if not documents or not bm25 or not index:
        return jsonify({'error': 'No documents indexed yet'}), 400
    
    # BM25检索
    tokenized_query = query.split()
    bm25_scores = bm25.get_scores(tokenized_query)
    bm25_results = [(i, score) for i, score in enumerate(bm25_scores)]
    bm25_results = sorted(bm25_results, key=lambda x: x[1], reverse=True)[:10]
    
    # 向量检索
    query_embedding = model.encode([query])
    D, I = index.search(query_embedding, 10)
    vector_results = [(i, 1/(d+1)) for i, d in zip(I[0], D[0])]  # 转换为相似度得分
    
    # 融合排序
    fused_results = rrf_fusion(vector_results, bm25_results)
    
    # 获取最相关的文档
    retrieved_docs = [{
        'doc_id': doc_id,
        'content': documents[doc_id],
        'score': score
    } for doc_id, score in fused_results[:5]]
    
    # 调用大模型生成答案
    context = '\n'.join([doc['content'] for doc in retrieved_docs])
    prompt = f"基于以下上下文回答问题：\n\n上下文：{context}\n\n问题：{query}\n\n回答："
    
    try:
        # 调用vllm提供的大模型服务
        response = requests.post(
            VLLM_SERVER_URL,
            json={'prompt': prompt, 'temperature': 0.7, 'max_tokens': 512}
        )
        
        if response.status_code == 200:
            answer = response.json().get('text', '')
        else:
            answer = '大模型服务调用失败'
            
    except Exception as e:
        answer = f'大模型服务调用异常：{str(e)}'
    
    return jsonify({
        'query': query,
        'answer': answer,
        'retrieved_docs': retrieved_docs
    })

@rag.route('/rag/docs', methods=['GET'])
def get_docs():
    """
    获取所有已索引的文档
    """
    return jsonify({
        'total_docs': len(documents),
        'documents': documents
    })