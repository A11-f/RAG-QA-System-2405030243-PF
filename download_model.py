import requests
import json

print("正在下载嵌入模型 nomic-embed-text...")
response = requests.post(
    'http://localhost:11434/api/pull',
    json={'name': 'nomic-embed-text'},
    stream=True
)

for line in response.iter_lines():
    if line:
        data = json.loads(line)
        if 'status' in data:
            print(f"状态: {data['status']}", end='\r')
            if 'completed' in data:
                print(f"进度: {data['completed']}/{data['total']}")
print("\n嵌入模型下载完成！")

print("\n正在下载LLM模型 qwen2:0.5b...")
response = requests.post(
    'http://localhost:11434/api/pull',
    json={'name': 'qwen2:0.5b'},
    stream=True
)

for line in response.iter_lines():
    if line:
        data = json.loads(line)
        if 'status' in data:
            print(f"状态: {data['status']}", end='\r')
            if 'completed' in data:
                print(f"进度: {data['completed']}/{data['total']}")
print("\nLLM模型下载完成！")
