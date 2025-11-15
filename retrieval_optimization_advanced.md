# 高级检索精度优化方案

## 1. 当前系统概述
当前检索系统已实现：
- 多检索源融合（BM25+向量检索+关键词匹配）
- RRF融合排序
- VLLM rerank模型集成
- 基本的分块策略

## 2. 进一步优化建议

### 2.1 分块策略优化

#### 2.1.1 智能分块（语义分块）
**问题**：当前固定长度和按段分块可能会破坏语义完整性
**解决方案**：使用句子嵌入或语义分割模型进行智能分块

```python
# 示例：使用语义嵌入进行智能分块
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def semantic_split(text, max_chunk_size=512, similarity_threshold=0.8):
    # 将文本分割为句子
    sentences = re.split(r'([。！？\n])', text)
    combined_sentences = [sentences[i]+sentences[i+1] for i in range(0, len(sentences)-1, 2)]
    if len(sentences) % 2 == 1:
        combined_sentences.append(sentences[-1])
    
    if not combined_sentences:
        return []
    
    # 生成句子嵌入
    sentence_embeddings = model.encode(combined_sentences)
    
    chunks = []
    current_chunk = [combined_sentences[0]]
    current_embedding = sentence_embeddings[0]
    
    for i in range(1, len(combined_sentences)):
        sentence = combined_sentences[i]
        embedding = sentence_embeddings[i]
        
        # 计算当前块与新句子的相似度
        similarity = np.dot(current_embedding, embedding) / (np.linalg.norm(current_embedding) * np.linalg.norm(embedding))
        
        # 检查块长度和相似度
        if len(''.join(current_chunk)) + len(sentence) > max_chunk_size or similarity < similarity_threshold:
            chunks.append(''.join(current_chunk))
            current_chunk = [sentence]
            current_embedding = embedding
        else:
            current_chunk.append(sentence)
            # 更新当前块的嵌入（取平均）
            current_embedding = np.mean([current_embedding, embedding], axis=0)
    
    if current_chunk:
        chunks.append(''.join(current_chunk))
    
    return chunks
```

#### 2.1.2 元数据增强分块
**策略**：在分块时保留文档元数据（如标题、章节、日期等）
**优势**：提高检索时的上下文理解能力

### 2.2 检索模型优化

#### 2.2.1 更好的嵌入模型
**推荐**：使用更适合中文的嵌入模型
- `shibing624/text2vec-base-chinese`
- `BAAI/bge-large-zh`
- `Doubao/tb-small-zh-v2`

**修改方式**：
```python
EMBEDDING_MODEL = 'BAAI/bge-large-zh'  # 替换为更优的中文嵌入模型
```

#### 2.2.2 BM25参数调优
**策略**：调整BM25的参数（k1, b等）
**优势**：提高关键词匹配的精度

```python
# 示例：调整BM25参数
bm25 = BM25Okapi(tokenized_docs, k1=1.5, b=0.75)
```

#### 2.2.3 多向量检索
**策略**：为每个文档生成多个向量（如标题向量+内容向量+关键词向量）
**优势**：提高向量检索的召回率和精度

### 2.3 Rerank优化

#### 2.3.1 多模型Rerank
**策略**：使用多个rerank模型进行融合
**优势**：提高重排的鲁棒性

#### 2.3.2 上下文增强Rerank
**策略**：在rerank时提供更多上下文信息（如文档元数据、查询历史等）
**修改方式**：
```python
rerank_input = {
    'query': query,
    'documents': [f"标题：{metadata[doc_id]['title']}\n内容：{documents[doc_id]}" for doc_id, score in candidate_docs],
    'top_n': RERANK_TOP_N
}
```

### 2.4 查询理解优化

#### 2.4.1 查询扩展
**策略**：对用户查询进行扩展（同义词、上下位词、实体链接等）

```python
# 示例：使用同义词扩展
import jieba.posseg as pseg
import synonyms

def expand_query(query):
    words = pseg.cut(query)
    expanded_words = []
    
    for word, pos in words:
        if pos in ['n', 'v', 'a']:  # 只扩展名词、动词、形容词
            syns = synonyms.nearby(word, topn=2)[0]
            expanded_words.extend(syns)
        else:
            expanded_words.append(word)
    
    return ' '.join(expanded_words)
```

#### 2.4.2 查询分类
**策略**：对用户查询进行分类（如事实类、定义类、比较类等）
**优势**：针对不同类型查询使用不同检索策略

### 2.5 后处理优化

#### 2.5.1 冗余文档过滤
**策略**：过滤内容高度相似的文档
**优势**：提高上下文的多样性

```python
# 示例：基于余弦相似度过滤冗余文档
def filter_duplicate_docs(docs, similarity_threshold=0.9):
    filtered_docs = []
    
    if not docs:
        return filtered_docs
    
    filtered_docs.append(docs[0])
    doc_embeddings = model.encode([doc['content'] for doc in docs])
    
    for i in range(1, len(docs)):
        doc = docs[i]
        embedding = doc_embeddings[i]
        is_duplicate = False
        
        for j in range(len(filtered_docs)):
            existing_embedding = doc_embeddings[docs.index(filtered_docs[j])]
            similarity = np.dot(embedding, existing_embedding) / (np.linalg.norm(embedding) * np.linalg.norm(existing_embedding))
            
            if similarity > similarity_threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            filtered_docs.append(doc)
    
    return filtered_docs
```

#### 2.5.2 上下文排序
**策略**：根据文档在原始文本中的位置进行排序
**优势**：保持上下文的连续性

## 3. 实施优先级建议

1. **嵌入模型升级**：高收益，低实施成本
2. **智能分块**：中收益，中实施成本
3. **查询扩展**：中收益，低实施成本
4. **BM25参数调优**：低收益，低实施成本
5. **冗余文档过滤**：中收益，低实施成本

## 4. 效果评估

建议使用以下指标评估优化效果：
- **召回率**：相关文档被检索到的比例
- **精确率**：检索到的文档中相关文档的比例
- **MAP**：平均精度均值
- **MRR**：平均倒数排名
- **人工评估**：邀请用户或专家评估检索结果质量

## 5. 代码实现示例

```python
# 嵌入模型升级示例
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('BAAI/bge-large-zh')  # 使用更好的中文嵌入模型

# 查询扩展示例
import synonyms
def expand_query(query):
    syns = synonyms.expand(query)
    return ' '.join(set(syns + query.split()))

# 冗余文档过滤示例
import numpy as np
def filter_duplicates(docs, threshold=0.9):
    embeddings = model.encode([doc['content'] for doc in docs])
    filtered = []
    for i, doc in enumerate(docs):
        if i == 0:
            filtered.append(doc)
            continue
        sims = np.dot(embeddings[:i], embeddings[i]) / (np.linalg.norm(embeddings[:i], axis=1) * np.linalg.norm(embeddings[i]))
        if not any(sim > threshold for sim in sims):
            filtered.append(doc)
    return filtered
```