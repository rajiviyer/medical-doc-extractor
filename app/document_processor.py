"""
Comprehensive Document Processor for Medical Document Extractor

This module provides a complete pipeline for processing medical documents,
combining directory scanning, text extraction, error handling, and standardized output.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

from app.directory_scanner import DirectoryScanner, FileInfo
from app.text_extractor import TextExtractor, ExtractionResult

logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """Represents the complete result of document processing."""
    processing_id: str
    timestamp: str
    input_directory: str
    total_files_discovered: int
    successful_extractions: int
    failed_extractions: int
    processing_time: float
    extraction_results: List[ExtractionResult]
    errors: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Convert ExtractionResult objects to dictionaries
        result['extraction_results'] = [
            {
                'filename': r.filename,
                'file_type': r.file_type,
                'extraction_method': r.extraction_method,
                'extraction_success': r.extraction_success,
                'text_content': r.text_content,
                'confidence_score': r.confidence_score,
                'processing_time': r.processing_time,
                'page_count': r.page_count,
                'error_message': r.error_message,
                'metadata': r.metadata
            }
            for r in self.extraction_results
        ]
        return result

class DocumentProcessor:
    """
    Comprehensive document processor that handles the complete pipeline.
    
    Features:
    - Directory scanning and file discovery
    - Text extraction with fallback strategies
    - Error handling and logging
    - Standardized JSON output
    - Batch processing capabilities
    """
    
    def __init__(self, 
                 base_directory: str = "app/data",
                 output_directory: str = "app/output",
                 enable_fallback: bool = True,
                 max_file_size: int = 50 * 1024 * 1024):  # 50MB
        """
        Initialize the document processor.
        
        Args:
            base_directory: Root directory to scan
            output_directory: Directory for output files
            enable_fallback: Whether to use OCR fallback for failed PDF extraction
            max_file_size: Maximum file size to process
        """
        self.base_directory = Path(base_directory)
        self.output_directory = Path(output_directory)
        self.enable_fallback = enable_fallback
        self.max_file_size = max_file_size
        
        # Initialize components
        self.scanner = DirectoryScanner(base_directory=base_directory)
        self.extractor = TextExtractor(
            enable_fallback=enable_fallback,
            max_file_size=max_file_size
        )
        
        # Ensure output directory exists
        self.output_directory.mkdir(parents=True, exist_ok=True)
    
    def process_directory(self, 
                         target_directory: Optional[str] = None,
                         file_filter: Optional[str] = None) -> ProcessingResult:
        """
        Process all documents in a directory.
        
        Args:
            target_directory: Specific directory to process (relative to base_directory)
            file_filter: Optional filename pattern to filter files
            
        Returns:
            ProcessingResult with complete processing details
        """
        start_time = datetime.now()
        processing_id = f"proc_{start_time.strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Starting document processing: {processing_id}")
        logger.info(f"Target directory: {target_directory or 'all'}")
        
        # Step 1: Discover files
        logger.info("Step 1: Discovering files...")
        discovered_files = self._discover_files(target_directory, file_filter)
        
        if not discovered_files:
            logger.warning("No files discovered for processing")
            return self._create_empty_result(processing_id, start_time)
        
        logger.info(f"Discovered {len(discovered_files)} files")
        
        # Step 2: Extract text from files
        logger.info("Step 2: Extracting text from files...")
        extraction_results = self._extract_text_from_files(discovered_files)
        
        # Step 3: Generate processing result
        logger.info("Step 3: Generating processing result...")
        result = self._create_processing_result(
            processing_id, start_time, discovered_files, extraction_results
        )
        
        # Step 4: Save results
        logger.info("Step 4: Saving results...")
        self._save_results(result)
        
        logger.info(f"Document processing completed: {result.successful_extractions}/{result.total_files_discovered} successful")
        
        return result
    
    def process_by_directory_name(self, 
                                 directory_name: str,
                                 recursive: bool = True) -> ProcessingResult:
        """
        Process documents from a specific directory by name.
        
        Args:
            directory_name: Name of the directory to process
            recursive: Whether to process subdirectories
            
        Returns:
            ProcessingResult with complete processing details
        """
        logger.info(f"Processing directory: {directory_name}")
        
        # Discover files from specific directory
        discovered_files = self.scanner.scan_by_directory_name(
            directory_name, recursive=recursive
        )
        
        if not discovered_files:
            logger.warning(f"No files found in directory: {directory_name}")
            return self._create_empty_result(
                f"proc_{datetime.now().strftime('%Y%m%d_%H%M%S')}", 
                datetime.now()
            )
        
        # Extract text from discovered files
        extraction_results = self._extract_text_from_files(discovered_files)
        
        # Create and save processing result
        result = self._create_processing_result(
            f"proc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            datetime.now(),
            discovered_files,
            extraction_results
        )
        
        self._save_results(result)
        
        return result
    
    def _discover_files(self, 
                        target_directory: Optional[str] = None,
                        file_filter: Optional[str] = None) -> List[FileInfo]:
        """Discover files using the directory scanner."""
        try:
            if file_filter:
                from app.directory_scanner import filter_by_filename_pattern
                filter_func = filter_by_filename_pattern(file_filter)
                files = self.scanner.scan_directory(
                    target_directory=target_directory,
                    file_filter=filter_func
                )
            else:
                files = self.scanner.scan_directory(target_directory=target_directory)
            
            return files
            
        except Exception as e:
            logger.error(f"Error discovering files: {e}")
            return []
    
    def _extract_text_from_files(self, files: List[FileInfo]) -> List[ExtractionResult]:
        """Extract text from a list of files."""
        file_paths = [f.absolute_path for f in files]
        return self.extractor.batch_extract(file_paths)
    
    def _create_processing_result(self,
                                 processing_id: str,
                                 start_time: datetime,
                                 discovered_files: List[FileInfo],
                                 extraction_results: List[ExtractionResult]) -> ProcessingResult:
        """Create a comprehensive processing result."""
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        successful_extractions = sum(1 for r in extraction_results if r.extraction_success)
        failed_extractions = len(extraction_results) - successful_extractions
        
        # Collect errors
        errors = []
        for result in extraction_results:
            if not result.extraction_success and result.error_message:
                errors.append(f"{result.filename}: {result.error_message}")
        
        # Calculate statistics
        total_text_length = sum(
            len(r.text_content) for r in extraction_results 
            if r.extraction_success and r.text_content
        )
        
        avg_confidence = sum(r.confidence_score for r in extraction_results) / len(extraction_results) if extraction_results else 0
        
        metadata = {
            'total_text_length': total_text_length,
            'average_confidence': avg_confidence,
            'file_types': list(set(r.file_type for r in extraction_results)),
            'extraction_methods': list(set(r.extraction_method for r in extraction_results)),
            'base_directory': str(self.base_directory),
            'enable_fallback': self.enable_fallback,
            'max_file_size': self.max_file_size
        }
        
        return ProcessingResult(
            processing_id=processing_id,
            timestamp=start_time.isoformat(),
            input_directory=str(self.base_directory),
            total_files_discovered=len(discovered_files),
            successful_extractions=successful_extractions,
            failed_extractions=failed_extractions,
            processing_time=processing_time,
            extraction_results=extraction_results,
            errors=errors,
            metadata=metadata
        )
    
    def _create_empty_result(self, processing_id: str, start_time: datetime) -> ProcessingResult:
        """Create an empty processing result for when no files are found."""
        return ProcessingResult(
            processing_id=processing_id,
            timestamp=start_time.isoformat(),
            input_directory=str(self.base_directory),
            total_files_discovered=0,
            successful_extractions=0,
            failed_extractions=0,
            processing_time=0.0,
            extraction_results=[],
            errors=["No files discovered for processing"],
            metadata={}
        )
    
    def _save_results(self, result: ProcessingResult):
        """Save processing results to JSON file."""
        try:
            output_file = self.output_directory / f"{result.processing_id}_results.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to: {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def get_available_directories(self) -> List[str]:
        """Get list of available directories for processing."""
        return self.scanner.list_available_directories()
    
    def get_directory_structure(self, max_depth: int = 3) -> Dict:
        """Get directory structure for visualization."""
        return self.scanner.get_directory_structure(max_depth)

# Utility functions for common processing patterns

def create_policy_processor(base_dir: str = "app/data", output_dir: str = "app/output") -> DocumentProcessor:
    """Create a processor optimized for policy documents."""
    return DocumentProcessor(
        base_directory=base_dir,
        output_directory=output_dir,
        enable_fallback=True,
        max_file_size=100 * 1024 * 1024  # 100MB for policy documents
    )

def create_medical_processor(base_dir: str = "app/data", output_dir: str = "app/output") -> DocumentProcessor:
    """Create a processor for general medical documents."""
    return DocumentProcessor(
        base_directory=base_dir,
        output_directory=output_dir,
        enable_fallback=True,
        max_file_size=50 * 1024 * 1024  # 50MB for medical documents
    ) 