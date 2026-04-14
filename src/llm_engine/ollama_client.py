"""
llm_engine/ollama_client.py - Ollama local and remote LLM interaction
"""
import json
import requests
from typing import Dict, Any, Optional
from pathlib import Path
import time
import os
from dotenv import load_dotenv

from ..utils.logger import get_logger

# Load environment variables from .env
load_dotenv()

logger = get_logger(__name__)


class OllamaClient:
    """Client for interacting with Ollama (local or remote)"""
    
    def __init__(self, model_name: Optional[str] = None, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize Ollama client.
        
        Args:
            model_name: Name of the model to use (default: env OLLAMA_MODEL)
            base_url: Base URL for Ollama API (default: env OLLAMA_BASE_URL)
            api_key: API key for authentication (default: env OLLAMA_API_KEY)
        """
        self.model_name = model_name or os.getenv('OLLAMA_MODEL', 'gemma4:31b-cloud')
        self.base_url = base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.api_key = api_key or os.getenv('OLLAMA_API_KEY')
        self.api_url = f"{self.base_url}/api/generate"
        
        # Determine if this is remote (has API key or is not localhost)
        self.is_remote = self.api_key is not None or 'localhost' not in self.base_url
        
        logger.info(
            "ollama_client_initialized",
            model=self.model_name,
            base_url=self.base_url,
            is_remote=self.is_remote,
            has_api_key=self.api_key is not None
        )
        
    def is_available(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            headers = self._get_headers()
            response = requests.get(f"{self.base_url}/api/tags", headers=headers, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error("ollama_unavailable", error=str(e), base_url=self.base_url)
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for requests (includes auth if needed)"""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def query(self, prompt: str, max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Send a query to Ollama and get response.
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response
            
        Returns:
            Dictionary with response and metadata
            
        Raises:
            RuntimeError: If Ollama is not available
            ValueError: If response is invalid
        """
        if not self.is_available():
            if self.is_remote:
                raise RuntimeError(
                    f"Ollama not available at {self.base_url}. "
                    f"Check: base URL, API key, and remote server status."
                )
            else:
                raise RuntimeError(
                    f"Ollama not available at {self.base_url}. "
                    "Ensure Ollama is running locally: ollama serve"
                )
        
        logger.info("ollama_query_sent", model=self.model_name, prompt_length=len(prompt), is_remote=self.is_remote)
        
        try:
            headers = self._get_headers()
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,  # Lower temperature for consistency
                },
                headers=headers,
                timeout=1200  # 1200 second timeout for remote servers
            )
            
            if response.status_code != 200:
                raise ValueError(f"Ollama API error: {response.status_code}")
            
            result = response.json()
            
            logger.info(
                "ollama_response_received",
                model=self.model_name,
                tokens_used=result.get("eval_count", 0)
            )
            
            return {
                "success": True,
                "response_text": result.get("response", ""),
                "model": self.model_name,
                "tokens_used": result.get("eval_count", 0),
                "total_duration": result.get("total_duration", 0)
            }
            
        except requests.exceptions.Timeout:
            logger.error("ollama_timeout", model=self.model_name)
            raise RuntimeError("Ollama query timed out after 120 seconds")
        except Exception as e:
            logger.error("ollama_query_failed", error=str(e))
            raise


def load_prompt_template(template_path: str) -> str:
    """Load prompt template from file"""
    path = Path(template_path)
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def format_prompt(template: str, **kwargs) -> str:
    """Format prompt template with provided arguments"""
    return template.format(**kwargs)
