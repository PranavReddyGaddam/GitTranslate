"""
Utility functions for the GitHub Repo → Podcast generator workers.
"""

import json
import sys
import os
import uuid
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def read_input(input_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Read JSON input from file or stdin.
    
    Args:
        input_file: Path to input JSON file, or None for stdin
        
    Returns:
        Parsed JSON data
    """
    try:
        if input_file:
            with open(input_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return json.load(sys.stdin)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON input: {e}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_file}")


def write_output(data: Dict[str, Any], output_file: Optional[str] = None) -> None:
    """
    Write JSON output to file or stdout.
    
    Args:
        data: Data to write
        output_file: Path to output JSON file, or None for stdout
    """
    try:
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to write output: {e}")
        raise


def create_error_response(error_message: str, status: str = "error") -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        error_message: Error message
        status: Status string (default: "error")
        
    Returns:
        Error response dictionary
    """
    return {
        'status': status,
        'data': None,
        'error': error_message
    }


def create_success_response(data: Any, status: str = "success") -> Dict[str, Any]:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        status: Status string (default: "success")
        
    Returns:
        Success response dictionary
    """
    return {
        'status': status,
        'data': data,
        'error': None
    }


def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure a directory exists, create it if it doesn't.
    
    Args:
        directory_path: Path to the directory
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def generate_uuid() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())


def get_audio_output_dir() -> str:
    """Get the audio output directory from environment or use default."""
    return os.getenv('AUDIO_OUTPUT_DIR', 'static/audio')


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """
    Validate that required fields are present in the input data.
    
    Args:
        data: Input data dictionary
        required_fields: List of required field names
        
    Raises:
        ValueError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing or replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    import re
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    return sanitized


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "2m 30s")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def get_file_content_from_repo(repo, file_path: str, branch: str = 'main') -> str:
    """
    Get the content of a file from a GitHub repository.
    
    Args:
        repo: PyGithub Repository object
        file_path: Path to the file in the repository
        branch: Branch name (default: 'main')
        
    Returns:
        File content as string, or empty string if file not found
    """
    try:
        # Try to get the file from the specified branch
        contents = repo.get_contents(file_path, ref=branch)
        return contents.decoded_content.decode('utf-8')
    except Exception as e:
        # If the specified branch fails, try the default branch
        try:
            contents = repo.get_contents(file_path, ref=repo.default_branch)
            return contents.decoded_content.decode('utf-8')
        except Exception:
            logger.warning(f"Could not find {file_path} in repository {repo.full_name}")
            return "" 