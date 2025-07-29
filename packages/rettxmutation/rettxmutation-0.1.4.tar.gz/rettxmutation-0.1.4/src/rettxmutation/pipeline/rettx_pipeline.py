"""
RettX Pipeline

Defines the standard RettXPipeline that orchestrates:
1️⃣ OCR
2️⃣ Document validation
3️⃣ Mutation extraction
4️⃣ Mutation validation
5️⃣ Report summarization
6️⃣ Summary correction
"""

import logging
from typing import List, Tuple
from rettxmutation.config import RettxConfig
from rettxmutation.services.services_factory import RettxServices
from rettxmutation.models.document import Document
from rettxmutation.models.gene_models import GeneMutation

logger = logging.getLogger(__name__)

class RettxPipeline:
    """Standard RettX processing pipeline."""

    def __init__(self, config: RettxConfig):
        """
        Initialize pipeline with configuration.
        
        Args:
            config: RettxConfig instance containing all necessary configuration
        """
        self.config = config
        self.services = RettxServices(config)
        
        logger.debug(f"{self.__class__.__name__} initialized with config")

    async def run_pipeline(self, file_stream) -> Tuple[Document, List[GeneMutation]]:
        """
        Full pipeline:
        - OCR → Validate → Extract Mutations → Validate Mutations → Return Results

        Args:
            file_stream: File-like object containing the document

        Returns:
            Tuple[Document, List[GeneMutation]]: Processed document and validated mutations
        """
        logger.info("🚀 Starting RettX pipeline")

        # 1️⃣ OCR
        logger.info("📝 Running OCR processing")
        document = self.services.ocr_service.extract_and_process_text(file_stream)

        # 2️⃣ Validation
        logger.info("🔍 Running document validation")
        is_valid, validation_conf = await self.services.validation_agent.validate_document(
            document.cleaned_text, document.language
        )

        if not is_valid:
            raise Exception(f"Document failed validation (confidence={validation_conf:.2f})")

        # 3️⃣ Text analytics for Healthcare entities (optional)
        try:
            logger.info("🔍 Running text analytics")
            document.text_analytics_result = self.services.text_analytics_service.identify_genetic_variants(
                document.cleaned_text
            )
            logger.info(f"Text analytics result: {document.text_analytics_result}")
        except Exception as e:
            logger.warning(f"Text analytics not available or failed: {e}")
            document.text_analytics_result = None

        # 4️⃣ Mutation extraction
        logger.info("🧬 Running mutation extraction")
        raw_mutations = await self.services.extraction_agent.extract_mutations(
            document.cleaned_text,
            document.dump_keywords(),
            document.dump_text_analytics_keywords()
        )

        # 5️⃣ Mutation validation
        validated_mutations = []
        if raw_mutations:
            logger.info(f"🔬 Validating {len(raw_mutations)} extracted mutations")
            try:
                validated_mutations = await self.services.mutation_validator.validate_mutations(
                    raw_mutations=raw_mutations
                )
                logger.info(f"✅ Successfully validated {len(validated_mutations)} mutations")
            except Exception as e:
                logger.error(f"❌ Error during mutation validation: {e}")
                # Continue with empty list or raise depending on requirements
                validated_mutations = []
        else:
            logger.warning("⚠️ No mutations detected in the document")

        logger.info("✅ RettX pipeline completed successfully")
        
        # Return the Document and the list of validated GeneMutation objects
        return document, validated_mutations

    def close(self):
        """Clean up resources."""
        # Clean up services via the factory
        if hasattr(self, 'services'):
            self.services.close()

    def _build_text_analytics_summary(self, mutations):
        """Summarize mutations for correction step."""
        if not mutations:
            return "No mutations detected."
        else:
            lines = [
                f"{m.mutation} (confidence={m.confidence:.2f})"
                for m in mutations
            ]
            return "High confidence mutations detected: " + "; ".join(lines)
