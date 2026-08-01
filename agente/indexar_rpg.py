import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# SUBSTUIÇÃO DO IMPORT:
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_chroma import Chroma

PASTA_DOS_LIVROS = "./meus_livros_rpg"
PASTA_DO_BANCO_DADOS = "./banco_vetorial_rpg"

def treinar_sistema_rpg():
    if not os.path.exists(PASTA_DOS_LIVROS):
        os.makedirs(PASTA_DOS_LIVROS, exist_ok=True)
        print(f"📁 Pasta '{PASTA_DOS_LIVROS}' criada automaticamente.")
        return

    print("📖 Passo 1: Carregando e mapeando os livros de RPG da pasta...")
    loader = PyPDFDirectoryLoader(PASTA_DOS_LIVROS)
    documentos_completos = loader.load()
    
    if not documentos_completos:
        print(f"⚠️ Aviso: Nenhum arquivo PDF válido localizado.")
        return
        
    print(f"📄 Total de páginas lidas: {len(documentos_completos)}")

    print("✂️ Passo 2: Fatiando os livros em blocos semânticos menores (chunks)...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    blocos_de_texto = text_splitter.split_documents(documentos_completos)
    
    print(f"🧩 Total de blocos de texto gerados: {len(blocos_de_texto)}")

    print("🧠 Passo 3: Computando vetores numéricos (HuggingFace Local) e gravando no banco ChromaDB...")
    try:
        # [MUDANÇA CRÍTICA]: Carrega o modelo gratuito que roda no seu PC
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2") 
        
        Chroma.from_documents(
            documents=blocos_de_texto, 
            embedding=embeddings, 
            persist_directory=PASTA_DO_BANCO_DADOS
        )
        print("✅ Sucesso! Banco de dados de RPG compilado localmente e pronto para o LangGraph!")
        
    except Exception as error:
        print(f"❌ Ocorreu um erro inesperado: {error}")

if __name__ == "__main__":
    treinar_sistema_rpg()
