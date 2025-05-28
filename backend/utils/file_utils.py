import os
import logging
from typing import List, Set

logger = logging.getLogger(__name__)

def get_allowed_extensions() -> Set[str]:
    """Get the set of allowed file extensions"""
    return {'pdf', 'jpg', 'jpeg', 'png'}

def is_allowed_file(filename: str, allowed_extensions: Set[str] = None) -> bool:
    """
    Check if a file has an allowed extension
    
    Args:
        filename: Name of the file to check
        allowed_extensions: Set of allowed extensions (defaults to get_allowed_extensions())
        
    Returns:
        True if the file has an allowed extension, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = get_allowed_extensions()
        
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_extension(filename: str) -> str:
    """
    Get the extension of a file
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension (lowercase, without the dot)
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''

def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary
    
    Args:
        directory_path: Path to the directory
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
        logger.info(f"Created directory: {directory_path}")

def list_files_in_directory(directory_path: str, extensions: List[str] = None) -> List[str]:
    """
    List files in a directory, optionally filtered by extension
    
    Args:
        directory_path: Path to the directory
        extensions: List of extensions to filter by (without the dot)
        
    Returns:
        List of filenames
    """
    if not os.path.exists(directory_path):
        logger.warning(f"Directory does not exist: {directory_path}")
        return []
        
    files = os.listdir(directory_path)
    
    if extensions:
        return [f for f in files if get_file_extension(f) in extensions]
    
    return files




import re
import json

def extract_json_from_response(response_text):
    # Try to find a JSON code block
    match = re.search(r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL)
    if match:
        return match.group(1)
    # Fallback: try to find any JSON object in the text
    match = re.search(r"(\{.*\})", response_text, re.DOTALL)
    if match:
        return match.group(1)
    raise ValueError("No JSON object found in LLM response")