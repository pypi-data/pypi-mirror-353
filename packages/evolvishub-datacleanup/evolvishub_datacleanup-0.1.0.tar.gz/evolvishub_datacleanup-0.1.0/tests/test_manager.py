"""
Tests for the data cleanup management functionality.
"""

import os
import tempfile
import time
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from evolvishub_datacleanup.manager import DataCleanupManager

@pytest.fixture
def temp_data_dir():
    """Create a temporary directory with test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        data_dir = Path(temp_dir) / 'data'
        data_dir.mkdir()
        
        # Create some test files
        (data_dir / 'test1.txt').write_text('test1')
        (data_dir / 'test2.txt').write_text('test2')
        (data_dir / 'test3.log').write_text('test3')
        
        # Create a subdirectory with files
        subdir = data_dir / 'subdir'
        subdir.mkdir()
        (subdir / 'test4.txt').write_text('test4')
        
        yield temp_dir

@pytest.fixture
def temp_config(temp_data_dir):
    """Create a temporary configuration file."""
    config_content = f"""
[folders]
data = {temp_data_dir}/data

[thresholds]
max_size_gb = 0.0001
max_age_days = 1

[backup]
directory = {temp_data_dir}/backup
max_age_days = 7

[monitoring]
check_interval_seconds = 1

[retention]
policy_log = 1
policy_temp = 1
policy_archive = 7

[scheduler]
days = Monday,Wednesday,Friday
hours = 2,14,22
cron = 0 2 * * 1,3,5

[archive]
directory = {temp_data_dir}/archives
format = zip
compress_level = 6
password_protect = false
password = 
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write(config_content)
    yield f.name
    os.unlink(f.name)

@pytest.fixture
def temp_yaml_config(temp_data_dir):
    """Create a temporary YAML configuration file."""
    config_content = f"""
data_folders:
  - {temp_data_dir}/data

cleanup_thresholds:
  max_size_gb: 0.0001
  max_age_days: 1

backup_settings:
  directory: {temp_data_dir}/backup
  max_backup_age_days: 7

monitoring_settings:
  check_interval: 1

retention_policies:
  .log:
    max_age_days: 1
  .tmp:
    max_age_days: 1
  archive:
    max_age_days: 7

scheduler:
  days: [Monday, Wednesday, Friday]
  hours: [2, 14, 22]
  cron: "0 2 * * 1,3,5"

archive_settings:
  directory: {temp_data_dir}/archives
  format: zip
  compress_level: 6
  password_protect: false
  password: ""
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
    yield f.name
    os.unlink(f.name)

def test_initialization(temp_config):
    """Test DataCleanupManager initialization."""
    manager = DataCleanupManager(temp_config)
    assert manager.data_folders
    assert manager.thresholds
    assert manager.backup_settings
    assert manager.monitoring_settings
    assert manager.retention_policies
    assert manager.scheduler_settings
    assert manager.archive_settings

def test_get_total_size(temp_config, temp_data_dir):
    """Test getting total size of data files."""
    manager = DataCleanupManager(temp_config)
    total_size = manager.get_total_size()
    assert total_size > 0

def test_get_file_info(temp_config, temp_data_dir):
    """Test getting file information."""
    manager = DataCleanupManager(temp_config)
    file_info = manager.get_file_info()
    assert len(file_info) == 4  # 4 test files
    for path, size, mod_time in file_info:
        assert isinstance(path, Path)
        assert isinstance(size, (int, float))
        assert isinstance(mod_time, datetime)

def test_cleanup_old_files(temp_config, temp_data_dir):
    """Test cleaning up old files."""
    manager = DataCleanupManager(temp_config)
    
    # Create an old file
    old_file = Path(temp_data_dir) / 'data' / 'old.txt'
    old_file.write_text('old')
    old_time = datetime.now() - timedelta(days=2)
    os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))
    
    # Run cleanup
    manager.cleanup_old_files()
    
    # Check if file was moved to backup
    backup_dir = Path(temp_data_dir) / 'backup'
    assert any(f.name.startswith('old_') for f in backup_dir.glob('*.txt'))
    
    # Check if archive was created
    archive_dir = Path(temp_data_dir) / 'archives'
    assert any(f.suffix == '.zip' for f in archive_dir.glob('*'))

def test_cleanup_backup_files(temp_config, temp_data_dir):
    """Test cleaning up old backup files."""
    manager = DataCleanupManager(temp_config)
    
    # Create an old backup file
    backup_dir = Path(temp_data_dir) / 'backup'
    backup_dir.mkdir(exist_ok=True)
    old_backup = backup_dir / 'old_backup.txt'
    old_backup.write_text('old backup')
    old_time = datetime.now() - timedelta(days=8)
    os.utime(old_backup, (old_time.timestamp(), old_time.timestamp()))
    
    # Run cleanup
    manager.cleanup_backup_files()
    
    # Check if old backup was deleted
    assert not old_backup.exists()

def test_monitoring(temp_config, temp_data_dir):
    """Test monitoring functionality."""
    manager = DataCleanupManager(temp_config)
    
    # Start monitoring
    manager.start_monitoring()
    
    # Create a new file
    new_file = Path(temp_data_dir) / 'data' / 'new.txt'
    new_file.write_text('new')
    
    # Wait for monitoring to detect changes
    time.sleep(2)
    
    # Stop monitoring
    manager.stop_monitoring()
    
    # Check if file was processed
    assert not new_file.exists()
    backup_dir = Path(temp_data_dir) / 'backup'
    assert any(f.name.startswith('new_') for f in backup_dir.glob('*.txt'))

def test_scheduler(temp_config, temp_data_dir):
    """Test scheduler functionality."""
    manager = DataCleanupManager(temp_config)
    
    # Start monitoring (includes scheduler)
    manager.start_monitoring()
    
    # Create a test file
    test_file = Path(temp_data_dir) / 'data' / 'scheduled.txt'
    test_file.write_text('scheduled')
    
    # Wait for scheduler to run
    time.sleep(3)
    
    # Stop monitoring
    manager.stop_monitoring()
    
    # Check if file was processed
    assert not test_file.exists()
    backup_dir = Path(temp_data_dir) / 'backup'
    assert any(f.name.startswith('scheduled_') for f in backup_dir.glob('*.txt'))

def test_archive_creation(temp_config, temp_data_dir):
    """Test archive creation functionality."""
    manager = DataCleanupManager(temp_config)
    
    # Create a test file
    test_file = Path(temp_data_dir) / 'data' / 'to_archive.txt'
    test_file.write_text('test content')
    
    # Create archive
    archive_dir = Path(temp_data_dir) / 'archives'
    archive_path = archive_dir / 'test.zip'
    manager._create_archive(test_file, archive_path)
    
    # Check if archive was created
    assert archive_path.exists()
    assert archive_path.stat().st_size > 0

def test_password_protected_archive(temp_config, temp_data_dir):
    """Test password-protected archive creation."""
    # Modify config to enable password protection
    config_content = f"""
[folders]
data = {temp_data_dir}/data

[thresholds]
max_size_gb = 0.0001
max_age_days = 1

[backup]
directory = {temp_data_dir}/backup
max_age_days = 7

[monitoring]
check_interval_seconds = 1

[retention]
policy_log = 1
policy_temp = 1
policy_archive = 7

[scheduler]
days = Monday,Wednesday,Friday
hours = 2,14,22
cron = 0 2 * * 1,3,5

[archive]
directory = {temp_data_dir}/archives
format = zip
compress_level = 6
password_protect = true
password = test123
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write(config_content)
    
    try:
        manager = DataCleanupManager(f.name)
        
        # Create a test file
        test_file = Path(temp_data_dir) / 'data' / 'protected.txt'
        test_file.write_text('protected content')
        
        # Create archive
        archive_dir = Path(temp_data_dir) / 'archives'
        archive_path = archive_dir / 'protected.zip'
        manager._create_archive(test_file, archive_path)
        
        # Check if archive was created
        assert archive_path.exists()
        assert archive_path.stat().st_size > 0
        
    finally:
        os.unlink(f.name)

def test_yaml_config_initialization(temp_yaml_config):
    """Test DataCleanupManager initialization with YAML config."""
    manager = DataCleanupManager(temp_yaml_config)
    assert manager.data_folders
    assert manager.thresholds
    assert manager.backup_settings
    assert manager.monitoring_settings
    assert manager.retention_policies
    assert manager.scheduler_settings
    assert manager.archive_settings

def test_yaml_config_cleanup(temp_yaml_config, temp_data_dir):
    """Test cleanup with YAML config."""
    manager = DataCleanupManager(temp_yaml_config)
    
    # Create an old file
    old_file = Path(temp_data_dir) / 'data' / 'old.txt'
    old_file.write_text('old')
    old_time = datetime.now() - timedelta(days=2)
    os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))
    
    # Run cleanup
    manager.cleanup_old_files()
    
    # Check if file was moved to backup
    backup_dir = Path(temp_data_dir) / 'backup'
    assert any(f.name.startswith('old_') for f in backup_dir.glob('*.txt'))
    
    # Check if archive was created
    archive_dir = Path(temp_data_dir) / 'archives'
    assert any(f.suffix == '.zip' for f in archive_dir.glob('*')) 