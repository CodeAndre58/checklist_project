"""
tests/test_pdf_processor.py - Basic tests for PDF processing
"""
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pdf_processor.extractor import detect_sections
from src.pdf_processor.parser import chunk_document_text


def test_section_detection():
    """Test basic section detection"""
    text = """
    Introduction
    This is the introduction section.
    
    Methods
    This is the methods section.
    
    Results
    This is the results section.
    
    Discussion
    This is the discussion section.
    """
    
    sections = detect_sections(text)
    print(f"Detected sections: {sections}")
    
    expected = {"introduction", "methods", "results", "discussion"}
    assert set(sections) == expected, f"Expected {expected}, got {set(sections)}"
    print("✓ Section detection test passed")


def test_chunking():
    """Test document chunking"""
    text = "This is a sample document. " * 200  # Repeated text to create chunks
    
    chunks = chunk_document_text("test_doc.pdf", text, chunk_size=500)
    print(f"Created {len(chunks)} chunks")
    
    assert len(chunks) >= 1, "Should create at least one chunk"
    assert all(len(c.text) > 0 for c in chunks), "All chunks should have text"
    assert all(c.chunk_id for c in chunks), "All chunks should have IDs"
    print(f"✓ Chunking test passed ({len(chunks)} chunks created)")


if __name__ == "__main__":
    print("Running PDF processor tests...\n")
    test_section_detection()
    print()
    test_chunking()
    print("\n✅ All tests passed!")
