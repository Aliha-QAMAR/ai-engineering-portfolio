import json
import math
import os
import re

class MemoryStore:
    def __init__(self, storage_file="agent_memory.json"):
        self.storage_file = storage_file
        self.memories = self._load_storage()

    def _load_storage(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, "r") as f:
                return json.load(f)
        return []

    def _save_storage(self):
        with open(self.storage_file, "w") as f:
            json.dump(self.memories, f, indent=2)

    def _get_embedding(self, text: str) -> list[float]:
        # Lightweight Deterministic Term-Frequency Vectorizer (Zero-dependency fallback)
        words = re.findall(r'\w+', text.lower())
        vocab = ["revenue", "sales", "drop", "eu", "missing", "data", "september", "product", "outlier", "q3"]
        vec = [words.count(w) for w in vocab]
        norm = math.sqrt(sum(v*v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def _cosine_similarity(self, vec1, vec2):
        return sum(a * b for a, b in zip(vec1, vec2))

    def store_memory(self, fact: str, source: str = "session_discovery", confidence: float = 0.95):
        embedding = self._get_embedding(fact)
        mem_id = len(self.memories) + 1
        memory_item = {
            "id": mem_id,
            "fact": fact,
            "source": source,
            "confidence": confidence,
            "embedding": embedding
        }
        self.memories.append(memory_item)
        self._save_storage()
        print(f"💾 [MEMORY STORED] ID {mem_id}: {fact}")

    def retrieve_memories(self, query: str, top_k: int = 2, threshold: float = 0.1) -> list[dict]:
        query_vec = self._get_embedding(query)
        scored = []
        for m in self.memories:
            sim = self._cosine_similarity(query_vec, m["embedding"])
            if sim >= threshold:
                scored.append((sim, m))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, m in scored[:top_k]:
            results.append({
                "id": m["id"],
                "fact": m["fact"],
                "source": m["source"],
                "confidence": m["confidence"],
                "relevance_score": round(score, 3)
            })
        return results

    def delete_memory(self, memory_id: int):
        self.memories = [m for m in self.memories if m["id"] != memory_id]
        self._save_storage()
        print(f"🗑️ [MEMORY DELETED] ID: {memory_id}")

if __name__ == "__main__":
    mem = MemoryStore()
    mem.store_memory("In sales_q3.csv, September revenue drop was caused by missing EU data.", source="sales_q3.csv")
    mem.store_memory("Product B has a higher margin than Product A.", source="margin_analysis.csv")

    query = "Why did revenue drop in September?"
    print(f"\n🔎 Searching Memory for: '{query}'")
    retrieved = mem.retrieve_memories(query)
    print("Retrieved Memories:", json.dumps(retrieved, indent=2))
    mem.delete_memory(2)
