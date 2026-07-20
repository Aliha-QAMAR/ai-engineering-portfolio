import time

class RAGRetriever:
    """
    Coordinates query embedding, vector database search, similarity threshold filtering,
    and returns ranked text chunks with detailed retrieval diagnostics.
    """
    def __init__(self, vector_db, embedding_manager):
        self.db = vector_db
        self.em = embedding_manager

    def retrieve(self, query: str, top_k: int = 5, threshold: float = 0.45, doc_ids: list[int] = None) -> dict:
        """
        Retrieves top_k chunks matching the query that exceed similarity threshold.
        Returns a dict containing:
          - 'chunks': list of chunks above threshold
          - 'all_retrieved': list of all top_k retrieved chunks before threshold filter
          - 'latency_ms': float search latency
          - 'diagnostics': metadata diagnostic details
        """
        start_time = time.time()
        
        # 1. Embed query
        query_vector = self.em.embed_query(query)
        
        # 2. Query Vector DB
        all_retrieved = self.db.query_similarity(query_vector, top_k=top_k, doc_ids=doc_ids)
        
        # 3. Filter by similarity threshold
        filtered_chunks = [c for c in all_retrieved if c["similarity_score"] >= threshold]
        
        latency_ms = (time.time() - start_time) * 1000
        
        # 4. Formulate retrieval diagnostics
        passed_filter = len(filtered_chunks)
        highest_score = all_retrieved[0]["similarity_score"] if all_retrieved else 0.0
        
        # Calculate overlap words to show diagnostics
        query_words = set(query.lower().split())
        
        diagnostics = {
            "highest_similarity_score": highest_score,
            "passed_threshold_count": passed_filter,
            "total_retrieved_count": len(all_retrieved),
            "threshold_applied": threshold,
            "top_k_applied": top_k,
            "latency_ms": latency_ms,
            "query_keywords": list(query_words),
            "status": "success" if passed_filter > 0 else ("refused_low_similarity" if all_retrieved else "refused_no_documents")
        }
        
        return {
            "chunks": filtered_chunks,
            "all_retrieved": all_retrieved,
            "latency_ms": latency_ms,
            "diagnostics": diagnostics
        }
