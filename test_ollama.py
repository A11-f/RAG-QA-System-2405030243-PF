import requests
import config


def test_ollama_connection():
    try:
        response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            print("✅ Ollama 连接成功")
            models = response.json().get("models", [])
            print(f"可用模型: {[model['name'] for model in models]}")
            return True
        else:
            print(f"❌ Ollama 连接失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama 连接异常: {e}")
        return False


def test_llm_inference():
    try:
        data = {
            "model": config.LLM_MODEL,
            "prompt": "你好，请用一句话介绍你自己。",
            "stream": False
        }
        response = requests.post(f"{config.OLLAMA_BASE_URL}/api/generate", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ LLM 推理成功")
            print(f"回答: {result.get('response', '')}")
            return True
        else:
            print(f"❌ LLM 推理失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ LLM 推理异常: {e}")
        return False


if __name__ == "__main__":
    print("=== 测试 Ollama API ===")
    conn_ok = test_ollama_connection()
    if conn_ok:
        test_llm_inference()