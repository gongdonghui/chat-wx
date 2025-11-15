#!/usr/bin/env python3
"""
查询扩展模块
"""

import jieba
import jieba.posseg as pseg

# 初始化jieba
jieba.setLogLevel(20)

def load_synonyms_dict(file_path='keywords.txt'):
    """
    加载同义词词典
    :param file_path: 词典文件路径
    :return: 同义词词典，格式：{关键词: [同义词列表]}
    """
    synonyms_dict = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                words = line.split()
                if len(words) >= 2:
                    main_word = words[0]
                    synonyms = words[1:]
                    synonyms_dict[main_word] = synonyms
    except FileNotFoundError:
        # 如果词典文件不存在，返回空词典
        pass
    
    return synonyms_dict


def expand_query(query, synonyms_dict=None, topn=2):
    """
    查询扩展
    :param query: 原始查询
    :param synonyms_dict: 同义词词典
    :param topn: 每个关键词保留的同义词数量
    :return: 扩展后的查询
    """
    if not query:
        return query
    
    if synonyms_dict is None:
        synonyms_dict = load_synonyms_dict()
    
    # 使用jieba进行词性标注
    words = pseg.cut(query)
    
    expanded_words = []
    
    for word, pos in words:
        # 只处理名词、动词、形容词
        if pos.startswith('n') or pos.startswith('v') or pos.startswith('a'):
            expanded_words.append(word)
            
            # 添加同义词
            if word in synonyms_dict:
                expanded_words.extend(synonyms_dict[word][:topn])
        else:
            expanded_words.append(word)
    
    # 去重并保持顺序
    seen = set()
    result = []
    for word in expanded_words:
        if word not in seen:
            seen.add(word)
            result.append(word)
    
    return ' '.join(result)


if __name__ == "__main__":
    # 测试查询扩展
    test_queries = [
        "什么是人工智能？",
        "机器学习和深度学习的区别",
        "如何优化RAG系统",
        "自然语言处理应用"
    ]
    
    synonyms_dict = load_synonyms_dict()
    print(f"加载同义词词典：{synonyms_dict}")
    
    for query in test_queries:
        expanded = expand_query(query, synonyms_dict)
        print(f"原始查询: {query}")
        print(f"扩展查询: {expanded}")
        print()
