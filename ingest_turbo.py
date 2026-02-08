import os
import glob
from tqdm import tqdm
import torch
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
# FIXED IMPORT:
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# --- CONFIGURATIONS ---
PASTA_ORIGEM = r"E:\biblioteca_juridica\direito"
PASTA_DB = "vector_db"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MODEL_EMBEDDING = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

def main():
    print("--- TURBO INGESTION (FIXED) ---")

    # 1. Fast File Reading
    files = glob.glob(os.path.join(PASTA_ORIGEM, "**/*.md"), recursive=True)
    print(f"Found {len(files)} Markdown files.")

    docs = []
    print("Reading files...")
    for path in tqdm(files):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
                if len(text.strip()) > 10:
                    docs.append(Document(page_content=text, metadata={"source": os.path.basename(path)}))
        except:
            pass

    if not docs:
        print("ERROR: No documents found.")
        return

    # 2. Split
    print(f"\nSplitting {len(docs)} documents...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_documents(docs)
    print(f"Created {len(chunks)} chunks.")

    # 3. Embed & Save (GPU Enforced)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\nHardware Mode: {device.upper()}")

    embedding = HuggingFaceEmbeddings(model_name=MODEL_EMBEDDING, model_kwargs={'device': device})

    batch_size = 5000
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"   Saving batch {i} to {i + len(batch)}...")
        if i == 0:
            Chroma.from_documents(batch, embedding, persist_directory=PASTA_DB)
        else:
            db = Chroma(persist_directory=PASTA_DB, embedding_function=embedding)
            db.add_documents(batch)

    print("\nDONE! Database created in 'vector_db'.")

if __name__ == "__main__":
    main()
