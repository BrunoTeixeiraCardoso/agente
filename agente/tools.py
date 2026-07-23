# Declaração de todas as ferramentas (skills)

from langchain_tavily import TavilySearch

# # Inicializa a busca na web
# search_tool = TavilySearch(max_results=2)

# # Lista central de ferramentas exportada para o grafo
# tools = [search_tool]


# Reduzimos max_results para 1 e focamos em respostas diretas e curtas
search_tool = TavilySearch(
    max_results=1, 
    search_depth="advanced",
    include_answer=True # Se o Tavily já achar a resposta direta, ele envia apenas ela resumida
)

tools = [search_tool]