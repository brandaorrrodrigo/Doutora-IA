#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration file for RAG system
Modify these settings to customize the system behavior
"""

import os

# ============================================================================
# PATHS CONFIGURATION
# ============================================================================

# Directory containing legal documents (Markdown files)
DOCUMENTS_DIR = r"E:\biblioteca_juridica\direito"

# Directory where ChromaDB will be stored (created if doesn't exist)
VECTOR_DB_DIR = "vector_db"

# ============================================================================
# EMBEDDING MODEL CONFIGURATION
# ============================================================================

# HuggingFace embedding model
# Options:
#   - "sentence-transformers/paraphrase-multilingual-mpnet-base-v2" (RECOMMENDED - excellent for Portuguese)
#   - "sentence-transformers/all-MiniLM-L6-v2" (smaller, faster)
#   - "sentence-transformers/all-mpnet-base-v2" (larger, better)
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# Device for embeddings ("cuda" for GPU, "cpu" for CPU)
EMBEDDING_DEVICE = "cuda"  # Change to "cpu" if CUDA not available

# ============================================================================
# DOCUMENT CHUNKING CONFIGURATION
# ============================================================================

# Size of each chunk in characters
# Larger = more context, slower processing
# Smaller = less context, faster processing
# Recommended: 800-1200
CHUNK_SIZE = 1000

# Overlap between chunks (preserves context between chunks)
# Larger = more redundancy, better context continuity
# Smaller = less redundancy, faster processing
# Recommended: 150-250
CHUNK_OVERLAP = 200

# Characters per line in markdown (for separator detection)
CHUNK_SEPARATOR_LENGTH = 50

# ============================================================================
# LLM CONFIGURATION (Ollama)
# ============================================================================

# Model name (must be available via ollama pull)
# Popular options:
#   - "llama3" (recommended, ~4GB, very good quality)
#   - "mistral" (~5GB, good quality, very fast)
#   - "neural-chat" (~3GB, compact, good quality)
#   - "orca-mini" (~2GB, very compact, basic quality)
#   - "openchat" (~4GB, fast, good quality)
#   - "vicuna" (~4GB, conversational)
LLM_MODEL = "llama3"

# Ollama server address
OLLAMA_BASE_URL = "http://localhost:11434"

# Temperature for LLM responses
# 0.0 = deterministic, always same answer
# 0.5 = balanced
# 1.0 = very creative, random
# Recommended for legal documents: 0.2-0.4
LLM_TEMPERATURE = 0.3

# Top-k sampling (keep tokens with top k probability)
# Recommended: 30-50
LLM_TOP_K = 40

# Top-p (nucleus) sampling (cumulative probability threshold)
# Recommended: 0.8-0.95
LLM_TOP_P = 0.9

# ============================================================================
# RETRIEVAL CONFIGURATION
# ============================================================================

# Number of chunks to retrieve from vector database
# More = better context but slower, more tokens
# Fewer = faster but may miss relevant context
# Recommended: 3-7 (RTX 3090: can handle up to 10)
RETRIEVAL_K = 5

# Retrieval method
# Options: "similarity", "mmr" (maximal marginal relevance)
RETRIEVAL_TYPE = "similarity"

# ============================================================================
# CONVERSATION MEMORY CONFIGURATION
# ============================================================================

# Enable conversation memory (for follow-up questions)
ENABLE_MEMORY = True

# Maximum number of messages to keep in memory
# Larger = more context for follow-ups, but slower LLM processing
# Smaller = faster but may lose context
# Recommended: 5-10 exchanges (10-20 messages)
MAX_MEMORY_MESSAGES = 10

# ============================================================================
# PROMPT CONFIGURATION
# ============================================================================

# System prompt template (in Portuguese)
SYSTEM_PROMPT_PT = """Você é um assistente jurídico especializado em legislação brasileira e direito em geral.

INSTRUÇÕES CRÍTICAS:
1. Responda APENAS baseado no contexto fornecido
2. Se a informação não estiver no contexto, responda claramente "Não tenho informação sobre isso nos documentos"
3. Cite SEMPRE a fonte (nome do arquivo) das informações usadas
4. Se o contexto for insuficiente, indique isso explicitamente
5. Mantenha uma linguagem jurídica clara e profissional
6. Seja conciso mas completo
7. Use formatação clara (listas, parágrafos numerados quando apropriado)

CONTEXTO DO DOCUMENTO:
{context}

Responda em português (Brasil)."""

# Alternative prompt template (in English)
SYSTEM_PROMPT_EN = """You are a legal assistant specialized in Brazilian law and general law.

CRITICAL INSTRUCTIONS:
1. Answer ONLY based on provided context
2. If information is not in context, clearly state "I don't have information about this in the documents"
3. ALWAYS cite the source (filename) of information used
4. If context is insufficient, indicate this explicitly
5. Maintain clear and professional legal language
6. Be concise but complete
7. Use clear formatting (lists, numbered paragraphs when appropriate)

DOCUMENT CONTEXT:
{context}

Answer in English."""

# Select which prompt to use: "pt" for Portuguese, "en" for English
PROMPT_LANGUAGE = "pt"

# ============================================================================
# INGESTION CONFIGURATION
# ============================================================================

# Show progress bar during ingestion
SHOW_PROGRESS_BAR = True

# Use multithreading for document loading
USE_MULTITHREADING = True

# Maximum documents to load (for testing, set to 0 to load all)
MAX_DOCUMENTS = 0  # 0 = unlimited

# ============================================================================
# CHAT INTERFACE CONFIGURATION
# ============================================================================

# Show sources for each answer
SHOW_SOURCES = True

# Number of source documents to show
MAX_SOURCES_DISPLAY = 5

# Show conversation memory status
SHOW_MEMORY_STATUS = True

# ============================================================================
# PERFORMANCE TUNING
# ============================================================================

# Batch size for embedding creation (higher = faster, more memory)
# Recommended: 32-128 for RTX 3090
EMBEDDING_BATCH_SIZE = 64

# Use GPU for embeddings (much faster)
USE_GPU_EMBEDDINGS = True

# Normalize embeddings (improves similarity search)
NORMALIZE_EMBEDDINGS = True

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# Show timestamps in logs
LOG_TIMESTAMPS = True

# ============================================================================
# COLLECTION CONFIGURATION
# ============================================================================

# ChromaDB collection name
CHROMA_COLLECTION_NAME = "legal_documents"

# ============================================================================
# ADVANCED OPTIONS
# ============================================================================

# Persist ChromaDB to disk (recommended: True)
PERSIST_DB = True

# Allow adding new documents to existing database
ALLOW_UPDATE = True

# Delete old database before re-ingesting (set False to update)
DELETE_OLD_DB = False

# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_config():
    """Validate configuration values"""
    errors = []

    if not os.path.exists(DOCUMENTS_DIR):
        errors.append(f"DOCUMENTS_DIR does not exist: {DOCUMENTS_DIR}")

    if CHUNK_SIZE < 100:
        errors.append("CHUNK_SIZE too small (minimum 100)")

    if CHUNK_OVERLAP >= CHUNK_SIZE:
        errors.append("CHUNK_OVERLAP must be less than CHUNK_SIZE")

    if not (0.0 <= LLM_TEMPERATURE <= 1.0):
        errors.append("LLM_TEMPERATURE must be between 0.0 and 1.0")

    if RETRIEVAL_K < 1:
        errors.append("RETRIEVAL_K must be at least 1")

    if RETRIEVAL_K > 20:
        print("⚠️  Warning: RETRIEVAL_K > 20 may be slow")

    if errors:
        for error in errors:
            print(f"❌ Config Error: {error}")
        raise ValueError("Configuration validation failed")

    return True


def print_config():
    """Print current configuration"""
    print("\n" + "="*80)
    print("CURRENT CONFIGURATION")
    print("="*80 + "\n")

    print("📁 PATHS:")
    print(f"   Documents: {DOCUMENTS_DIR}")
    print(f"   Vector DB: {VECTOR_DB_DIR}\n")

    print("🧠 EMBEDDING:")
    print(f"   Model: {EMBEDDING_MODEL}")
    print(f"   Device: {EMBEDDING_DEVICE}")
    print(f"   Batch Size: {EMBEDDING_BATCH_SIZE}\n")

    print("📄 CHUNKING:")
    print(f"   Chunk Size: {CHUNK_SIZE} characters")
    print(f"   Overlap: {CHUNK_OVERLAP} characters\n")

    print("🤖 LLM (Ollama):")
    print(f"   Model: {LLM_MODEL}")
    print(f"   Temperature: {LLM_TEMPERATURE}")
    print(f"   Top-K: {LLM_TOP_K}")
    print(f"   Top-P: {LLM_TOP_P}\n")

    print("📚 RETRIEVAL:")
    print(f"   Top-K chunks: {RETRIEVAL_K}")
    print(f"   Method: {RETRIEVAL_TYPE}\n")

    print("💬 CONVERSATION:")
    print(f"   Memory enabled: {ENABLE_MEMORY}")
    print(f"   Max messages: {MAX_MEMORY_MESSAGES}\n")

    print("="*80 + "\n")


if __name__ == "__main__":
    validate_config()
    print_config()
    print("✓ Configuration is valid!\n")
