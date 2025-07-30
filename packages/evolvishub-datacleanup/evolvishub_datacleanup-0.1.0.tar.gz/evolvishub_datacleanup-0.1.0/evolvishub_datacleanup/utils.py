"""
Utility functions for the Data Cleanup Manager.
"""

import logging
import os
from pathlib import Path
from typing import Optional

def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Name of the logger
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger

def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path: Path to the project root
    """
    return Path(__file__).parent.parent

def get_data_dir() -> Path:
    """
    Get the data directory.
    
    Returns:
        Path: Path to the data directory
    """
    return get_project_root() / 'data'

def ensure_dir(path: Path) -> None:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        path: Path to the directory
    """
    path.mkdir(parents=True, exist_ok=True)

def get_file_size(path: Path) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        path: Path to the file
        
    Returns:
        int: Size in bytes
    """
    return path.stat().st_size

def format_size(size_bytes: int) -> str:
    """
    Format size in bytes to human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB" 