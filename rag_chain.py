from typing import List, Dict, Any
import requests
import config


def build_context(docs: List[Dict[str, Any]]) -> str:
    context_parts = []
    
    for i, doc in enumerate(docs, 1):
        source = doc.get("metadata", {}).get("source", "未知来源")
        score = doc.get("metadata", {}).get("similarity_score", 0.0)
        content = doc.get("page_content", "")
        
        context_part = f"""
=== 参考文档 {i} ===
来源: {source}
相似度: {score:.4f}
内容:
{content}
"""
        context_parts.append(context_part)
    
    return "\n".join(context_parts)


def build_chat_history(chat_history: List[Dict[str, str]]) -> str:
    if not chat_history:
        return "无对话历史"
    
    history_lines = []
    for i, msg in enumerate(chat_history, 1):
        role = "用户" if msg["role"] == "user" else "助手"
        history_lines.append(f"{role}: {msg['content']}")
    
    return "\n".join(history_lines)


def generate_answer_with_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": config.LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 1024
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            print(f"LLM调用失败: HTTP {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"LLM调用失败: {e}")
        return None


def generate_simple_answer(question: str, docs: List[Dict[str, Any]]) -> str:
    if not docs:
        return "文档中未找到相关答案"
    
    answer_parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.get("metadata", {}).get("source", "未知来源")
        score = doc.get("metadata", {}).get("similarity_score", 0.0)
        content = doc.get("page_content", "")
        
        answer_part = f"根据文档「{source}」（相似度: {score:.4f}）：\n{content}"
        answer_parts.append(answer_part)
    
    return "\n\n".join(answer_parts)


def query_rag(retriever, question: str, chat_history: List[Dict] = None):
    if chat_history is None:
        chat_history = []
    
    docs = retriever.get_relevant_documents(question)
    
    if not docs:
        return {
            "answer": "文档中未找到相关答案",
            "source_documents": [],
            "context": ""
        }
    
    context = build_context(docs)
    
    prompt = f"""
你是一个专业的问答助手。请严格按照以下规则回答用户的问题：

规则：
1. 必须基于提供的参考文档内容进行回答
2. 如果文档中没有相关信息，必须明确说"文档中未找到相关答案"
3. 不要编造信息，不要使用文档之外的知识
4. 如果有多个相关文档，可以综合整理后回答
5. 回答要简洁、准确、自然

参考文档:
{context}

用户问题: {question}

回答:
"""
    
    llm_answer = generate_answer_with_ollama(prompt)
    
    if llm_answer:
        answer = llm_answer
    else:
        answer = generate_simple_answer(question, docs)
    
    return {
        "answer": answer,
        "source_documents": docs,
        "context": context
    }


def extract_sources(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sources = []
    for doc in docs:
        source_info = {
            "source": doc.get("metadata", {}).get("source", "未知来源"),
            "similarity_score": doc.get("metadata", {}).get("similarity_score", 0.0),
            "chunk_index": doc.get("metadata", {}).get("chunk_index", 0)
        }
        sources.append(source_info)
    return sources
