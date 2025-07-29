"""
Service Factory for the RettX Mutation Library.

This module provides centralized service creation and management following Azure best practices
for connection pooling, resource management, and dependency injection.
"""

import logging
from typing import Optional
from .config import RettxLibraryConfig, ConfigValidator
from rettxmutation.openai_agent.embedding_client import EmbeddingClient
from rettxmutation.services.embedding_service import EmbeddingService
from rettxmutation.services.text_analytics import HealthcareTextAnalyzer
from rettxmutation.services.mutation_service import MutationService
from rettxmutation.services.mutation_validator import MutationValidator
from rettxmutation.services.mutation_tokenizator import MutationTokenizator

logger = logging.getLogger(__name__)


class RettxServices:
    """
    Central service factory for the RettX Mutation Library.
    
    Provides lazy initialization and connection pooling for Azure services.
    Follows Azure best practices for resource management and dependency injection.
    """
    
    def __init__(self, config: RettxLibraryConfig):
        """
        Initialize the service factory with configuration.
        
        Args:
            config: Configuration object implementing RettxLibraryConfig protocol
            
        Raises:
            ValueError: If configuration validation fails
        """
        # Validate configuration early (fail fast)
        ConfigValidator.validate_config(config)
        
        self._config = config
        
        # Lazy-initialized Azure clients (connection pooling)
        self._embedding_client: Optional[EmbeddingClient] = None
        self._text_analytics_client: Optional[HealthcareTextAnalyzer] = None
        
        # Lazy-initialized services
        self._embedding_service: Optional[EmbeddingService] = None
        self._mutation_service: Optional[MutationService] = None
        self._mutation_validator: Optional[MutationValidator] = None
        self._mutation_tokenizator: Optional[MutationTokenizator] = None
        
        logger.info("RettxServices initialized successfully")
    
    def get_embedding_client(self) -> EmbeddingClient:
        """
        Get or create the embedding client with connection pooling.
        
        Returns:
            EmbeddingClient: Configured Azure OpenAI embedding client
        """
        if self._embedding_client is None:
            logger.debug("Creating new EmbeddingClient instance")
            self._embedding_client = EmbeddingClient(
                api_key=self._config.RETTX_OPENAI_KEY,
                api_version=self._config.RETTX_OPENAI_MODEL_VERSION,
                azure_endpoint=self._config.RETTX_OPENAI_ENDPOINT,
                model_name=self._config.RETTX_OPENAI_MODEL_NAME,
                embedding_deployment=self._config.RETTX_EMBEDDING_DEPLOYMENT
            )
            logger.debug("EmbeddingClient created successfully")
        
        return self._embedding_client
    
    def get_embedding_service(self) -> EmbeddingService:
        """
        Get or create the embedding service.
        
        Returns:
            EmbeddingService: Configured embedding service with Azure OpenAI integration
        """
        if self._embedding_service is None:
            logger.debug("Creating new EmbeddingService instance")
            embedding_client = self.get_embedding_client()
            self._embedding_service = EmbeddingService(embedding_client)
            logger.debug("EmbeddingService created successfully")
        return self._embedding_service
    
    def get_healthcare_text_analyzer(self) -> Optional[HealthcareTextAnalyzer]:
        """
        Get or create the healthcare text analyzer client.
        
        Returns:
            HealthcareTextAnalyzer: Configured Azure Text Analytics client for healthcare
            None: If cognitive services endpoint/key not configured
        """
        # Check if cognitive services are configured (they are optional)
        if not (self._config.RETTX_COGNITIVE_SERVICES_ENDPOINT and 
                self._config.RETTX_COGNITIVE_SERVICES_KEY):
            logger.debug("Cognitive Services not configured, returning None")
            return None
            
        if self._text_analytics_client is None:
            logger.debug("Creating new HealthcareTextAnalyzer instance")
            self._text_analytics_client = HealthcareTextAnalyzer(
                endpoint=self._config.RETTX_COGNITIVE_SERVICES_ENDPOINT,
                key=self._config.RETTX_COGNITIVE_SERVICES_KEY
            )
            logger.debug("HealthcareTextAnalyzer created successfully")
        
        return self._text_analytics_client
    
    def get_mutation_service(self) -> MutationService:
        """
        Get or create the mutation service.
        
        Returns:
            MutationService: Service for normalizing and mapping HGVS mutations
        """
        if self._mutation_service is None:
            logger.debug("Creating new MutationService instance")
            self._mutation_service = MutationService()
            logger.debug("MutationService created successfully")
        
        return self._mutation_service
    
    def get_mutation_validator(self) -> MutationValidator:
        """
        Get or create the mutation validator service.
        
        Returns:
            MutationValidator: Service for validating RawMutation objects
        """
        if self._mutation_validator is None:
            logger.debug("Creating new MutationValidator instance")
            mutation_service = self.get_mutation_service()
            self._mutation_validator = MutationValidator(mutation_service)
            logger.debug("MutationValidator created successfully")
        
        return self._mutation_validator
    
    def get_mutation_tokenizator(self) -> MutationTokenizator:
        """
        Get or create the mutation tokenizator.
        
        Returns:
            MutationTokenizator: Service for tokenizing mutation strings
        """
        if self._mutation_tokenizator is None:
            logger.debug("Creating new MutationTokenizator instance")
            self._mutation_tokenizator = MutationTokenizator()
            logger.debug("MutationTokenizator created successfully")
        return self._mutation_tokenizator
    
    def close(self) -> None:
        """
        Clean up resources and close connections.
        
        Call this method when done using the services to ensure proper resource cleanup.
        """
        logger.debug("Cleaning up RettxServices resources")
        
        # Reset all cached instances to allow garbage collection
        self._embedding_client = None
        self._embedding_service = None
        self._text_analytics_client = None
        self._mutation_service = None
        self._mutation_validator = None
        self._mutation_tokenizator = None
        
        logger.debug("RettxServices cleanup completed")
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self.close()
