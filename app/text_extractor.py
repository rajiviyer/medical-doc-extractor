"""
Modular Text Extractor for Medical Document Extractor

This module provides flexible text extraction capabilities for various file types,
integrating PDF parsing with pdfplumber and OCR functionality.
"""

import os
import logging
import time
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from datetime import datetime

import pdfplumber
from app.utils import ocr_from_image, ocr_from_scanned_pdf

logger = logging.getLogger(__name__)

@dataclass
class ExtractionResult:
    """Represents the result of text extraction from a file."""
    filename: str
    file_type: str
    extraction_method: str
    extraction_success: bool
    text_content: Optional[str]
    confidence_score: float
    processing_time: float
    page_count: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class TextExtractor:
    """
    Modular text extractor supporting PDF and image files.
    
    Features:
    - PDF text extraction using pdfplumber
    - OCR for images and scanned PDFs
    - Fallback strategies for failed extractions
    - Confidence scoring
    - Comprehensive error handling
    """
    
    def __init__(self, 
                 enable_fallback: bool = True,
                 max_file_size: int = 50 * 1024 * 1024,  # 50MB
                 timeout_seconds: int = 300):  # 5 minutes
        """
        Initialize the text extractor.
        
        Args:
            enable_fallback: Whether to use OCR fallback for failed PDF extraction
            max_file_size: Maximum file size to process in bytes
            timeout_seconds: Maximum processing time per file
        """
        self.enable_fallback = enable_fallback
        self.max_file_size = max_file_size
        self.timeout_seconds = timeout_seconds
    
    def extract_text(self, file_path: Path) -> ExtractionResult:
        """
        Extract text from a file using appropriate method.
        
        Args:
            file_path: Path to the file to extract text from
            
        Returns:
            ExtractionResult with extraction details
        """
        start_time = time.time()
        
        # Validate file
        if not self._validate_file(file_path):
            return self._create_error_result(
                file_path, "File validation failed", start_time
            )
        
        file_type = self._determine_file_type(file_path)
        
        try:
            if file_type == 'pdf':
                result = self._extract_from_pdf(file_path, start_time)
            elif file_type == 'image':
                result = self._extract_from_image(file_path, start_time)
            else:
                result = self._create_error_result(
                    file_path, f"Unsupported file type: {file_type}", start_time
                )
            
            # Add processing time
            result.processing_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return self._create_error_result(
                file_path, str(e), start_time
            )
    
    def _validate_file(self, file_path: Path) -> bool:
        """Validate file before processing."""
        try:
            if not file_path.exists():
                logger.error(f"File does not exist: {file_path}")
                return False
            
            if not file_path.is_file():
                logger.error(f"Path is not a file: {file_path}")
                return False
            
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                logger.error(f"File too large ({file_size} bytes): {file_path}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating file {file_path}: {e}")
            return False
    
    def _determine_file_type(self, file_path: Path) -> str:
        """Determine file type based on extension."""
        ext = file_path.suffix.lower()
        if ext == '.pdf':
            return 'pdf'
        elif ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            return 'image'
        else:
            return 'other'
    
    def _extract_from_pdf(self, file_path: Path, start_time: float) -> ExtractionResult:
        """Extract text from PDF file using pdfplumber with OCR fallback."""
        logger.info(f"Extracting text from PDF: {file_path}")
        
        try:
            # Try PDF text extraction first
            with pdfplumber.open(file_path) as pdf:
                extracted_text = ""
                page_count = len(pdf.pages)
                
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    extracted_text += page_text + "\n"
                
                # Check if we got meaningful text
                if extracted_text.strip():
                    logger.info(f"Successfully extracted text from PDF: {file_path}")
                    return ExtractionResult(
                        filename=file_path.name,
                        file_type='pdf',
                        extraction_method='pdf_text',
                        extraction_success=True,
                        text_content=extracted_text.strip(),
                        confidence_score=0.95,
                        processing_time=time.time() - start_time,
                        page_count=page_count,
                        metadata={'pages_processed': page_count}
                    )
                
                # If no text found, try OCR fallback
                if self.enable_fallback:
                    logger.info(f"No text found in PDF, attempting OCR: {file_path}")
                    return self._extract_from_scanned_pdf(file_path, start_time)
                else:
                    logger.warning(f"No text found in PDF and fallback disabled: {file_path}")
                    return self._create_error_result(
                        file_path, "No text found in PDF", start_time
                    )
                    
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            if self.enable_fallback:
                logger.info(f"Attempting OCR fallback for failed PDF: {file_path}")
                return self._extract_from_scanned_pdf(file_path, start_time)
            else:
                return self._create_error_result(
                    file_path, f"PDF extraction failed: {str(e)}", start_time
                )
    
    def _extract_from_scanned_pdf(self, file_path: Path, start_time: float) -> ExtractionResult:
        """Extract text from scanned PDF using OCR."""
        logger.info(f"Extracting text from scanned PDF using OCR: {file_path}")
        
        try:
            ocr_text = ocr_from_scanned_pdf(str(file_path))
            
            if ocr_text and ocr_text.strip():
                logger.info(f"Successfully extracted text via OCR: {file_path}")
                return ExtractionResult(
                    filename=file_path.name,
                    file_type='pdf',
                    extraction_method='ocr',
                    extraction_success=True,
                    text_content=ocr_text.strip(),
                    confidence_score=0.85,  # OCR typically has lower confidence
                    processing_time=time.time() - start_time,
                    metadata={'ocr_used': True}
                )
            else:
                logger.error(f"OCR failed to extract text: {file_path}")
                return self._create_error_result(
                    file_path, "OCR extraction failed", start_time
                )
                
        except Exception as e:
            logger.error(f"Error in OCR extraction from {file_path}: {e}")
            return self._create_error_result(
                file_path, f"OCR extraction failed: {str(e)}", start_time
            )
    
    def _extract_from_image(self, file_path: Path, start_time: float) -> ExtractionResult:
        """Extract text from image file using OCR."""
        logger.info(f"Extracting text from image: {file_path}")
        
        try:
            ocr_text = ocr_from_image(str(file_path))
            
            if ocr_text and ocr_text.strip():
                logger.info(f"Successfully extracted text from image: {file_path}")
                return ExtractionResult(
                    filename=file_path.name,
                    file_type='image',
                    extraction_method='image_ocr',
                    extraction_success=True,
                    text_content=ocr_text.strip(),
                    confidence_score=0.80,  # Image OCR typically has lower confidence
                    processing_time=time.time() - start_time,
                    metadata={'ocr_used': True}
                )
            else:
                logger.error(f"OCR failed to extract text from image: {file_path}")
                return self._create_error_result(
                    file_path, "Image OCR extraction failed", start_time
                )
                
        except Exception as e:
            logger.error(f"Error in image OCR extraction from {file_path}: {e}")
            return self._create_error_result(
                file_path, f"Image OCR extraction failed: {str(e)}", start_time
            )
    
    def _create_error_result(self, file_path: Path, error_message: str, start_time: float) -> ExtractionResult:
        """Create an error result for failed extraction."""
        return ExtractionResult(
            filename=file_path.name,
            file_type=self._determine_file_type(file_path),
            extraction_method='unknown',
            extraction_success=False,
            text_content=None,
            confidence_score=0.0,
            processing_time=time.time() - start_time,
            error_message=error_message
        )
    
    def batch_extract(self, file_paths: List[Path]) -> List[ExtractionResult]:
        """
        Extract text from multiple files in batch.
        
        Args:
            file_paths: List of file paths to process
            
        Returns:
            List of ExtractionResult objects
        """
        results = []
        total_files = len(file_paths)
        
        logger.info(f"Starting batch extraction of {total_files} files")
        
        for i, file_path in enumerate(file_paths, 1):
            logger.info(f"Processing file {i}/{total_files}: {file_path.name}")
            
            result = self.extract_text(file_path)
            results.append(result)
            
            # Log progress
            if i % 10 == 0 or i == total_files:
                success_count = sum(1 for r in results if r.extraction_success)
                logger.info(f"Progress: {i}/{total_files} files processed, {success_count} successful")
        
        # Summary
        success_count = sum(1 for r in results if r.extraction_success)
        avg_time = sum(r.processing_time for r in results) / len(results) if results else 0
        
        logger.info(f"Batch extraction complete: {success_count}/{total_files} successful, "
                   f"average time: {avg_time:.2f}s per file")
        
        return results

# Utility functions for common extraction patterns

def create_pdf_extractor(enable_fallback: bool = True) -> TextExtractor:
    """Create a text extractor optimized for PDF files."""
    return TextExtractor(
        enable_fallback=enable_fallback,
        max_file_size=100 * 1024 * 1024,  # 100MB for PDFs
        timeout_seconds=600  # 10 minutes for large PDFs
    )

def create_image_extractor() -> TextExtractor:
    """Create a text extractor optimized for image files."""
    return TextExtractor(
        enable_fallback=False,  # No fallback needed for images
        max_file_size=25 * 1024 * 1024,  # 25MB for images
        timeout_seconds=180  # 3 minutes for image processing
    )

def create_general_extractor() -> TextExtractor:
    """Create a general-purpose text extractor."""
    return TextExtractor(
        enable_fallback=True,
        max_file_size=50 * 1024 * 1024,
        timeout_seconds=300
    ) 