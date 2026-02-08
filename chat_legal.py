#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Doutora IA - Advanced Legal Document Drafting Assistant
Specialized RAG system for drafting legal procedural documents ("peças jurídicas")
with source categorization: Fundamentação Legal, Doutrina e Teses, Jurisprudência
"""

import os
import sys
from typing import List, Dict, Any, Tuple
import logging
import re

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import RetrievalQA
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_core.documents import Document

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SourceClassifier:
    """Classifies retrieved documents into legal source categories"""

    # Keywords for detection
    KEYWORDS_JURISPRUDENCIA = {
        'jurisprudência', 'acórdão', 'sentença', 'julgado', 'decisão',
        'tribunal', 'stf', 'stj', 'oab', 'súmula', 'precedente',
        'vinculante', 'entendimento jurisprudencial', 'orientação jurisprudencial',
        'decisão do tribunal', 'agravo', 'recurso extraordinário', 'ministro',
        'desembargador', 'juiz', 'julgamento', 'condenado', 'absolvido',
        'caso', 'process', 'ação', 'apelação', 'habeas corpus',
    }

    KEYWORDS_DOUTRINA = {
        'autor', 'book', 'livro', 'manual', 'obra', 'tratado',
        'comentário', 'doutrina', 'conceito', 'definição', 'explicação',
        'professor', 'doutor', 'teoria', 'tese', 'princípio',
        'corrente doutrinária', 'escola', 'pensamento', 'entendimento',
    }

    KEYWORDS_FUNDAMENTACAO = {
        'lei', 'código', 'artigo', 'art.', 'artigos', 'inc',
        'inciso', 'parágrafo', 'caput', 'alínea', 'decreto',
        'resolução', 'portaria', 'instrução normativa', 'constituição',
        'clt', 'cc', 'cpc', 'cpp', 'regulamento', 'norma', 'dispositivo',
    }

    @staticmethod
    def classify_document(doc: Document, content: str) -> str:
        """
        Classify a document into one of three categories.

        Args:
            doc: LangChain Document object
            content: Document content text

        Returns:
            Category: 'jurisprudencia', 'doutrina', 'fundamentacao', or 'misto'
        """
        source = doc.metadata.get('source', '').lower()
        content_lower = content.lower()

        # Count keyword matches
        jurisp_score = sum(1 for kw in SourceClassifier.KEYWORDS_JURISPRUDENCIA
                          if kw in content_lower or kw in source)
        doutrina_score = sum(1 for kw in SourceClassifier.KEYWORDS_DOUTRINA
                            if kw in content_lower or kw in source)
        fund_score = sum(1 for kw in SourceClassifier.KEYWORDS_FUNDAMENTACAO
                        if kw in content_lower or kw in source)

        # Determine category
        scores = {
            'jurisprudencia': jurisp_score,
            'doutrina': doutrina_score,
            'fundamentacao': fund_score,
        }

        max_score = max(scores.values())
        if max_score == 0:
            return 'misto'

        # Return the category with highest score
        category = max(scores, key=scores.get)

        # If scores are very close, classify as mixed
        sorted_scores = sorted(scores.values(), reverse=True)
        if sorted_scores[0] - sorted_scores[1] <= 1:
            return 'misto'

        return category

    @staticmethod
    def get_category_display(category: str) -> str:
        """Get display name for category"""
        mapping = {
            'jurisprudencia': '📜 JURISPRUDÊNCIA RELACIONADA',
            'doutrina': '📚 DOUTRINA E TESES',
            'fundamentacao': '⚖️ FUNDAMENTAÇÃO LEGAL',
            'misto': '📋 FUNDAMENTAÇÃO (MISTA)',
        }
        return mapping.get(category, category)


class LawyerRAGChat:
    """
    Advanced Legal Document Drafting Assistant
    Specialized for drafting legal procedural documents with source categorization
    """

    def __init__(
        self,
        vector_db_dir: str = "vector_db",
        model_name: str = "llama3",
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        top_k: int = 8,
        temperature: float = 0.2
    ):
        """
        Initialize the Legal RAG Chat system.

        Args:
            vector_db_dir: Directory where ChromaDB is stored
            model_name: Ollama model name
            embedding_model: HuggingFace embedding model
            top_k: Number of chunks to retrieve (increased to 8 for legal research)
            temperature: Model temperature (lower for accuracy)
        """
        self.vector_db_dir = vector_db_dir
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.top_k = top_k
        self.temperature = temperature
        self.vectorstore = None
        self.retriever = None
        self.llm = None
        self.memory = None
        self.chain = None
        self.source_classifier = SourceClassifier()

    def initialize(self):
        """Initialize all components."""
        logger.info("\n")
        logger.info("╔" + "="*78 + "╗")
        logger.info("║" + " "*12 + "DOUTORA IA - Advanced Legal Document Assistant" + " "*19 + "║")
        logger.info("╚" + "="*78 + "╝")
        logger.info("\n")

        try:
            # Load embeddings
            logger.info("Loading embedding model...")
            embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model,
                model_kwargs={"device": "cuda"},
                encode_kwargs={"normalize_embeddings": True}
            )
            logger.info("✓ Embedding model loaded\n")

            # Load vector database
            logger.info(f"Loading ChromaDB from: {self.vector_db_dir}")
            self.vectorstore = Chroma(
                persist_directory=self.vector_db_dir,
                embedding_function=embeddings,
                collection_name="legal_documents"
            )
            logger.info("✓ Vector database loaded\n")

            # Create retriever with INCREASED k=8 for better legal research
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": self.top_k}
            )
            logger.info(f"✓ Retriever configured (top-{self.top_k} chunks for comprehensive research)\n")

            # Initialize Ollama LLM with lower temperature for legal accuracy
            logger.info(f"Initializing Ollama with model: {self.model_name}")
            self.llm = Ollama(
                model=self.model_name,
                temperature=self.temperature,
                top_k=40,
                top_p=0.9,
                callbacks=[StreamingStdOutCallbackHandler()]
            )
            logger.info("✓ Ollama LLM initialized\n")

            # Initialize conversation memory
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                input_key="question",
                output_key="answer"
            )
            logger.info("✓ Conversation memory initialized\n")

            # Create RAG chain with sophisticated legal prompt
            self._create_legal_chain()

            logger.info("="*80)
            logger.info("✨ Sistema ready! Type your legal questions to draft documents.\n")

        except Exception as e:
            logger.error(f"✗ Error initializing system: {e}")
            raise

    def _create_legal_chain(self):
        """Create the RAG chain with sophisticated legal prompt in Portuguese"""

        # SOPHISTICATED LAWYER PERSONA PROMPT
        system_prompt = """Você é uma Assistente Jurídica Especializada (Doutora IA), dedicada à elaboração de peças processuais de alta qualidade.

🏛️ SUA MISSÃO:
Fornecer fundamentação jurídica abrangente e bem estruturada, distinguindo claramente entre fontes legais, doutrina e jurisprudência para que o usuário possa draftar documentos jurídicos profissionais.

📋 ESTRUTURA OBRIGATÓRIA DE RESPOSTA:

Organize SEMPRE sua resposta em até 3 categorias, apenas quando encontrar informação no contexto:

1️⃣ **FUNDAMENTAÇÃO LEGAL**
   - Cite ESPECIFICAMENTE artigos, incisos, alíneas, parágrafos
   - Inclua a numeração precisa (Ex: "Art. 123, inciso II, alínea 'a' do Código Civil")
   - Para cada artigo, cite [Fonte: nome_do_arquivo.md]
   - Mantenha a ordem: Lei Maior (Constituição) → Códigos → Leis Especiais

2️⃣ **DOUTRINA E TESES**
   - Explique os conceitos com base nos autores/manuais consultados
   - Cite nomes de autores quando disponíveis
   - Indique correntes doutrinárias quando existirem
   - Sempre: [Fonte: nome_do_autor_ou_manual.md]
   - Use citações que podem ser incluídas diretamente em peças

3️⃣ **JURISPRUDÊNCIA RELACIONADA**
   - Cite ESPECIFICAMENTE acórdãos, súmulas, precedentes vinculantes
   - Indique órgão julgador (STF, STJ, TJ, etc.)
   - Para cada decisão: [Fonte: arquivo_origem.md]
   - Priorize jurisprudência recente e consolidada

⚠️ REGRAS CRÍTICAS:

✓ SEMPRE cite a fonte COMPLETA (filename) para CADA informação usada
✓ Diferencie explicitamente entre Lei, Doutrina e Jurisprudência
✓ Se uma categoria estiver vazia, indique: "❌ Não foi encontrada [categoria] específica nos documentos consultados para este ponto."
✓ Quando houver lacuna, indique claramente: "Este aspecto requer pesquisa complementar além dos documentos disponíveis."
✓ Use Markdown com **negrito** para destacar conceitos chave
✓ Organize em listas numeradas ou com bullets para fácil copy-paste
✓ Mantenha linguagem jurídica rigorosa e formal
✓ Seja conciso mas completo - cada parágrafo deve ser útil em uma peça
✓ Se o usuário pedir algo não jurídico, recuse educadamente

📄 FORMATO FINAL:
Sua resposta deve ser formatada para COPY-PASTE direto em documentos jurídicos.
Use estrutura clara, parágrafos curtos, negrito para destaques, listas para facilitar leitura.

CONTEXTO DOS DOCUMENTOS CONSULTADOS:
{context}

Responda em português (Brasil), com rigor jurídico e estrutura clara para drafting de peças."""

        prompt = ChatPromptTemplate.from_template(system_prompt)

        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            memory=self.memory,
            chain_type_kwargs={
                "prompt": prompt,
                "verbose": False
            }
        )

    def categorize_sources(self, source_documents: List[Document]) -> Dict[str, List[Tuple[str, str]]]:
        """
        Categorize retrieved documents into legal source types.

        Returns:
            Dictionary with categories as keys and list of (filename, content_preview) as values
        """
        categorized = {
            'jurisprudencia': [],
            'doutrina': [],
            'fundamentacao': [],
            'misto': []
        }

        for doc in source_documents:
            category = self.source_classifier.classify_document(doc, doc.page_content)
            source_file = os.path.basename(doc.metadata.get('source', 'Unknown'))
            content_preview = doc.page_content[:100].strip()

            categorized[category].append((source_file, content_preview))

        return categorized

    def format_categorized_sources(self, categorized: Dict[str, List[Tuple[str, str]]]) -> str:
        """Format categorized sources for display."""

        output = "\n" + "="*80 + "\n"
        output += "🔍 ANÁLISE DE FONTES CONSULTADAS\n"
        output += "="*80 + "\n"

        category_order = ['fundamentacao', 'doutrina', 'jurisprudencia', 'misto']

        for category in category_order:
            sources = categorized[category]
            if sources:
                display_name = SourceClassifier.get_category_display(category)
                output += f"\n{display_name}\n"
                output += "─" * 60 + "\n"

                # Deduplicate sources
                unique_sources = {}
                for filename, preview in sources:
                    if filename not in unique_sources:
                        unique_sources[filename] = preview

                for i, (filename, preview) in enumerate(unique_sources.items(), 1):
                    output += f"\n{i}. **{filename}**\n"
                    output += f"   Preview: {preview}...\n"

        output += "\n" + "="*80 + "\n"
        return output

    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the legal RAG system with source categorization.

        Args:
            question: User legal question

        Returns:
            Dictionary with answer, categorized sources, and metadata
        """
        try:
            result = self.chain({"query": question})

            # Categorize the retrieved sources
            source_documents = result.get("source_documents", [])
            categorized = self.categorize_sources(source_documents)

            return {
                "answer": result.get("result", ""),
                "sources": source_documents,
                "categorized_sources": categorized,
                "num_sources": len(source_documents)
            }

        except Exception as e:
            logger.error(f"✗ Error processing query: {e}")
            return {
                "answer": f"Erro ao processar a pergunta: {e}",
                "sources": [],
                "categorized_sources": {},
                "num_sources": 0
            }

    def format_response_for_drafting(self, result: Dict[str, Any]) -> str:
        """Format response optimized for legal document drafting."""

        output = "\n" + "█"*80 + "\n"
        output += "💼 DOUTORA IA - RESPOSTA PARA DRAFTING\n"
        output += "█"*80 + "\n\n"

        # Main answer
        output += "📝 FUNDAMENTAÇÃO:\n"
        output += "─" * 80 + "\n"
        output += result["answer"]
        output += "\n\n"

        # Source categorization
        output += self.format_categorized_sources(result["categorized_sources"])

        # Metadata
        output += "📊 METADADOS:\n"
        output += f"   Fontes consultadas: {result['num_sources']}\n"
        output += f"   Modelo: {self.model_name}\n"
        output += f"   Contexto: {len(result['sources'])} chunks recuperados\n\n"

        return output

    def validate_legal_question(self, question: str) -> Tuple[bool, str]:
        """
        Validate if the question is legal-related.

        Returns:
            Tuple of (is_valid, message)
        """
        non_legal_indicators = [
            'receita', 'culinária', 'receita de bolo', 'como cozinhar',
            'poesia', 'música', 'criar música', 'história não jurídica',
            'ficção', 'romance', 'diversão'
        ]

        question_lower = question.lower()
        for indicator in non_legal_indicators:
            if indicator in question_lower:
                return False, f"⚠️  Pergunta não jurídica detectada. Doutora IA é especializada em direito."

        if len(question) < 10:
            return False, "⚠️  Pergunta muito curta. Fornceça mais contexto ou detalhes."

        return True, ""

    def chat_loop(self):
        """Run the interactive chat loop optimized for legal document drafting."""
        self.initialize()

        print("\n" + "="*80)
        print("👩‍⚖️  DOUTORA IA - ASSISTENTE JURÍDICA PARA DRAFTING DE PEÇAS")
        print("="*80)
        print("\nEspecializada em: Fundamentação Legal | Doutrina | Jurisprudência")
        print("\nFuncionamento:")
        print("  • Digite suas perguntas sobre direito para drafting de peças processuais")
        print("  • Respostas organizadas em: Lei, Doutrina e Jurisprudência")
        print("  • Cada informação é citada com a fonte (filename)")
        print("  • Saídas formatadas para copy-paste em documentos jurídicos")
        print("\nComandos:")
        print("  'sair' / 'quit' / 'exit' - Encerrar")
        print("  'limpar' - Limpar histórico de conversas")
        print("  'config' - Ver configuração do sistema")
        print("="*80 + "\n")

        while True:
            try:
                # Get user input
                user_input = input("\n👤 Sua pergunta jurídica: ").strip()

                if not user_input:
                    print("⚠️  Digite uma pergunta válida.")
                    continue

                # Check for commands
                if user_input.lower() in ['sair', 'quit', 'exit']:
                    print("\n👋 Até logo! Boa sorte com suas peças jurídicas!\n")
                    break

                if user_input.lower() == 'limpar':
                    self.memory.clear()
                    print("✓ Histórico de conversas limpo.\n")
                    continue

                if user_input.lower() == 'config':
                    self._print_config()
                    continue

                # Validate question is legal-related
                is_valid, message = self.validate_legal_question(user_input)
                if not is_valid:
                    print(f"\n{message}\n")
                    continue

                # Process query
                print("\n⏳ Pesquisando jurisprudência, doutrina e legislação...\n")
                result = self.query(user_input)

                # Display formatted response
                print(self.format_response_for_drafting(result))

                # Show conversation memory status
                memory_lines = len(self.memory.buffer_as_str.split('\n')) if hasattr(self.memory, 'buffer_as_str') else 0
                print(f"📌 Contexto de conversa: {memory_lines} linhas no histórico")
                print("   Dica: Use 'limpar' para resetar se as respostas ficarem muito longas\n")

            except KeyboardInterrupt:
                print("\n\n👋 Chat interrompido. Até logo!\n")
                break
            except Exception as e:
                print(f"\n✗ Erro: {e}")
                print("Tente novamente ou digite 'sair' para encerrar.\n")

    def _print_config(self):
        """Print current system configuration."""
        print("\n" + "="*80)
        print("⚙️  CONFIGURAÇÃO DO SISTEMA")
        print("="*80)
        print(f"\n🤖 Modelo LLM: {self.model_name}")
        print(f"📚 Contexto: {self.top_k} chunks recuperados (aumentado para pesquisa jurídica)")
        print(f"🧠 Temperatura: {self.temperature} (baixa para maior precisão)")
        print(f"🔍 Embedding: {self.embedding_model.split('/')[-1]}")
        print(f"📁 Database: {self.vector_db_dir}")
        print(f"💾 Modelo: ChromaDB com {len(self.vectorstore._collection.get()['ids'])} vectors\n")
        print("="*80 + "\n")


def main():
    """Main entry point."""

    # Configuration
    VECTOR_DB_DIR = "vector_db"
    MODEL_NAME = "llama3"  # llama3, mistral, neural-chat
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    TOP_K = 8  # INCREASED from 5 to 8 for comprehensive legal research
    TEMPERATURE = 0.2  # LOWERED from 0.3 to 0.2 for legal accuracy

    # Verify vector DB exists
    if not os.path.exists(VECTOR_DB_DIR):
        logger.error(f"✗ Vector database not found at: {VECTOR_DB_DIR}")
        logger.error("Please run 'python ingest.py' first to create the database.")
        sys.exit(1)

    # Initialize and run chat
    chat = LawyerRAGChat(
        vector_db_dir=VECTOR_DB_DIR,
        model_name=MODEL_NAME,
        embedding_model=EMBEDDING_MODEL,
        top_k=TOP_K,
        temperature=TEMPERATURE
    )

    chat.chat_loop()


if __name__ == "__main__":
    main()
