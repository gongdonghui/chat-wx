#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
性能测试：比较线性匹配和AC自动机的过滤速度
"""

import time
import sys
import os

# 插入当前目录到路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import filter_content, ACAutomaton

# 创建测试数据
def create_test_data():
    """创建大量测试文本"""
    # 正常文本
    normal_text = "这是一个正常的测试文本，用于测试敏感词过滤性能。"
    
    # 包含敏感词的文本
    sensitive_text = "这是一个包含敏感内容的文本，比如赌博、色情、暴力等违法内容。"
    
    # 生成大量重复文本
    large_text = normal_text * 100000  # 约500万字
    large_sensitive_text = sensitive_text * 100000  # 约800万字
    
    return normal_text, sensitive_text, large_text, large_sensitive_text

def test_linear_performance(sensitive_words, test_texts):
    """测试线性匹配性能"""
    print("\n=== 线性匹配性能测试 ===")
    
    def linear_filter(content):
        """模拟原始的线性匹配"""
        if not content:
            return False
        processed_content = content.lower()
        for word in sensitive_words:
            if word.lower() in processed_content:
                return True
        return False
    
    for name, text in test_texts:
        start_time = time.time()
        result = linear_filter(text)
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"{name}: {elapsed:.4f}秒, 结果: {'敏感' if result else '正常'}")

def test_ac_performance(automaton, test_texts):
    """测试AC自动机性能"""
    print("\n=== AC自动机性能测试 ===")
    
    def ac_filter(content):
        """AC自动机过滤"""
        if not content:
            return False
        processed_content = content.lower()
        found = automaton.search(processed_content)
        return len(found) > 0
    
    for name, text in test_texts:
        start_time = time.time()
        result = ac_filter(text)
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"{name}: {elapsed:.4f}秒, 结果: {'敏感' if result else '正常'}")

def main():
    # 加载敏感词
    with open('sensitive_words.txt', 'r', encoding='utf-8') as f:
        sensitive_words = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    # 创建AC自动机
    automaton = ACAutomaton()
    for word in sensitive_words:
        automaton.add_word(word.lower())
    automaton.build_fail()
    
    # 创建测试数据
    normal_text, sensitive_text, large_text, large_sensitive_text = create_test_data()
    
    test_texts = [
        ("短文本(正常)", normal_text),
        ("短文本(敏感)", sensitive_text),
        ("长文本(正常, 约500万字)", large_text),
        ("长文本(敏感, 约800万字)", large_sensitive_text),
    ]
    
    print("测试准备就绪...")
    print(f"敏感词数量: {len(sensitive_words)}")
    print(f"短文本长度: {len(normal_text)}字符")
    print(f"长文本长度: {len(large_text)}字符")
    
    # 测试线性匹配性能
    test_linear_performance(sensitive_words, test_texts)
    
    # 测试AC自动机性能
    test_ac_performance(automaton, test_texts)
    
    # 测试多次运行的平均性能
    print("\n=== 多次运行平均性能测试 (10次) ===")
    runs = 10
    
    # 线性匹配平均性能
    linear_total = 0
    for i in range(runs):
        start = time.time()
        linear_filter(large_sensitive_text)
        linear_total += time.time() - start
    print(f"线性匹配平均: {(linear_total/runs):.4f}秒")
    
    # AC自动机平均性能  
    ac_total = 0
    for i in range(runs):
        start = time.time()
        ac_filter(large_sensitive_text)
        ac_total += time.time() - start
    print(f"AC自动机平均: {(ac_total/runs):.4f}秒")
    
    print(f"\n性能提升倍数: {(linear_total/ac_total):.2f}倍")

def linear_filter(content):
    """模拟原始的线性匹配"""
    with open('sensitive_words.txt', 'r', encoding='utf-8') as f:
        sensitive_words = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    if not content:
        return False
    processed_content = content.lower()
    for word in sensitive_words:
        if word.lower() in processed_content:
            return True
    return False

def ac_filter(content):
    """AC自动机过滤"""
    with open('sensitive_words.txt', 'r', encoding='utf-8') as f:
        sensitive_words = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    automaton = ACAutomaton()
    for word in sensitive_words:
        automaton.add_word(word.lower())
    automaton.build_fail()
    if not content:
        return False
    processed_content = content.lower()
    found = automaton.search(processed_content)
    return len(found) > 0

if __name__ == "__main__":
    main()
