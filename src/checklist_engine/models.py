"""
checklist_engine/models.py - Checklist analysis result models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ItemStatus(str, Enum):
    PRESENTE = "presente"
    PARZIALE = "parziale"
    ASSENTE = "assente"
    NON_APPLICABILE = "non_applicabile"
    INCERTO = "incerto"


class EvidenceType(str, Enum):
    EXPLICIT = "explicit"
    INFERRED = "inferred"
    ABSENT = "absent"


class TextEvidence(BaseModel):
    """A traceable text excerpt as evidence"""
    text_excerpt: str
    page_number: Optional[int] = None
    chunk_id: Optional[str] = None
    evidence_type: EvidenceType
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str
    
    class Config:
        use_enum_values = True


class PRISMAItem(BaseModel):
    """PRISMA 2020 checklist item definition"""
    item_id: str
    section: str
    title: str
    description: str
    guidance: str
    applicability_to_scoping: str  # "fully", "partial", "not"
    
    class Config:
        use_enum_values = True


class ItemAnalysisResult(BaseModel):
    """Result of LLM analysis for a single PRISMA item"""
    item_id: str
    item_title: str
    status: ItemStatus
    confidence: float = Field(..., ge=0.0, le=1.0)
    is_applicable: bool
    motivation: str
    evidence_items: List[TextEvidence] = []
    improvement_suggestions: Optional[str] = None
    criticalities: Optional[str] = None
    professional_note: Optional[str] = None
    llm_model_used: str
    llm_reasoning: Optional[str] = None
    analysis_timestamp: datetime
    
    class Config:
        use_enum_values = True


class ChecklistAnalysisReport(BaseModel):
    """Complete analysis report for a document"""
    report_id: str
    document_filename: str
    document_total_pages: int
    prisma_version: str = "2020"
    review_type: str = "scoping_review"
    analysis_results: List[ItemAnalysisResult] = []
    generated_at: datetime
    generated_by: str = "PRISMA Analyzer MVP v0.1"
    llm_model: str
    assumptions_made: List[str] = []
    limitations_noted: List[str] = []
    extraction_quality: str
    
    def stats_summary(self) -> dict:
        """Calculate summary statistics"""
        status_counts = {}
        for status in ItemStatus:
            count = len([
                r for r in self.analysis_results 
                if r.status == status.value
            ])
            status_counts[status.value] = count
        
        return {
            "total_items_analyzed": len(self.analysis_results),
            "status_breakdown": status_counts,
            "items_applicable": len([r for r in self.analysis_results if r.is_applicable]),
            "average_confidence": (
                sum(r.confidence for r in self.analysis_results) / len(self.analysis_results)
                if self.analysis_results else 0.0
            )
        }
    
    class Config:
        use_enum_values = True
