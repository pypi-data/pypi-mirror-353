"""
Tests for the configuration management functionality.
"""

import os
import tempfile
import pytest
from pathlib import Path
from evolvishub_datacleanup.config import ConfigManager

@pytest.fixture
def temp_ini_config():
    """Create a temporary INI configuration file."""
    config_content = """
[folders]
data1 = /path/to/data1
data2 = /path/to/data2

[thresholds]
max_size_gb = 1.0
max_age_days = 30

[backup]
directory = /path/to/backup
max_age_days = 90

[monitoring]
check_interval_seconds = 3600

[retention]
policy_log = 7
policy_temp = 1
policy_archive = 365

[scheduler]
days = Monday,Wednesday,Friday
hours = 2,14,22
cron = 0 2 * * 1,3,5

[archive]
directory = /path/to/archives
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
def temp_yaml_config():
    """Create a temporary YAML configuration file."""
    config_content = """
data_folders:
  - /path/to/data1
  - /path/to/data2

cleanup_thresholds:
  max_size_gb: 1.0
  max_age_days: 30

backup_settings:
  directory: /path/to/backup
  max_backup_age_days: 90

monitoring_settings:
  check_interval: 3600

retention_policies:
  .log:
    max_age_days: 7
  .tmp:
    max_age_days: 1
  archive:
    max_age_days: 365

scheduler:
  days: [Monday, Wednesday, Friday]
  hours: [2, 14, 22]
  cron: "0 2 * * 1,3,5"

archive_settings:
  directory: /path/to/archives
  format: zip
  compress_level: 6
  password_protect: false
  password: ""
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
    yield f.name
    os.unlink(f.name)

def test_ini_config_loading(temp_ini_config):
    """Test loading INI configuration."""
    config = ConfigManager(temp_ini_config)
    
    # Test data folders
    folders = config.get_data_folders()
    assert len(folders) == 2
    assert '/path/to/data1' in folders
    assert '/path/to/data2' in folders
    
    # Test thresholds
    thresholds = config.get_cleanup_thresholds()
    assert thresholds['max_size_gb'] == 1.0
    assert thresholds['max_age_days'] == 30
    
    # Test backup settings
    backup = config.get_backup_settings()
    assert backup['backup_dir'] == '/path/to/backup'
    assert backup['max_backup_age_days'] == 90
    
    # Test monitoring settings
    monitoring = config.get_monitoring_settings()
    assert monitoring['check_interval'] == 3600
    
    # Test retention policies
    policies = config.get_retention_policies()
    assert policies['log']['max_age_days'] == 7
    assert policies['temp']['max_age_days'] == 1
    assert policies['archive']['max_age_days'] == 365
    
    # Test scheduler settings
    scheduler = config.get_scheduler_settings()
    assert 'Monday,Wednesday,Friday' in scheduler['days']
    assert '2,14,22' in scheduler['hours']
    assert '0 2 * * 1,3,5' in scheduler['cron']
    
    # Test archive settings
    archive = config.get_archive_settings()
    assert archive['archive_dir'] == '/path/to/archives'
    assert archive['format'] == 'zip'
    assert archive['compress_level'] == 6
    assert not archive['password_protect']

def test_yaml_config_loading(temp_yaml_config):
    """Test loading YAML configuration."""
    config = ConfigManager(temp_yaml_config)
    
    # Test data folders
    folders = config.get_data_folders()
    assert len(folders) == 2
    assert '/path/to/data1' in folders
    assert '/path/to/data2' in folders
    
    # Test thresholds
    thresholds = config.get_cleanup_thresholds()
    assert thresholds['max_size_gb'] == 1.0
    assert thresholds['max_age_days'] == 30
    
    # Test backup settings
    backup = config.get_backup_settings()
    assert backup['directory'] == '/path/to/backup'
    assert backup['max_backup_age_days'] == 90
    
    # Test monitoring settings
    monitoring = config.get_monitoring_settings()
    assert monitoring['check_interval'] == 3600
    
    # Test retention policies
    policies = config.get_retention_policies()
    assert policies['.log']['max_age_days'] == 7
    assert policies['.tmp']['max_age_days'] == 1
    assert policies['archive']['max_age_days'] == 365
    
    # Test scheduler settings
    scheduler = config.get_scheduler_settings()
    assert scheduler['days'] == ['Monday', 'Wednesday', 'Friday']
    assert scheduler['hours'] == [2, 14, 22]
    assert scheduler['cron'] == '0 2 * * 1,3,5'
    
    # Test archive settings
    archive = config.get_archive_settings()
    assert archive['directory'] == '/path/to/archives'
    assert archive['format'] == 'zip'
    assert archive['compress_level'] == 6
    assert not archive['password_protect']

def test_invalid_config_file():
    """Test handling of invalid configuration file."""
    with pytest.raises(FileNotFoundError):
        ConfigManager('nonexistent.ini')

def test_invalid_config_format():
    """Test handling of invalid configuration format."""
    with tempfile.NamedTemporaryFile(suffix='.txt') as f:
        with pytest.raises(ValueError):
            ConfigManager(f.name) 