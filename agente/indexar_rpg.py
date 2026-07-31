import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# 1. Definição das pastas de trabalho locais
PASTA_DOS_LIVROS = "./meus_livros_rpg"
PASTA_DO_BANCO_DADOS = "./banco_vetorial_rpg"

def treinar_sistema_rpg():
    # [PROTEÇÃO]: Verifica a presença da chave OpenAI antes de gastar processamento lendo os PDFs
    if "OPENAI_API_KEY" not in os.environ or not os.environ["OPENAI_API_KEY"].strip():
        print("❌ Erro Crítico: A variável de ambiente 'OPENAI_API_KEY' não foi localizada.")
        print("Configure-a no seu terminal antes de executar o script novamente.")
        return

    # Garante que a pasta de origem contendo os livros realmente existe no disco
    if not os.path.exists(PASTA_DOS_LIVROS):
        os.makedirs(PASTA_DOS_LIVROS, exist_ok=True)
        print(f"📁 Pasta '{PASTA_DOS_LIVROS}' criada automaticamente. Insira seus PDFs de RPG dentro dela e execute novamente.")
        return

    print("📖 Passo 1: Carregando e mapeando os livros de RPG da pasta...")
    loader = PyPDFDirectoryLoader(PASTA_DOS_LIVROS)
    documentos_completos = loader.load()
    
    if not documentos_completos:
        print(f"⚠️ Aviso: Nenhum arquivo PDF válido foi localizado dentro de '{PASTA_DOS_LIVROS}'.")
        return
        
    print(f"📄 Total de páginas lidas: {len(documentos_completos)}")

    print("✂️ Passo 2: Fatiando os livros em blocos semânticos menores (chunks)...")
    # Divisão em blocos de 1000 caracteres com sobreposição de 200 para manter o contexto entre as quebras
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    blocos_de_texto = text_splitter.split_documents(documentos_completos)
    
    print(f"🧩 Total de blocos de texto gerados: {len(blocos_de_texto)}")

    print("🧠 Passo 3: Computando vetores numéricos (Embeddings) e gravando no banco ChromaDB...")
    try:
        embeddings = OpenAIEmbeddings() 
        
        # Cria e persiste automaticamente o banco de dados Chroma local na pasta configurada
        Chroma.from_documents(
            documents=blocos_de_texto, 
            embedding=embeddings, 
            persist_directory=PASTA_DO_BANCO_DADOS
        )
        print("✅ Sucesso! Banco de dados de RPG compilado com sucesso e pronto para o LangGraph!")
        
    except Exception as error:
        print(f"❌ Ocorreu um erro inesperado durante a geração dos embeddings: {error}")

if __name__ == "__main__":
    treinar_sistema_rpg()
