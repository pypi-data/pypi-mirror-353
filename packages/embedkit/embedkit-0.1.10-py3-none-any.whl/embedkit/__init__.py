# ./src/embedkit/__init__.py
"""
EmbedKit: A unified toolkit for generating vector embeddings.
"""

from typing import Union, List, Optional
from pathlib import Path

from .models import Model
from .base import EmbeddingError, EmbeddingResponse
from .providers import ColPaliProvider, CohereProvider, JinaProvider, SnowflakeProvider, QwenProvider


class EmbedKit:
    """Main interface for generating embeddings."""

    def __init__(self, provider_instance):
        """
        Initialize EmbedKit with a provider instance.

        Args:
            provider_instance: An initialized provider (use class methods to create)
        """
        self._provider = provider_instance

    @classmethod
    def colpali(
        cls,
        model: Model = Model.ColPali.COLPALI_V1_3,
        device: Optional[str] = None,
        text_batch_size: int = 32,
        image_batch_size: int = 8,
    ):
        """
        Create EmbedKit instance with ColPali provider.

        Args:
            model: ColPali model enum
            device: Device to run on ('cuda', 'mps', 'cpu', or None for auto-detect)
            text_batch_size: Batch size for text embedding generation
            image_batch_size: Batch size for image embedding generation
        """
        if not isinstance(model, Model.ColPali):
            raise ValueError(
                f"Unsupported model: {model}. Must be a Model.ColPali enum value."
            )

        provider = ColPaliProvider(
            model=model,
            device=device,
            text_batch_size=text_batch_size,
            image_batch_size=image_batch_size,
        )
        return cls(provider)

    @classmethod
    def cohere(
        cls,
        api_key: str,
        model: Model = Model.Cohere.EMBED_V4_0,
        text_batch_size: int = 32,
        image_batch_size: int = 8,
    ):
        """
        Create EmbedKit instance with Cohere provider.

        Args:
            api_key: Cohere API key
            model: Cohere model enum
            text_batch_size: Batch size for text embedding generation
            image_batch_size: Batch size for image embedding generation
        """
        if not api_key:
            raise ValueError("API key is required")

        if not isinstance(model, Model.Cohere):
            raise ValueError(f"Unsupported model: {model}")

        provider = CohereProvider(
            api_key=api_key,
            model=model,
            text_batch_size=text_batch_size,
            image_batch_size=image_batch_size,
        )
        return cls(provider)

    @classmethod
    def jina(
        cls,
        api_key: str,
        model: Model = Model.Jina.CLIP_V2,
        text_batch_size: int = 32,
        image_batch_size: int = 8,
    ):
        """
        Create EmbedKit instance with Jina provider.

        Args:
            api_key: Jina API key
            model: Jina model enum
            text_batch_size: Batch size for text embedding generation
            image_batch_size: Batch size for image embedding generation
        """
        if not api_key:
            raise ValueError("API key is required")

        if not isinstance(model, Model.Jina):
            raise ValueError(f"Unsupported model: {model}")

        provider = JinaProvider(
            api_key=api_key,
            model=model,
            text_batch_size=text_batch_size,
            image_batch_size=image_batch_size,
        )
        return cls(provider)

    @classmethod
    def snowflake(
        cls,
        model: Model = Model.Snowflake.ARCTIC_EMBED_M_V1_5,
        text_batch_size: int = 32,
        image_batch_size: int = 8,
        device: Optional[str] = None,
    ):
        """
        Create EmbedKit instance with Snowflake provider.

        Args:
            model: Snowflake model enum
            text_batch_size: Batch size for text embedding generation
            image_batch_size: Batch size for image embedding generation (not used)
            device: Device to run on ('cuda', 'mps', 'cpu', or None for auto-detect)
        """
        if not isinstance(model, Model.Snowflake):
            raise ValueError(f"Unsupported model: {model}")

        provider = SnowflakeProvider(
            model=model,
            text_batch_size=text_batch_size,
            image_batch_size=image_batch_size,
            device=device,
        )
        return cls(provider)

    @classmethod
    def qwen(
        cls,
        model: Model = Model.Qwen.QWEN3_EMBEDDING_0_6B,
        text_batch_size: int = 32,
        image_batch_size: int = 8,
        device: Optional[str] = None,
    ):
        """
        Create EmbedKit instance with Qwen provider.

        Args:
            model: Qwen model enum
            text_batch_size: Batch size for text embedding generation
            image_batch_size: Batch size for image embedding generation (not used)
            device: Device to run on ('cuda', 'mps', 'cpu', or None for auto-detect)
        """
        if not isinstance(model, Model.Qwen):
            raise ValueError(f"Unsupported model: {model}")

        provider = QwenProvider(
            model=model,
            text_batch_size=text_batch_size,
            image_batch_size=image_batch_size,
            device=device,
        )
        return cls(provider)

    # Future class methods:
    # @classmethod
    # def openai(cls, api_key: str, model_name: str = "text-embedding-3-large"):
    #     """Create EmbedKit instance with OpenAI provider."""
    #     provider = OpenAIProvider(api_key=api_key, model_name=model_name)
    #     return cls(provider)
    #
    # @classmethod
    # def huggingface(cls, model_name: str = "all-MiniLM-L6-v2", device: Optional[str] = None):
    #     """Create EmbedKit instance with HuggingFace provider."""
    #     provider = HuggingFaceProvider(model_name=model_name, device=device)
    #     return cls(provider)

    def embed_document(self, texts: Union[str, List[str]], **kwargs) -> EmbeddingResponse:
        """Generate document text embeddings using the configured provider.

        This is the primary method for generating embeddings for documents or longer text.
        For providers that differentiate between query and document embeddings (Cohere and Snowflake),
        this will use the document-specific embedding model.

        Args:
            texts: Text or list of texts to embed
            **kwargs: Additional provider-specific arguments

        Returns:
            EmbeddingResult containing the embeddings
        """
        return self._provider.embed_document(texts, **kwargs)

    def embed_query(self, texts: Union[str, List[str]], **kwargs) -> EmbeddingResponse:
        """Generate query text embeddings using the configured provider.

        For providers that differentiate between query and document embeddings (Cohere and Snowflake),
        this will use the query-specific embedding model. For other providers (ColPali and Jina),
        this aliases to embed_document.

        Args:
            texts: Text or list of texts to embed
            **kwargs: Additional provider-specific arguments

        Returns:
            EmbeddingResult containing the embeddings
        """
        return self._provider.embed_query(texts, **kwargs)

    def embed_image(
        self, images: Union[Path, str, List[Union[Path, str]]]
    ) -> EmbeddingResponse:
        """Generate image embeddings using the configured provider."""
        return self._provider.embed_image(images)

    def embed_pdf(self, pdf: Union[Path, str]) -> EmbeddingResponse:
        """Generate image embeddings from PDFs using the configured provider. Takes a single PDF file."""
        return self._provider.embed_pdf(pdf)

    @property
    def provider_info(self) -> str:
        """Get information about the current provider."""
        return f"{self._provider.__class__.__name__}"


# Main exports
__version__ = "0.1.0"
__all__ = ["EmbedKit", "Model", "EmbeddingError"]
