"""
Modular Directory Scanner for Medical Document Extractor

This module provides flexible directory scanning and file discovery capabilities
for processing medical documents from various directory structures.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Optional, Callable, Set
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class FileInfo:
    """Represents information about a discovered file."""
    absolute_path: Path
    relative_path: str
    filename: str
    file_type: str
    file_size: int
    last_modified: datetime
    is_directory: bool = False
    
    def __post_init__(self):
        if not self.is_directory:
            self.file_type = self._determine_file_type()
    
    def _determine_file_type(self) -> str:
        """Determine file type based on extension."""
        ext = self.absolute_path.suffix.lower()
        if ext == '.pdf':
            return 'pdf'
        elif ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            return 'image'
        elif ext in ['.txt', '.doc', '.docx']:
            return 'text'
        else:
            return 'other'

class DirectoryScanner:
    """
    Modular directory scanner for discovering files in directory structures.
    
    Supports:
    - Recursive directory traversal
    - File type filtering
    - Custom file filters
    - Directory-based processing
    - Metadata tracking
    """
    
    def __init__(self, 
                 base_directory: str = "app/data",
                 supported_extensions: Set[str] = None,
                 max_depth: int = None):
        """
        Initialize the directory scanner.
        
        Args:
            base_directory: Root directory to scan
            supported_extensions: Set of file extensions to include (e.g., {'.pdf', '.jpg'})
            max_depth: Maximum directory depth to traverse (None for unlimited)
        """
        self.base_directory = Path(base_directory)
        self.supported_extensions = supported_extensions or {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
        self.max_depth = max_depth
        self._validate_base_directory()
    
    def _validate_base_directory(self):
        """Validate that the base directory exists and is accessible."""
        if not self.base_directory.exists():
            raise FileNotFoundError(f"Base directory does not exist: {self.base_directory}")
        if not self.base_directory.is_dir():
            raise NotADirectoryError(f"Base directory is not a directory: {self.base_directory}")
    
    def scan_directory(self, 
                      target_directory: Optional[str] = None,
                      file_filter: Optional[Callable[[Path], bool]] = None,
                      directory_filter: Optional[Callable[[Path], bool]] = None) -> List[FileInfo]:
        """
        Scan directory and discover files.
        
        Args:
            target_directory: Specific directory to scan (relative to base_directory)
            file_filter: Custom function to filter files (returns True to include)
            directory_filter: Custom function to filter directories (returns True to include)
            
        Returns:
            List of FileInfo objects representing discovered files
        """
        scan_path = self.base_directory
        if target_directory:
            scan_path = self.base_directory / target_directory
            if not scan_path.exists():
                logger.warning(f"Target directory does not exist: {scan_path}")
                return []
        
        discovered_files = []
        
        try:
            for root, dirs, files in os.walk(scan_path):
                # Apply directory filter if provided
                if directory_filter:
                    dirs[:] = [d for d in dirs if directory_filter(Path(root) / d)]
                
                # Check depth limit
                current_depth = len(Path(root).relative_to(scan_path).parts)
                if self.max_depth is not None and current_depth >= self.max_depth:
                    dirs.clear()  # Don't traverse deeper
                    continue
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # Apply extension filter
                    if file_path.suffix.lower() not in self.supported_extensions:
                        continue
                    
                    # Apply custom file filter if provided
                    if file_filter and not file_filter(file_path):
                        continue
                    
                    try:
                        file_info = self._create_file_info(file_path, scan_path)
                        discovered_files.append(file_info)
                        logger.debug(f"Discovered file: {file_info.relative_path}")
                    except Exception as e:
                        logger.error(f"Error processing file {file_path}: {e}")
                        
        except Exception as e:
            logger.error(f"Error scanning directory {scan_path}: {e}")
        
        logger.info(f"Discovered {len(discovered_files)} files in {scan_path}")
        return discovered_files
    
    def scan_by_directory_name(self, 
                              directory_name: str,
                              recursive: bool = True) -> List[FileInfo]:
        """
        Scan files from a specific directory by name.
        
        Args:
            directory_name: Name of the directory to scan
            recursive: Whether to scan subdirectories
            
        Returns:
            List of FileInfo objects
        """
        target_path = self.base_directory / directory_name
        
        if not target_path.exists():
            logger.warning(f"Directory not found: {target_path}")
            return []
        
        if recursive:
            return self.scan_directory(target_directory=directory_name)
        else:
            # Non-recursive scan
            discovered_files = []
            try:
                for item in target_path.iterdir():
                    if item.is_file() and item.suffix.lower() in self.supported_extensions:
                        file_info = self._create_file_info(item, self.base_directory)
                        discovered_files.append(file_info)
                        logger.debug(f"Discovered file: {file_info.relative_path}")
            except Exception as e:
                logger.error(f"Error scanning directory {target_path}: {e}")
            
            logger.info(f"Discovered {len(discovered_files)} files in {target_path}")
            return discovered_files
    
    def _create_file_info(self, file_path: Path, base_path: Path) -> FileInfo:
        """Create a FileInfo object from a file path."""
        stat = file_path.stat()
        return FileInfo(
            absolute_path=file_path,
            relative_path=str(file_path.relative_to(base_path)),
            filename=file_path.name,
            file_type='',  # Will be set by __post_init__
            file_size=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
            is_directory=False
        )
    
    def get_directory_structure(self, max_depth: int = 3) -> Dict:
        """
        Get the directory structure for visualization/debugging.
        
        Args:
            max_depth: Maximum depth to show in structure
            
        Returns:
            Dictionary representing directory structure
        """
        structure = {}
        
        def build_structure(path: Path, depth: int = 0):
            if depth > max_depth:
                return
            
            if not path.exists():
                return
            
            current_level = {}
            
            try:
                for item in path.iterdir():
                    if item.is_dir():
                        sub_structure = build_structure(item, depth + 1)
                        if sub_structure:
                            current_level[item.name] = sub_structure
                    else:
                        if item.suffix.lower() in self.supported_extensions:
                            current_level[item.name] = {
                                'type': 'file',
                                'size': item.stat().st_size,
                                'extension': item.suffix.lower()
                            }
            except PermissionError:
                logger.warning(f"Permission denied accessing: {path}")
            except Exception as e:
                logger.error(f"Error accessing {path}: {e}")
            
            return current_level
        
        structure = build_structure(self.base_directory)
        return structure
    
    def list_available_directories(self) -> List[str]:
        """
        List all available directories in the base directory.
        
        Returns:
            List of directory names
        """
        directories = []
        try:
            for item in self.base_directory.iterdir():
                if item.is_dir():
                    directories.append(item.name)
        except Exception as e:
            logger.error(f"Error listing directories: {e}")
        
        return sorted(directories)

# Utility functions for common scanning patterns

def create_policy_document_scanner(base_dir: str = "app/data") -> DirectoryScanner:
    """Create a scanner specifically for policy documents."""
    return DirectoryScanner(
        base_directory=base_dir,
        supported_extensions={'.pdf', '.jpg', '.jpeg', '.png'},
        max_depth=None
    )

def create_medical_document_scanner(base_dir: str = "app/data") -> DirectoryScanner:
    """Create a scanner for general medical documents."""
    return DirectoryScanner(
        base_directory=base_dir,
        supported_extensions={'.pdf', '.jpg', '.jpeg', '.png', '.tiff'},
        max_depth=None
    )

def filter_by_filename_pattern(pattern: str) -> Callable[[Path], bool]:
    """Create a file filter based on filename pattern."""
    def filter_func(file_path: Path) -> bool:
        return pattern.lower() in file_path.name.lower()
    return filter_func

def filter_by_size(min_size: int = 0, max_size: int = None) -> Callable[[Path], bool]:
    """Create a file filter based on file size."""
    def filter_func(file_path: Path) -> bool:
        try:
            size = file_path.stat().st_size
            if size < min_size:
                return False
            if max_size and size > max_size:
                return False
            return True
        except (OSError, IOError):
            return False
    return filter_func 