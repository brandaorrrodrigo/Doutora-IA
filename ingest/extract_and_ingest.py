#!/usr/bin/env python3
"""
DOUTORA IA - EXTRAÇÃO E INGESTÃO DE EBOOKS JURÍDICOS
Processa PDFs, extrai texto, gera embeddings e insere no Qdrant
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import PyPDF2
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# Configuração
EBOOKS_DIR = Path("D:/doutora-ia/direito")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "documentos_juridicos"
EMBEDDING_MODEL = "intfloat/multilingual-e5-large"
CHUNK_SIZE = 500  # caracteres por chunk
CHUNK_OVERLAP = 50  # overlap entre chunks

# Inicializar
encoder = SentenceTransformer(EMBEDDING_MODEL)
qdrant = QdrantClient(url=QDRANT_URL)

# Metadata para rastreamento
METADATA_FILE = Path("D:/doutora-ia/ingest/processed_books.json")


def load_processed_metadata() -> Dict:
    """Carrega metadata de livros já processados"""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed_files": {}, "last_update": None, "total_processed": 0}


def save_processed_metadata(metadata: Dict):
    """Salva metadata de livros processados"""
    metadata["last_update"] = datetime.now().isoformat()
    METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def get_file_hash(file_path: Path) -> str:
    """Gera hash MD5 do arquivo para detectar duplicatas"""
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()


def extract_text_from_pdf(pdf_path: Path) -> Optional[str]:
    """Extrai texto de um PDF"""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)

            # Extrair texto de todas as páginas
            for page_num in range(total_pages):
                try:
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as e:
                    print(f"  ⚠️  Erro na página {page_num + 1}: {str(e)}")
                    continue

            if len(text.strip()) < 100:
                print(f"  ⚠️  Texto muito curto ({len(text)} chars) - PDF pode ser imagem")
                return None

            return text.strip()

    except Exception as e:
        print(f"  ❌ Erro ao processar PDF: {str(e)}")
        return None


def split_into_chunks(text: str, metadata: Dict) -> List[Dict]:
    """Divide texto em chunks com overlap"""
    chunks = []
    text_length = len(text)

    start = 0
    chunk_id = 0

    while start < text_length:
        end = start + CHUNK_SIZE

        # Tentar quebrar em fim de sentença
        if end < text_length:
            # Procurar por ponto final, nova linha ou ponto e vírgula
            for delim in ['. ', '.\n', '; ', ';\n']:
                delim_pos = text.rfind(delim, start, end)
                if delim_pos != -1:
                    end = delim_pos + len(delim)
                    break

        chunk_text = text[start:end].strip()

        if len(chunk_text) > 50:  # Ignorar chunks muito pequenos
            chunks.append({
                "text": chunk_text,
                "chunk_id": chunk_id,
                "start_pos": start,
                "end_pos": end,
                **metadata
            })
            chunk_id += 1

        start = end - CHUNK_OVERLAP

    return chunks


def ensure_collection_exists():
    """Garante que a coleção existe no Qdrant"""
    try:
        collections = qdrant.get_collections().collections
        collection_names = [c.name for c in collections]

        if COLLECTION_NAME not in collection_names:
            print(f"📦 Criando coleção '{COLLECTION_NAME}'...")

            # Gerar um embedding de teste para obter dimensão
            test_embedding = encoder.encode("teste")
            vector_size = len(test_embedding)

            qdrant.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            print(f"✅ Coleção criada! Dimensão dos vetores: {vector_size}")
        else:
            print(f"✅ Coleção '{COLLECTION_NAME}' já existe")

    except Exception as e:
        print(f"❌ Erro ao criar/verificar coleção: {e}")
        raise


def process_pdf(pdf_path: Path, metadata: Dict) -> int:
    """Processa um PDF completo"""
    print(f"\n📖 Processando: {pdf_path.name}")

    # Verificar se já foi processado
    file_hash = get_file_hash(pdf_path)
    if file_hash in metadata["processed_files"]:
        print(f"  ⏭️  Já processado anteriormente")
        return 0

    # Extrair texto
    print(f"  📄 Extraindo texto...")
    text = extract_text_from_pdf(pdf_path)

    if not text:
        print(f"  ❌ Falha na extração de texto")
        return 0

    print(f"  ✅ Extraído: {len(text):,} caracteres")

    # Criar metadata do documento
    doc_metadata = {
        "filename": pdf_path.name,
        "filepath": str(pdf_path),
        "file_hash": file_hash,
        "total_chars": len(text),
        "processed_at": datetime.now().isoformat(),
        "tipo": "livro_juridico"
    }

    # Detectar área do direito pelo nome do arquivo
    filename_lower = pdf_path.name.lower()
    areas = {
        "penal": ["penal", "criminal", "juri", "crime"],
        "civil": ["civil", "responsabilidade"],
        "trabalhista": ["trabalh", "clt", "emprego"],
        "tributario": ["tribut", "fiscal", "imposto"],
        "empresarial": ["empresa", "societar", "comercial"],
        "consumidor": ["consumidor", "cdc"],
        "familia": ["familia", "divorcio", "alimentos"],
        "saude": ["saude", "plano", "medic", "ans"],
        "digital": ["digital", "lgpd", "internet", "dados"],
        "previdenciario": ["previdenc", "inss", "aposentad"],
    }

    for area, keywords in areas.items():
        if any(kw in filename_lower for kw in keywords):
            doc_metadata["area"] = area
            break

    # Dividir em chunks
    print(f"  ✂️  Dividindo em chunks...")
    chunks = split_into_chunks(text, doc_metadata)
    print(f"  ✅ Criados: {len(chunks)} chunks")

    # Gerar embeddings
    print(f"  🧠 Gerando embeddings...")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = encoder.encode(texts, show_progress_bar=True)

    # Preparar pontos para inserção
    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        point = PointStruct(
            id=abs(hash(f"{file_hash}_{i}")) % (10 ** 12),  # ID único
            vector=embedding.tolist(),
            payload=chunk
        )
        points.append(point)

    # Inserir no Qdrant
    print(f"  💾 Inserindo no Qdrant...")
    try:
        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        print(f"  ✅ {len(points)} chunks inseridos!")

        # Salvar metadata
        metadata["processed_files"][file_hash] = {
            "filename": pdf_path.name,
            "chunks": len(chunks),
            "chars": len(text),
            "processed_at": datetime.now().isoformat()
        }
        metadata["total_processed"] += 1
        save_processed_metadata(metadata)

        return len(points)

    except Exception as e:
        print(f"  ❌ Erro ao inserir no Qdrant: {e}")
        return 0


def main():
    """Função principal"""
    print("=" * 80)
    print("🏛️  DOUTORA IA - INGESTÃO DE BIBLIOTECA JURÍDICA")
    print("=" * 80)
    print()

    # Verificar diretório
    if not EBOOKS_DIR.exists():
        print(f"❌ Diretório não encontrado: {EBOOKS_DIR}")
        return

    # Listar PDFs
    pdf_files = list(EBOOKS_DIR.glob("*.pdf"))
    print(f"📚 Encontrados: {len(pdf_files)} arquivos PDF")
    print()

    # Carregar metadata
    metadata = load_processed_metadata()
    already_processed = len(metadata["processed_files"])
    print(f"📊 Já processados anteriormente: {already_processed} livros")
    print()

    # Garantir coleção existe
    ensure_collection_exists()
    print()

    # Processar cada PDF
    total_chunks = 0
    new_processed = 0

    print(f"🚀 Iniciando processamento...")
    print(f"⏱️  Tempo estimado: {len(pdf_files) * 2} minutos")
    print("=" * 80)

    for pdf_path in tqdm(pdf_files, desc="Processando livros"):
        chunks_added = process_pdf(pdf_path, metadata)
        if chunks_added > 0:
            total_chunks += chunks_added
            new_processed += 1

    print()
    print("=" * 80)
    print("✅ PROCESSAMENTO CONCLUÍDO!")
    print("=" * 80)
    print()
    print(f"📊 Estatísticas:")
    print(f"  • Total de livros: {len(pdf_files)}")
    print(f"  • Novos processados: {new_processed}")
    print(f"  • Total processados: {len(metadata['processed_files'])}")
    print(f"  • Chunks inseridos: {total_chunks:,}")
    print()
    print(f"💾 Metadata salvo em: {METADATA_FILE}")
    print()

    # Verificar coleção
    try:
        collection_info = qdrant.get_collection(COLLECTION_NAME)
        print(f"📦 Coleção Qdrant:")
        print(f"  • Nome: {COLLECTION_NAME}")
        print(f"  • Total de vetores: {collection_info.points_count:,}")
        print()
    except Exception as e:
        print(f"⚠️  Não foi possível verificar coleção: {e}")

    print("🎉 Sistema pronto para uso!")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processamento interrompido pelo usuário")
        print("💡 Progresso foi salvo - pode continuar depois executando novamente")
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
