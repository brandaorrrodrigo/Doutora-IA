"""
RAG (Retrieval-Augmented Generation) system for Doutora IA
"""
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue


class RAGSystem:
    def __init__(self):
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-large")

        # Lazy initialization (will be initialized on first use)
        self._client = None
        self._encoder = None

        # Initialize collections and hierarchy
        self._init_collections()

    @property
    def client(self):
        """Lazy load Qdrant client on first access"""
        if self._client is None:
            try:
                self._client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
            except Exception as e:
                print(f"Warning: Could not connect to Qdrant: {e}")
                return None
        return self._client

    @property
    def encoder(self):
        """Lazy load embedding model on first access"""
        if self._encoder is None:
            try:
                self._encoder = SentenceTransformer(self.embedding_model_name)
            except Exception as e:
                print(f"Warning: Could not load embedding model: {e}")
                return None
        return self._encoder

    def _init_collections(self):
        """Initialize collections and hierarchy weights"""
        # Collection names
        self.collections = {
            "legis": "legis",
            "sumulas": "sumulas",
            "juris": "juris",
            "regulatorio": "regulatorio",
            "doutrina": "doutrina"
        }

        # Hierarchy weights for ranking
        self.hierarchy_weights = {
            "lei": 1.0,
            "sumula": 0.95,
            "repetitivo": 0.95,
            "leading_case": 0.85,
            "precedente": 0.75,
            "regulatorio": 0.70,
            "doutrina": 0.60
        }

    def create_collections(self):
        """Create all Qdrant collections if they don't exist"""
        vector_size = 1024  # intfloat/multilingual-e5-large dimension

        for collection_name in self.collections.values():
            try:
                self.client.get_collection(collection_name)
                print(f"Collection {collection_name} already exists")
            except:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created collection {collection_name}")

    def encode_text(self, text: str) -> List[float]:
        """Encode text to vector using sentence transformer"""
        # Add query prefix for better retrieval (e5 model specific)
        prefixed_text = f"query: {text}"
        embedding = self.encoder.encode(prefixed_text, convert_to_numpy=True)
        return embedding.tolist()

    def encode_document(self, text: str) -> List[float]:
        """Encode document text to vector"""
        # Add passage prefix for better retrieval (e5 model specific)
        prefixed_text = f"passage: {text}"
        embedding = self.encoder.encode(prefixed_text, convert_to_numpy=True)
        return embedding.tolist()

    def search(
        self,
        query: str,
        tipo: Optional[str] = None,
        area: Optional[str] = None,
        orgao: Optional[str] = None,
        tribunal: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Unified search across all collections with filters and ranking

        Ranking priority:
        1. Lei vigente
        2. Súmula / Repetitivo
        3. Leading case recente
        4. Regulatório
        5. Doutrina
        """
        query_vector = self.encode_text(query)
        all_results = []

        # Determine which collections to search
        collections_to_search = []
        if tipo:
            if tipo == "lei":
                collections_to_search = ["legis"]
            elif tipo == "sumula":
                collections_to_search = ["sumulas"]
            elif tipo == "juris":
                collections_to_search = ["juris"]
            elif tipo == "regulatorio":
                collections_to_search = ["regulatorio"]
            elif tipo == "doutrina":
                collections_to_search = ["doutrina"]
        else:
            # Search all collections
            collections_to_search = list(self.collections.values())

        # Search each collection
        for collection_name in collections_to_search:
            try:
                # Build filter
                filter_conditions = []

                if area:
                    filter_conditions.append(
                        FieldCondition(key="area", match=MatchValue(value=area))
                    )

                if orgao:
                    filter_conditions.append(
                        FieldCondition(key="orgao", match=MatchValue(value=orgao))
                    )

                if tribunal:
                    filter_conditions.append(
                        FieldCondition(key="tribunal", match=MatchValue(value=tribunal))
                    )

                # Build filter object
                search_filter = None
                if filter_conditions:
                    search_filter = Filter(must=filter_conditions)

                # Search
                search_results = self.client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=limit * 2,  # Get more results for ranking
                    query_filter=search_filter
                )

                # Convert to dict and add to results
                for result in search_results:
                    payload = result.payload
                    payload["_score"] = result.score
                    payload["_collection"] = collection_name
                    all_results.append(payload)

            except Exception as e:
                print(f"Error searching {collection_name}: {e}")
                continue

        # Rank results
        ranked_results = self._rank_results(all_results, data_inicio, data_fim)

        # Return top N
        return ranked_results[:limit]

    def _rank_results(
        self,
        results: List[Dict],
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None
    ) -> List[Dict]:
        """
        Rank results by:
        1. Hierarchy (lei > súmula > precedente > regulatório > doutrina)
        2. Vigência (vigente > não vigente)
        3. Date (more recent > older)
        4. Similarity score
        """
        scored_results = []

        for result in results:
            score = 0.0

            # Base similarity score (0-1)
            similarity_score = result.get("_score", 0.0)
            score += similarity_score * 0.3

            # Hierarchy weight (0-1)
            tipo = result.get("tipo", "")
            hierarchy_score = self.hierarchy_weights.get(tipo, 0.5)
            score += hierarchy_score * 0.4

            # Vigência bonus
            vigencia_fim = result.get("vigencia_fim")
            if vigencia_fim is None:  # Still active
                score += 0.2

            # Recency bonus (newer is better for jurisprudence)
            data_str = result.get("data")
            if data_str:
                try:
                    data = datetime.fromisoformat(data_str)
                    years_ago = (datetime.now() - data).days / 365
                    recency_score = max(0, 1 - (years_ago / 10))  # Decay over 10 years
                    score += recency_score * 0.1
                except:
                    pass

            # Date range filter
            if data_inicio or data_fim:
                data_str = result.get("data")
                if data_str:
                    try:
                        data = datetime.fromisoformat(data_str)
                        if data_inicio and data < datetime.fromisoformat(data_inicio):
                            continue
                        if data_fim and data > datetime.fromisoformat(data_fim):
                            continue
                    except:
                        pass

            result["_final_score"] = score
            scored_results.append(result)

        # Sort by final score
        scored_results.sort(key=lambda x: x["_final_score"], reverse=True)

        return scored_results

    def search_by_article(self, artigo: str, lei: str, area: Optional[str] = None) -> List[Dict]:
        """Search for specific article of law (e.g., Art. 300 CPC)"""
        query = f"{artigo} {lei}"

        results = self.search(
            query=query,
            tipo="lei",
            area=area,
            limit=5
        )

        # Filter to exact article match if possible
        exact_matches = [
            r for r in results
            if artigo.lower() in r.get("artigo_ou_tema", "").lower()
        ]

        return exact_matches if exact_matches else results[:1]

    def get_context_for_case(self, descricao: str, area: Optional[str] = None, limit_per_type: int = 3) -> str:
        """
        Get comprehensive context for a case by searching multiple types
        Returns formatted context string
        """
        context_parts = []

        # 1. Search laws
        leis = self.search(query=descricao, tipo="lei", area=area, limit=limit_per_type)
        if leis:
            context_parts.append("=== LEGISLAÇÃO APLICÁVEL ===")
            for lei in leis:
                context_parts.append(f"- {lei.get('titulo', '')}: {lei.get('texto', '')[:300]}...")

        # 2. Search súmulas and repetitivos
        sumulas = self.search(query=descricao, tipo="sumula", area=area, limit=limit_per_type)
        if sumulas:
            context_parts.append("\n=== SÚMULAS E TESES ===")
            for sumula in sumulas:
                context_parts.append(f"- {sumula.get('titulo', '')}: {sumula.get('texto', '')[:300]}...")

        # 3. Search jurisprudence
        juris = self.search(query=descricao, tipo="juris", area=area, limit=limit_per_type)
        if juris:
            context_parts.append("\n=== JURISPRUDÊNCIA ===")
            for j in juris:
                context_parts.append(f"- {j.get('titulo', '')} ({j.get('tribunal', '')}): {j.get('texto', '')[:300]}...")

        # 4. Search regulatório
        regulatorio = self.search(query=descricao, tipo="regulatorio", area=area, limit=limit_per_type)
        if regulatorio:
            context_parts.append("\n=== NORMAS REGULATÓRIAS ===")
            for reg in regulatorio:
                context_parts.append(f"- {reg.get('titulo', '')}: {reg.get('texto', '')[:300]}...")

        # 5. Search doutrina
        doutrina = self.search(query=descricao, tipo="doutrina", area=area, limit=2)
        if doutrina:
            context_parts.append("\n=== DOUTRINA ===")
            for doc in doutrina:
                context_parts.append(f"- {doc.get('titulo', '')}: {doc.get('texto', '')[:200]}...")

        return "\n".join(context_parts)

    def insert_document(self, collection: str, doc_id: str, document: Dict, text: str):
        """Insert a single document into collection"""
        vector = self.encode_document(text)

        point = PointStruct(
            id=doc_id,
            vector=vector,
            payload=document
        )

        self.client.upsert(
            collection_name=collection,
            points=[point]
        )

    def bulk_insert(self, collection: str, documents: List[Tuple[str, Dict, str]]):
        """
        Bulk insert documents
        documents: List of (id, payload, text) tuples
        """
        points = []

        for doc_id, payload, text in documents:
            vector = self.encode_document(text)
            point = PointStruct(
                id=doc_id,
                vector=vector,
                payload=payload
            )
            points.append(point)

        # Insert in batches of 100
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=collection,
                points=batch
            )
            print(f"Inserted batch {i // batch_size + 1} ({len(batch)} documents)")


# Singleton instance
_rag_system = None

def get_rag_system() -> RAGSystem:
    """Get or create RAG system singleton"""
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem()
    return _rag_system
