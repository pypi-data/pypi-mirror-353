"""
Test suite for Pipeline components

Tests the RettxPipeline, pipeline factory, and pipeline integration.
"""

import pytest
import os
import asyncio
import io
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / "examples" / ".env")

from rettxmutation.pipeline import (
    create_default_pipeline,
    RettxPipeline
)
from rettxmutation.config import DefaultConfig
from rettxmutation.services.mutation_validator import MutationValidator
from rettxmutation.models.document import Document
from rettxmutation.models.gene_models import GeneMutation, RawMutation


class TestPipelineConfig:
    """Test cases for pipeline configuration."""
    
    @pytest.fixture
    def env_config(self):
        """Create configuration from environment variables."""
        class EnvConfig:
            def __init__(self):
                self.RETTX_DOCUMENT_ANALYSIS_ENDPOINT = os.getenv('RETTX_DOCUMENT_ANALYSIS_ENDPOINT')
                self.RETTX_DOCUMENT_ANALYSIS_KEY = os.getenv('RETTX_DOCUMENT_ANALYSIS_KEY')
                self.RETTX_OPENAI_KEY = os.getenv('RETTX_OPENAI_KEY')
                self.RETTX_OPENAI_MODEL_VERSION = os.getenv('RETTX_OPENAI_MODEL_VERSION', '2024-02-01')
                self.RETTX_OPENAI_ENDPOINT = os.getenv('RETTX_OPENAI_ENDPOINT')
                self.RETTX_OPENAI_MODEL_NAME = os.getenv('RETTX_OPENAI_MODEL_NAME', 'gpt-4o')
                self.RETTX_EMBEDDING_DEPLOYMENT = os.getenv('RETTX_EMBEDDING_DEPLOYMENT', 'text-embedding-ada-002')
        return EnvConfig()
    
    def test_config_has_required_attributes(self, env_config):
        """Test that configuration has all required attributes."""
        required_attrs = [
            'RETTX_DOCUMENT_ANALYSIS_ENDPOINT',
            'RETTX_DOCUMENT_ANALYSIS_KEY',
            'RETTX_OPENAI_KEY',
            'RETTX_OPENAI_MODEL_VERSION',
            'RETTX_OPENAI_ENDPOINT',
            'RETTX_OPENAI_MODEL_NAME',
            'RETTX_EMBEDDING_DEPLOYMENT'
        ]
        
        for attr in required_attrs:
            assert hasattr(env_config, attr), f"Missing configuration attribute: {attr}"
    
    def test_config_validation(self, env_config):
        """Test configuration validation."""
        # Test that critical values are not None (if environment is configured)
        if env_config.RETTX_OPENAI_KEY and env_config.RETTX_OPENAI_KEY != 'test_key':
            assert env_config.RETTX_OPENAI_KEY is not None
            assert env_config.RETTX_OPENAI_ENDPOINT is not None
            assert len(env_config.RETTX_OPENAI_KEY) > 10  # Basic validation


class TestRettxPipeline:
    """Test cases for RettxPipeline."""
    
    @pytest.fixture
    def test_config(self):
        """Create a test configuration."""
        config = DefaultConfig()
        # Set Azure Document Intelligence fields (correct field names)
        config.RETTX_DOCUMENT_ANALYSIS_ENDPOINT = "https://test-endpoint.cognitiveservices.azure.com/"
        config.RETTX_DOCUMENT_ANALYSIS_KEY = "test_key"
        config.RETTX_OPENAI_KEY = "test_openai_key"
        config.RETTX_OPENAI_MODEL_VERSION = "2024-02-15-preview"
        config.RETTX_OPENAI_ENDPOINT = "https://test-openai.openai.azure.com/"
        config.RETTX_OPENAI_MODEL_NAME = "gpt-4"
        config.RETTX_EMBEDDING_DEPLOYMENT = "text-embedding-ada-002"
        config.RETTX_COGNITIVE_SERVICES_ENDPOINT = "https://test-cognitive.cognitiveservices.azure.com/"
        config.RETTX_COGNITIVE_SERVICES_KEY = "test_cognitive_key"
        return config

    @pytest.fixture
    def pipeline(self, test_config):
        """Create pipeline with test configuration."""
        return RettxPipeline(test_config)

    def test_pipeline_initialization(self, test_config):
        """Test pipeline initialization with configuration."""
        pipeline = RettxPipeline(test_config)
        
        assert pipeline.config is test_config
        assert pipeline.services is not None
        assert hasattr(pipeline.services, 'ocr_service')
        assert hasattr(pipeline.services, 'validation_agent')
        assert hasattr(pipeline.services, 'extraction_agent')
        assert hasattr(pipeline.services, 'mutation_validator')

    def test_pipeline_has_required_methods(self, pipeline):
        """Test that pipeline has all required methods."""
        assert hasattr(pipeline, 'run_pipeline')
        assert hasattr(pipeline, '_build_text_analytics_summary')
        assert hasattr(pipeline, 'close')
        
        # Check that run_pipeline is async
        assert asyncio.iscoroutinefunction(pipeline.run_pipeline)

    def test_build_text_analytics_summary_empty(self, pipeline):
        """Test _build_text_analytics_summary with empty mutations."""
        summary = pipeline._build_text_analytics_summary([])
        assert "No mutations detected" in summary

    def test_build_text_analytics_summary_with_mutations(self, pipeline):
        """Test _build_text_analytics_summary with mutations."""
        class MockMutation:
            def __init__(self, mutation, confidence):
                self.mutation = mutation
                self.confidence = confidence
        
        mutations = [
            MockMutation("BRCA1:c.68_69delAG", 0.95),
            MockMutation("MECP2:c.763C>T", 0.87)
        ]
        
        summary = pipeline._build_text_analytics_summary(mutations)
        assert "High confidence mutations detected" in summary
        assert "BRCA1:c.68_69delAG" in summary
        assert "MECP2:c.763C>T" in summary
        assert "0.95" in summary
        assert "0.87" in summary

    @pytest.mark.asyncio
    async def test_run_pipeline_success(self, test_config):
        """Test successful pipeline execution with mocked services."""
        pipeline = RettxPipeline(test_config)
        
        # Mock the services
        with patch.object(pipeline.services, 'ocr_service') as mock_ocr, \
             patch.object(pipeline.services, 'validation_agent') as mock_validate, \
             patch.object(pipeline.services, 'extraction_agent') as mock_extract, \
             patch.object(pipeline.services, 'mutation_validator') as mock_validator:            # Setup mocks
            mock_doc = Document(
                raw_text="Test document with BRCA1:c.68_69delAG mutation",
                cleaned_text="Test document with BRCA1:c.68_69delAG mutation",
                language="en",
                words=[],
                lines=[]
            )
            mock_ocr.extract_and_process_text.return_value = mock_doc
            mock_validate.validate_document = AsyncMock(return_value=(True, 0.95))
            mock_extract.extract_mutations = AsyncMock(return_value=[{"mutation": "BRCA1:c.68_69delAG"}])
            mock_validator.validate_mutations = AsyncMock(return_value=[])
            
            # Create a mock file stream
            file_stream = io.BytesIO(b"test content")
            
            # Run pipeline
            document, mutations = await pipeline.run_pipeline(file_stream)
            
            # Verify results
            assert document is not None
            assert isinstance(mutations, list)
            
            # Verify service calls
            mock_ocr.extract_and_process_text.assert_called_once_with(file_stream)
            mock_validate.validate_document.assert_called_once()
            mock_extract.extract_mutations.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_pipeline_validation_failure(self, test_config):
        """Test pipeline execution when document validation fails."""
        pipeline = RettxPipeline(test_config)
        
        # Mock the services
        with patch.object(pipeline.services, 'ocr_service') as mock_ocr, \
             patch.object(pipeline.services, 'validation_agent') as mock_validate:            # Setup mocks for failure case
            mock_doc = Document(
                raw_text="Invalid document",
                cleaned_text="Invalid document",
                language="en",
                words=[],
                lines=[]
            )
            mock_ocr.extract_and_process_text.return_value = mock_doc
            mock_validate.validate_document = AsyncMock(return_value=(False, 0.2))
            
            # Create a mock file stream
            file_stream = io.BytesIO(b"test content")              # Run pipeline and expect exception
            with pytest.raises(Exception, match="Document failed validation"):
                await pipeline.run_pipeline(file_stream)


class TestPipelineFactory:
    """Test cases for pipeline factory functions."""
    
    @pytest.fixture
    def config(self):
        """Provide test configuration."""
        class TestConfig:
            # Use correct field names for Azure Document Intelligence
            RETTX_DOCUMENT_ANALYSIS_ENDPOINT = os.getenv('RETTX_DOCUMENT_ANALYSIS_ENDPOINT', 'https://test.cognitiveservices.azure.com/')
            RETTX_DOCUMENT_ANALYSIS_KEY = os.getenv('RETTX_DOCUMENT_ANALYSIS_KEY', 'test_key')
            RETTX_OPENAI_KEY = os.getenv('RETTX_OPENAI_KEY', 'test_key')
            RETTX_OPENAI_MODEL_VERSION = os.getenv('RETTX_OPENAI_MODEL_VERSION', '2024-02-01')
            RETTX_OPENAI_ENDPOINT = os.getenv('RETTX_OPENAI_ENDPOINT', 'https://test.openai.azure.com/')
            RETTX_OPENAI_MODEL_NAME = os.getenv('RETTX_OPENAI_MODEL_NAME', 'gpt-4o')
            RETTX_EMBEDDING_DEPLOYMENT = os.getenv('RETTX_EMBEDDING_DEPLOYMENT', 'text-embedding-ada-002')
        return TestConfig()
    
    def test_create_default_pipeline_success(self, config):
        """Test successful creation of default pipeline."""
        pipeline = create_default_pipeline(config)
        
        assert isinstance(pipeline, RettxPipeline)
        assert pipeline.config is not None
        assert pipeline.services is not None
        assert hasattr(pipeline.services, 'ocr_service')
        assert hasattr(pipeline.services, 'validation_agent')
        assert hasattr(pipeline.services, 'extraction_agent')
        assert hasattr(pipeline.services, 'mutation_validator')

    def test_create_default_pipeline_invalid_config(self):
        """Test pipeline creation with invalid configuration."""
        from rettxmutation.ocr.exceptions import OcrExtractionError
        
        class InvalidConfig:
            # Use correct field names for Azure Document Intelligence
            RETTX_DOCUMENT_ANALYSIS_ENDPOINT = None
            RETTX_DOCUMENT_ANALYSIS_KEY = None
            RETTX_OPENAI_KEY = None
            RETTX_OPENAI_MODEL_VERSION = None
            RETTX_OPENAI_ENDPOINT = None
            RETTX_OPENAI_MODEL_NAME = None
            RETTX_EMBEDDING_DEPLOYMENT = None
        
        # This might still create the pipeline but components will fail on usage
        # The exact behavior depends on the implementation
        with pytest.raises((ValueError, TypeError, AttributeError, OcrExtractionError)):
            create_default_pipeline(InvalidConfig())
    def test_pipeline_components_are_properly_configured(self, config):
        """Test that pipeline components are properly configured."""
        pipeline = create_default_pipeline(config)
        
        # Verify services are accessible through the factory
        assert hasattr(pipeline.services.ocr_service, 'extract_and_process_text')
        
        # Verify agents have required methods
        assert hasattr(pipeline.services.validation_agent, 'validate_document')
        assert hasattr(pipeline.services.extraction_agent, 'extract_mutations')
        assert hasattr(pipeline.services.summarization_agent, 'summarize_report')
        assert hasattr(pipeline.services.summarization_agent, 'correct_summary_mistakes')


class TestPipelineIntegration:
    """Integration tests for the complete pipeline."""
    
    @pytest.fixture
    def config(self):
        """Provide test configuration."""
        class TestConfig:
            # Use correct field names for Azure Document Intelligence
            RETTX_DOCUMENT_ANALYSIS_ENDPOINT = os.getenv('RETTX_DOCUMENT_ANALYSIS_ENDPOINT', 'https://test.cognitiveservices.azure.com/')
            RETTX_DOCUMENT_ANALYSIS_KEY = os.getenv('RETTX_DOCUMENT_ANALYSIS_KEY', 'test_key')
            RETTX_OPENAI_KEY = os.getenv('RETTX_OPENAI_KEY', 'test_key')
            RETTX_OPENAI_MODEL_VERSION = os.getenv('RETTX_OPENAI_MODEL_VERSION', '2024-02-01')
            RETTX_OPENAI_ENDPOINT = os.getenv('RETTX_OPENAI_ENDPOINT', 'https://test.openai.azure.com/')
            RETTX_OPENAI_MODEL_NAME = os.getenv('RETTX_OPENAI_MODEL_NAME', 'gpt-4o')
            RETTX_EMBEDDING_DEPLOYMENT = os.getenv('RETTX_EMBEDDING_DEPLOYMENT', 'text-embedding-ada-002')
        return TestConfig()
    
    def test_end_to_end_pipeline_creation(self, config):
        """Test end-to-end pipeline creation and structure."""
        # Skip if no configuration available
        if not config.RETTX_OPENAI_KEY or config.RETTX_OPENAI_KEY == 'test_key':
            pytest.skip("No API configuration available")
        
        pipeline = create_default_pipeline(config)
        
        # Verify pipeline structure
        assert isinstance(pipeline, RettxPipeline)
        assert pipeline.config is not None
        assert pipeline.services is not None
        assert pipeline.services.ocr_service is not None
        assert pipeline.services.validation_agent is not None
        assert pipeline.services.extraction_agent is not None
        assert pipeline.services.summarization_agent is not None
        
        # Verify pipeline methods
        assert hasattr(pipeline, 'run_pipeline')
        assert asyncio.iscoroutinefunction(pipeline.run_pipeline)
    
    @pytest.mark.asyncio
    async def test_mock_pipeline_workflow(self, config):
        """Test complete pipeline workflow with mocked components."""
        # Skip if no configuration available
        if not config.RETTX_OPENAI_KEY:
            pytest.skip("No API configuration available")
        pipeline = create_default_pipeline(config)
        
        # Mock all the async calls to avoid actual API usage
        with patch.object(pipeline.services.ocr_service, 'extract_and_process_text') as mock_ocr, \
             patch.object(pipeline.services.validation_agent, 'validate_document', new_callable=AsyncMock) as mock_validate, \
             patch.object(pipeline.services.extraction_agent, 'extract_mutations', new_callable=AsyncMock) as mock_extract, \
             patch.object(pipeline.services.mutation_validator, 'validate_mutations', new_callable=AsyncMock) as mock_mutation_validator, \
             patch.object(pipeline.services.summarization_agent, 'summarize_report', new_callable=AsyncMock) as mock_summarize, \
             patch.object(pipeline.services.summarization_agent, 'correct_summary_mistakes', new_callable=AsyncMock) as mock_correct:
            
            # Set up mock returns
            mock_document = Mock(spec=Document)
            mock_document.cleaned_text = "Patient report with MECP2 mutation c.916C>T."
            mock_document.language = "en"
            mock_document.dump_keywords.return_value = "MECP2, c.916C>T"
            mock_document.dump_text_analytics_keywords.return_value = "MECP2 (gene), c.916C>T (mutation)"
            
            class MockRawMutation:
                def __init__(self, mutation, confidence):
                    self.mutation = mutation
                    self.confidence = confidence
                def model_dump(self):
                    return {'mutation': self.mutation, 'confidence': self.confidence}
            
            # Mock validated GeneMutation objects
            mock_gene_mutation = Mock(spec=GeneMutation)
            mock_gene_mutation.variant_type = "SNV"
            mock_gene_mutation.primary_transcript = Mock()
            mock_gene_mutation.primary_transcript.hgvs_transcript_variant = "NM_004992.4:c.916C>T"
            
            mock_ocr.return_value = mock_document
            mock_validate.return_value = (True, 0.95)
            mock_extract.return_value = [MockRawMutation("c.916C>T", 0.95)]
            mock_mutation_validator.return_value = [mock_gene_mutation]
            mock_summarize.return_value = "Patient has MECP2 mutation."
            mock_correct.return_value = "Patient has MECP2 mutation c.916C>T (p.Arg306Cys)."
            
            # Run the pipeline
            mock_file = io.BytesIO(b"mock medical report pdf")
            document, validated_mutations = await pipeline.run_pipeline(mock_file)
            
            # Verify the workflow was executed
            mock_ocr.assert_called_once()
            mock_validate.assert_called_once_with("Patient report with MECP2 mutation c.916C>T.", "en")
            mock_extract.assert_called_once()
            mock_mutation_validator.assert_called_once()
            # Note: summarization functionality is currently commented out
            # mock_summarize.assert_called_once()
            # mock_correct.assert_called_once()
            
            # Verify the result - now returns tuple instead of dict
            assert isinstance(document, Mock)  # Should be Document object
            assert isinstance(validated_mutations, list)
            assert len(validated_mutations) == 1
            assert validated_mutations[0] is mock_gene_mutation
            # Note: summary functionality is currently commented out
            # assert "MECP2" in result['summary']
            # assert "c.916C>T" in result['corrected_summary']


if __name__ == "__main__":
    pytest.main([__file__])
