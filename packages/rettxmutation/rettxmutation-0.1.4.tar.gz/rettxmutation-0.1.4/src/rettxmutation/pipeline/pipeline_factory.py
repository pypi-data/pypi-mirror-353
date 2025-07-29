"""
RettX Pipeline Factory

Provides helper functions to create fully configured pipeline instances.
"""

import logging
from rettxmutation.pipeline.rettx_pipeline import RettxPipeline
from rettxmutation.config import RettxConfig

logger = logging.getLogger(__name__)

def create_default_pipeline(config: RettxConfig) -> RettxPipeline:
    """
    Creates a fully configured RettXPipeline using the new config-based approach.

    Args:
        config: RettxConfig instance containing all necessary configuration fields

    Returns:
        RettxPipeline: Fully configured pipeline instance
        
    Raises:
        ValueError: If required configuration fields are missing or invalid
    """
    logger.info("🔧 Creating default RettX pipeline")
    
    # Validate required configuration fields upfront
    _validate_config(config)
    
    # The pipeline now handles all service creation internally via the config
    pipeline = RettxPipeline(config)

    logger.info("✅ Default RettX pipeline created")

    return pipeline


def _validate_config(config: RettxConfig) -> None:
    """
    Validate that the configuration has all required fields for pipeline creation.
    
    Args:
        config: Configuration to validate
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    required_fields = [
        ('RETTX_DOCUMENT_ANALYSIS_ENDPOINT', 'Azure Document Intelligence endpoint'),
        ('RETTX_DOCUMENT_ANALYSIS_KEY', 'Azure Document Intelligence key'),
        ('RETTX_OPENAI_KEY', 'OpenAI API key'),
        ('RETTX_OPENAI_ENDPOINT', 'OpenAI endpoint'),
        ('RETTX_OPENAI_MODEL_NAME', 'OpenAI model name'),
        ('RETTX_OPENAI_MODEL_VERSION', 'OpenAI model version'),
    ]
    
    missing_fields = []
    for field_name, description in required_fields:
        value = getattr(config, field_name, None)
        if value is None or (isinstance(value, str) and value.strip() == ''):
            missing_fields.append(f"{description} ({field_name})")
    
    if missing_fields:
        raise ValueError(f"Missing required configuration fields: {', '.join(missing_fields)}")
    
    logger.debug("Configuration validation passed")
