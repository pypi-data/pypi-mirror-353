"""
Configuration module for the RettX Mutation Library.

This module defines configuration protocols and classes that follow Azure best practices
for secure, maintainable configuration management.
"""

import logging
from typing import Protocol
from rettxmutation.pipeline.config_types import RettxPipelineConfig

logger = logging.getLogger(__name__)


class RettxLibraryConfig(RettxPipelineConfig, Protocol):
    """
    Protocol defining the complete configuration interface for the RettX Mutation Library.
    
    This extends RettxPipelineConfig to include all necessary Azure service configurations.
    Implementing classes must provide all required configuration values.
    
    Security Note: This protocol ensures type safety while maintaining flexibility
    for different configuration sources (environment, Key Vault, etc.).
    """
    pass  # Inherits all configuration from RettxPipelineConfig


class ConfigValidator:
    """
    Validates configuration objects to ensure all required fields are present.
    Follows Azure best practices for fail-fast configuration validation.
    """
    
    @staticmethod
    def validate_config(config: RettxLibraryConfig) -> None:
        """
        Validates that all required configuration fields are present and non-empty.
        
        Args:
            config: Configuration object to validate
            
        Raises:
            ValueError: If any required configuration is missing or empty
        """
        required_fields = [
            'RETTX_DOCUMENT_ANALYSIS_ENDPOINT',
            'RETTX_DOCUMENT_ANALYSIS_KEY',
            'RETTX_OPENAI_KEY',
            'RETTX_OPENAI_MODEL_VERSION',
            'RETTX_OPENAI_ENDPOINT',
            'RETTX_OPENAI_MODEL_NAME',
            'RETTX_EMBEDDING_DEPLOYMENT'
        ]

        missing_fields = []
        empty_fields = []
        
        for field in required_fields:
            if not hasattr(config, field):
                missing_fields.append(field)
            elif not getattr(config, field):
                empty_fields.append(field)
        
        error_messages = []
        if missing_fields:
            error_messages.append(f"Missing required configuration fields: {', '.join(missing_fields)}")
        if empty_fields:
            error_messages.append(f"Empty required configuration fields: {', '.join(empty_fields)}")
        
        if error_messages:
            error_msg = "; ".join(error_messages)
            logger.error(f"Configuration validation failed: {error_msg}")
            raise ValueError(f"Configuration validation failed: {error_msg}")
        
        logger.debug("Configuration validation successful")


class DefaultConfig:
    """
    Default configuration implementation for development and testing.
    
    Warning: This uses environment variables and should not be used in production
    without proper Azure Key Vault integration for credential management.
    """
    
    def __init__(self, env_file_path: str = None):
        """
        Initialize configuration from environment variables.
        
        Args:
            env_file_path: Optional path to .env file. If None, searches for .env
                          in current directory and examples/ directory.
        """
        import os
        from pathlib import Path
        
        # Load environment variables from .env file
        try:
            from dotenv import load_dotenv
            
            if env_file_path:
                load_dotenv(env_file_path)
                logger.debug(f"Loaded environment variables from {env_file_path}")
            else:
                # Try to find .env file in common locations
                current_dir = Path.cwd()
                env_locations = [
                    current_dir / ".env",
                    current_dir / "examples" / ".env",
                    Path(__file__).parent.parent.parent.parent / "examples" / ".env"
                ]
                
                for env_path in env_locations:
                    if env_path.exists():
                        load_dotenv(env_path)
                        logger.debug(f"Loaded environment variables from {env_path}")
                        break
                else:
                    logger.warning("No .env file found in standard locations")
                    
        except ImportError:
            logger.warning("python-dotenv not available, skipping .env file loading")
        
        # Document Analysis Service
        self.RETTX_DOCUMENT_ANALYSIS_ENDPOINT = os.getenv('RETTX_DOCUMENT_ANALYSIS_ENDPOINT', '')
        self.RETTX_DOCUMENT_ANALYSIS_KEY = os.getenv('RETTX_DOCUMENT_ANALYSIS_KEY', '')
        
        # Azure OpenAI Configuration
        self.RETTX_OPENAI_KEY = os.getenv('RETTX_OPENAI_KEY', '')
        self.RETTX_OPENAI_MODEL_VERSION = os.getenv('RETTX_OPENAI_MODEL_VERSION', '2024-02-01')
        self.RETTX_OPENAI_ENDPOINT = os.getenv('RETTX_OPENAI_ENDPOINT', '')
        self.RETTX_OPENAI_MODEL_NAME = os.getenv('RETTX_OPENAI_MODEL_NAME', '')
        self.RETTX_EMBEDDING_DEPLOYMENT = os.getenv('RETTX_EMBEDDING_DEPLOYMENT', '')
        
        # Optional Cognitive Services
        self.RETTX_COGNITIVE_SERVICES_ENDPOINT = os.getenv('RETTX_COGNITIVE_SERVICES_ENDPOINT')
        self.RETTX_COGNITIVE_SERVICES_KEY = os.getenv('RETTX_COGNITIVE_SERVICES_KEY')
        
        # Optional AI Search
        self.RETTX_AI_SEARCH_SERVICE = os.getenv('RETTX_AI_SEARCH_SERVICE')
        
        # Validate configuration on initialization
        ConfigValidator.validate_config(self)
