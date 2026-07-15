import os
import chromadb
from sentence_transformers import SentenceTransformer
from chunking import chunk_text_with_overlap
mock_documents = {
    "security_policy.md": {
        "page_1": "All employees must use Multi-Factor Authentication (MFA) to access corporate systems. Passwords must be at least 16 characters long and changed every 90 days.",
        "page_2": "Physical security is also critical. Tailgating is strictly prohibited in the server rooms. Visitors must be escorted by an authorized badge holder at all times."
    },
    "leave_policy.md": {
        "page_1": "Annual leaves consist of 20 paid days off per calendar year. Employees must submit leave requests at least 2 weeks in advance through the HR portal.",
        "page_2": "Sick leave requires a medical certificate if the absence exceeds three consecutive business days. Maternity leave is fully paid for 12 weeks."
    }
}
chroma_client = chromadb.Client()
model = SentenceTransformer('all-MiniLM-L6-v2')
def ingest_documents(chunk_size, overlap, collection_name):
    print(f"\n================ Ingesting with Chunk Size: {chunk_size} ================")
    collection = chroma_client.get_or_create_collection(name=collection_name)    
    chunk_id_counter = 0
    all_stored_chunks = [] 
    
    for filename, pages in mock_documents.items():
        for page_num, text in pages.items():
            chunks = chunk_text_with_overlap(text, chunk_size=chunk_size, overlap=overlap)   
            for chunk_data in chunks:
                chunk_text = chunk_data["text"]            
                # Metadata create kar rhe hn
                metadata = {
                    "source": filename,
                    "page": page_num,
                    "start_character": chunk_data["start_idx"],
                    "chunk_size_used": chunk_size
                }
                embedding = model.encode(chunk_text).tolist()
                chunk_id = f"{collection_name}_id_{chunk_id_counter}"
                collection.add(
                    embeddings=[embedding],
                    documents=[chunk_text],
                    metadatas=[metadata],
                    ids=[chunk_id]
                )
                
                all_stored_chunks.append({"id": chunk_id, "text": chunk_text, "meta": metadata})
                chunk_id_counter += 1
                
    print(f"Successfully stored {chunk_id_counter} chunks into '{collection_name}' collection.")
    return collection, all_stored_chunks

def search_system(query, collection, stored_chunks, top_k=2):
    query_vector = model.encode(query).tolist()
    vector_results = collection.query(query_embeddings=[query_vector], n_results=top_k)
    
    print(f"\n--- SEMANTIC SEARCH RESULTS FOR: '{query}' ---")
    for i in range(len(vector_results['documents'][0])):
        print(f"Match {i+1}: [Score: {vector_results['distances'][0][i]:.4f}]")
        print(f"Text: '{vector_results['documents'][0][i]}'")
        print(f"Meta: {vector_results['metadatas'][0][i]}\n")
    print(f"--- KEYWORD SEARCH RESULTS FOR: '{query}' ---")
    keyword_matches = []
    query_words = query.lower().split()
    
    for chunk in stored_chunks:
        score = sum(1 for word in query_words if word in chunk["text"].lower())
        if score > 0:
            keyword_matches.append((chunk, score))
    keyword_matches.sort(key=lambda x: x[1], reverse=True)
    
    for i, (chunk, score) in enumerate(keyword_matches[:top_k]):
        print(f"Match {i+1}: [Matched words: {score}]")
        print(f"Text: '{chunk['text']}'")
        print(f"Meta: {chunk['meta']}\n")

if __name__ == "__main__":
    collection_small, chunks_small = ingest_documents(chunk_size=400, overlap=50, collection_name="small_chunks")
    collection_large, chunks_large = ingest_documents(chunk_size=1000, overlap=100, collection_name="large_chunks")
    print("\n--- MANUAL INSPECTION OF STORED CHUNKS (Small Chunks Collection) ---")
    for item in chunks_small[:2]: # Sirf pehle 2 chunks inspect karte hain
        print(f"ID: {item['id']} | Content: '{item['text']}' | Meta: {item['meta']}")

    search_query = "What is the password requirement?"
    search_system(search_query, collection_small, chunks_small)
    print("\n" + "="*50)
    print("CHUNKING DECISION EXPLANATION:")
    print("1. Why 400 characters? Great for precise lookup of specific rules (e.g., password length). High precision, less noise.")
    print("2. Why 1000-1200 characters? Better for complex policies (like HR Leave rules) where context spans across multiple sentences. It keeps related ideas together but adds some extra text (noise) to the LLM prompt.")
    print("="*50)