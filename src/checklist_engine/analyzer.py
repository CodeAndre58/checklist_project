"""
checklist_engine/analyzer.py - Main analysis engine
"""
from typing import List, Dict, Any
from datetime import datetime
import yaml
from pathlib import Path

from .models import (
    ItemAnalysisResult, PRISMAItem, ChecklistAnalysisReport, 
    ItemStatus, TextEvidence, EvidenceType
)
from ..llm_engine.ollama_client import OllamaClient, load_prompt_template, format_prompt
from ..llm_engine.response_parser import parse_evidence_response, parse_classification_response
from ..pdf_processor.models import Document, Chunk
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ChecklistAnalyzer:
    """Main engine for PRISMA checklist analysis"""
    
    def __init__(
        self, 
        prisma_items_yaml: str, 
        ollama_model: str = "gemma4:31b-cloud",
        ollama_base_url: str = "http://localhost:11434",
        ollama_api_key: str = None
    ):
        """
        Initialize analyzer.
        
        Args:
            prisma_items_yaml: Path to PRISMA items YAML file
            ollama_model: Ollama model name
            ollama_base_url: Ollama server base URL
            ollama_api_key: Ollama API key (if remote/authenticated)
        """
        self.ollama = OllamaClient(
            model_name=ollama_model,
            base_url=ollama_base_url,
            api_key=ollama_api_key
        )
        self.prisma_items = self._load_prisma_items(prisma_items_yaml)
        self.ollama_model = ollama_model
        
        # Load prompt templates
        base_dir = Path(__file__).parent.parent.parent
        self.evidence_prompt_template = load_prompt_template(
            str(base_dir / "config/prompts/evidence_extraction.txt")
        )
        self.classification_prompt_template = load_prompt_template(
            str(base_dir / "config/prompts/classification.txt")
        )
        
        logger.info(
            "checklist_analyzer_initialized",
            items_loaded=len(self.prisma_items),
            model=ollama_model,
            ollama_url=ollama_base_url
        )
    
    def _load_prisma_items(self, yaml_path: str) -> List[PRISMAItem]:
        """Load PRISMA items from YAML"""
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        items = []
        for item_data in data.get("prisma_items", []):
            item = PRISMAItem(**item_data)
            items.append(item)
        
        logger.info("prisma_items_loaded", count=len(items))
        return items
    
    def analyze_document(
        self, 
        document: Document, 
        chunks: List[Chunk],
        analysis_limit: int = None
    ) -> ChecklistAnalysisReport:
        """
        Analyze document against PRISMA checklist.
        
        Args:
            document: Document metadata
            chunks: Document text chunks
            analysis_limit: Limit analysis to first N items (for testing)
            
        Returns:
            ChecklistAnalysisReport with all item analyses
        """
        logger.info(
            "starting_checklist_analysis",
            document=document.filename,
            items_to_analyze=len(self.prisma_items),
            chunks_available=len(chunks)
        )
        
        # Combine chunks into manageable context
        full_context = self._prepare_context(chunks)
        
        # Analyze each PRISMA item
        results = []
        items_to_analyze = (
            self.prisma_items[:analysis_limit] if analysis_limit 
            else self.prisma_items
        )
        
        for item in items_to_analyze:
            logger.info("analyzing_item", item_id=item.item_id, title=item.title)
            
            try:
                result = self._analyze_single_item(item, full_context, document)
                results.append(result)
            except Exception as e:
                logger.error(
                    "error_analyzing_item",
                    item_id=item.item_id,
                    error=str(e)
                )
                # Create error result
                result = ItemAnalysisResult(
                    item_id=item.item_id,
                    item_title=item.title,
                    status=ItemStatus.INCERTO,
                    confidence=0.0,
                    is_applicable=item.applicability_to_scoping == "fully",
                    motivation=f"Error during analysis: {str(e)}",
                    evidence_items=[],
                    llm_model_used=self.ollama_model,
                    analysis_timestamp=datetime.now()
                )
                results.append(result)
        
        # Build report
        report = ChecklistAnalysisReport(
            report_id=f"{document.filename.replace('.pdf', '')}_prisma",
            document_filename=document.filename,
            document_total_pages=document.total_pages,
            analysis_results=results,
            generated_at=datetime.now(),
            llm_model=self.ollama_model,
            extraction_quality=document.extraction_quality,
            assumptions_made=[
                "PRISMA 2020 items adapted for scoping review context",
                f"Full document processed with chunking strategy",
                "LLM-based evidence extraction with explicit/inferred distinction",
            ],
            limitations_noted=[
                "LLM responses may contain hallucinations - verify evidence manually",
                "Non-English papers may be processed with reduced accuracy",
                f"Analysis quality depends on OCR quality ({document.extraction_quality})",
            ]
        )
        
        logger.info(
            "analysis_complete",
            document=document.filename,
            items_analyzed=len(results),
            stats=report.stats_summary()
        )
        
        return report
    
    def _prepare_context(self, chunks: List[Chunk], max_chars: int = 8000) -> str:
        """Prepare document context for LLM analysis"""
        # Concatenate chunks, respecting size limit
        context = ""
        for chunk in chunks:
            if len(context) + len(chunk.text) < max_chars:
                context += f"\n[Section: {chunk.section}, Page: {chunk.page_number}]\n"
                context += chunk.text + "\n"
            else:
                break
        
        if len(context) > max_chars:
            context = context[:max_chars] + "..."
        
        return context
    
    def _analyze_single_item(
        self, 
        item: PRISMAItem,
        context: str,
        document: Document
    ) -> ItemAnalysisResult:
        """Analyze a single PRISMA item"""
        
        # Step 1: Extract evidence
        evidence_prompt = format_prompt(
            self.evidence_prompt_template,
            item_id=item.item_id,
            item_title=item.title,
            item_section=item.section,
            item_description=item.description,
            item_guidance=item.guidance,
            document_text=context
        )
        
        logger.debug("querying_ollama_for_evidence", item_id=item.item_id)
        evidence_response = self.ollama.query(evidence_prompt)
        
        evidence_data = parse_evidence_response(evidence_response["response_text"])
        
        # Convert evidence to objects
        evidence_items = []
        if evidence_data.get("success"):
            for ev in evidence_data.get("evidence_items", []):
                evidence_items.append(
                    TextEvidence(
                        text_excerpt=ev.get("text_excerpt", ""),
                        page_number=ev.get("page_number"),
                        evidence_type=ev.get("evidence_type", "explicit"),
                        confidence=ev.get("confidence", 0.5),
                        explanation=ev.get("explanation", "")
                    )
                )
        
        evidence_summary = (
            f"Evidence found: {len(evidence_items)}\n"
            + f"Overall assessment: {evidence_data.get('overall_assessment', 'N/A')}\n"
            + (
                f"Evidence types: " +
                ", ".join(set(ev.evidence_type for ev in evidence_items))
                if evidence_items else "No evidence found"
            )
        )
        
        # Step 2: Classify status
        classification_prompt = format_prompt(
            self.classification_prompt_template,
            item_id=item.item_id,
            item_title=item.title,
            item_section=item.section,
            item_guidance=item.guidance,
            evidence_summary=evidence_summary
        )
        
        logger.debug("querying_ollama_for_classification", item_id=item.item_id)
        classification_response = self.ollama.query(classification_prompt)
        
        classification_data = parse_classification_response(
            classification_response["response_text"]
        )
        
        # Build result
        result = ItemAnalysisResult(
            item_id=item.item_id,
            item_title=item.title,
            status=classification_data.get("status", "incerto"),
            confidence=classification_data.get("confidence", 0.5),
            is_applicable=classification_data.get("is_applicable", True),
            motivation=classification_data.get("motivation", ""),
            evidence_items=evidence_items,
            improvement_suggestions=classification_data.get("improvement_suggestions"),
            professional_note=classification_data.get("professional_note"),
            llm_model_used=self.ollama_model,
            llm_reasoning=evidence_response.get("response_text", ""),
            analysis_timestamp=datetime.now()
        )
        
        logger.info(
            "item_analysis_complete",
            item_id=item.item_id,
            status=result.status,
            evidence_count=len(evidence_items),
            confidence=result.confidence
        )
        
        return result
