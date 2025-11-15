import re

# 文本分块函数
def split_text(text, chunk_size=512, chunk_overlap=50, mode='fixed'):
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
    print(f"   块{i+1}: {chunk[:100]}... ({len(chunk)}字符)")

print(f"\n   共生成 {len(chunks)} 个块")

# 测试2：小块大小固定长度分块
print("\n2. 小块大小固定长度分块 (chunk_size=100):")
chunks = split_text(test_text, chunk_size=100, chunk_overlap=20)
for i, chunk in enumerate(chunks):
    print(f"   块{i+1}: {chunk[:100]}... ({len(chunk)}字符)")

print(f"\n   共生成 {len(chunks)} 个块")

# 测试3：按段分割
print("\n3. 按段分割：")
chunks = split_text(test_text, mode='paragraph')
for i, chunk in enumerate(chunks):
    print(f"   段{i+1}: {chunk[:100]}... ({len(chunk)}字符)")

print(f"\n   共生成 {len(chunks)} 个块")

# 测试4：自定义滑动窗口
print("\n4. 自定义滑动窗口 (chunk_size=150, chunk_overlap=50):")
chunks = split_text(test_text, chunk_size=150, chunk_overlap=50)
for i, chunk in enumerate(chunks):
    print(f"   块{i+1}: {chunk[:100]}... ({len(chunk)}字符)")

print(f"\n   共生成 {len(chunks)} 个块")

print("\n=== 测试完成 ===")