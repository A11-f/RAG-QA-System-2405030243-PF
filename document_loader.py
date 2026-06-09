import os
from typing import List
from PyPDF2 import PdfReader
from docx import Document
import config


def load_pdf(file_path: str) -> str:
    text = ""
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


def load_docx(file_path: str) -> str:
    doc = Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text


def load_document(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        text = load_pdf(file_path)
    elif ext == ".docx":
        text = load_docx(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {ext}")
    
    return {
        "page_content": text,
        "metadata": {"source": os.path.basename(file_path), "path": file_path}
    }


def load_documents_from_dir(directory: str) -> List:
    documents = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            ext = os.path.splitext(filename)[1].lower()
            if ext in [".pdf", ".docx"]:
                try:
                    doc = load_document(file_path)
                    documents.append(doc)
                except Exception as e:
                    print(f"加载文件 {filename} 时出错: {e}")
    return documents


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        
        if end < text_length:
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            split_pos = max(last_period, last_newline)
            
            if split_pos > chunk_size // 2:
                chunk = chunk[:split_pos + 1]
                end = start + split_pos + 1
        
        chunks.append(chunk)
        start = end - chunk_overlap
    
    return chunks


def split_documents(documents: List) -> List:
    split_docs = []
    for doc in documents:
        chunks = split_text(doc["page_content"], config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        for i, chunk in enumerate(chunks):
            split_docs.append({
                "page_content": chunk,
                "metadata": {
                    **doc["metadata"],
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            })
    return split_docs