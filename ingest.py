#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Legal Document Ingestion Script
Loads Markdown files, chunks them, and creates a ChromaDB vector database.
Optimized for Portuguese legal documents.
"""

import os
import sys
from pathlib import Path
from typing import List
import logging

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LegalDocumentIngester:
    def __init__(self, docs_dir: str, vector_db_dir: str = "vector_db"):
        """
        Initialize the ingester.

        Args:
            docs_dir: Directory containing .md files
            vector_db_dir: Directory to store ChromaDB
        """
        self.docs_dir = docs_dir
        self.vector_db_dir = vector_db_dir
        self.documents = []
        self.chunks = []

        # Create vector_db directory if it doesn't exist
        Path(self.vector_db_dir).mkdir(exist_ok=True)

        logger.info(f"Initializing ingester for directory: {docs_dir}")
        logger.info(f"Vector DB will be stored at: {vector_db_dir}")

    def load_documents(self) -> int:
        """
        Load all Markdown files from the directory recursively.

        Returns:
            Number of documents loaded
        """
        logger.info("\n" + "="*80)
        logger.info("PHASE 1: LOADING MARKDOWN DOCUMENTS")
        logger.info("="*80 + "\n")

        try:
            # Use DirectoryLoader to load all .md files
            loader = DirectoryLoader(
                self.docs_dir,
                glob="**/*.md",
                use_multithreading=True,
                show_progress=True
            )

            self.documents = loader.load()
            logger.info(f"\n✓ Successfully loaded {len(self.documents)} documents\n")

            # Show sample of loaded documents
            if self.documents:
                logger.info("Sample loaded documents:")
                for doc in self.documents[:3]:
                    source = doc.metadata.get('source', 'Unknown')
                    logger.info(f"  • {source} ({len(doc.page_content)} chars)")
                if len(self.documents) > 3:
                    logger.info(f"  ... and {len(self.documents) - 3} more\n")

            return len(self.documents)

        except Exception as e:
            logger.error(f"✗ Error loading documents: {e}")
            raise

    def chunk_documents(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> int:
        """
        Split documents into chunks using RecursiveCharacterTextSplitter.
        Optimized for legal documents with context preservation.

        Args:
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks to preserve context

        Returns:
            Number of chunks created
        """
        logger.info("="*80)
        logger.info("PHASE 2: CHUNKING DOCUMENTS")
        logger.info("="*80)
        logger.info(f"Chunk size: {chunk_size} characters")
        logger.info(f"Chunk overlap: {chunk_overlap} characters\n")

        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=[
                    "\n## ",      # Markdown headers (secondary)
                    "\n### ",     # Markdown headers (tertiary)
                    "\n\n",       # Paragraph breaks
                    "\n",         # Line breaks
                    ". ",         # Sentences
                    " ",          # Words
                    ""            # Characters
                ],
                length_function=len,
            )

            # Process documents with progress bar
            for doc in tqdm(self.documents, desc="Chunking documents", unit="doc"):
                doc_chunks = splitter.split_documents([doc])
                self.chunks.extend(doc_chunks)

            logger.info(f"\n✓ Successfully created {len(self.chunks)} chunks\n")

            # Show statistics
            chunk_sizes = [len(chunk.page_content) for chunk in self.chunks]
            logger.info("Chunk statistics:")
            logger.info(f"  • Total chunks: {len(self.chunks)}")
            logger.info(f"  • Average chunk size: {sum(chunk_sizes) / len(chunk_sizes):.0f} characters")
            logger.info(f"  • Min chunk size: {min(chunk_sizes)}")
            logger.info(f"  • Max chunk size: {max(chunk_sizes)}\n")

            return len(self.chunks)

        except Exception as e:
            logger.error(f"✗ Error chunking documents: {e}")
            raise

    def create_embeddings_and_db(self, model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"):
        """
        Create embeddings and store them in ChromaDB.
        Uses HuggingFaceEmbeddings for Portuguese-optimized representations.

        Args:
            model_name: HuggingFace model for embeddings
        """
        logger.info("="*80)
        logger.info("PHASE 3: CREATING EMBEDDINGS AND VECTOR DATABASE")
        logger.info("="*80)
        logger.info(f"Embedding model: {model_name}\n")

        try:
            # Initialize embeddings with GPU support
            logger.info("Loading embedding model...")
            embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={"device": "cuda"},  # Use GPU
                encode_kwargs={"normalize_embeddings": True}
            )
            logger.info("✓ Embedding model loaded\n")

            # Create or update ChromaDB
            logger.info("Creating/updating ChromaDB...")
            vectorstore = Chroma.from_documents(
                documents=self.chunks,
                embedding=embeddings,
                persist_directory=self.vector_db_dir,
                collection_name="legal_documents"
            )

            logger.info("✓ ChromaDB created successfully\n")

            # Verify the database
            collection = vectorstore._collection
            count = collection.count()
            logger.info(f"✓ Vector database verified: {count} vectors stored\n")

            return vectorstore

        except Exception as e:
            logger.error(f"✗ Error creating embeddings/database: {e}")
            raise

    def run(self):
        """Execute the complete ingestion pipeline."""
        logger.info("\n")
        logger.info("╔" + "="*78 + "╗")
        logger.info("║" + " "*15 + "LEGAL DOCUMENT INGESTION PIPELINE" + " "*30 + "║")
        logger.info("╚" + "="*78 + "╝")
        logger.info("\n")

        try:
            # Phase 1: Load
            num_docs = self.load_documents()
            if num_docs == 0:
                logger.error("✗ No documents found!")
                return

            # Phase 2: Chunk
            num_chunks = self.chunk_documents()

            # Phase 3: Embed and store
            vectorstore = self.create_embeddings_and_db()

            # Summary
            logger.info("="*80)
            logger.info("SUMMARY")
            logger.info("="*80 + "\n")
            logger.info(f"✓ Documents loaded: {num_docs}")
            logger.info(f"✓ Documents chunked: {num_chunks}")
            logger.info(f"✓ Vector DB location: {os.path.abspath(self.vector_db_dir)}")
            logger.info(f"✓ Collection: legal_documents\n")
            logger.info("✨ Ingestion completed successfully!\n")
            logger.info("Ready for RAG chat! Run: python chat.py\n")

        except Exception as e:
            logger.error(f"\n✗ Ingestion failed: {e}\n")
            raise


def main():
    """Main entry point."""
    # Configuration
    DOCS_DIR = r"E:\biblioteca_juridica\direito"
    VECTOR_DB_DIR = "vector_db"

    # Verify documents directory exists
    if not os.path.exists(DOCS_DIR):
        logger.error(f"✗ Documents directory not found: {DOCS_DIR}")
        sys.exit(1)

    # Run ingestion
    ingester = LegalDocumentIngester(
        docs_dir=DOCS_DIR,
        vector_db_dir=VECTOR_DB_DIR
    )
    ingester.run()


if __name__ == "__main__":
    main()
