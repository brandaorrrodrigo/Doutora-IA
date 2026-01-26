from sentence_transformers import SentenceTransformer
import os
from typing import List
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        model_name = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-large")
        device = os.getenv("EMBEDDING_DEVICE", "cpu")
        
        logger.info(f"Loading embedding model: {model_name} on {device}")
        self.model = SentenceTransformer(model_name, device=device)
        
    def encode_query(self, text: str) -> List[float]:
        """Encode search query with 'query:' prefix for E5 models"""
        prefixed = f"query: {text}"
        embedding = self.model.encode(prefixed, normalize_embeddings=True)
        return embedding.tolist()
    
    def encode_document(self, text: str) -> List[float]:
        """Encode document with 'passage:' prefix for E5 models"""
        prefixed = f"passage: {text}"
        embedding = self.model.encode(prefixed, normalize_embeddings=True)
        return embedding.tolist()
    
    def encode_batch(self, texts: List[str], is_query: bool = False) -> List[List[float]]:
        """Encode multiple texts at once"""
        prefix = "query: " if is_query else "passage: "
        prefixed_texts = [f"{prefix}{text}" for text in texts]
        embeddings = self.model.encode(prefixed_texts, normalize_embeddings=True)
        return embeddings.tolist()

# Global instance
embedding_service = EmbeddingService()
