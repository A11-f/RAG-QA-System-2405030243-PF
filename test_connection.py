import requests
import json
import os
import config

print("=== 检查RAG系统状态 ===")

# 检查Ollama服务是否运行
print("\n1. 检查Ollama服务:")
try:
    response = requests.get(f'{config.OLLAMA_BASE_URL}/api/tags', timeout=5)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print("   ✓ Ollama服务正常运行")
        print(f"   可用模型: {[m['name'] for m in models]}")
    else:
        print(f"   ✗ Ollama服务返回错误: HTTP {response.status_code}")
except Exception as e:
    print(f"   ✗ Ollama服务连接失败: {e}")
    print(f"   请确保Ollama已安装并运行: ollama serve")

# 检查嵌入模型
print("\n2. 测试嵌入模型:")
try:
    test_text = "自然语言处理"
    response = requests.post(
        f"{config.OLLAMA_BASE_URL}/api/embeddings",
        json={"model": config.EMBEDDING_MODEL, "prompt": test_text},
        timeout=30
    )
    if response.status_code == 200:
        embedding = response.json().get("embedding", [])
        print(f"   ✓ 嵌入模型 {config.EMBEDDING_MODEL} 正常")
        print(f"   嵌入向量维度: {len(embedding)}")
    else:
        print(f"   ✗ 嵌入模型调用失败: HTTP {response.status_code}")
        print(f"   请先下载模型: ollama pull {config.EMBEDDING_MODEL}")
except Exception as e:
    print(f"   ✗ 嵌入模型调用失败: {e}")

# 检查向量数据库文件
print("\n3. 检查向量数据库:")
db_path = os.path.join(config.VECTOR_DB_DIR, 'vector_store.json')
if os.path.exists(db_path):
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    texts = data.get('texts', {})
    embeddings = data.get('embeddings', {})
    print(f"   ✓ 向量数据库文件存在")
    print(f"   文档块数量: {len(texts)}")
    print(f"   嵌入向量数量: {len(embeddings)}")
    
    if texts:
        print("\n   第一个文档内容预览:")
        first_text = list(texts.values())[0]
        print(f"   {first_text[:100]}..." if len(first_text) > 100 else f"   {first_text}")
else:
    print("   ✗ 向量数据库文件不存在")
    print("   请先构建知识库")

# 检查上传目录
print("\n4. 检查上传目录:")
upload_dir = config.UPLOAD_DIR
if os.path.exists(upload_dir):
    files = [f for f in os.listdir(upload_dir) if f.endswith(('.pdf', '.docx'))]
    print(f"   ✓ 上传目录存在")
    print(f"   文档数量: {len(files)}")
    if files:
        print(f"   文件列表: {files}")
else:
    print("   ✗ 上传目录不存在")
