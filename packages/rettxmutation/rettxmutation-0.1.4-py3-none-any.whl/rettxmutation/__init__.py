"""
RettX Mutation Library

A Python library for analyzing genetic mutations with Azure AI services integration.
Provides embeddings, similarity search, and mutation analysis capabilities.

Example usage:
    ```python
    from rettxmutation import RettxServices, DefaultConfig
    
    # Initialize with configuration
    config = DefaultConfig()  # or your custom config class
    
    # Create services with context manager for automatic cleanup
    with RettxServices(config) as services:
        embedding_service = services.embedding_service
        
        # Use the service
        embedding = embedding_service.create_embedding(mutation)
    ```
"""

# Import unified configuration and services
from .config import RettxConfig, DefaultConfig, validate_config_fields
from .services import (
    RettxServices, 
    create_services,
    EmbeddingService, 
    MutationService, 
    MutationValidator, 
    HealthcareTextAnalyzer,
    MutationTokenizator
)
from .ocr import OcrService

__version__ = "1.0.0"

__all__ = [
    # Core configuration
    "RettxConfig",
    "DefaultConfig",
    "validate_config_fields",
    
    # Central service factory
    "RettxServices", 
    "create_services",
    
    # Individual services
    "EmbeddingService",
    "MutationService",
    "MutationValidator", 
    "HealthcareTextAnalyzer",
    "MutationTokenizator",
    "OcrService",
    
    # Version
    "__version__"
]
