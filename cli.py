"""
cli.py - Command-line interface for PRISMA Analyzer
"""
import click
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

from src.utils.logger import setup_logger, get_logger
from src.pdf_processor.extractor import extract_text_from_pdf
from src.pdf_processor.parser import chunk_document_text
from src.checklist_engine.analyzer import ChecklistAnalyzer
from src.report_engine.json_reporter import generate_json_report
from src.report_engine.markdown_reporter import generate_markdown_report

# Load environment variables from .env file
load_dotenv()


@click.command()
@click.argument("pdf_file", type=click.Path(exists=True))
@click.option(
    "--model",
    default=None,
    help="Ollama model name (default: from .env or gemma4:31b-cloud)"
)
@click.option(
    "--url",
    default=None,
    help="Ollama server URL (default: from .env or http://localhost:11434)"
)
@click.option(
    "--api-key",
    default=None,
    help="Ollama API key for remote server (default: from .env)"
)
@click.option(
    "--limit",
    type=int,
    default=None,
    help="Limit analysis to first N PRISMA items (for testing)"
)
@click.option(
    "--output-dir",
    type=click.Path(),
    default="output/reports",
    help="Output directory for reports"
)
@click.option(
    "--skip-markdown",
    is_flag=True,
    help="Skip Markdown report generation"
)
def main(pdf_file, model, url, api_key, limit, output_dir, skip_markdown):
    """
    Analyze a scientific paper PDF against PRISMA 2020 checklist.
    
    Usage:
        python cli.py path/to/paper.pdf                              # Local Ollama
        python cli.py path/to/paper.pdf --url https://... --api-key  # Remote Ollama
    """
    
    # Setup logging
    logger = setup_logger()
    log = get_logger("cli")
    
    # Get configuration from CLI args or .env
    ollama_model = model or os.getenv('OLLAMA_MODEL', 'gemma4:31b-cloud')
    ollama_url = url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    ollama_api_key = api_key or os.getenv('OLLAMA_API_KEY')
    
    # Determine if remote
    is_remote = ollama_api_key is not None or 'localhost' not in ollama_url
    
    log.info(
        "analysis_started",
        pdf=pdf_file,
        model=ollama_model,
        ollama_url=ollama_url,
        is_remote=is_remote
    )
    
    # Show connection info
    click.echo(f"\n🌐 Ollama Configuration:")
    click.echo(f"   URL: {ollama_url}")
    click.echo(f"   Model: {ollama_model}")
    click.echo(f"   Type: {'Remote (Cloud)' if is_remote else 'Local'}")
    if is_remote:
        click.echo(f"   Auth: {'✓ API Key configured' if ollama_api_key else '✗ No API key'}")
    
    try:
        # ─── Step 1: Extract PDF ───
        click.echo("\n📖 Extracting PDF text...")
        document, full_text = extract_text_from_pdf(pdf_file)
        click.echo(
            f"✓ Extracted {document.total_pages} pages "
            f"({len(full_text)} chars, quality: {document.extraction_quality})"
        )
        
        # ─── Step 2: Chunk document ───
        click.echo("\n✂️  Chunking document...")
        chunks = chunk_document_text(document.filename, full_text)
        click.echo(f"✓ Created {len(chunks)} chunks")
        
        # ─── Step 3: Initialize analyzer ───
        click.echo("\n🤖 Initializing PRISMA analyzer...")
        base_dir = Path(__file__).parent
        prisma_yaml = base_dir / "config/prisma_2020_items.yaml"
        analyzer = ChecklistAnalyzer(
            str(prisma_yaml),
            ollama_model=ollama_model,
            ollama_base_url=ollama_url,
            ollama_api_key=ollama_api_key
        )
        click.echo(f"✓ Loaded {len(analyzer.prisma_items)} PRISMA items")
        
        # ─── Step 4: Analyze document ───
        click.echo(f"\n🔍 Analyzing document against PRISMA checklist...")
        if limit:
            click.echo(f"(Limited to first {limit} items for testing)")
        
        report = analyzer.analyze_document(document, chunks, analysis_limit=limit)
        stats = report.stats_summary()
        click.echo(f"✓ Analysis complete!")
        click.echo(f"  - Items analyzed: {stats['total_items_analyzed']}")
        click.echo(f"  - Status breakdown:")
        breakdown = stats.get("status_breakdown", {})
        for status, count in breakdown.items():
            click.echo(f"    • {status}: {count}")
        
        # ─── Step 5: Generate reports ───
        click.echo(f"\n📄 Generating reports...")
        
        output_path = Path(output_dir)
        
        # JSON report
        json_file = generate_json_report(report, output_path)
        click.echo(f"✓ JSON report: {json_file}")
        
        # Markdown report (unless skipped)
        if not skip_markdown:
            md_file = generate_markdown_report(report, output_path)
            click.echo(f"✓ Markdown report: {md_file}")
        
        click.echo(f"\n✅ Analysis complete! Reports saved to: {output_path}")
        log.info("analysis_completed_successfully", pdf=pdf_file)
        
    except FileNotFoundError as e:
        click.echo(f"\n❌ File not found: {e}", err=True)
        log.error("file_not_found", error=str(e))
        raise click.Exit(1)
    except RuntimeError as e:
        click.echo(f"\n❌ Ollama error: {e}", err=True)
        click.echo("   Make sure Ollama is running: ollama serve", err=True)
        log.error("ollama_error", error=str(e))
        raise click.Exit(1)
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        log.error("analysis_failed", error=str(e))
        raise click.Exit(1)


if __name__ == "__main__":
    main()
