import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.rag import split_text

# 测试文本
test_text = """
这是第一段测试文本。它包含了一些句子，用于测试文本分块功能。

这是第二段测试文本。它与第一段之间有一个空行，用于测试按段分割。

这是第三段测试文本，内容比较长。它包含了更多的句子，以便测试固定长度分块和滑动窗口功能。文本分块是RAG系统中的重要组成部分，它将长文本分割成适合处理的小块，同时保持上下文的连贯性。滑动窗口技术可以确保相邻块之间有一定的重叠，从而避免信息丢失。

这是第四段测试文本，用于测试不同的分块参数。
"""

print("=== 文本分块测试 ===\n")

# 测试1：默认固定长度分块
print("1. 默认固定长度分块：")
chunks = split_text(test_text)
for i, chunk in enumerate(chunks):
    print(f"   块{i+1}: {chunk[:50]}... ({len(chunk)}字符)")

print(f"\n   共生成 {len(chunks)} 个块")

# 测试2：小块大小固定长度分块
print("\n2. 小块大小固定长度分块 (chunk_size=100):")
chunks = split_text(test_text, chunk_size=100, chunk_overlap=20)
for i, chunk in enumerate(chunks):
    print(f"   块{i+1}: {chunk[:50]}... ({len(chunk)}字符)")

print(f"\n   共生成 {len(chunks)} 个块")

# 测试3：按段分割
print("\n3. 按段分割：")
chunks = split_text(test_text, mode='paragraph')
for i, chunk in enumerate(chunks):
    print(f"   段{i+1}: {chunk[:50]}... ({len(chunk)}字符)")

print(f"\n   共生成 {len(chunks)} 个块")

# 测试4：自定义滑动窗口
print("\n4. 自定义滑动窗口 (chunk_size=150, chunk_overlap=50):")
chunks = split_text(test_text, chunk_size=150, chunk_overlap=50)
for i, chunk in enumerate(chunks):
    print(f"   块{i+1}: {chunk[:50]}... ({len(chunk)}字符)")

print(f"\n   共生成 {len(chunks)} 个块")

print("\n=== 测试完成 ===")