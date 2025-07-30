"""Utility functions for dependent metadata validation and management."""

import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from agent_sdk.exceptions import ValidationError

logger = logging.getLogger(__name__)


class DependentMetadataValidator:
    """Validator for dependent metadata directories and files."""

    def __init__(self, metadata_dir: str):
        """Initialize the validator.
        
        Args:
            metadata_dir (str): Path to the dependent metadata directory
        """
        self.metadata_dir = Path(metadata_dir)

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the dependent metadata directory.
        
        Simply checks that package.xml exists.
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        # Basic directory validation
        try:
            if not self.metadata_dir.exists():
                errors.append(f"Metadata directory does not exist: {self.metadata_dir}")
                return False, errors
                
            if not self.metadata_dir.is_dir():
                errors.append(f"Metadata path is not a directory: {self.metadata_dir}")
                return False, errors

            # Check that package.xml exists
            package_xml = self.metadata_dir / "package.xml"
            if not package_xml.exists():
                errors.append("package.xml is required but not found in dependent metadata directory")
        except (PermissionError, OSError) as e:
            errors.append(f"Metadata directory does not exist or is not accessible: {self.metadata_dir}")
            return False, errors

        return len(errors) == 0, errors

    def get_summary(self) -> Dict:
        """Get a simple summary of the dependent metadata.
        
        Returns:
            Dict: Basic summary information about the metadata
        """
        package_xml = self.metadata_dir / "package.xml"
        
        summary = {
            'metadata_dir': str(self.metadata_dir),
            'has_package_xml': package_xml.exists(),
            'total_files': len(list(self.metadata_dir.rglob('*'))) if self.metadata_dir.exists() else 0,
        }
        
        return summary


def validate_dependent_metadata(metadata_dir: str) -> Tuple[bool, List[str]]:
    """Validate dependent metadata directory.
    
    Args:
        metadata_dir (str): Path to the dependent metadata directory
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    validator = DependentMetadataValidator(metadata_dir)
    return validator.validate()


def get_metadata_summary(metadata_dir: str) -> Dict:
    """Get a summary of dependent metadata.
    
    Args:
        metadata_dir (str): Path to the dependent metadata directory
        
    Returns:
        Dict: Summary information about the metadata
    """
    validator = DependentMetadataValidator(metadata_dir)
    return validator.get_summary()


def is_valid_metadata_directory(metadata_dir: str) -> bool:
    """Check if a directory contains valid dependent metadata.
    
    Args:
        metadata_dir (str): Path to the dependent metadata directory
        
    Returns:
        bool: True if valid, False otherwise
    """
    is_valid, _ = validate_dependent_metadata(metadata_dir)
    return is_valid 