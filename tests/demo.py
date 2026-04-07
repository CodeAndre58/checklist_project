"""
tests/demo.py - Demo script showing how to use the analyzer programmatically
"""
from pathlib import Path
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger, get_logger
from src.pdf_processor.extractor import extract_text_from_pdf
from src.pdf_processor.parser import chunk_document_text
from src.pdf_processor.models import Document, ExtractionMethod, ExtractionQuality
from src.checklist_engine.analyzer import ChecklistAnalyzer
from src.report_engine.json_reporter import generate_json_report
from src.report_engine.markdown_reporter import generate_markdown_report


def demo_with_mock_document():
    """
    Demo: Analyze a mock document without PDF file.
    Useful for testing before connecting to Ollama.
    """
    logger = setup_logger()
    log = get_logger("demo")
    
    print("\n" + "="*70)
    print("PRISMA 2020 ANALYZER - DEMO (Mock Document)")
    print("="*70 + "\n")
    
    # Create a mock document
    print("📄 Creating mock document...")
    mock_text = """
    TITLE: Systematic Mapping of Remote Monitoring in Chronic Disease
    
    ABSTRACT
    Background: Remote monitoring technologies expand in chronic disease management.
    Methods: Scoping review of 2018-2024 literature. Searched MEDLINE, Embase, Google Scholar.
    Results: 287 publications identified, 45 met criteria. Technologies ranged from SMS to AI wearables.
    Conclusions: Remote monitoring shows promise but needs standardization.
    
    INTRODUCTION
    Chronic diseases affect millions globally. Remote monitoring offers opportunities for better management.
    We conducted a scoping review to map the landscape of technologies and evidence.
    
    METHODS
    Eligibility: Peer-reviewed and grey literature describing remote monitoring for chronic disease.
    Study design: Any design included. Exclusion: non-English language papers.
    Search strategy: MEDLINE ("remote monitoring" OR "telemedicine"), Embase, Google Scholar.
    Data extraction: Technology type, disease, population, outcomes, implementation context.
    
    RESULTS
    We found 287 unique publications initially, 45 in final review.
    Technologies: 18 SMS-based, 12 wearable devices, 8 web portals, 7 mobile apps.
    Implementation: Primary care (22), specialist clinics (15), community (8).
    Outcomes: Improved adherence (28 studies), reduced readmissions (24), better control (20).
    
    DISCUSSION
    Heterogeneity in implementation and outcomes limits evidence synthesis.
    Key gaps include standardized outcome reporting and long-term effectiveness data.
    
    FUNDING
    Supported by National Research Foundation Grant XYZ123.
    
    CONFLICTS OF INTEREST
    All authors declare no conflicts of interest.
    
    REFERENCES
    1. Author et al. Journal. 2024.
    2. Researcher et al. Review. 2023.
    """
    
    # Create Document object
    mock_doc = Document(
        file_path="mock_paper.txt",
        filename="mock_paper.txt",
        total_pages=5,
        extraction_method=ExtractionMethod.NATIVE_PDF_TEXT,
        extraction_quality=ExtractionQuality.HIGH,
        sections_detected=["title", "abstract", "introduction", "methods", "results", "discussion"],
        processed_at=datetime.now(),
        full_text=mock_text
    )
    
    print(f"✓ Mock document created: {mock_doc.filename} ({len(mock_text)} chars)")
    
    # Chunk document
    print("\n✂️  Chunking document...")
    chunks = chunk_document_text(mock_doc.filename, mock_text)
    print(f"✓ Created {len(chunks)} chunks")
    
    # Initialize analyzer
    print("\n🤖 Initializing PRISMA analyzer...")
    base_dir = Path(__file__).parent.parent
    prisma_yaml = base_dir / "config/prisma_2020_items.yaml"
    
    try:
        analyzer = ChecklistAnalyzer(str(prisma_yaml), ollama_model="gemma4:31b-cloud")
        print(f"✓ Analyzer ready with {len(analyzer.prisma_items)} items")
        
        # Note: Analysis requires Ollama to be running
        print("\n⚠️  NOTE: Full analysis requires Ollama to be running.")
        print("   To continue with Ollama analysis:")
        print("   1. Run 'ollama serve' in another terminal")
        print("   2. Pull the model: 'ollama pull gemma4:31b-cloud'")
        print("   3. Then run: python -m cli path/to/demo-paper.pdf")
        
        demo_mock_analysis(analyzer, mock_doc, chunks)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("   This is expected - full demo needs Ollama running.")


def demo_mock_analysis(analyzer, doc, chunks):
    """
    Show what the analysis output looks like (without calling LLM).
    """
    from src.checklist_engine.models import (
        ItemAnalysisResult, TextEvidence, EvidenceType, ItemStatus,
        ChecklistAnalysisReport
    )
    
    print("\n📊 Example analysis output (simulated):")
    print("-" * 70)
    
    # Create example results
    example_results = [
        ItemAnalysisResult(
            item_id="1",
            item_title="Title",
            status=ItemStatus.PRESENTE,
            confidence=0.95,
            is_applicable=True,
            motivation="Paper has clear, descriptive title that identifies it as a scoping review",
            evidence_items=[
                TextEvidence(
                    text_excerpt="Systematic Mapping of Remote Monitoring in Chronic Disease",
                    page_number=1,
                    evidence_type=EvidenceType.EXPLICIT,
                    confidence=1.0,
                    explanation="Title clearly states the topic and review type"
                )
            ],
            llm_model_used="gemma4:31b-cloud",
            analysis_timestamp=datetime.now()
        ),
        ItemAnalysisResult(
            item_id="2",
            item_title="Abstract",
            status=ItemStatus.PRESENTE,
            confidence=0.90,
            is_applicable=True,
            motivation="Abstract contains background, methods, results, and conclusions sections",
            evidence_items=[],
            llm_model_used="gemma4:31b-cloud",
            analysis_timestamp=datetime.now()
        ),
    ]
    
    # Create mock report
    mock_report = ChecklistAnalysisReport(
        report_id="demo_paper_prisma",
        document_filename=doc.filename,
        document_total_pages=doc.total_pages,
        analysis_results=example_results,
        generated_at=datetime.now(),
        llm_model="gemma4:31b-cloud (simulated)",
        extraction_quality="high"
    )
    
    stats = mock_report.stats_summary()
    
    print(f"\nDocument: {doc.filename}")
    print(f"Pages: {doc.total_pages}")
    print(f"\nItems Analyzed: {stats['total_items_analyzed']}")
    print(f"Items Applicable: {stats['items_applicable']}")
    print(f"Average Confidence: {stats['average_confidence']:.0%}")
    print(f"\nStatus Summary:")
    for status, count in stats['status_breakdown'].items():
        print(f"  {status.upper()}: {count}")
    
    # Show example item
    print("\n" + "-" * 70)
    print("Example Item Analysis:")
    print("-" * 70)
    
    result = example_results[0]
    print(f"\n✅ Item {result.item_id}: {result.item_title}")
    print(f"   Status: {result.status.upper()}")
    print(f"   Confidence: {result.confidence:.0%}")
    print(f"   Assessment: {result.motivation}")
    
    if result.evidence_items:
        print(f"\n   Evidence:")
        for ev in result.evidence_items:
            print(f"   - \"{ev.text_excerpt}\"")
            print(f"     ({ev.evidence_type}, confidence: {ev.confidence:.0%})")
    
    print("\n" + "=" * 70)
    print("In production, this analysis would be output to JSON + Markdown reports.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    demo_with_mock_document()
