#!/usr/bin/env python3
"""
Script para ingestão completa do corpus jurídico no Qdrant

Processa PDFs da pasta 01-ebooks-recuperados e dados existentes em data/samples

Uso:
    python scripts/ingest_full_corpus.py --samples     # Ingerir apenas samples
    python scripts/ingest_full_corpus.py --ebooks     # Processar e ingerir e-books
    python scripts/ingest_full_corpus.py --all        # Ingerir tudo
"""

import os
import sys
import json
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "api"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_id(text: str, prefix: str = "") -> str:
    """Generate a unique ID from text content"""
    hash_obj = hashlib.md5(text.encode('utf-8'))
    return f"{prefix}_{hash_obj.hexdigest()[:12]}"


def load_sample_data(samples_dir: Path) -> Dict[str, List[Dict]]:
    """Load sample JSON files from data/samples directory"""
    documents = {
        "legis": [],
        "sumulas": [],
        "juris": [],
        "regulatorio": [],
        "doutrina": [],
        "temas": []
    }

    if not samples_dir.exists():
        logger.warning(f"Samples directory not found: {samples_dir}")
        return documents

    # Map subdirectories to collection names
    dir_mapping = {
        "legis": "legis",
        "sumulas": "sumulas",
        "juris": "juris",
        "regulatorio": "regulatorio",
        "doutrina": "doutrina",
        "temas": "temas"
    }

    for subdir, collection in dir_mapping.items():
        subdir_path = samples_dir / subdir
        if not subdir_path.exists():
            continue

        for json_file in subdir_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Normalize the document
                if isinstance(data, list):
                    for item in data:
                        doc = normalize_sample_doc(item, collection)
                        if doc:
                            documents[collection].append(doc)
                else:
                    doc = normalize_sample_doc(data, collection)
                    if doc:
                        documents[collection].append(doc)

                logger.info(f"Loaded {json_file.name}")

            except Exception as e:
                logger.error(f"Error loading {json_file}: {e}")

    return documents


def normalize_sample_doc(data: Dict, collection: str) -> Optional[Dict]:
    """Normalize a sample document to standard format"""
    try:
        # Get the main text content
        texto = (
            data.get("texto") or
            data.get("texto_completo") or
            data.get("ementa") or
            data.get("conteudo") or
            ""
        )

        if not texto:
            return None

        # Generate ID
        doc_id = data.get("id") or generate_id(texto, collection[:3])

        # Get title
        titulo = (
            data.get("titulo") or
            data.get("nome") or
            f"{collection.capitalize()} - {doc_id}"
        )

        return {
            "id": doc_id,
            "tipo": collection,
            "titulo": titulo,
            "texto": texto,
            "area": data.get("area"),
            "orgao": data.get("orgao"),
            "tribunal": data.get("tribunal"),
            "data": data.get("data"),
            "tema": data.get("tema"),
            "artigo_ou_tema": data.get("artigo") or data.get("tema"),
            "fonte_url": data.get("fonte_url"),
            "hierarquia": get_hierarchy_score(collection),
            "metadata": {
                "original_file": data.get("_source_file"),
                "ingested_at": datetime.utcnow().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error normalizing document: {e}")
        return None


def get_hierarchy_score(collection: str) -> float:
    """Get hierarchy score for collection type"""
    scores = {
        "legis": 1.0,
        "sumulas": 0.95,
        "temas": 0.95,
        "juris": 0.85,
        "regulatorio": 0.80,
        "doutrina": 0.70
    }
    return scores.get(collection, 0.5)


def process_pdf_to_chunks(pdf_path: Path, chunk_size: int = 1000) -> List[Dict]:
    """
    Process a PDF file and split into chunks for ingestion

    Uses PyMuPDF (fitz) for PDF extraction
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.error("PyMuPDF not installed. Run: pip install pymupdf")
        return []

    chunks = []

    try:
        doc = fitz.open(pdf_path)
        full_text = ""

        # Extract text from all pages
        for page_num, page in enumerate(doc):
            text = page.get_text()
            full_text += text + "\n"

        doc.close()

        if not full_text.strip():
            logger.warning(f"No text extracted from {pdf_path.name}")
            return []

        # Determine document type from filename
        filename = pdf_path.stem.lower()
        doc_type = categorize_document(filename)

        # Split into chunks
        words = full_text.split()
        current_chunk = []
        current_size = 0
        chunk_num = 0

        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1

            if current_size >= chunk_size:
                chunk_text = " ".join(current_chunk)
                chunk_id = generate_id(chunk_text, f"ebook_{pdf_path.stem[:20]}")

                chunks.append({
                    "id": f"{chunk_id}_chunk{chunk_num}",
                    "tipo": doc_type,
                    "titulo": f"{pdf_path.stem} - Parte {chunk_num + 1}",
                    "texto": chunk_text,
                    "area": detect_area(filename + " " + chunk_text[:500]),
                    "fonte_url": None,
                    "hierarquia": get_hierarchy_score(doc_type),
                    "metadata": {
                        "source_file": pdf_path.name,
                        "chunk_number": chunk_num,
                        "total_pages": len(doc) if 'doc' in dir() else None,
                        "ingested_at": datetime.utcnow().isoformat()
                    }
                })

                current_chunk = []
                current_size = 0
                chunk_num += 1

        # Add remaining text
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk_id = generate_id(chunk_text, f"ebook_{pdf_path.stem[:20]}")

            chunks.append({
                "id": f"{chunk_id}_chunk{chunk_num}",
                "tipo": doc_type,
                "titulo": f"{pdf_path.stem} - Parte {chunk_num + 1}",
                "texto": chunk_text,
                "area": detect_area(filename + " " + chunk_text[:500]),
                "fonte_url": None,
                "hierarquia": get_hierarchy_score(doc_type),
                "metadata": {
                    "source_file": pdf_path.name,
                    "chunk_number": chunk_num,
                    "ingested_at": datetime.utcnow().isoformat()
                }
            })

        logger.info(f"Processed {pdf_path.name}: {len(chunks)} chunks")
        return chunks

    except Exception as e:
        logger.error(f"Error processing {pdf_path}: {e}")
        return []


def categorize_document(filename: str) -> str:
    """Categorize document based on filename"""
    filename = filename.lower()

    if any(k in filename for k in ["código", "codigo", "lei", "constituição", "constituicao", "clt", "cpc", "cpp", "ctn"]):
        return "legis"
    elif any(k in filename for k in ["súmula", "sumula"]):
        return "sumulas"
    elif any(k in filename for k in ["jurisprudência", "jurisprudencia", "julgado", "acórdão", "acordao"]):
        return "juris"
    elif any(k in filename for k in ["resolução", "resolucao", "portaria", "instrução normativa", "ans", "anac", "bacen"]):
        return "regulatorio"
    else:
        return "doutrina"


def detect_area(text: str) -> Optional[str]:
    """Detect legal area from text content"""
    text = text.lower()

    areas = {
        "familia": ["família", "familia", "alimentos", "divórcio", "divorcio", "guarda", "casamento", "sucessões", "inventário"],
        "consumidor": ["consumidor", "cdc", "fornecedor", "produto", "serviço defeituoso", "recall"],
        "bancario": ["banco", "bancário", "bancario", "financeiro", "pix", "crédito", "credito", "empréstimo", "juros"],
        "saude": ["saúde", "saude", "plano de saúde", "ans", "hospital", "médico", "medico", "tratamento"],
        "aereo": ["aéreo", "aereo", "aviação", "aviacao", "anac", "passageiro", "voo", "bagagem"],
        "penal": ["penal", "crime", "prisão", "prisao", "pena", "delito"],
        "trabalhista": ["trabalhista", "trabalho", "emprego", "clt", "fgts", "rescisão"],
        "tributario": ["tributário", "tributario", "imposto", "tributo", "icms", "irpf", "ctn"],
        "administrativo": ["administrativo", "licitação", "licitacao", "improbidade", "servidor público"]
    }

    for area, keywords in areas.items():
        if any(k in text for k in keywords):
            return area

    return None


def ingest_to_qdrant(documents: Dict[str, List[Dict]], batch_size: int = 100):
    """Ingest documents into Qdrant"""
    try:
        from api.rag import get_rag_system
    except ImportError as e:
        logger.error(f"Could not import RAG system: {e}")
        logger.info("Make sure you're running from the project root and have installed requirements")
        return False

    try:
        rag = get_rag_system()

        # Create collections
        logger.info("Creating Qdrant collections...")
        rag.create_collections()

        total_ingested = 0

        for collection, docs in documents.items():
            if not docs:
                continue

            logger.info(f"\nIngesting {len(docs)} documents into '{collection}'...")

            # Process in batches
            for i in range(0, len(docs), batch_size):
                batch = docs[i:i + batch_size]

                # Prepare for bulk insert: (id, payload, text)
                bulk_data = [
                    (doc["id"], doc, doc["texto"])
                    for doc in batch
                ]

                try:
                    rag.bulk_insert(collection, bulk_data)
                    total_ingested += len(batch)
                    logger.info(f"  Batch {i // batch_size + 1}: {len(batch)} docs ingested")
                except Exception as e:
                    logger.error(f"  Error ingesting batch: {e}")

        logger.info(f"\n{'='*50}")
        logger.info(f"Total documents ingested: {total_ingested}")
        logger.info(f"{'='*50}")

        return True

    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Ingest legal corpus into Qdrant")
    parser.add_argument("--samples", action="store_true", help="Ingest sample data from data/samples")
    parser.add_argument("--ebooks", action="store_true", help="Process and ingest e-books from 01-ebooks-recuperados")
    parser.add_argument("--all", action="store_true", help="Ingest all available data")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed without ingesting")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of PDFs to process (0 = no limit)")

    args = parser.parse_args()

    if not any([args.samples, args.ebooks, args.all]):
        parser.print_help()
        return

    all_documents = {
        "legis": [],
        "sumulas": [],
        "juris": [],
        "regulatorio": [],
        "doutrina": [],
        "temas": []
    }

    # Process sample data
    if args.samples or args.all:
        logger.info("Loading sample data...")
        samples_dir = PROJECT_ROOT / "data" / "samples"
        sample_docs = load_sample_data(samples_dir)

        for collection, docs in sample_docs.items():
            all_documents[collection].extend(docs)
            if docs:
                logger.info(f"  {collection}: {len(docs)} documents")

    # Process e-books
    if args.ebooks or args.all:
        ebooks_dir = PROJECT_ROOT / "01-ebooks-recuperados"

        if not ebooks_dir.exists():
            logger.warning(f"E-books directory not found: {ebooks_dir}")
        else:
            logger.info(f"\nProcessing e-books from {ebooks_dir}...")

            pdf_files = list(ebooks_dir.glob("*.pdf"))

            if args.limit > 0:
                pdf_files = pdf_files[:args.limit]

            logger.info(f"Found {len(pdf_files)} PDF files to process")

            for i, pdf_path in enumerate(pdf_files):
                logger.info(f"\n[{i+1}/{len(pdf_files)}] Processing: {pdf_path.name}")

                if args.dry_run:
                    doc_type = categorize_document(pdf_path.stem)
                    logger.info(f"  Would be categorized as: {doc_type}")
                    continue

                chunks = process_pdf_to_chunks(pdf_path)

                if chunks:
                    doc_type = chunks[0]["tipo"]
                    all_documents[doc_type].extend(chunks)

    # Show summary
    logger.info("\n" + "="*50)
    logger.info("SUMMARY")
    logger.info("="*50)

    total = 0
    for collection, docs in all_documents.items():
        if docs:
            logger.info(f"  {collection}: {len(docs)} documents")
            total += len(docs)

    logger.info(f"\nTotal: {total} documents")

    if args.dry_run:
        logger.info("\n[DRY RUN] No data was ingested")
        return

    if total == 0:
        logger.warning("No documents to ingest")
        return

    # Ingest to Qdrant
    logger.info("\nStarting ingestion to Qdrant...")
    success = ingest_to_qdrant(all_documents)

    if success:
        logger.info("\nIngestion completed successfully!")
    else:
        logger.error("\nIngestion failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
