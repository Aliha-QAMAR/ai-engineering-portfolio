import os
import csv
from datetime import datetime
import chromadb
from sentence_transformers import SentenceTransformer
from chunking import process_document

chroma_client = chromadb.Client()
model = SentenceTransformer('all-MiniLM-L6-v2')

def create_default_files():
    if not os.path.exists("policy.md"):
        dummy_content = """# Company Security & Leave Policy

## Section 1: Security
All employees must use Multi-Factor Authentication (MFA) to access corporate systems. Passwords must be at least 16 characters long and changed every 90 days. Physical security is also critical. Tailgating is strictly prohibited in the server rooms. Visitors must be escorted by an authorized badge holder at all times.

## Section 2: Leaves
Annual leaves consist of 20 paid days off per calendar year. Employees must submit leave requests at least 2 weeks in advance through the HR portal. Sick leave requires a medical certificate if the absence exceeds three consecutive business days. Maternity leave is fully paid for 12 weeks.
"""
        with open("policy.md", "w", encoding="utf-8") as f:
            f.write(dummy_content)
        print("Created default 'policy.md' file automatically!")

def ingest_documents(file_paths, chunk_size, overlap, collection_name):
    print(f"\n================ Ingesting with Chunk Size: {chunk_size} ================")
    collection = chroma_client.get_or_create_collection(name=collection_name)    
    chunk_id_counter = 0
    all_stored_chunks = [] 
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        chunks = process_document(file_path, chunk_size=chunk_size, overlap=overlap)   
        
        for chunk_data in chunks:
            chunk_text = chunk_data["text"]            
            metadata = chunk_data["metadata"]
            metadata["chunk_size_used"] = chunk_size
            
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

def save_results_to_csv(query, search_type, matches, csv_filename="search_results.csv"):
    file_exists = os.path.exists(csv_filename)
    
    with open(csv_filename, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Agar file pehle se nahi bani hui, toh headers likhein
        if not file_exists:
            writer.writerow([
                "Timestamp", 
                "Query", 
                "Search Type", 
                "Rank", 
                "Score", 
                "Matched Text", 
                "Source File", 
                "Page", 
                "Chunk Size"
            ])
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for rank, (text, score, meta) in enumerate(matches, 1):
            writer.writerow([
                timestamp,
                query,
                search_type,
                rank,
                f"{score:.4f}" if isinstance(score, float) else score,
                text.replace("\n", " ").strip(),
                meta.get("source", "N/A"),
                meta.get("page", "N/A"),
                meta.get("chunk_size_used", "N/A")
            ])
            
    print(f"Saved {search_type} results to '{csv_filename}'!")

def search_system(query, collection, stored_chunks, top_k=2):
    # 1. SEMANTIC SEARCH
    query_vector = model.encode(query).tolist()
    vector_results = collection.query(query_embeddings=[query_vector], n_results=top_k)
    
    semantic_matches = []
    print(f"\n--- SEMANTIC SEARCH RESULTS FOR: '{query}' ---")
    for i in range(len(vector_results['documents'][0])):
        text = vector_results['documents'][0][i]
        score = vector_results['distances'][0][i]
        meta = vector_results['metadatas'][0][i]
        semantic_matches.append((text, score, meta))
        
        print(f"Match {i+1}: [Score: {score:.4f}]")
        print(f"Text: '{text}'")
        print(f"Meta: {meta}\n")
        
    save_results_to_csv(query, "Semantic", semantic_matches)
        
    # 2. KEYWORD SEARCH
    print(f"--- KEYWORD SEARCH RESULTS FOR: '{query}' ---")
    keyword_matches = []
    query_words = query.lower().split()
    
    for chunk in stored_chunks:
        score = sum(1 for word in query_words if word in chunk["text"].lower())
        if score > 0:
            keyword_matches.append((chunk["text"], score, chunk["meta"]))
            
    # Score ke mutabiq sort karein descending order mein
    keyword_matches.sort(key=lambda x: x[1], reverse=True)
    top_keyword_matches = keyword_matches[:top_k]
    
    for i, (text, score, meta) in enumerate(top_keyword_matches, 1):
        print(f"Match {i+1}: [Matched words: {score}]")
        print(f"Text: '{text}'")
        print(f"Meta: {meta}\n")
        
    save_results_to_csv(query, "Keyword", top_keyword_matches)

if __name__ == "__main__":
    create_default_files()
    
    my_files = ["policy.md"]
    
    collection_small, chunks_small = ingest_documents(
        file_paths=my_files, 
        chunk_size=400, 
        overlap=50, 
        collection_name="small_chunks"
    )
    
    collection_large, chunks_large = ingest_documents(
        file_paths=my_files, 
        chunk_size=1000, 
        overlap=100, 
        collection_name="large_chunks"
    )
    
    print("\n--- MANUAL INSPECTION OF STORED CHUNKS (Small Chunks Collection) ---")
    if chunks_small:
        for item in chunks_small[:2]:
            print(f"ID: {item['id']} | Content: '{item['text']}' | Meta: {item['meta']}")

        search_query = "What is the password requirement?"
        search_system(search_query, collection_small, chunks_small)
    else:
        print("No chunks were stored. Make sure your files exist!")
        
    print("\n" + "="*50)
    print("CHUNKING DECISION EXPLANATION:")
    print("1. Why 400 characters? Great for precise lookup of specific rules (e.g., password length). High precision, less noise.")
    print("2. Why 1000-1200 characters? Better for complex policies (like HR Leave rules) where context spans across multiple sentences. It keeps related ideas together but adds some extra text (noise) to the LLM prompt.")
    print("="*50)