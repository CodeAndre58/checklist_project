"""
pdf_processor/extractor.py - Extract text from PDF files
"""
from pathlib import Path
from datetime import datetime
from typing import Tuple
import pdfplumber

from .models import Document, ExtractionMethod, ExtractionQuality
from ..utils.logger import get_logger


logger = get_logger(__name__)


def extract_text_from_pdf(pdf_path: str) -> Tuple[Document, str]:
    """
    Extract text from PDF file (native extraction).
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Tuple of (Document metadata, full text)
        
    Raises:
        FileNotFoundError: If PDF not found
        ValueError: If PDF is corrupted or empty
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    logger.info("extracting_pdf", file=str(pdf_path))
    
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            num_pages = len(pdf.pages)
            
            # Extract text from all pages
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text() or ""
                full_text += f"\n--- PAGE {page.page_number} ---\n{text}"
            
            if not full_text.strip():
                raise ValueError("No text could be extracted from PDF")
            
            # Assess extraction quality based on text length
            chars_per_page = len(full_text) / num_pages
            if chars_per_page < 500:
                quality = ExtractionQuality.LOW
                logger.warning("low_extraction_quality", chars_per_page=chars_per_page)
            elif chars_per_page < 2000:
                quality = ExtractionQuality.MEDIUM
            else:
                quality = ExtractionQuality.HIGH
            
            # Basic section detection from text
            sections = detect_sections(full_text)
            
            doc = Document(
                file_path=str(pdf_path),
                filename=pdf_path.name,
                total_pages=num_pages,
                extraction_method=ExtractionMethod.NATIVE_PDF_TEXT,
                extraction_quality=quality,
                sections_detected=sections,
                processed_at=datetime.now(),
                full_text=full_text
            )
            
            logger.info(
                "pdf_extracted_successfully",
                filename=pdf_path.name,
                pages=num_pages,
                quality=quality.value,
                sections=sections
            )
            
            return doc, full_text
            
    except Exception as e:
        logger.error("pdf_extraction_failed", file=str(pdf_path), error=str(e))
        raise


def detect_sections(text: str) -> list:
    """
    Detect common academic paper sections from text.
    
    Args:
        text: Full extracted text
        
    Returns:
        List of detected sections
    """
    section_keywords = {
        "abstract": ["abstract"],
        "introduction": ["introduction"],
        "methods": ["methods", "methodology", "study design"],
        "results": ["results", "findings"],
        "discussion": ["discussion"],
        "conclusion": ["conclusion", "conclusions"],
        "references": ["references", "bibliography"],
        "acknowledgments": ["acknowledgments", "funding", "conflicts"],
    }
    
    detected = []
    text_lower = text.lower()
    
    for section, keywords in section_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected.append(section)
                break
    
    return list(set(detected))  # Remove duplicates
