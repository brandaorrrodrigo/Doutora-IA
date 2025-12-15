#!/usr/bin/env python3
"""
DOUTORA IA - ADICIONAR NOVOS EBOOKS
Script simplificado para processar apenas livros novos
"""

import sys
from pathlib import Path

# Importar do script principal
sys.path.insert(0, str(Path(__file__).parent))
from extract_and_ingest import (
    load_processed_metadata,
    save_processed_metadata,
    get_file_hash,
    process_pdf,
    ensure_collection_exists,
    EBOOKS_DIR,
    COLLECTION_NAME
)

def main():
    """Processa apenas PDFs novos"""
    print("=" * 80)
    print("📚 DOUTORA IA - ADICIONAR NOVOS LIVROS")
    print("=" * 80)
    print()

    # Listar PDFs
    pdf_files = list(EBOOKS_DIR.glob("*.pdf"))
    print(f"📖 Total de PDFs no diretório: {len(pdf_files)}")

    # Carregar metadata
    metadata = load_processed_metadata()
    processed_hashes = set(metadata["processed_files"].keys())
    print(f"✅ Já processados: {len(processed_hashes)} livros")
    print()

    # Identificar novos
    new_files = []
    for pdf_path in pdf_files:
        file_hash = get_file_hash(pdf_path)
        if file_hash not in processed_hashes:
            new_files.append(pdf_path)

    if not new_files:
        print("✨ Nenhum livro novo encontrado!")
        print("📚 Biblioteca está atualizada")
        return

    print(f"🆕 Encontrados {len(new_files)} novos livros:")
    for i, pdf in enumerate(new_files[:10], 1):
        print(f"  {i}. {pdf.name}")
    if len(new_files) > 10:
        print(f"  ... e mais {len(new_files) - 10} livros")
    print()

    # Confirmar
    print(f"⏱️  Tempo estimado: {len(new_files) * 2} minutos")
    input("Pressione ENTER para iniciar ou Ctrl+C para cancelar...")
    print()

    # Garantir coleção existe
    ensure_collection_exists()

    # Processar novos
    total_chunks = 0
    for i, pdf_path in enumerate(new_files, 1):
        print(f"\n[{i}/{len(new_files)}]", end=" ")
        chunks = process_pdf(pdf_path, metadata)
        total_chunks += chunks

    print("\n" + "=" * 80)
    print("✅ NOVOS LIVROS ADICIONADOS!")
    print("=" * 80)
    print(f"  • Processados: {len(new_files)} livros")
    print(f"  • Chunks adicionados: {total_chunks:,}")
    print(f"  • Total na biblioteca: {len(metadata['processed_files'])} livros")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelado pelo usuário")
