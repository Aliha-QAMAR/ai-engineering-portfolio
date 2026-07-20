import sqlite3
import numpy as np
import io
import time
import os

class LiteVectorDB:
    """
    A lightweight, production-grade custom vector database using SQLite
    for relational metadata storage and NumPy for exact Cosine Similarity vector search.
    """
    def __init__(self, db_path: str = "workspace.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        # We enable foreign keys for cascade deletes
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            # Create documents table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT UNIQUE,
                    upload_date TEXT,
                    file_size INTEGER,
                    character_count INTEGER,
                    chunk_count INTEGER,
                    embedding_model TEXT,
                    chunk_size INTEGER,
                    chunk_overlap INTEGER,
                    pages INTEGER
                )
            """)
            # Create chunks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id INTEGER,
                    chunk_index INTEGER,
                    text TEXT,
                    page_number INTEGER,
                    char_start INTEGER,
                    char_end INTEGER,
                    FOREIGN KEY (doc_id) REFERENCES documents (id) ON DELETE CASCADE
                )
            """)
            # Create embeddings table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    chunk_id INTEGER PRIMARY KEY,
                    vector BLOB,
                    FOREIGN KEY (chunk_id) REFERENCES chunks (id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def add_document(self, doc_metadata: dict, chunks: list[dict], embeddings: list[list[float]]) -> int:
        """
        Ingests a document, its text chunks, and their vector embeddings.
        All-or-nothing transaction.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                # 1. Insert document
                cursor.execute("""
                    INSERT OR REPLACE INTO documents 
                    (filename, upload_date, file_size, character_count, chunk_count, embedding_model, chunk_size, chunk_overlap, pages)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    doc_metadata["filename"],
                    doc_metadata["upload_date"],
                    doc_metadata["file_size"],
                    doc_metadata["character_count"],
                    len(chunks),
                    doc_metadata["embedding_model"],
                    doc_metadata["chunk_size"],
                    doc_metadata["chunk_overlap"],
                    doc_metadata["pages"]
                ))
                doc_id = cursor.lastrowid

                # 2. Insert chunks and embeddings
                for chunk, vec in zip(chunks, embeddings):
                    cursor.execute("""
                        INSERT INTO chunks (doc_id, chunk_index, text, page_number, char_start, char_end)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        doc_id,
                        chunk["chunk_index"],
                        chunk["text"],
                        chunk["page_number"],
                        chunk["char_start"],
                        chunk["char_end"]
                    ))
                    chunk_id = cursor.lastrowid

                    # Serialize float vector to byte array for SQLite storage
                    vec_arr = np.array(vec, dtype=np.float32)
                    vec_bytes = vec_arr.tobytes()

                    cursor.execute("""
                        INSERT INTO embeddings (chunk_id, vector)
                        VALUES (?, ?)
                    """, (chunk_id, vec_bytes))

                conn.commit()
                return doc_id
            except Exception as e:
                conn.rollback()
                raise e

    def delete_document(self, doc_id: int):
        """
        Deletes a document from the system. Cascadings handle chunks and embeddings.
        """
        with self._get_connection() as conn:
            conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            conn.commit()

    def get_all_documents(self) -> list[dict]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM documents ORDER BY id DESC").fetchall()
            return [dict(row) for row in rows]

    def get_document(self, doc_id: int) -> dict:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
            return dict(row) if row else None

    def get_document_chunks(self, doc_id: int) -> list[dict]:
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT c.id, c.chunk_index, c.text, c.page_number, c.char_start, c.char_end 
                FROM chunks c 
                WHERE c.doc_id = ? 
                ORDER BY c.chunk_index ASC
            """, (doc_id,)).fetchall()
            return [dict(row) for row in rows]

    def query_similarity(self, query_vector: list[float], top_k: int = 5, doc_ids: list[int] = None) -> list[dict]:
        """
        Queries the database for top_k most similar chunks.
        Applies document scope filtering if doc_ids is supplied.
        """
        q_vec = np.array(query_vector, dtype=np.float32)
        # Normalize just in case
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        results = []
        with self._get_connection() as conn:
            # Construct base query
            sql = """
                SELECT c.id, c.doc_id, c.chunk_index, c.text, c.page_number, c.char_start, c.char_end,
                       d.filename as doc_name, d.embedding_model, d.chunk_size, e.vector
                FROM chunks c
                JOIN documents d ON c.doc_id = d.id
                JOIN embeddings e ON c.id = e.chunk_id
            """
            params = []
            if doc_ids:
                placeholders = ",".join(["?"] * len(doc_ids))
                sql += f" WHERE c.doc_id IN ({placeholders})"
                params.extend(doc_ids)

            rows = conn.execute(sql, params).fetchall()
            if not rows:
                return []

            # Perform in-memory cosine similarity scanning
            all_chunks = []
            all_vectors = []
            
            for row in rows:
                row_dict = dict(row)
                vec_bytes = row_dict.pop('vector')
                vec = np.frombuffer(vec_bytes, dtype=np.float32)
                
                # Check dimensional consistency
                if len(vec) == len(q_vec):
                    all_chunks.append(row_dict)
                    all_vectors.append(vec)

            if not all_vectors:
                return []

            all_vectors = np.array(all_vectors)
            
            # Compute cosine similarity
            # Since vectors in DB are normalized, similarity is simple dot product
            # norm_vectors = all_vectors / np.linalg.norm(all_vectors, axis=1)[:, None]
            # But let's compute explicitly:
            norms = np.linalg.norm(all_vectors, axis=1)
            # Avoid division by zero
            norms[norms == 0] = 1e-10
            normalized_vectors = all_vectors / norms[:, np.newaxis]

            similarities = np.dot(normalized_vectors, q_vec)

            # Combine similarity with chunks
            for chunk, score in zip(all_chunks, similarities):
                chunk["similarity_score"] = float(score)

            # Sort and return top_k
            all_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)
            return all_chunks[:top_k]

    def get_stats(self) -> dict:
        """
        Returns stats about documents, total chunks, sizes, and model parameters.
        """
        with self._get_connection() as conn:
            doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            chunk_count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
            total_chars = conn.execute("SELECT SUM(character_count) FROM documents").fetchone()[0] or 0
            avg_chunk_len = conn.execute("SELECT AVG(LENGTH(text)) FROM chunks").fetchone()[0] or 0
            
            return {
                "document_count": doc_count,
                "chunk_count": chunk_count,
                "total_characters": total_chars,
                "average_chunk_length": round(avg_chunk_len, 1)
            }
            
    def clear_database(self):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM documents")
            conn.commit()
            
    def close(self):
        pass
