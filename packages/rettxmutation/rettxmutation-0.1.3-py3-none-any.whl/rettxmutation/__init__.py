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
        embedding_service = services.get_embedding_service()
        
        # Use the service
        embedding = embedding_service.create_embedding(mutation)
    ```
"""

from .core import RettxLibraryConfig, RettxServices, DefaultConfig, ConfigValidator
from .services import EmbeddingService, MutationService, MutationValidator, HealthcareTextAnalyzer

__version__ = "1.0.0"

__all__ = [
    # Core configuration and services
    "RettxLibraryConfig",
    "RettxServices", 
    "DefaultConfig",
    "ConfigValidator",
    
    # Services
    "EmbeddingService",
    "MutationService",
    "MutationValidator", 
    "HealthcareTextAnalyzer",
    
    # Version
    "__version__"
]
