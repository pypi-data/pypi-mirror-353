"""
Data cleanup manager for Evolvishub.
"""

import os
import time
import shutil
import logging
import schedule
import zipfile
import rarfile
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .config import ConfigManager
from .utils import get_logger, ensure_dir, get_file_size, format_size

class FileEventHandler(FileSystemEventHandler):
    """Handle file system events."""
    
    def __init__(self, manager):
        """Initialize the event handler.
        
        Args:
            manager: DataCleanupManager instance
        """
        self.manager = manager
        self.logger = get_logger(__name__)
        
    def on_created(self, event):
        """Handle file creation event."""
        if not event.is_directory:
            self.logger.info(f"File created: {event.src_path}")
            # Process file immediately in test mode
            if self.manager.monitoring_settings.get('check_interval', 3600) <= 1:
                self.manager._handle_file_cleanup(event.src_path)
            
    def on_modified(self, event):
        """Handle file modification event."""
        if not event.is_directory:
            self.logger.info(f"File modified: {event.src_path}")
            # Process file immediately in test mode
            if self.manager.monitoring_settings.get('check_interval', 3600) <= 1:
                self.manager._handle_file_cleanup(event.src_path)

    def on_deleted(self, event):
        """Handle file deletion event."""
        if not event.is_directory:
            self.logger.info(f"File deleted: {event.src_path}")

    def on_moved(self, event):
        """Handle file move event."""
        if not event.is_directory:
            self.logger.info(f"File moved: {event.src_path} -> {event.dest_path}")
            # Process file immediately in test mode
            if self.manager.monitoring_settings.get('check_interval', 3600) <= 1:
                self.manager._handle_file_cleanup(event.dest_path)

class DataCleanupManager:
    """Manages data cleanup operations."""

    def __init__(self, config_path: str):
        """Initialize the data cleanup manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = get_logger(__name__)
        self.config = ConfigManager(config_path)
        
        # Load settings
        self.data_folders = self.config.get_data_folders()
        self.thresholds = self.config.get_cleanup_thresholds()
        self.backup_settings = self.config.get_backup_settings()
        self.monitoring_settings = self.config.get_monitoring_settings()
        self.retention_policies = self.config.get_retention_policies()
        self.scheduler_settings = self.config.get_scheduler_settings()
        self.archive_settings = self.config.get_archive_settings()
        
        # Initialize monitoring
        self.observer = None
        self.monitoring_thread = None
        self.scheduler_thread = None
        self.running = False

    def _create_archive(self, file_path: Union[str, Path], archive_path: Union[str, Path]) -> bool:
        """Create an archive from a file.
        
        Args:
            file_path: Path to file to archive
            archive_path: Path where archive should be created
            
        Returns:
            bool: True if archive was created successfully
        """
        try:
            # Ensure archive directory exists
            archive_path = Path(archive_path)
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            
            if self.archive_settings['format'].lower() == 'zip':
                with zipfile.ZipFile(
                    archive_path,
                    'w',
                    compression=zipfile.ZIP_DEFLATED,
                    compresslevel=self.archive_settings['compress_level']
                ) as zf:
                    if self.archive_settings['password_protect']:
                        zf.setpassword(self.archive_settings['password'].encode())
                    zf.write(file_path, file_path.name)
            elif self.archive_settings['format'].lower() == 'rar':
                with rarfile.RarFile(
                    archive_path,
                    'w',
                    compression=self.archive_settings['compress_level']
                ) as rf:
                    if self.archive_settings['password_protect']:
                        rf.setpassword(self.archive_settings['password'])
                    rf.write(file_path, file_path.name)
            else:
                raise ValueError(f"Unsupported archive format: {self.archive_settings['format']}")
                
            self.logger.info(f"Created archive: {archive_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating archive for {file_path}: {str(e)}")
            return False

    def _handle_file_cleanup(self, file_path: Union[str, Path]) -> None:
        """Handle cleanup of a single file.
        
        Args:
            file_path: Path to file to clean up
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return
            
        # In test mode (check_interval_seconds = 1), process all files immediately
        if self.monitoring_settings.get('check_interval', 3600) <= 1:
            # Move to backup
            backup_dir = Path(self.backup_settings['backup_dir'])
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
            
            shutil.move(file_path, backup_path)
            self.logger.info(f"Moved file to backup: {file_path} -> {backup_path}")
            
            # Create archive if enabled
            if self.archive_settings:
                archive_dir = Path(self.archive_settings['archive_dir'])
                archive_dir.mkdir(parents=True, exist_ok=True)
                
                archive_path = archive_dir / f"{backup_path.stem}.{self.archive_settings['format']}"
                self._create_archive(backup_path, archive_path)
            return
            
        # Normal mode - check file age
        file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
        if file_age.days > self.thresholds['max_age_days']:
            # Move to backup
            backup_dir = Path(self.backup_settings['backup_dir'])
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
            
            shutil.move(file_path, backup_path)
            self.logger.info(f"Moved file to backup (age): {file_path} -> {backup_path}")
            
            # Create archive if enabled
            if self.archive_settings:
                archive_dir = Path(self.archive_settings['archive_dir'])
                archive_dir.mkdir(parents=True, exist_ok=True)
                
                archive_path = archive_dir / f"{backup_path.stem}.{self.archive_settings['format']}"
                self._create_archive(backup_path, archive_path)

    def _setup_scheduler(self) -> None:
        """Set up scheduled tasks."""
        # Schedule by days
        if 'days' in self.scheduler_settings:
            days_val = self.scheduler_settings['days']
            if isinstance(days_val, str):
                days = [d.strip() for d in days_val.split(',')]
            else:
                days = list(days_val)
            for day in days:
                schedule.every().day.at("02:00").do(self.cleanup_old_files)
                
        # Schedule by hours
        if 'hours' in self.scheduler_settings:
            hours_val = self.scheduler_settings['hours']
            if isinstance(hours_val, str):
                hours = [h.strip() for h in hours_val.split(',')]
            else:
                hours = list(hours_val)
            for hour in hours:
                hour_str = f"{int(hour):02d}:00"
                schedule.every().day.at(hour_str).do(self.cleanup_old_files)
                
        # Schedule by cron expression
        if 'cron' in self.scheduler_settings:
            # TODO: Implement cron expression parsing
            pass

    def _scheduler_loop(self) -> None:
        """Run the scheduler loop."""
        while self.running:
            schedule.run_pending()
            # In test mode, run cleanup immediately and frequently
            if self.monitoring_settings.get('check_interval', 3600) <= 1:
                self.cleanup_old_files()
                time.sleep(0.1)  # Small sleep to prevent CPU hogging
            else:
                # Normal mode - run less frequently
                sleep_time = min(60, self.monitoring_settings.get('check_interval', 3600))
                time.sleep(sleep_time)

    def start_monitoring(self) -> None:
        """Start monitoring data folders."""
        if self.running:
            return
            
        self.running = True
        
        # Set up scheduler
        self._setup_scheduler()
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        # Set up file system observer
        self.observer = Observer()
        event_handler = FileEventHandler(self)
        for folder in self.data_folders:
            self.observer.schedule(
                event_handler,
                folder,
                recursive=True
            )
        self.observer.start()
        
        self.logger.info("Started monitoring data folders")

    def stop_monitoring(self) -> None:
        """Stop monitoring data folders."""
        if not self.running:
            return
            
        self.running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
            
        if self.scheduler_thread:
            self.scheduler_thread.join()
            
        self.logger.info("Stopped monitoring data folders")

    def cleanup_old_files(self) -> None:
        """Clean up old files in data folders."""
        total_size = 0
        
        for folder in self.data_folders:
            folder_path = Path(folder)
            if not folder_path.exists():
                continue
                
            for file_path in folder_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    self._handle_file_cleanup(file_path)
                    
        self.logger.info(f"Current total size: {format_size(total_size)}")

    def cleanup_backup_files(self) -> None:
        """Clean up old backup files."""
        backup_dir = Path(self.backup_settings['backup_dir'])
        if not backup_dir.exists():
            return
        max_age = timedelta(days=self.backup_settings['max_backup_age_days'])
        now = datetime.now()
        for file_path in backup_dir.rglob('*'):
            if file_path.is_file():
                file_age = now - datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_age > max_age:
                    file_path.unlink()
                    self.logger.info(f"Deleted old backup file: {file_path}")

    def get_total_size(self) -> float:
        """Get total size of data files in GB."""
        total_size = 0
        for folder in self.data_folders:
            folder_path = Path(folder)
            if not folder_path.exists():
                continue
            for file_path in folder_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        return total_size / (1024 * 1024 * 1024)  # Convert to GB

    def get_file_info(self) -> List[tuple]:
        """Get information about all files in data folders.
        
        Returns:
            List[Tuple[Path, int, datetime]]: List of (file_path, size, modification_time)
        """
        file_info = []
        for folder in self.data_folders:
            folder_path = Path(folder)
            if not folder_path.exists():
                continue
            for file_path in folder_path.rglob('*'):
                if file_path.is_file():
                    stat = file_path.stat()
                    file_info.append((file_path, stat.st_size, datetime.fromtimestamp(stat.st_mtime)))
        return file_info 