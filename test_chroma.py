import chromadb
from chromadb.utils import embedding_functions
import shutil
import os

print("=== 测试ChromaDB ===")

# 删除旧的测试数据库
if os.path.exists("test_db"):
    shutil.rmtree("test_db")

try:
    # 创建客户端
    client = chromadb.PersistentClient(path="test_db")
    print("✓ 创建客户端成功")
    
    # 创建集合
    collection = client.create_collection("test_collection")
    print("✓ 创建集合成功")
    
    # 添加文档
    collection.add(
        documents=["自然语言处理是计算机科学的一个分支", "机器学习是人工智能的核心技术"],
        metadatas=[{"source": "doc1"}, {"source": "doc2"}],
        ids=["id1", "id2"]
    )
    print("✓ 添加文档成功")
    
    # 查询
    results = collection.query(
        query_texts=["什么是自然语言处理"],
        n_results=1
    )
    print("✓ 查询成功")
    print(f"结果文档: {results['documents'][0]}")
    print(f"来源: {results['metadatas'][0]}")
    
except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()
