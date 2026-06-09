import os
import shutil
import time
import streamlit as st
from document_loader import load_document, split_documents, load_documents_from_dir
from vector_store import create_vector_store, load_vector_store, add_documents_to_vector_store, get_retriever
from rag_chain import query_rag, extract_sources
import config


def initialize_session_state():
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = load_vector_store()
    
    if "retriever" not in st.session_state:
        if st.session_state.vector_store:
            st.session_state.retriever = get_retriever(st.session_state.vector_store)
        else:
            st.session_state.retriever = None
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "document_count" not in st.session_state:
        st.session_state.document_count = 0
    
    if "chunk_count" not in st.session_state:
        st.session_state.chunk_count = 0
    
    if "processing_time" not in st.session_state:
        st.session_state.processing_time = 0
    
    if "similarity_scores" not in st.session_state:
        st.session_state.similarity_scores = []


def main():
    st.set_page_config(
        page_title="RAG 智能问答系统",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    initialize_session_state()
    
    st.title("🤖 RAG 智能问答系统")
    st.markdown("基于本地知识库的智能问答系统，支持文档上传、向量检索和多轮对话")
    
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        st.sidebar.header("📚 知识库管理")
        
        uploaded_files = st.sidebar.file_uploader(
            "上传文档 (PDF/DOCX)",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            help="支持PDF和DOCX格式的文档文件"
        )
        
        use_sample_docs = st.sidebar.checkbox("使用示例文档", help="使用内置的5份NLP相关示例文档")
        
        if st.sidebar.button("🔄 构建知识库", type="primary", use_container_width=True):
            with st.spinner("正在处理文档..."):
                start_time = time.time()
                all_docs = []
                
                if use_sample_docs:
                    docs = load_documents_from_dir(config.DATA_DIR)
                    all_docs.extend(docs)
                    st.sidebar.info(f"已加载 {len(docs)} 份示例文档")
                
                if uploaded_files:
                    app_dir = os.path.dirname(os.path.abspath(__file__))
                    local_upload_dir = os.path.join(app_dir, "local_uploads")
                    os.makedirs(local_upload_dir, exist_ok=True)
                    
                    for uploaded_file in uploaded_files:
                        temp_path = os.path.join(local_upload_dir, uploaded_file.name)
                        try:
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            doc = load_document(temp_path)
                            all_docs.append(doc)
                        except Exception as e:
                            st.sidebar.error(f"处理文件 {uploaded_file.name} 时出错: {e}")
                
                if all_docs:
                    split_docs = split_documents(all_docs)
                    
                    if st.session_state.vector_store is None:
                        st.session_state.vector_store = create_vector_store(split_docs)
                        st.session_state.vector_store.persist()
                    else:
                        add_documents_to_vector_store(st.session_state.vector_store, split_docs)
                    
                    st.session_state.retriever = get_retriever(st.session_state.vector_store)
                    
                    st.session_state.document_count += len(all_docs)
                    st.session_state.chunk_count += len(split_docs)
                    
                    processing_time = time.time() - start_time
                    st.session_state.processing_time = round(processing_time, 2)
                    
                    st.sidebar.success(f"✅ 知识库构建成功！\n⏱️ 耗时: {st.session_state.processing_time}秒")
                else:
                    st.sidebar.warning("请先上传文档或勾选使用示例文档")
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 知识库状态")
        
        if st.session_state.vector_store:
            st.sidebar.metric("📄 文档数量", st.session_state.document_count)
            st.sidebar.metric("📝 文本块数量", st.session_state.chunk_count)
            st.sidebar.metric("⏱️ 最近处理耗时", f"{st.session_state.processing_time}秒")
        else:
            st.sidebar.info("知识库尚未构建")
        
        if st.sidebar.button("🗑️ 清空知识库", use_container_width=True):
            if os.path.exists(config.VECTOR_DB_DIR):
                shutil.rmtree(config.VECTOR_DB_DIR)
                os.makedirs(config.VECTOR_DB_DIR)
            
            st.session_state.vector_store = None
            st.session_state.retriever = None
            st.session_state.document_count = 0
            st.session_state.chunk_count = 0
            st.session_state.chat_history = []
            st.session_state.similarity_scores = []
            st.sidebar.success("✅ 知识库已清空")
    
    with col2:
        st.subheader("💬 问答交互")
        
        question = st.text_input(
            "请输入你的问题：",
            placeholder="例如：什么是自然语言处理？",
            help="输入与知识库相关的问题"
        )
        
        if st.button("🚀 提问", type="primary", use_container_width=True):
            if not st.session_state.retriever:
                st.warning("⚠️ 请先构建知识库")
            elif not question:
                st.warning("⚠️ 请输入问题")
            else:
                with st.spinner("🤔 正在分析问题..."):
                    start_time = time.time()
                    try:
                        result = query_rag(st.session_state.retriever, question, st.session_state.chat_history)
                        
                        processing_time = time.time() - start_time
                        
                        st.session_state.chat_history.append({
                            "role": "user",
                            "content": question
                        })
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": result["answer"],
                            "sources": extract_sources(result["source_documents"]),
                            "processing_time": round(processing_time, 2),
                            "context": result.get("context", "")
                        })
                        
                    except Exception as e:
                        st.error(f"❌ 查询出错: {e}")
        
        st.markdown("---")
        st.subheader("📜 对话历史")
        
        if st.session_state.chat_history:
            for i in range(len(st.session_state.chat_history)-1, -1, -2):
                if i > 0:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.write(st.session_state.chat_history[i]["content"])
                        
                        with st.expander("📋 详细信息"):
                            st.info(f"⏱️ 处理耗时: {st.session_state.chat_history[i].get('processing_time', 0)}秒")
                            
                            if "sources" in st.session_state.chat_history[i]:
                                st.subheader("参考来源")
                                for idx, source in enumerate(st.session_state.chat_history[i]["sources"], 1):
                                    st.write(f"{idx}. **{source['source']}** (相似度: {source['similarity_score']:.4f})")
                
                with st.chat_message("user", avatar="👤"):
                    if i > 0:
                        st.write(st.session_state.chat_history[i-1]["content"])
                    else:
                        if st.session_state.chat_history:
                            st.write(st.session_state.chat_history[0]["content"])
        else:
            st.info("暂无对话记录，请先构建知识库并提问")


if __name__ == "__main__":
    main()