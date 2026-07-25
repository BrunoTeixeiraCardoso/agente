import os

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import tool
#from langchain_tavily import TavilySearch
from pypdf import PdfReader
from tavily import TavilyClient


# Ferramenta personalizada que permite ao agente ler o conteúdo de um PDF local.
@tool
def ler_conteudo_pdf_local(caminho_do_arquivo: str) -> str:
    """
    Lê e extrai texto de um PDF local.
    Use esta ferramenta quando o usuário pedir informações contidas em um arquivo PDF enviado.
    """
    if not os.path.exists(caminho_do_arquivo):
        return f"Erro: O arquivo no caminho '{caminho_do_arquivo}' não foi encontrado."

    try:
        reader = PdfReader(caminho_do_arquivo)
        texto_completo = ""

        for pagina in reader.pages:
            texto_da_pagina = pagina.extract_text()
            if texto_da_pagina:
                texto_completo += texto_da_pagina + "\n"

        if not texto_completo.strip():
            return "O PDF foi lido, mas parece estar em branco ou contém apenas imagens (sem texto extraível)."

        return texto_completo[:4000]
    except Exception as error:
        return f"Ocorreu um erro ao tentar ler o arquivo PDF: {error}"

@tool
def pesquisar_na_internet(query: str) -> str:
    """Pesquisa na internet em tempo real por notícias, eventos e fatos atualizados."""
    try:
        # Garante que pegamos a chave do arquivo .env
        chave = os.getenv("TAVILY_API_KEY")
        if not chave:
            return "Erro: Chave TAVILY_API_KEY não encontrada no ambiente."
            
        client = TavilyClient(api_key=chave)
        resposta = client.search(query=query)
        
        # Extrai os resultados textuais de forma limpa
        resultados = resposta.get("results", [])
        if not resultados:
            return f"Nenhum resultado encontrado na internet para a busca: '{query}'."
            
        # Junta os títulos e conteúdos encontrados em uma string contínua
        texto_final = ""
        for res in resultados:
            texto_final += f"Título: {res.get('title')}\nConteúdo: {res.get('content')}\n\n"
            
        return texto_final.strip()
        
    except Exception as e:
        # Se der qualquer erro na API, retorna o erro como texto para o Gemini não quebrar
        return f"Falha ao pesquisar na internet: {str(e)}"



def build_tools() -> list:
    """Constrói a lista de ferramentas reutilizável pelo grafo."""
    # # Busca na web para responder perguntas atuais ou externas.
    # search_tool = TavilySearch(max_results=1,search_depth="advanced",include_answer=True)

    # Busca em artigos da Wikipédia, útil para conhecimento geral.
    api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000)
    wikipedia_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

    # Junta todas as ferramentas disponíveis para o agente usar quando necessário.
    return [ wikipedia_tool, ler_conteudo_pdf_local, pesquisar_na_internet]


tools = build_tools()

