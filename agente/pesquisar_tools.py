from langchain_core.tools import tool
from tavily import TavilyClient

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