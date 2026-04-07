"""
tests/test_imports.py - Verify all imports work correctly
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("🔍 Testing imports...\n")

try:
    print("  ✓ Importing src.utils...")
    from src.utils.logger import setup_logger, get_logger
    
    print("  ✓ Importing src.pdf_processor...")
    from src.pdf_processor.models import Document, Chunk
    from src.pdf_processor.extractor import extract_text_from_pdf, detect_sections
    from src.pdf_processor.parser import chunk_document_text
    
    print("  ✓ Importing src.llm_engine...")
    from src.llm_engine.ollama_client import OllamaClient, load_prompt_template
    from src.llm_engine.response_parser import (
        extract_json_from_response,
        parse_evidence_response,
        parse_classification_response
    )
    
    print("  ✓ Importing src.checklist_engine...")
    from src.checklist_engine.models import (
        ItemStatus, EvidenceType, TextEvidence, PRISMAItem,
        ItemAnalysisResult, ChecklistAnalysisReport
    )
    from src.checklist_engine.analyzer import ChecklistAnalyzer
    
    print("  ✓ Importing src.report_engine...")
    from src.report_engine.json_reporter import generate_json_report, load_json_report
    from src.report_engine.markdown_reporter import generate_markdown_report
    
    print("\n✅ All imports successful!\n")
    print("Now verify dependencies:")
    
    try:
        import pdfplumber
        print(f"  ✓ pdfplumber {pdfplumber.__version__}")
    except ImportError:
        print("  ✗ pdfplumber not installed")
    
    try:
        import pydantic
        print(f"  ✓ pydantic {pydantic.__version__}")
    except ImportError:
        print("  ✗ pydantic not installed")
    
    try:
        import yaml
        print(f"  ✓ pyyaml available")
    except ImportError:
        print("  ✗ pyyaml not installed")
    
    try:
        import structlog
        print(f"  ✓ structlog available")
    except ImportError:
        print("  ✗ structlog not installed")
    
    try:
        import click
        print(f"  ✓ click available")
    except ImportError:
        print("  ✗ click not installed")
    
    try:
        import ollama
        print(f"  ✓ ollama available")
    except ImportError:
        print("  ✓ ollama (will use requests fallback)")
    
    print("\n✅ Setup verification complete!")
    
except ImportError as e:
    print(f"\n✗ Import failed: {e}")
    sys.exit(1)
