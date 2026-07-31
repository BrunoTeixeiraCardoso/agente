import os

# Imports compatíveis com pacotes oficiais do LangChain
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma


# 1. Defina a pasta onde estão seus PDFs de RPG no computador
PASTA_DOS_LIVROS = "./meus_livros_rpg"
PASTA_DO_BANCO_DADOS = "./banco_vetorial_rpg"

def treinar_sistema_rpg():
    print("📖 Carregando os livros de RPG da pasta...")
    # Carrega todos os PDFs que estiverem na pasta configurada
    loader = PyPDFDirectoryLoader(PASTA_DOS_LIVROS)
    documentos_completos = loader.load()
    
    print(f"📄 Total de páginas lidas: {len(documentos_completos)}")

    print("✂️ Cortando os livros em blocos menores (chunks)...")
    # Como livros de RPG são enormes, dividimos o texto em pedaços de 1000 caracteres
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    blocos_de_texto = text_splitter.split_documents(documentos_completos)
    
    print(f"🧩 Total de blocos gerados para o banco: {len(blocos_de_texto)}")

    print("🧠 Convertendo textos em vetores (Embeddings) e salvando no PC...")
    # Cria o banco de dados Chroma local com base nos seus PDFs
    # Nota: Certifique-se de ter a sua OPENAI_API_KEY configurada nas variáveis de ambiente
    embeddings = OpenAIEmbeddings() 
    Chroma.from_documents(
        documents=blocos_de_texto, 
        embedding=embeddings, 
        persist_directory=PASTA_DO_BANCO_DADOS
    )
    print("✅ Banco de dados de RPG criado com sucesso e pronto para uso!")

if __name__ == "__main__":
    treinar_sistema_rpg()
