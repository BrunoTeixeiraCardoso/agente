# helpers_grafo.py
import os
from langchain_core.messages import trim_messages
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from config import get_llms, CONFIG_PADRAO
from tools import tools as default_tools

def criar_trimmador(max_tokens: int, modelo_contador):
    """Centraliza a política de trimming de mensagens para reduzir tokens."""
    return trim_messages(
        max_tokens=max_tokens,
        strategy="last",
        token_counter=modelo_contador,
        include_system=False,
        start_on="human",
    )

def inicializar_dependencias_grafo(llm_gemini=None, llm_groq=None, ferramentas=None, trimmador=None):
    """Inicializa, vincula ferramentas e prepara o banco vetorial de forma isolada."""
    # 1. Carrega instâncias básicas de LLMs e Ferramentas
    llm_gemini = llm_gemini or get_llms()["gemini"]
    llm_groq = llm_groq or get_llms()["groq"]
    ferramentas = ferramentas or default_tools
    
    # 2. Configura e monta o trimmador de histórico
    limite_tokens = CONFIG_PADRAO.get("max_tokens", 2048)
    trimmador = trimmador or criar_trimmador(max_tokens=limite_tokens, modelo_contador=llm_groq)

    # 3. Associa as ferramentas aos modelos
    llm_gemini_com_tools = llm_gemini.bind_tools(ferramentas)
    llm_groq_com_tools = llm_groq.bind_tools(ferramentas)

    # 4. Inicializa o banco de dados vetorial local (RAG)
    PASTA_DO_BANCO_DADOS = "./banco_vetorial_rpg"
    banco_vetorial = None
    
    if os.path.exists(PASTA_DO_BANCO_DADOS):
        try:
            embeddings = OpenAIEmbeddings()
            banco_vetorial = Chroma(
                persist_directory=PASTA_DO_BANCO_DADOS, 
                embedding_function=embeddings
            )
        except Exception as e:
            print(f"⚠️ [RAG] Falha ao pré-carregar o ChromaDB: {e}")

    # Retorna tudo estruturado para o nó consumir
    return {
        "gemini_tools": llm_gemini_com_tools,
        "groq_tools": llm_groq_com_tools,
        "groq_puro": llm_groq,
        "trimmador": trimmador,
        "banco_vetorial": banco_vetorial
    }
