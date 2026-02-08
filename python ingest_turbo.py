import os
import glob
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from tqdm import tqdm
import torch

# --- CONFIGURAÇÕES ---
PASTA_ORIGEM = r"E:\biblioteca_juridica\direito"
PASTA_DB = "vector_db" # Cria o banco dentro de D:\doutora-ia
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MODELO_EMBEDDING = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

def carregar_documentos_rapido():
    print(f"--- 🚀 MODO TURBO ATIVADO ---")
    print(f"Lendo arquivos de: {PASTA_ORIGEM}")
    
    arquivos = glob.glob(os.path.join(PASTA_ORIGEM, "**/*.md"), recursive=True)
    print(f"📄 Encontrados {len(arquivos)} arquivos Markdown.")
    
    docs = []
    erros = 0
    
    # Barra de progresso para leitura
    print("Lendo conteúdo dos arquivos...")
    for caminho in tqdm(arquivos, unit="docs"):
        try:
            with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                texto = f.read()
            
            # Só adiciona se tiver conteúdo
            if len(texto.strip()) > 10:
                # Cria o objeto Documento do LangChain manualmente (muito mais rápido)
                metadados = {"source": os.path.basename(caminho)}
                docs.append(Document(page_content=texto, metadata=metadados))
        except Exception as e:
            erros += 1
            
    print(f"✅ Sucesso: {len(docs)} documentos carregados.")
    if erros > 0:
        print(f"⚠️ Pulos/Erros: {erros} arquivos.")
        
    return docs

def main():
    # 1. Carregar (Rápido)
    documentos = carregar_documentos_rapido()
    
    if not documentos:
        print("❌ Nenhum documento encontrado. Verifique o caminho.")
        return

    # 2. Dividir (Chunking)
    print("\n✂️  Dividindo em pedaços (Chunks)...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documentos)
    print(f"📦 Total de pedaços criados: {len(chunks)}")

    # 3. Criar Banco de Dados (Embeddings)
    print(f"\n🧠 Iniciando Embeddings com GPU...")
    
    # Verifica GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🔌 Hardware detectado: {device.upper()} (Se for CUDA, vai voar!)")
    
    embedding_model = HuggingFaceEmbeddings(
        model_name=MODELO_EMBEDDING,
        model_kwargs={'device': device}
    )

    # Processa em lotes para não estourar memória RAM
    batch_size = 5000 
    total_chunks = len(chunks)
    
    print(f"💾 Salvando no ChromaDB em lotes de {batch_size}...")
    
    for i in range(0, total_chunks, batch_size):
        lote = chunks[i:i + batch_size]
        print(f"   Processando lote {i} a {i+len(lote)} de {total_chunks}...")
        
        if i == 0:
            # Primeiro lote cria/sobrescreve o banco
            vectorstore = Chroma.from_documents(
                documents=lote,
                embedding=embedding_model,
                persist_directory=PASTA_DB
            )
        else:
            # Lotes seguintes apenas adicionam
            vectorstore.add_documents(lote)
            
    print("-" * 50)
    print("🎉 SUCESSO! Banco de dados criado.")
    print(f"Agora rode: python chat_legal.py")

if __name__ == "__main__":
    main()