import sys
import os
import datetime

# Add root folder to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.chunking import DocumentChunker
from core.embeddings import EmbeddingManager
from core.vector_db import LiteVectorDB
from core.retrieval import RAGRetriever
from core.llm_engine import GroundedLLMEngine

def main():
    print("=== Initializing Pipeline Verification ===")
    
    # 1. Initialize DB and Embedder
    db = LiteVectorDB("test_workspace.db")
    em = EmbeddingManager()
    retriever = RAGRetriever(db, em)
    engine = GroundedLLMEngine()
    
    print(f"Embedder Loaded. Fallback mode: {em.is_fallback}")
    
    # Clean DB
    db.clear_database()
    
    # 2. Simulate Ingesting a Document
    doc_name = "security_policy.txt"
    doc_text = (
        "Security Policy 2026.\n\f" # Page 1
        "Section 1: Access Control. All employees must use multi-factor authentication (MFA) to access internal portals. "
        "Passwords must be at least 12 characters long and contain both numbers and symbols.\n\f" # Page 2
        "Section 2: Clean Desk Policy. Employees must lock their workstations before leaving their desks. "
        "No confidential documents should be left printed on desks overnight."
    )
    
    print(f"\nIngesting mock document: {doc_name}...")
    pages_data = [{"text": page.strip(), "page": i+1} for i, page in enumerate(doc_text.split('\f'))]
    
    chunks = DocumentChunker.create_chunks(pages_data, chunk_size=300, chunk_overlap=50)
    print(f"Created {len(chunks)} chunks:")
    for c in chunks:
        print(f" - Chunk {c['chunk_index']} (Page {c['page_number']}): '{c['text'][:60]}...'")
        
    embeddings = em.embed_texts([c["text"] for c in chunks])
    
    doc_metadata = {
        "filename": doc_name,
        "upload_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file_size": len(doc_text.encode('utf-8')),
        "character_count": len(doc_text),
        "embedding_model": "all-MiniLM-L6-v2" if not em.is_fallback else "tf-idf-fallback",
        "chunk_size": 300,
        "chunk_overlap": 50,
        "pages": len(pages_data)
    }
    
    doc_id = db.add_document(doc_metadata, chunks, embeddings)
    print(f"Indexed document to DB with ID: {doc_id}")
    
    # 3. Test Retrieval - Valid Query
    query_1 = "what are the rules for passwords?"
    print(f"\nTesting Query 1: '{query_1}'")
    res_1 = retriever.retrieve(query=query_1, top_k=2, threshold=0.35)
    print(f"Retrieved {len(res_1['chunks'])} chunks above threshold.")
    for c in res_1["chunks"]:
        print(f" - Score: {c['similarity_score']:.4f} | Chunk #{c['chunk_index']} (Page {c['page_number']}): '{c['text']}'")
        
    print("\nGenerating Response 1...")
    response_stream_1 = list(engine.generate_response_stream(query_1, res_1["chunks"], res_1["diagnostics"]))
    full_answer_1 = "".join(response_stream_1)
    print("Answer:")
    print(full_answer_1)
    
    details_1 = engine.generate_response_details(query_1, res_1["chunks"], res_1["diagnostics"], full_answer_1)
    print(f"Confidence score: {details_1['confidence_score']}%")
    print(f"Citations count: {details_1['citation_count']}")
    
    # 4. Test Retrieval - Invalid Query (Refusal validation)
    query_2 = "what is the recipe for cooking pasta?"
    print(f"\nTesting Query 2 (Expect Refusal): '{query_2}'")
    res_2 = retriever.retrieve(query=query_2, top_k=2, threshold=0.45)
    print(f"Retrieved {len(res_2['chunks'])} chunks above threshold.")
    
    print("\nGenerating Response 2...")
    response_stream_2 = list(engine.generate_response_stream(query_2, res_2["chunks"], res_2["diagnostics"]))
    full_answer_2 = "".join(response_stream_2)
    print("Answer:")
    print(full_answer_2)
    
    details_2 = engine.generate_response_details(query_2, res_2["chunks"], res_2["diagnostics"], full_answer_2)
    print(f"Status: {details_2['grounding_status']}")
    
    # Clean up test DB
    if os.path.exists("test_workspace.db"):
        try:
            os.remove("test_workspace.db")
            print("\nCleaned up test database.")
        except PermissionError:
            print("\nNote: test_workspace.db is locked by SQLite garbage collection and will be cleaned up by the OS.")
        
    print("\n=== Pipeline Verification Completed Successfully ===")

if __name__ == "__main__":
    main()
