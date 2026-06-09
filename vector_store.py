import os
import json
import hashlib
from typing import List, Optional, Dict, Any
import requests
import config


class SimpleVectorStore:
    def __init__(self):
        self.embeddings: Dict[int, List[float]] = {}
        self.texts: Dict[int, str] = {}
        self.metadatas: Dict[int, Dict[str, Any]] = {}
        self.embedding_cache: Dict[str, List[float]] = {}
        self.next_id = 0
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None):
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        for text, metadata in zip(texts, metadatas):
            text_hash = self._hash_text(text)
            
            if text_hash in self.embedding_cache:
                embedding = self.embedding_cache[text_hash]
            else:
                embedding = self._get_embedding(text)
                self.embedding_cache[text_hash] = embedding
            
            self.texts[self.next_id] = text
            self.metadatas[self.next_id] = metadata
            self.embeddings[self.next_id] = embedding
            self.next_id += 1
    
    def similarity_search(self, query: str, k: int = 3):
        query_hash = self._hash_text(query)
        
        if query_hash in self.embedding_cache:
            query_embedding = self.embedding_cache[query_hash]
        else:
            query_embedding = self._get_embedding(query)
            self.embedding_cache[query_hash] = query_embedding
        
        if not query_embedding:
            return []
        
        scores = []
        for doc_id, embedding in self.embeddings.items():
            if embedding:
                score = self._cosine_similarity(query_embedding, embedding)
                scores.append((doc_id, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        top_k = scores[:k]
        
        results = []
        for doc_id, score in top_k:
            if score > 0.0:
                results.append({
                    'page_content': self.texts[doc_id],
                    'metadata': {**self.metadatas[doc_id], 'similarity_score': round(score, 4)}
                })
        
        return results
    
    def _get_embedding(self, text: str) -> List[float]:
        try:
            response = requests.post(
                f"{config.OLLAMA_BASE_URL}/api/embeddings",
                json={"model": config.EMBEDDING_MODEL, "prompt": text},
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get("embedding", [])
        except requests.exceptions.RequestException as e:
            print(f"获取嵌入向量失败: {e}")
        return []
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
    
    def _hash_text(self, text: str) -> str:
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def persist(self, persist_directory: str = None):
        if persist_directory is None:
            persist_directory = config.VECTOR_DB_DIR
        
        os.makedirs(persist_directory, exist_ok=True)
        
        data = {
            'embeddings': {str(k): v for k, v in self.embeddings.items()},
            'texts': {str(k): v for k, v in self.texts.items()},
            'metadatas': {str(k): v for k, v in self.metadatas.items()},
            'next_id': self.next_id
        }
        
        with open(os.path.join(persist_directory, 'vector_store.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self, persist_directory: str = None):
        if persist_directory is None:
            persist_directory = config.VECTOR_DB_DIR
        
        file_path = os.path.join(persist_directory, 'vector_store.json')
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.embeddings = {int(k): v for k, v in data.get('embeddings', {}).items()}
            self.texts = {int(k): v for k, v in data.get('texts', {}).items()}
            self.metadatas = {int(k): v for k, v in data.get('metadatas', {}).items()}
            self.next_id = data.get('next_id', 0)
            
            for text in self.texts.values():
                text_hash = self._hash_text(text)
                doc_id = next(k for k, v in self.texts.items() if v == text)
                if text_hash not in self.embedding_cache:
                    self.embedding_cache[text_hash] = self.embeddings.get(doc_id, [])
            
            return True
        except Exception as e:
            print(f"加载向量数据库失败: {e}")
            return False
    
    def get_document_count(self) -> int:
        return len(self.texts)


def create_vector_store(documents: List[Dict], persist_directory: Optional[str] = None) -> SimpleVectorStore:
    vs = SimpleVectorStore()
    
    texts = [doc["page_content"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    
    vs.add_texts(texts=texts, metadatas=metadatas)
    
    if persist_directory:
        vs.persist(persist_directory)
    
    return vs


def load_vector_store(persist_directory: Optional[str] = None) -> Optional[SimpleVectorStore]:
    if persist_directory is None:
        persist_directory = config.VECTOR_DB_DIR
    
    vs = SimpleVectorStore()
    if vs.load(persist_directory):
        return vs
    return None


def add_documents_to_vector_store(vector_store: SimpleVectorStore, documents: List[Dict]):
    texts = [doc["page_content"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    vector_store.add_texts(texts=texts, metadatas=metadatas)
    vector_store.persist()


class SimpleRetriever:
    def __init__(self, vector_store: SimpleVectorStore, k: int = 3):
        self.vector_store = vector_store
        self.k = k
    
    def get_relevant_documents(self, query: str):
        return self.vector_store.similarity_search(query, k=self.k)


def get_retriever(vector_store: SimpleVectorStore, k: int = None) -> SimpleRetriever:
    if k is None:
        k = config.TOP_K
    return SimpleRetriever(vector_store, k=k)
