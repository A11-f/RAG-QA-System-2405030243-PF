from document_loader import load_documents_from_dir, split_documents
from vector_store import create_vector_store, get_retriever
from rag_chain import query_rag
import config
import os


def main():
    print("=== 测试 RAG 问答系统 ===")
    
    data_dir = config.DATA_DIR
    
    if not os.listdir(data_dir):
        print(f"⚠️  {data_dir} 目录为空，请先放入测试文档")
        return
    
    print("1. 加载文档...")
    documents = load_documents_from_dir(data_dir)
    print(f"   加载了 {len(documents)} 份文档")
    
    print("2. 分块处理...")
    split_docs = split_documents(documents)
    print(f"   分成了 {len(split_docs)} 个文本块")
    
    print("3. 创建向量数据库...")
    vector_store = create_vector_store(split_docs)
    print("   ✓ 向量数据库创建成功")
    
    print("4. 获取检索器...")
    retriever = get_retriever(vector_store)
    print("   ✓ 检索器创建成功")
    
    print("\n=== 开始问答测试 ===")
    
    test_questions = [
        "什么是自然语言处理？",
        "词向量是什么？",
        "Transformer的主要结构是什么？",
        "BERT模型有什么特点？",
        "如何进行文本分类？",
        "火星上有生命吗？",
        "怎么制作蛋糕？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n问题 {i}: {question}")
        try:
            result = query_rag(retriever, question)
            print(f"回答: {result['answer']}")
            print("参考来源:")
            for doc in result["source_documents"]:
                print(f"  - {doc.get('metadata', {}).get('source', 'Unknown')}")
        except Exception as e:
            print(f"错误: {e}")


if __name__ == "__main__":
    main()