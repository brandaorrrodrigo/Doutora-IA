#!/usr/bin/env python3
"""
Ingestão de ebooks MD no Qdrant com embeddings GPU (RTX 3090)

Uso:
    python scripts/ingest_ebooks_md.py --data-dir D:\doutora-ia\direito\ebooksmds
    python scripts/ingest_ebooks_md.py --data-dir D:\doutora-ia\direito\ebooksmds --dry-run
    python scripts/ingest_ebooks_md.py --data-dir D:\doutora-ia\direito\ebooksmds --limit 10
"""

import os
import sys
import gc
import hashlib
import logging
import argparse
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from collections import Counter, defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-large")
VECTOR_DIM = 1024
CHUNK_SIZE = 4000       # characters (~1000 tokens)
CHUNK_OVERLAP = 800     # characters (~200 tokens)
ENCODE_BATCH_SIZE = 256 # texts per GPU batch
QDRANT_BATCH_SIZE = 100 # points per upsert
FLUSH_EVERY = 10000     # encode+upsert buffer size
CHECKPOINT_FILE = "ingest_checkpoint.json"

# Directory → Qdrant collection mapping
DIR_TO_COLLECTION = {
    "legislacao": "legis",
    "jurisprudencia": "juris",
}
DEFAULT_COLLECTION = "doutrina"

# Directory → area do direito mapping
DIR_TO_AREA = {
    "administrativo": "administrativo",
    "ambiental": "ambiental",
    "civil": "civil",
    "constitucional": "constitucional",
    "consumidor": "consumidor",
    "digital_e_lgpd": "digital",
    "direito_da_crianca_adolescente": "crianca_adolescente",
    "direito_da_familia": "familia",
    "direito_imobiliario": "imobiliario",
    "empresarial": "empresarial",
    "ENGENHARIA_DA_IA_JURIDICA": "ia_juridica",
    "filosofia_juridica": "filosofia",
    "internacional": "internacional",
    "metodologia_cientifica": "metodologia",
    "modelos_praticos": "pratica",
    "oabconcursos": "oab",
    "penal": "penal",
    "previdenciario": "previdenciario",
    "processo_civil": "processo_civil",
    "processo_penal": "processo_penal",
    "processo_trabalho": "processo_trabalho",
    "teoria_geral_do_direito": "teoria_geral",
    "trabalho": "trabalhista",
    "tributario": "tributario",
}

HIERARQUIA = {"legis": 1.0, "sumulas": 0.95, "juris": 0.85,
              "regulatorio": 0.70, "doutrina": 0.60}


# ==================== HELPERS ====================

def generate_id(text: str, prefix: str = "") -> int:
    h = hashlib.md5(f"{prefix}_{text}".encode('utf-8')).hexdigest()
    return int(h[:15], 16)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size

        if end < len(text):
            para_break = text.rfind('\n\n', start + chunk_size // 2, end + 100)
            if para_break > start:
                end = para_break
            else:
                for sep in ['. ', '.\n', ';\n', '\n']:
                    sent_break = text.rfind(sep, start + chunk_size // 2, end + 50)
                    if sent_break > start:
                        end = sent_break + len(sep)
                        break

        chunk = text[start:end].strip()
        if chunk and len(chunk) > 50:
            chunks.append(chunk)

        start = end - overlap
        if start >= len(text):
            break

    return chunks


def extract_title(text: str, filename: str) -> str:
    for line in text[:2000].split('\n'):
        line = line.strip()
        if line.startswith('# ') and len(line) > 3:
            return line[2:].strip()[:200]
    name = Path(filename).stem
    for prefix in ['#', '00. ', '0. ']:
        if name.startswith(prefix):
            name = name[len(prefix):]
    return name[:200]


def categorize_by_filename(filename: str) -> Optional[str]:
    fn = filename.lower()
    if any(k in fn for k in ["código", "codigo", "lei ", "constituição", "constituicao",
                              "clt", " cpc", " cpp", " ctn", "estatuto", "decreto"]):
        return "legis"
    elif any(k in fn for k in ["súmula", "sumula"]):
        return "sumulas"
    elif any(k in fn for k in ["jurisprudência", "jurisprudencia", "julgado",
                                "acórdão", "acordao", "stf", "stj"]):
        return "juris"
    elif any(k in fn for k in ["resolução", "resolucao", "portaria",
                                "instrução normativa", "instrucao normativa"]):
        return "regulatorio"
    return None


def detect_area(text: str) -> Optional[str]:
    sample = text[:3000].lower()
    areas = {
        "familia": ["família", "familia", "alimentos", "divórcio", "guarda", "casamento"],
        "consumidor": ["consumidor", "cdc", "fornecedor"],
        "bancario": ["bancário", "bancario", "financeiro", "crédito"],
        "saude": ["saúde", "saude", "plano de saúde", "ans", "hospital"],
        "penal": ["penal", "crime", "prisão", "delito", "homicídio"],
        "trabalhista": ["trabalhista", "trabalho", "emprego", "clt", "fgts"],
        "tributario": ["tributário", "tributario", "imposto", "tributo"],
        "administrativo": ["administrativo", "licitação", "improbidade"],
        "civil": ["civil", "obrigações", "contratos", "responsabilidade civil"],
        "constitucional": ["constitucional", "constituição", "direitos fundamentais"],
    }
    for area, keywords in areas.items():
        if any(k in sample for k in keywords):
            return area
    return None


# ==================== MAIN PIPELINE ====================

def scan_files(data_dir: Path) -> List[Tuple[Path, str, str]]:
    """Scan all .md files (lightweight - only stores paths + metadata)"""
    results = []
    for md_file in sorted(data_dir.rglob('*.md')):
        parts = md_file.relative_to(data_dir).parts
        if 'venv' in parts:
            continue
        subdir = parts[0] if len(parts) > 1 else ""
        collection = DIR_TO_COLLECTION.get(subdir, None)
        if not collection:
            collection = categorize_by_filename(md_file.name) or DEFAULT_COLLECTION
        area = DIR_TO_AREA.get(subdir, subdir if subdir else None)
        results.append((md_file, collection, area))
    return results


def process_file_to_chunks(md_file: Path, collection: str, area: Optional[str]):
    """Generator: yields (text_for_embedding, payload, doc_id) for each chunk."""
    try:
        text = md_file.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        logger.warning(f"  Error reading {md_file.name}: {e}")
        return

    if len(text.strip()) < 100:
        return

    title = extract_title(text, md_file.name)
    if not area:
        area = detect_area(text)

    chunks = chunk_text(text)
    total = len(chunks)

    for i, chunk in enumerate(chunks):
        doc_id = generate_id(chunk, f"{md_file.stem}_{i}")
        payload = {
            "tipo": collection,
            "titulo": title if total == 1 else f"{title} [{i+1}/{total}]",
            "texto": chunk,
            "area": area,
            "hierarquia": HIERARQUIA.get(collection, 0.5),
            "fonte_arquivo": md_file.name,
            "chunk_index": i,
            "total_chunks": total,
            "metadata": {
                "source_file": md_file.name,
                "source_dir": md_file.parent.name,
                "ingested_at": datetime.utcnow().isoformat()
            }
        }
        yield (f"passage: {chunk}", payload, doc_id)


def flush_buffer(buffer, model, client, collection, qdrant_batch_size):
    """Encode a buffer of chunks and upsert to Qdrant. Returns count inserted."""
    if not buffer:
        return 0

    from qdrant_client.models import PointStruct

    texts = [item[0] for item in buffer]
    payloads = [item[1] for item in buffer]
    ids = [item[2] for item in buffer]

    # Encode
    enc_t0 = time.time()
    embeddings = model.encode(
        texts,
        batch_size=ENCODE_BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    enc_time = time.time() - enc_t0
    logger.info(f"    Encoded {len(texts)} in {enc_time:.1f}s ({len(texts)/max(enc_time,0.1):.0f}/s)")

    # Upsert in batches
    for i in range(0, len(buffer), qdrant_batch_size):
        batch_end = min(i + qdrant_batch_size, len(buffer))
        points = [
            PointStruct(
                id=ids[j],
                vector=embeddings[j].tolist(),
                payload=payloads[j]
            )
            for j in range(i, batch_end)
        ]
        client.upsert(collection_name=collection, points=points)

    count = len(buffer)
    del texts, payloads, ids, embeddings
    return count


def save_checkpoint(checkpoint_path, collection, file_idx, total_inserted):
    """Save progress checkpoint for resume."""
    import json
    data = {"collection": collection, "file_idx": file_idx, "total_inserted": total_inserted,
            "timestamp": datetime.utcnow().isoformat()}
    Path(checkpoint_path).write_text(json.dumps(data))


def load_checkpoint(checkpoint_path):
    """Load progress checkpoint."""
    import json
    p = Path(checkpoint_path)
    if p.exists():
        return json.loads(p.read_text())
    return None


def main():
    parser = argparse.ArgumentParser(description="Ingest ebook MDs into Qdrant")
    parser.add_argument("--data-dir", type=str, required=True, help="Directory with .md files")
    parser.add_argument("--dry-run", action="store_true", help="Count chunks without ingesting")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of files (0=all)")
    parser.add_argument("--skip-existing", action="store_true", help="Skip if collections have data")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        logger.error(f"Directory not found: {data_dir}")
        sys.exit(1)

    # ---- Step 1: Scan files (lightweight) ----
    logger.info(f"Scanning {data_dir} for .md files...")
    file_list = scan_files(data_dir)
    if args.limit > 0:
        file_list = file_list[:args.limit]
    logger.info(f"Found {len(file_list)} files to process")

    col_counts = Counter(col for _, col, _ in file_list)
    for col, cnt in sorted(col_counts.items()):
        logger.info(f"  {col}: {cnt} files")

    # Group file list by collection (just paths, not content)
    files_by_collection = defaultdict(list)
    for md_file, collection, area in file_list:
        files_by_collection[collection].append((md_file, area))

    if args.dry_run:
        logger.info("\n[DRY RUN] Counting chunks per collection...")
        total_chunks = 0
        for collection, files in sorted(files_by_collection.items()):
            col_chunks = 0
            for md_file, area in files:
                col_chunks += sum(1 for _ in process_file_to_chunks(md_file, collection, area))
            total_chunks += col_chunks
            logger.info(f"  {collection}: {col_chunks:,} chunks")
        logger.info(f"\nTotal chunks: {total_chunks:,}")
        logger.info("[DRY RUN] No data ingested.")
        return

    # ---- Step 2: Initialize model + Qdrant ----
    logger.info(f"\nLoading embedding model: {EMBEDDING_MODEL} ...")
    from sentence_transformers import SentenceTransformer
    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Device: {device}" + (f" ({torch.cuda.get_device_name(0)})" if device == "cuda" else ""))

    model = SentenceTransformer(EMBEDDING_MODEL, device=device)
    if device == "cuda":
        model.half()
        logger.info("Using FP16 for faster GPU encoding")
    logger.info(f"Model loaded. Vector dim: {model.get_sentence_embedding_dimension()}")

    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams

    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    logger.info(f"Connected to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")

    # Create collections if needed
    all_collections = set(files_by_collection.keys())
    skip_collections = set()
    for col_name in all_collections:
        try:
            info = client.get_collection(col_name)
            logger.info(f"Collection '{col_name}' exists ({info.points_count} points)")
            if args.skip_existing and info.points_count > 0:
                logger.info(f"  Skipping (--skip-existing)")
                skip_collections.add(col_name)
        except Exception:
            client.create_collection(
                collection_name=col_name,
                vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE)
            )
            logger.info(f"Created collection '{col_name}'")

    # ---- Step 3: Stream process each collection ----
    import torch
    checkpoint_path = data_dir / CHECKPOINT_FILE
    resume_col = None
    resume_file_idx = 0
    total_inserted = 0

    if args.resume:
        cp = load_checkpoint(checkpoint_path)
        if cp:
            resume_col = cp["collection"]
            resume_file_idx = cp["file_idx"]
            total_inserted = cp["total_inserted"]
            logger.info(f"Resuming from checkpoint: {resume_col} file {resume_file_idx}, "
                        f"{total_inserted:,} already inserted")
        else:
            logger.info("No checkpoint found, starting fresh")

    global_t0 = time.time()

    for collection in sorted(files_by_collection.keys()):
        if collection in skip_collections:
            continue

        # Skip collections already completed in previous run
        if resume_col and collection < resume_col:
            logger.info(f"Skipping '{collection}' (already completed in previous run)")
            continue

        files = files_by_collection[collection]
        start_file = resume_file_idx if collection == resume_col else 0

        logger.info(f"\n{'='*60}")
        logger.info(f"Collection: {collection} ({len(files)} files, starting at {start_file})")
        logger.info(f"{'='*60}")

        col_t0 = time.time()
        col_inserted = 0
        col_chunks = 0
        buffer = []  # list of (text, payload, id)

        for file_idx, (md_file, area) in enumerate(files):
            # Skip files already processed in previous run
            if file_idx < start_file:
                continue

            # Stream chunks from this file into the buffer
            for item in process_file_to_chunks(md_file, collection, area):
                buffer.append(item)
                col_chunks += 1

                # Flush buffer when full
                if len(buffer) >= FLUSH_EVERY:
                    logger.info(f"  Flush {col_inserted}-{col_inserted+len(buffer)} "
                                f"(file {file_idx+1}/{len(files)}, {col_chunks:,} chunks so far)")
                    inserted = flush_buffer(buffer, model, client, collection, QDRANT_BATCH_SIZE)
                    col_inserted += inserted
                    total_inserted += inserted
                    buffer.clear()
                    gc.collect()

                    # Save checkpoint
                    save_checkpoint(checkpoint_path, collection, file_idx, total_inserted)

                    elapsed = time.time() - global_t0
                    logger.info(f"    Total: {total_inserted:,} | Elapsed: {elapsed:.0f}s ({elapsed/60:.1f}min)")

            # Log progress every 200 files
            if (file_idx + 1) % 200 == 0:
                logger.info(f"  Processed {file_idx+1}/{len(files)} files, "
                            f"{col_chunks:,} chunks, buffer={len(buffer)}")

        # Flush remaining buffer
        if buffer:
            logger.info(f"  Final flush: {len(buffer)} chunks")
            inserted = flush_buffer(buffer, model, client, collection, QDRANT_BATCH_SIZE)
            col_inserted += inserted
            total_inserted += inserted
            buffer.clear()
            gc.collect()

        col_time = time.time() - col_t0
        logger.info(f"  Collection '{collection}' done: {col_inserted:,} chunks "
                    f"in {col_time:.0f}s ({col_time/60:.1f}min)")

    # Clean checkpoint on success
    if checkpoint_path.exists():
        checkpoint_path.unlink()

    # ---- Step 4: Summary ----
    total_time = time.time() - global_t0
    logger.info(f"\n{'='*60}")
    logger.info(f"INGESTION COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"Total chunks ingested: {total_inserted:,}")
    logger.info(f"Total time: {total_time:.0f}s ({total_time/60:.1f} min)")
    if total_time > 0:
        logger.info(f"Rate: {total_inserted/total_time:.0f} chunks/s")

    # Verify
    logger.info(f"\nVerification:")
    for col_name in sorted(files_by_collection.keys()):
        try:
            info = client.get_collection(col_name)
            logger.info(f"  {col_name}: {info.points_count:,} points")
        except Exception as e:
            logger.error(f"  {col_name}: ERROR - {e}")


if __name__ == "__main__":
    main()
