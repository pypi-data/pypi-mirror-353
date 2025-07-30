"""
Tests for utility functions.
"""

import os
import tempfile
import pytest
from pathlib import Path
from evolvishub_datacleanup.utils import (
    get_logger,
    get_project_root,
    get_data_dir,
    ensure_dir,
    get_file_size,
    format_size
)

def test_get_logger():
    """Test logger creation and configuration."""
    logger = get_logger('test')
    assert logger.name == 'test'
    assert logger.level == 20  # INFO level
    assert len(logger.handlers) > 0

def test_get_project_root():
    """Test getting project root directory."""
    root = get_project_root()
    assert isinstance(root, Path)
    assert root.exists()
    assert (root / 'evolvishub_datacleanup').exists()

def test_get_data_dir():
    """Test getting data directory."""
    data_dir = get_data_dir()
    assert isinstance(data_dir, Path)
    assert data_dir.parent == get_project_root()

def test_ensure_dir():
    """Test directory creation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / 'test_dir'
        ensure_dir(test_dir)
        assert test_dir.exists()
        assert test_dir.is_dir()

def test_get_file_size():
    """Test getting file size."""
    with tempfile.NamedTemporaryFile() as f:
        f.write(b'test content')
        f.flush()
        size = get_file_size(Path(f.name))
        assert size == len(b'test content')

def test_format_size():
    """Test size formatting."""
    assert format_size(1024) == '1.00 KB'
    assert format_size(1024 * 1024) == '1.00 MB'
    assert format_size(1024 * 1024 * 1024) == '1.00 GB'
    assert format_size(1024 * 1024 * 1024 * 1024) == '1.00 TB'
    assert format_size(1024 * 1024 * 1024 * 1024 * 1024) == '1.00 PB' 