"""
pdf_processor/parser.py - Parse and chunk document text
"""
from typing import List
from .models import Chunk
from ..utils.logger import get_logger


logger = get_logger(__name__)


def chunk_document_text(filename: str, full_text: str, chunk_size: int = 1000) -> List[Chunk]:
    """
    Divide document text into traceable chunks.
    
    Args:
        filename: Document filename
        full_text: Complete extracted text
        chunk_size: Characters per chunk (approximate)
        
    Returns:
        List of Chunk objects with metadata
    """
    chunks = []
    lines = full_text.split("\n")
    
    current_chunk_text = ""
    current_page = 1
    current_section = "unknown"
    chunk_index = 0
    
    for line in lines:
        # Track page numbers from extracted markers
        if line.startswith("--- PAGE"):
            try:
                current_page = int(line.split()[2].strip("---"))
            except:
                pass
            continue  # Don't add page markers to chunk text
        
        # Track sections
        line_lower = line.lower()
        if any(kw in line_lower for kw in ["abstract", "introduction", "methods", 
                                              "results", "discussion", "conclusion"]):
            if len(line) < 100:  # Likely a section header
                current_section = line.split()[0].lower()
        
        current_chunk_text += line + "\n"
        
        # Create chunk when size threshold reached
        if len(current_chunk_text) >= chunk_size:
            if current_chunk_text.strip():
                chunk_id = f"{filename.replace('.pdf', '')}_p{current_page:02d}_s{current_section}_c{chunk_index:03d}"
                chunk = Chunk(
                    chunk_id=chunk_id,
                    document_filename=filename,
                    page_number=current_page,
                    section=current_section,
                    text=current_chunk_text.strip(),
                    char_count=len(current_chunk_text)
                )
                chunks.append(chunk)
                chunk_index += 1
                current_chunk_text = ""
    
    # Add remaining text
    if current_chunk_text.strip():
        chunk_id = f"{filename.replace('.pdf', '')}_p{current_page:02d}_s{current_section}_c{chunk_index:03d}"
        chunk = Chunk(
            chunk_id=chunk_id,
            document_filename=filename,
            page_number=current_page,
            section=current_section,
            text=current_chunk_text.strip(),
            char_count=len(current_chunk_text)
        )
        chunks.append(chunk)
    
    logger.info("document_chunked", filename=filename, chunks_created=len(chunks))
    return chunks
