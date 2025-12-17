"""
Backend FastAPI - Doutora IA
"""
import os
import re
from typing import Optional, List
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

from prompts import PROMPT_CLIENTE_TRIAGE, PROMPT_CHAT_RAPIDO
from rag_mock import match_sources

# Config
PORT = int(os.getenv("PORT", "8080"))
API_KEY = os.getenv("API_KEY", "CHANGE_ME")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
LLM_MODEL_CHAT = os.getenv("LLM_MODEL_CHAT", "llama3.1:8b-instruct")
LLM_MODEL_TRIAGE = os.getenv("LLM_MODEL_TRIAGE", "llama3.1:8b-instruct")

app = FastAPI(title="Doutora IA API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.doutoraia.com",
        "https://app.doutoraia.com",
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class RAGSource(BaseModel):
    id: str
    tipo: str
    titulo: str
    url: str
    trecho: str

class TriageRequest(BaseModel):
    role: str = "cliente"
    assunto: str
    descricao: str
    cidade: str
    uf: str
    renda: str
    objetivo: str
    contato: dict
    consentimento: bool
    rag_sources: Optional[List[RAGSource]] = None

class ChatRequest(BaseModel):
    role: str
    query: str
    sessionId: Optional[str] = None
    rag_sources: Optional[List[RAGSource]] = None

# Security
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Utils
def sanitize_pii(text: str) -> str:
    """Remove CPF, telefones básicos"""
    text = re.sub(r'\d{3}\.\d{3}\.\d{3}-\d{2}', '[CPF]', text)
    text = re.sub(r'\(\d{2}\)\s?\d{4,5}-\d{4}', '[TEL]', text)
    return text

def call_ollama(system: str, user: str, model: str):
    """Chama Ollama"""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                "options": {"temperature": 0.2},
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "Sem resposta")
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Ollama timeout")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ollama error: {str(e)}")

# Routes
@app.get("/")
def read_root():
    return {"message": "Doutora IA API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/v1/triage", dependencies=[Depends(verify_api_key)])
def triage(req: TriageRequest):
    """Triagem do cliente"""
    # Sanitizar
    desc_clean = sanitize_pii(req.descricao)

    # RAG
    sources = req.rag_sources or []
    if not sources:
        sources = match_sources(desc_clean, req.assunto)

    if not sources:
        return {
            "error": "Não foram localizadas fontes adequadas no RAG para análise detalhada.",
            "ctas": [
                {"label": "Falar com advogado", "href": "/advogados"}
            ]
        }

    # Montar contexto
    context = f"""
ASSUNTO: {req.assunto}
DESCRIÇÃO: {desc_clean}
CIDADE/UF: {req.cidade}/{req.uf}
RENDA: {req.renda}
OBJETIVO: {req.objetivo}

FONTES RAG:
"""
    for s in sources:
        context += f"- [{s.get('tipo')}] {s.get('titulo')} ({s.get('url')}): {s.get('trecho')}\n"

    # LLM
    response_text = call_ollama(PROMPT_CLIENTE_TRIAGE, context, LLM_MODEL_TRIAGE)

    # Parse (simplificado - em produção usar parse robusto)
    return {
        "rawResponse": response_text,
        "tipificacaoProvavel": "Extrair do response",
        "fundamentosChave": [{"fonte": s['titulo'], "link": s['url']} for s in sources],
        "chancesAproximadas": {"favoravel": 0.6, "neutra": 0.25, "desfavoravel": 0.15},
        "faixaCustos": "Análise em desenvolvimento",
        "carimbo": "Base normativa atualizada em 17/12/2025"
    }

@app.post("/v1/chat", dependencies=[Depends(verify_api_key)])
def chat(req: ChatRequest):
    """Chat rápido"""
    # Sanitizar
    query_clean = sanitize_pii(req.query)

    # RAG
    sources = req.rag_sources or []
    if not sources:
        sources = match_sources(query_clean)

    if not sources:
        return {
            "messages": [{
                "role": "assistant",
                "text": "Não localizei fonte adequada no RAG para esta consulta. Sugiro:\n- Abrir pesquisa avançada em /advogados\n- Fazer triagem completa em /cliente"
            }],
            "sources": [],
            "suggestedCtas": [
                {"label": "Fazer triagem", "href": "/cliente"},
                {"label": "Pesquisa avançada", "href": "/advogados#pesquisa"}
            ]
        }

    # Contexto
    context = f"PERGUNTA ({req.role}): {query_clean}\n\nFONTES RAG:\n"
    for s in sources:
        context += f"- [{s.get('tipo')}] {s.get('titulo')} ({s.get('url')}): {s.get('trecho')}\n"

    # LLM
    response_text = call_ollama(PROMPT_CHAT_RAPIDO, context, LLM_MODEL_CHAT)

    return {
        "messages": [{"role": "assistant", "text": response_text}],
        "sources": [
            {"title": s['titulo'], "url": s['url'], "type": s['tipo']}
            for s in sources
        ],
        "suggestedCtas": [
            {"label": "Gerar relatório", "href": "/cliente"},
            {"label": "Pesquisa avançada", "href": "/advogados"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
