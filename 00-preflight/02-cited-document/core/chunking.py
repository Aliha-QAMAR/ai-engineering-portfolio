import re
import os
import io

class DocumentChunker:
    """
    Handles reading documents (PDF, MD, TXT) and dividing them into semantic chunks
    with metadata (page numbers, character offsets, document names).
    """

    @staticmethod
    def extract_text_from_file(file_bytes: bytes, file_name: str) -> list[dict]:
        """
        Extracts text from file bytes and returns a list of dictionaries with text and page number.
        [{"text": "...", "page": 1}, ...]
        """
        ext = os.path.splitext(file_name.lower())[1]
        pages_data = []

        if ext == '.pdf':
            # Attempt 1: pdfplumber
            try:
                import pdfplumber
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text() or ""
                        pages_data.append({"text": text, "page": i + 1})
                return pages_data
            except ImportError:
                pass
            except Exception as e:
                print(f"pdfplumber failed: {e}")

            # Attempt 2: pypdf fallback
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                for i, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    pages_data.append({"text": text, "page": i + 1})
                return pages_data
            except ImportError:
                pass
            except Exception as e:
                print(f"pypdf failed: {e}")

            # If all PDF libraries are missing, raise a clear error to the user
            raise RuntimeError(
                "PDF extraction libraries ('pdfplumber' or 'pypdf') are not installed in the Python environment. "
                "Please run 'pip install pdfplumber pypdf' to parse PDF files."
            )
        elif ext in ['.md', '.txt']:
            text_content = file_bytes.decode('utf-8', errors='ignore')
            # For TXT/MD, we can simulate pages by splitting on page breaks (form feeds)
            # or treat as a single large page. Let's split on '\f' if present, or paragraphs.
            parts = text_content.split('\f')
            for i, part in enumerate(parts):
                pages_data.append({"text": part, "page": i + 1})
        else:
            # General fallback
            text_content = file_bytes.decode('utf-8', errors='ignore')
            pages_data.append({"text": text_content, "page": 1})
            
        return pages_data

    @staticmethod
    def create_chunks(pages_data: list[dict], chunk_size: int, chunk_overlap: int) -> list[dict]:
        """
        Chunks pages_data into size-limited blocks while keeping page number association and overlaps.
        """
        chunks = []
        global_char_offset = 0
        chunk_idx = 0

        # We first build a single continuous text with page boundaries mapping,
        # or we chunk page-by-page. For portfolio presentation, page-by-page chunking is
        # very clean because it keeps chunk pages precise. Let's do intra-page chunking
        # but if a page is very small, we merge, or we just split each page individually.
        # Splitting each page individually is standard in legal/policy RAG to ensure page citations are exact.
        for page_obj in pages_data:
            page_text = page_obj["text"]
            page_num = page_obj["page"]
            
            if not page_text.strip():
                continue

            # Standard sliding window chunker on page text
            # Let's split by words or paragraphs
            # We want chunks of size ~chunk_size characters.
            start = 0
            text_len = len(page_text)

            while start < text_len:
                end = start + chunk_size
                if end < text_len:
                    # Look back for a clean boundary: period, question mark, newline, or space
                    boundary_found = False
                    for search_char in ['.\n', '\n', '. ', '? ', '! ', ' ']:
                        pos = page_text.rfind(search_char, start, end)
                        # We don't want to shrink the chunk too much (at least 50% of chunk_size)
                        if pos != -1 and pos > start + (chunk_size // 2):
                            end = pos + len(search_char)
                            boundary_found = True
                            break
                else:
                    end = text_len

                chunk_text = page_text[start:end].strip()
                if chunk_text:
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "text": chunk_text,
                        "page_number": page_num,
                        "char_start": start,
                        "char_end": end,
                        "length": len(chunk_text)
                    })
                    chunk_idx += 1

                # Slide window
                step = chunk_size - chunk_overlap
                if step <= 0:
                    step = chunk_size // 2  # prevent infinite loop
                start += step
                
        return chunks
