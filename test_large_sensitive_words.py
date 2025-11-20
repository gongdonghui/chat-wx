#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试大量敏感词情况下的性能差异
"""

import time
import sys
import os

# 插入当前目录到路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import ACAutomaton

def generate_large_sensitive_words(count=10000):
    """生成大量敏感词"""
    sensitive_words = []
    for i in range(count):
        # 生成不同长度的敏感词
        if i % 10 == 0:
            word = f"敏感词{i:05d}"
        elif i % 10 == 1:
            word = f"违法内容{i:05d}"
        elif i % 10 == 2:
            word = f"暴力行为{i:05d}"
        elif i % 10 == 3:
            word = f"赌博活动{i:05d}"
        elif i % 10 == 4:
            word = f"色情内容{i:05d}"
        elif i % 10 == 5:
            word = f"恐怖主义{i:05d}"
        elif i % 10 == 6:
            word = f"反动言论{i:05d}"
        elif i % 10 == 7:
            word = f"邪教组织{i:05d}"
        elif i % 10 == 8:
            word = f"毒品交易{i:05d}"
        else:
            word = f"诈骗行为{i:05d}"
        sensitive_words.append(word)
    return sensitive_words

def test_performance_with_large_words():
    """测试大量敏感词情况下的性能"""
    
    # 生成不同数量级的敏感词
    word_counts = [1000, 5000, 10000, 20000, 50000]
    
    # 创建测试文本
    test_text = "这是一个正常的测试文本，里面包含敏感词00123和违法内容00456等敏感内容。"
    large_test_text = test_text * 10000  # 约400万字
    
    print("性能测试开始...")
    print(f"测试文本长度: {len(large_test_text)}字符")
    
    for count in word_counts:
        print(f"\n=== 测试 {count} 个敏感词 ===")
        
        # 生成敏感词
        sensitive_words = generate_large_sensitive_words(count)
        
        # 测试线性匹配
        def linear_filter(content):
            processed_content = content.lower()
            for word in sensitive_words:
                if word.lower() in processed_content:
                    return True
            return False
        
        start_time = time.time()
        linear_result = linear_filter(large_test_text)
        linear_time = time.time() - start_time
        
        # 测试AC自动机
        automaton = ACAutomaton()
        for word in sensitive_words:
            automaton.add_word(word.lower())
        automaton.build_fail()
        
        def ac_filter(content):
            processed_content = content.lower()
            found = automaton.search(processed_content)
            return len(found) > 0
        
        start_time = time.time()
        ac_result = ac_filter(large_test_text)
        ac_time = time.time() - start_time
        
        print(f"线性匹配: {linear_time:.4f}秒, 结果: {'敏感' if linear_result else '正常'}")
        print(f"AC自动机: {ac_time:.4f}秒, 结果: {'敏感' if ac_result else '正常'}")
        print(f"性能差异: {'AC自动机快' if ac_time < linear_time else '线性匹配快'}, 速度提升: {max(linear_time, ac_time)/min(linear_time, ac_time):.2f}倍")
    
    print("\n=== 测试总结 ===")
    print("AC自动机在处理大量敏感词时具有显著的性能优势")
    print("时间复杂度：")
    print("- 线性匹配: O(n*m) (n=文本长度, m=敏感词数量)")
    print("- AC自动机: O(n) (仅与文本长度有关)")

if __name__ == "__main__":
    test_performance_with_large_words()
