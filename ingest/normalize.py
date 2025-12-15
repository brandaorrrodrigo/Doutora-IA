"""
Normalize legal documents to JSON format for RAG ingestion
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import hashlib


def generate_id(text: str, prefix: str = "") -> str:
    """Generate unique ID from text"""
    hash_obj = hashlib.md5(text.encode())
    return f"{prefix}_{hash_obj.hexdigest()[:12]}"


def chunk_text(text: str, max_length: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split text into chunks with overlap

    Args:
        text: Text to chunk
        max_length: Maximum characters per chunk
        overlap: Overlap between chunks

    Returns:
        List of text chunks
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + max_length

        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence ending
            sentence_end = max(
                text.rfind(". ", start, end),
                text.rfind(".\n", start, end),
                text.rfind("? ", start, end),
                text.rfind("! ", start, end)
            )

            if sentence_end > start:
                end = sentence_end + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def normalize_lei(data: Dict) -> List[Dict]:
    """
    Normalize law document to JSON schema

    Args:
        data: Raw law data with fields: titulo, texto, artigo, data, vigencia_inicio, vigencia_fim

    Returns:
        List of normalized chunks
    """
    chunks = []

    # Split by article if available
    texto = data.get("texto", "")
    artigo = data.get("artigo", "")

    # If specific article, create single chunk
    if artigo:
        chunk_id = generate_id(f"{data.get('titulo', '')}_{artigo}", "lei")

        chunk = {
            "id": chunk_id,
            "tipo": "lei",
            "area": data.get("area", ""),
            "orgao": data.get("orgao", "Congresso Nacional"),
            "titulo": data.get("titulo", ""),
            "artigo_ou_tema": artigo,
            "data": data.get("data", ""),
            "vigencia_inicio": data.get("vigencia_inicio", ""),
            "vigencia_fim": data.get("vigencia_fim"),
            "hierarquia": 1.0,
            "texto": texto,
            "fonte_url": data.get("fonte_url", ""),
            "tribunal": None,
            "classe": None,
            "numero": None
        }

        chunks.append(chunk)

    else:
        # Chunk the full text
        text_chunks = chunk_text(texto, max_length=1200)

        for i, chunk_text in enumerate(text_chunks):
            chunk_id = generate_id(f"{data.get('titulo', '')}_{i}", "lei")

            chunk = {
                "id": chunk_id,
                "tipo": "lei",
                "area": data.get("area", ""),
                "orgao": data.get("orgao", "Congresso Nacional"),
                "titulo": f"{data.get('titulo', '')} - Parte {i+1}",
                "artigo_ou_tema": None,
                "data": data.get("data", ""),
                "vigencia_inicio": data.get("vigencia_inicio", ""),
                "vigencia_fim": data.get("vigencia_fim"),
                "hierarquia": 1.0,
                "texto": chunk_text,
                "fonte_url": data.get("fonte_url", ""),
                "tribunal": None,
                "classe": None,
                "numero": None
            }

            chunks.append(chunk)

    return chunks


def normalize_sumula(data: Dict) -> Dict:
    """Normalize súmula to JSON schema"""
    chunk_id = generate_id(f"{data.get('titulo', '')}", "sumula")

    return {
        "id": chunk_id,
        "tipo": "sumula",
        "area": data.get("area", ""),
        "orgao": None,
        "titulo": data.get("titulo", ""),
        "artigo_ou_tema": data.get("tema", ""),
        "data": data.get("data", ""),
        "vigencia_inicio": data.get("data", ""),
        "vigencia_fim": None,
        "hierarquia": 0.95,
        "texto": data.get("texto", ""),
        "fonte_url": data.get("fonte_url", ""),
        "tribunal": data.get("tribunal", ""),
        "classe": None,
        "numero": data.get("numero", "")
    }


def normalize_jurisprudencia(data: Dict) -> List[Dict]:
    """Normalize jurisprudence to JSON schema"""
    chunks = []

    # Main chunk with ementa
    chunk_id = generate_id(f"{data.get('numero', '')}", "juris")

    main_chunk = {
        "id": chunk_id,
        "tipo": "juris",
        "area": data.get("area", ""),
        "orgao": None,
        "titulo": f"{data.get('tribunal', '')} - {data.get('classe', '')} {data.get('numero', '')}",
        "artigo_ou_tema": data.get("tema", ""),
        "data": data.get("data", ""),
        "vigencia_inicio": None,
        "vigencia_fim": None,
        "hierarquia": 0.85 if data.get("leading_case") else 0.75,
        "texto": data.get("ementa", ""),
        "fonte_url": data.get("fonte_url", ""),
        "tribunal": data.get("tribunal", ""),
        "classe": data.get("classe", ""),
        "numero": data.get("numero", "")
    }

    chunks.append(main_chunk)

    # If there's a full text, chunk it
    if data.get("texto_completo"):
        text_chunks = chunk_text(data["texto_completo"], max_length=1000)

        for i, chunk_text in enumerate(text_chunks):
            chunk_id = generate_id(f"{data.get('numero', '')}_{i}", "juris")

            chunk = {
                "id": chunk_id,
                "tipo": "juris",
                "area": data.get("area", ""),
                "orgao": None,
                "titulo": f"{data.get('tribunal', '')} - {data.get('classe', '')} {data.get('numero', '')} - Trecho {i+1}",
                "artigo_ou_tema": data.get("tema", ""),
                "data": data.get("data", ""),
                "vigencia_inicio": None,
                "vigencia_fim": None,
                "hierarquia": 0.80 if data.get("leading_case") else 0.70,
                "texto": chunk_text,
                "fonte_url": data.get("fonte_url", ""),
                "tribunal": data.get("tribunal", ""),
                "classe": data.get("classe", ""),
                "numero": data.get("numero", "")
            }

            chunks.append(chunk)

    return chunks


def normalize_regulatorio(data: Dict) -> List[Dict]:
    """Normalize regulatory document to JSON schema"""
    chunks = []

    texto = data.get("texto", "")
    text_chunks = chunk_text(texto, max_length=1000)

    for i, chunk_text in enumerate(text_chunks):
        chunk_id = generate_id(f"{data.get('titulo', '')}_{i}", "reg")

        chunk = {
            "id": chunk_id,
            "tipo": "regulatorio",
            "area": data.get("area", ""),
            "orgao": data.get("orgao", ""),
            "titulo": f"{data.get('titulo', '')} - Parte {i+1}" if len(text_chunks) > 1 else data.get('titulo', ''),
            "artigo_ou_tema": data.get("tema", ""),
            "data": data.get("data", ""),
            "vigencia_inicio": data.get("vigencia_inicio", data.get("data", "")),
            "vigencia_fim": data.get("vigencia_fim"),
            "hierarquia": 0.70,
            "texto": chunk_text,
            "fonte_url": data.get("fonte_url", ""),
            "tribunal": None,
            "classe": None,
            "numero": data.get("numero", "")
        }

        chunks.append(chunk)

    return chunks


def normalize_doutrina(data: Dict) -> List[Dict]:
    """Normalize doctrine to JSON schema"""
    chunks = []

    texto = data.get("texto", "")
    text_chunks = chunk_text(texto, max_length=800)

    for i, chunk_text in enumerate(text_chunks):
        chunk_id = generate_id(f"{data.get('titulo', '')}_{i}", "dout")

        chunk = {
            "id": chunk_id,
            "tipo": "doutrina",
            "area": data.get("area", ""),
            "orgao": None,
            "titulo": f"{data.get('titulo', '')} - {data.get('autor', '')}",
            "artigo_ou_tema": data.get("tema", ""),
            "data": data.get("data", ""),
            "vigencia_inicio": None,
            "vigencia_fim": None,
            "hierarquia": 0.60,
            "texto": chunk_text,
            "fonte_url": data.get("fonte_url", ""),
            "tribunal": None,
            "classe": None,
            "numero": None
        }

        chunks.append(chunk)

    return chunks


def normalize_document(data: Dict, tipo: str) -> List[Dict]:
    """
    Normalize any document type

    Args:
        data: Raw document data
        tipo: Document type (lei, sumula, juris, regulatorio, doutrina)

    Returns:
        List of normalized chunks
    """
    if tipo == "lei":
        return normalize_lei(data)
    elif tipo == "sumula":
        return [normalize_sumula(data)]
    elif tipo == "juris":
        return normalize_jurisprudencia(data)
    elif tipo == "regulatorio":
        return normalize_regulatorio(data)
    elif tipo == "doutrina":
        return normalize_doutrina(data)
    else:
        raise ValueError(f"Unknown document type: {tipo}")


if __name__ == "__main__":
    # Example usage
    example_lei = {
        "titulo": "Código de Processo Civil - Art. 300",
        "artigo": "Art. 300",
        "texto": "A tutela de urgência será concedida quando houver elementos que evidenciem a probabilidade do direito e o perigo de dano ou o risco ao resultado útil do processo.",
        "area": "familia",
        "orgao": "Congresso Nacional",
        "data": "2015-03-16",
        "vigencia_inicio": "2016-03-18",
        "vigencia_fim": None,
        "fonte_url": "http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm"
    }

    normalized = normalize_lei(example_lei)
    print(json.dumps(normalized, indent=2, ensure_ascii=False))
