import os
from typing import List
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from pypdf import PdfReader

# Importações corrigidas e atualizadas para o padrão atual do ecossistema LangChain
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper

# Importação de ferramentas personalizadas do seu ecossistema
from rpg_tools import rolar_dados_rpg
from pesquisar_tools import pesquisar_na_internet
from data_tool import consultar_data_e_hora_atual

# Configurações globais compartilhadas com o arquivo nodes.py
PASTA_DO_BANCO_DADOS = "./banco_vetorial_rpg"


@tool
def indexar_novo_pdf_no_rag(caminho_do_arquivo: str) -> str:
    """
    Registra e indexa um arquivo PDF local na base de conhecimento (RAG) do agente.
    Use esta ferramenta imediatamente quando o usuário fornecer o caminho de um novo documento 
    ou livro de RPG para que o sistema aprenda suas regras antes de responder perguntas sobre ele.
    """
    if not os.path.exists(caminho_do_arquivo):
        return f"Erro: O arquivo no caminho '{caminho_do_arquivo}' não foi encontrado para indexação."

    try:
        print(f"📖 [Ferramenta RAG] Extraindo texto do PDF: {caminho_do_arquivo}")
        reader = PdfReader(caminho_do_arquivo)
        texto_completo = ""

        # Extração limpa página por página
        for i, pagina in enumerate(reader.pages):
            texto_da_pagina = pagina.extract_text()
            if texto_da_pagina:
                texto_completo += f"\n[Página {i+1}]\n" + texto_da_pagina

        if not texto_completo.strip():
            return "Falha: O PDF foi lido, mas não contém texto extraível (pode ser um arquivo de imagens/escaneado)."

        # Fatiamento inteligente em pedaços estruturados para busca semântica
        print("✂️ [Ferramenta RAG] Fatiando conteúdo em blocos semânticos...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.create_documents(
            texts=[texto_completo], 
            metadatas=[{"source": os.path.basename(caminho_do_arquivo)}]
        )

        # Injeção e persistência direta no ChromaDB do projeto
        print(f"🧠 [Ferramenta RAG] Alimentando ChromaDB com {len(chunks)} novos blocos...")
        embeddings = OpenAIEmbeddings()
        banco_vetorial = Chroma(
            persist_directory=PASTA_DO_BANCO_DADOS, 
            embedding_function=embeddings
        )
        banco_vetorial.add_documents(chunks)
        
        return f"Sucesso! O documento '{os.path.basename(caminho_do_arquivo)}' foi fragmentado em {len(chunks)} blocos e totalmente indexado à sua biblioteca de RPG."
        
    except Exception as error:
        return f"Ocorreu um erro crítico ao tentar indexar o documento no RAG: {error}"


def build_tools() -> list:
    """Constrói a lista de ferramentas reutilizável pelo grafo."""
    
    api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000)
    wikipedia_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

    # Adicione a nova ferramenta aqui na lista!
    return [
        wikipedia_tool,
        indexar_novo_pdf_no_rag,
        pesquisar_na_internet,
        rolar_dados_rpg,
        consultar_data_e_hora_atual  # <--- NOVA FERRAMENTA REGISTRADA
    ]

# Exportação direta consumida pelo graph.py
tools = build_tools()
