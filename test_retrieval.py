from document_loader import load_document, split_documents
from vector_store import create_vector_store, get_retriever
from rag_chain import query_rag
import os

print("=== 测试检索功能 ===")

# 加载文档
upload_dir = 'uploads'
documents = []
for filename in os.listdir(upload_dir):
    if filename.endswith('.docx') and not filename.startswith('~$'):
        file_path = os.path.join(upload_dir, filename)
        doc = load_document(file_path)
        documents.append(doc)
        print(f'已加载: {filename}')

print(f'\n总文档数: {len(documents)}')

# 分割文档
split_docs = split_documents(documents)
print(f'文档块数量: {len(split_docs)}')

# 创建向量数据库
vs = create_vector_store(split_docs)
print(f'向量数据库文档数: {vs.get_document_count()}')

# 创建检索器
retriever = get_retriever(vs)

# 测试检索
questions = [
    '什么是自然语言处理',
    '什么是BERT',
    '什么是Transformer',
    '文本分类有哪些方法'
]

for question in questions:
    print(f'\n问题: {question}')
    result = query_rag(retriever, question)
    print(f'答案: {result["answer"][:200]}...' if len(result["answer"]) > 200 else f'答案: {result["answer"]}')
