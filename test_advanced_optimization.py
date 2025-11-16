#!/usr/bin/env python3
"""
测试高级检索优化功能
"""

import synonyms
import numpy as np
from sentence_transformers import SentenceTransformer

# 设置日志级别
synonyms.set_log_level(20)

def test_query_expansion():
    """测试查询扩展"""
    print("=== 测试查询扩展 ===")
    
    test_queries = [
        "什么是人工智能？",
        "机器学习和深度学习的区别",
        "如何优化RAG系统",
        "自然语言处理应用"
    ]
    
    for query in test_queries:
        try:
            syn_words = synonyms.nearby(query, topn=5)[0]
            expanded_query = ' '.join(set(query.split() + syn_words))
            print(f"原始查询: {query}")
            print(f"扩展查询: {expanded_query}")
            print(f"同义词: {syn_words}")
        except Exception as e:
            print(f"查询扩展失败: {query} -> {str(e)}")
        print()

def test_embedding_model():
    """测试新的嵌入模型"""
    print("=== 测试嵌入模型 ===")
    
    # 比较两个嵌入模型
    models = [
        'paraphrase-multilingual-MiniLM-L12-v2',  # 原模型
        'BAAI/bge-large-zh'  # 新模型
    ]
    
    test_sentences = [
        "人工智能是计算机科学的一个分支",
        "机器学习是人工智能的核心技术之一",
        "深度学习是机器学习的一个子领域",
        "自然语言处理是人工智能的重要应用领域"
    ]
    
    for model_name in models:
        print(f"\n使用模型: {model_name}")
        model = SentenceTransformer(model_name)
        embeddings = model.encode(test_sentences)
        
        # 计算相似度矩阵
        similarity_matrix = np.dot(embeddings, embeddings.T) / (np.linalg.norm(embeddings, axis=1)[:, np.newaxis] * np.linalg.norm(embeddings, axis=1))
        
        for i in range(len(test_sentences)):
            for j in range(i+1, len(test_sentences)):
                print(f"句子{i+1}与句子{j+1}的相似度: {similarity_matrix[i][j]:.4f}")

def test_semantic_similarity():
    """测试语义相似度"""
    print("=== 测试语义相似度 ===")
    
    model = SentenceTransformer('BAAI/bge-large-zh')
    
    test_pairs = [
        ("人工智能", "AI"),
        ("机器学习", "深度学习"),
        ("自然语言处理", "语音识别"),
        ("RAG系统", "检索增强生成")
    ]
    
    for pair in test_pairs:
        emb1 = model.encode(pair[0])
        emb2 = model.encode(pair[1])
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        print(f"'{pair[0]}' 与 '{pair[1]}' 的相似度: {similarity:.4f}")
    print()

if __name__ == "__main__":
    test_query_expansion()
    test_semantic_similarity()
    # test_embedding_model()  # 这个测试比较耗时，可以选择运行
