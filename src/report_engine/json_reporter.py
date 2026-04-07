"""
report_engine/json_reporter.py - JSON report generation
"""
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from ..checklist_engine.models import ChecklistAnalysisReport
from ..utils.logger import get_logger

logger = get_logger(__name__)


def generate_json_report(report: ChecklistAnalysisReport, output_dir: Path = None) -> Path:
    """
    Generate JSON report from analysis results.
    
    Args:
        report: ChecklistAnalysisReport object
        output_dir: Directory to save report (default: output/reports/)
        
    Returns:
        Path to generated JSON file
    """
    if output_dir is None:
        output_dir = Path("output/reports")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert report to dict
    report_dict = report.dict()
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{report.report_id}_{timestamp}.json"
    
    # Write JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2, ensure_ascii=False, default=str)
    
    logger.info("json_report_generated", file=str(output_file))
    return output_file


def load_json_report(json_file: Path) -> ChecklistAnalysisReport:
    """Load JSON report back into ChecklistAnalysisReport object"""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return ChecklistAnalysisReport(**data)
