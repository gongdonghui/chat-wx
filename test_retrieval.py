#!/usr/bin/env python3
"""
测试优化后的检索功能
"""

import jieba
import re

def test_keyword_extraction():
    """测试关键词提取"""
    print("=== 测试关键词提取 ===")
    
    # 设置jieba日志级别
    jieba.setLogLevel(20)
    
    test_queries = [
        "什么是人工智能？",
        "机器学习和深度学习的区别",
        "如何优化RAG系统的检索精度",
        "自然语言处理在金融领域的应用"
    ]
    
    for query in test_queries:
        keywords = list(jieba.cut_for_search(query))
        keywords = [kw for kw in keywords if len(kw) > 1]
        print(f"查询: {query}")
        print(f"关键词: {keywords}")
        print()

def test_similarity_conversion():
    """测试相似度转换"""
    print("=== 测试相似度转换 ===")
    
    # 模拟FAISS返回的L2距离
    l2_distances = [0.0, 0.5, 1.0, 2.0, 5.0, 10.0]
    
    for d in l2_distances:
        similarity = 1 / (1 + d)
        print(f"L2距离: {d:.2f} -> 相似度: {similarity:.4f}")
    print()

def test_rrf_fusion():
    """测试RRF融合"""
    print("=== 测试RRF融合 ===")
    
    def rrf_fusion(results_list, k=50):
        rrf_scores = {}
        for results in results_list:
            for rank, (doc_id, score) in enumerate(results):
                if doc_id not in rrf_scores:
                    rrf_scores[doc_id] = 0
                rrf_scores[doc_id] += 1 / (rank + k)
        return sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    
    # 模拟三个检索系统的结果
    bm25_results = [(0, 0.9), (1, 0.8), (2, 0.7), (3, 0.6), (4, 0.5)]
    vector_results = [(1, 0.95), (2, 0.85), (5, 0.8), (6, 0.75), (0, 0.7)]
    keyword_results = [(0, 3), (1, 2), (3, 2), (7, 1)]
    
    fused = rrf_fusion([bm25_results, vector_results, keyword_results])
    print("融合前:")
    print(f"BM25: {bm25_results}")
    print(f"向量: {vector_results}")
    print(f"关键词: {keyword_results}")
    print("融合后:")
    for doc_id, score in fused:
        print(f"文档 {doc_id}: 得分 {score:.4f}")
    print()

if __name__ == "__main__":
    test_keyword_extraction()
    test_similarity_conversion()
    test_rrf_fusion()
