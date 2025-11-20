#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试敏感词过滤功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import filter_content

def test_sensitive_filter():
    """测试敏感词过滤功能"""
    test_cases = [
        # (测试内容, 预期结果, 说明)
        ("这是一个正常的问题", False, "正常内容"),
        ("这是一个敏感的问题", True, "包含基础敏感词"),
        ("违法内容是不允许的", True, "包含违法敏感词"),
        ("暴力行为不可取", True, "包含暴力敏感词"),
        ("赌博是违法的", True, "包含赌博敏感词"),
        ("色情内容禁止传播", True, "包含色情敏感词"),
        ("恐怖主义是人类公敌", True, "包含恐怖敏感词"),
        ("反动言论不能传播", True, "包含反动敏感词"),
        ("邪教组织必须铲除", True, "包含邪教敏感词"),
        ("毒品危害健康", True, "包含毒品敏感词"),
        ("诈骗行为会被严惩", True, "包含诈骗敏感词"),
        ("黑客攻击是犯罪", True, "包含黑客敏感词"),
        ("散布谣言会被追责", True, "包含谣言敏感词"),
        ("人身攻击是不对的", True, "包含攻击敏感词"),
        ("辱骂他人不文明", True, "包含辱骂敏感词"),
        ("威胁他人要承担法律责任", True, "包含威胁敏感词"),
        ("谈论政治话题要谨慎", True, "包含政治敏感词"),
        ("宗教问题需要尊重", True, "包含宗教敏感词"),
        ("保护隐私很重要", True, "包含隐私敏感词"),
        ("个人信息不能泄露", True, "包含个人信息敏感词"),
        # 测试大小写不敏感
        ("这是一个SENSITIVE的问题", True, "包含大写敏感词"),
        ("这是一个Sensitive的问题", True, "包含首字母大写敏感词"),
        # 测试全角字符
        ("这是一个ｓｅｎｓｉｔｉｖｅ的问题", True, "包含全角英文字母敏感词"),
        ("这是一个ＳＥＮＳＩＴＩＶＥ的问题", True, "包含全角大写英文字母敏感词"),
        ("违法内容是不允许的", True, "包含全角违法敏感词"),
        # 测试混合情况
        ("这是一个SENSITIVE的违法问题", True, "包含多个敏感词"),
        ("这是一个非常敏感的话题", True, "包含敏感词在中间"),
        ("敏感话题需要避免", True, "包含敏感词在开头"),
        ("我们要避免敏感话题", True, "包含敏感词在结尾"),
    ]
    
    print("开始测试敏感词过滤功能...")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for content, expected, description in test_cases:
        result = filter_content(content)
        status = "✓" if result == expected else "✗"
        if result == expected:
            passed += 1
        else:
            failed += 1
        print(f"{status} {description}: {content}")
        if result != expected:
            print(f"  预期: {'敏感' if expected else '正常'}")
            print(f"  实际: {'敏感' if result else '正常'}")
    
    print("=" * 50)
    print(f"测试完成：共 {len(test_cases)} 个测试用例，通过 {passed} 个，失败 {failed} 个")
    
    return failed == 0

if __name__ == "__main__":
    success = test_sensitive_filter()
    sys.exit(0 if success else 1)
