import chromadb
import shutil
import os

print("Step 1: 删除旧数据库")
if os.path.exists("vector_db"):
    shutil.rmtree("vector_db")
if os.path.exists("test_db"):
    shutil.rmtree("test_db")

print("Step 2: 创建客户端")
client = chromadb.PersistentClient(path="test_db")

print("Step 3: 创建集合")
collection = client.create_collection("test")

print("Step 4: 添加文档")
collection.add(
    documents=["自然语言处理是计算机科学的分支"],
    metadatas=[{"source": "test"}],
    ids=["1"]
)
print("✓ 添加成功")

print("Step 5: 查询")
results = collection.query(query_texts=["什么是自然语言处理"], n_results=1)
print(f"✓ 查询成功: {results['documents'][0]}")
