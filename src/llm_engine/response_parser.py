"""
llm_engine/response_parser.py - Parse LLM responses
"""
import json
import re
from typing import Dict, Any, List
from ..utils.logger import get_logger

logger = get_logger(__name__)


def extract_json_from_response(response_text: str) -> Dict[str, Any]:
    """
    Extract JSON object from LLM response text.
    
    LLMs sometimes include explanatory text before/after JSON. This function 
    extracts the JSON portion robustly.
    
    Args:
        response_text: Raw response from LLM
        
    Returns:
        Parsed JSON as dictionary
        
    Raises:
        ValueError: If no valid JSON found
    """
    # Try direct parsing first
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON block with regex
    json_pattern = r'\{[\s\S]*\}'
    matches = re.finditer(json_pattern, response_text)
    
    for match in matches:
        try:
            parsed = json.loads(match.group())
            logger.info("json_extracted_from_llm_response")
            return parsed
        except json.JSONDecodeError:
            continue
    
    logger.error("no_json_found_in_response", response_preview=response_text[:200])
    raise ValueError("Could not extract valid JSON from LLM response")


def parse_evidence_response(llm_response: str) -> Dict[str, Any]:
    """
    Parse evidence extraction response from LLM.
    
    Expected JSON structure:
    {
      "evidence_found": bool,
      "evidence_items": [
        {
          "text_excerpt": str,
          "page_number": int or null,
          "evidence_type": "explicit" or "inferred",
          "confidence": float,
          "explanation": str
        }
      ],
      "overall_assessment": str,
      "professional_note": str
    }
    """
    try:
        data = extract_json_from_response(llm_response)
        
        # Validate structure
        required_fields = ["evidence_found", "evidence_items", "overall_assessment"]
        for field in required_fields:
            if field not in data:
                logger.warning(f"missing_field_in_evidence_response: {field}")
        
        # Normalize evidence items
        evidence_items = data.get("evidence_items", [])
        for item in evidence_items:
            if "confidence" not in item:
                item["confidence"] = 0.5
            # Ensure confidence is in [0, 1]
            item["confidence"] = max(0.0, min(1.0, item["confidence"]))
        
        return {
            "success": True,
            "evidence_found": data.get("evidence_found", False),
            "evidence_items": evidence_items,
            "overall_assessment": data.get("overall_assessment", ""),
            "professional_note": data.get("professional_note", "")
        }
        
    except Exception as e:
        logger.error("error_parsing_evidence_response", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "raw_response": llm_response
        }


def parse_classification_response(llm_response: str) -> Dict[str, Any]:
    """
    Parse classification response from LLM.
    
    Expected JSON structure:
    {
      "item_id": str,
      "status": "presente|parziale|assente|non_applicabile|incerto",
      "confidence": float,
      "is_applicable_to_scoping_review": bool,
      "motivation": str,
      "improvement_suggestions": str,
      "professional_note": str
    }
    """
    try:
        data = extract_json_from_response(llm_response)
        
        # Validate status
        valid_statuses = ["presente", "parziale", "assente", "non_applicabile", "incerto"]
        status = data.get("status", "incerto")
        
        if status not in valid_statuses:
            logger.warning(f"invalid_status_in_response: {status}, defaulting to 'incerto'")
            status = "incerto"
        
        # Normalize confidence
        confidence = data.get("confidence", 0.5)
        confidence = max(0.0, min(1.0, confidence))
        
        return {
            "success": True,
            "item_id": data.get("item_id", ""),
            "status": status,
            "confidence": confidence,
            "is_applicable": data.get("is_applicable_to_scoping_review", True),
            "motivation": data.get("motivation", ""),
            "improvement_suggestions": data.get("improvement_suggestions", ""),
            "professional_note": data.get("professional_note", "")
        }
        
    except Exception as e:
        logger.error("error_parsing_classification_response", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "raw_response": llm_response
        }
