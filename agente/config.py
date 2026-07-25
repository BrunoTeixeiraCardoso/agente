import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

# Define a pasta raiz do projeto e carrega as variáveis do arquivo .env.
PROJECT_ROOT = Path(__file__).parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# --- NOVA FUNÇÃO MODULAR DE PROMPT ---
def carregar_system_prompt(nome_arquivo: str = "system_prompt.txt") -> str:
    """Carrega as instruções do sistema a partir de um arquivo externo."""
    caminho_prompt = PROJECT_ROOT / nome_arquivo
    if not caminho_prompt.exists():
        # Fallback de segurança caso o arquivo suma
        return "Você é um assistente prestativo."
    
    return caminho_prompt.read_text(encoding="utf-8")


def validar_ambiente() -> None:
    """Garante que as chaves de API necessárias estejam disponíveis."""
    missing = [key for key in ("GOOGLE_API_KEY", "GROQ_API_KEY") if not os.getenv(key)]
    if missing:
        raise RuntimeError(
            "Erro Crítico: Certifique-se de ter as chaves GOOGLE_API_KEY e GROQ_API_KEY no seu .env!"
        )


# def get_default_config() -> dict:
#     """Retorna a configuração padrão compartilhada pelo fluxo."""
#     # Define limites simples de execução para evitar loops excessivos ou respostas longas.
#     return {"recursion_limit": 10, "max_tokens": 6}

def get_default_config() -> dict:
    return {
        "recursion_limit": 10, 
        "max_tokens": 2048 # <--- Mude para um valor real (ex: 2048 tokens)
    }


# Cache das instâncias dos modelos para não criar novas conexões a cada uso.
_cached_llms = None


# def get_llms() -> dict:
#     """Inicializa e reutiliza as instâncias dos modelos de linguagem."""
#     global _cached_llms
#     if _cached_llms is None:
#         # Verifica se as chaves estão presentes antes de criar os clientes das IAs.
#         validar_ambiente()
#         _cached_llms = {
#             "gemini": ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0),
#             "groq": ChatGroq(model="llama-3.3-70b-versatile", temperature=0),
#         }
#     return _cached_llms

def get_llms() -> dict:
    """Inicializa e reutiliza as instâncias dos modelos de linguagem."""
    global _cached_llms
    if _cached_llms is None:
        validar_ambiente()
        _cached_llms = {
            # ADICIONAMOS O PARÂMETRO convert_system_message_to_human=True
            # Isso limpa a comunicação do sistema e força o Gemini a devolver TEXTO PURO.
            "gemini": ChatGoogleGenerativeAI(
                model="gemini-3.5-flash", 
                temperature=0,
                convert_system_message_to_human=True
            ),
            "groq": ChatGroq(model="llama-3.3-70b-versatile", temperature=0),
        }
    return _cached_llms

# 3. CRIAÇÃO DAS VARIÁVEIS GLOBAIS E EXPORTAÇÃO (Sempre no final do arquivo)

# Gera o dicionário de configurações estruturais
CONFIG_PADRAO = get_default_config()

# Lê o arquivo txt e anexa o texto do prompt dentro do dicionário global
CONFIG_PADRAO["system_prompt"] = carregar_system_prompt()

llm_gemini = get_llms()["gemini"]
llm_groq = get_llms()["groq"]

