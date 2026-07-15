import os
from pypdf import PdfReader

def load_markdown_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def load_pdf_file(file_path):
    reader = PdfReader(file_path)
    pages_content = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages_content.append({
                "page_num": page_num + 1,
                "text": text
            })
    return pages_content

def chunk_text_with_overlap(text, chunk_size=400, overlap=50):
    chunks = []
    start = 0
    text_len = len(text)
    
    if text_len <= chunk_size:
        return [{"text": text, "start_idx": 0}]
        
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append({
            "text": chunk,
            "start_idx": start
        })
        start += (chunk_size - overlap)
        if start >= text_len or (chunk_size - overlap) <= 0:
            break
            
    return chunks

def process_document(file_path, chunk_size=400, overlap=50):
    filename = os.path.basename(file_path)
    extension = os.path.splitext(file_path)[1].lower()
    final_chunks = []

    if extension in ['.md', '.txt']:
        text = load_markdown_file(file_path)
        chunks = chunk_text_with_overlap(text, chunk_size, overlap)
        for c in chunks:
            final_chunks.append({
                "text": c["text"],
                "metadata": {
                    "source": filename,
                    "page": "N/A",
                    "start_character": c["start_idx"]
                }
            })

    elif extension == '.pdf':
        pages = load_pdf_file(file_path)
        for page_data in pages:
            p_num = page_data["page_num"]
            p_text = page_data["text"]
            chunks = chunk_text_with_overlap(p_text, chunk_size, overlap)
            for c in chunks:
                final_chunks.append({
                    "text": c["text"],
                    "metadata": {
                        "source": filename,
                        "page": f"Page {p_num}",
                        "start_character": c["start_idx"]
                    }
                })
        
    return final_chunks