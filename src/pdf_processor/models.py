"""
pdf_processor/models.py - Core data models for document processing
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ExtractionMethod(str, Enum):
    NATIVE_PDF_TEXT = "native_pdf_text"
    OCR = "ocr"


class ExtractionQuality(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Document(BaseModel):
    """Represents an analyzed PDF document"""
    file_path: str
    filename: str
    total_pages: int
    extraction_method: ExtractionMethod
    extraction_quality: ExtractionQuality
    sections_detected: List[str]
    processed_at: datetime
    full_text: str = Field(...)  # Complete extracted text
    
    class Config:
        use_enum_values = True


class Chunk(BaseModel):
    """Represents a traceable portion of text from document"""
    chunk_id: str  # Format: "file_p03_sec2_ch01"
    document_filename: str
    page_number: int
    section: Optional[str] = None
    text: str
    char_count: int
    language: str = "en"
    
    class Config:
        use_enum_values = True
