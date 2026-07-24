from langchain_tavily import TavilySearch
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from pypdf import PdfReader
from langchain_core.tools import tool # Importa o decorador de ferramentas


# 1. CRIANDO UMA FERRAMENTA CUSTOMIZADA DO ZERO COM @TOOL
# A "docstring" (o texto entre aspas triplas) é lida pela IA para saber o que a ferramenta faz!
@tool
def ler_conteudo_pdf_local(caminho_do_arquivo: str) -> str:
    """
    Útil para ler e extrair o conteúdo de texto de um arquivo PDF local. 
    Sempre use esta ferramenta quando o usuário perguntar sobre o conteúdo, resumos 
    ou informações contidas em um arquivo PDF que foi enviado para a pasta temporária.
    Recebe o caminho completo do arquivo string e retorna o texto extraído.
    """
    if not os.path.exists(caminho_do_arquivo):
        return f"Erro: O arquivo no caminho '{caminho_do_arquivo}' não foi encontrado."
    
    try:
        reader = PdfReader(caminho_do_arquivo)
        texto_completo = ""
        # Varre todas as páginas do PDF e extrai o texto bruto
        for pagina in reader.pages:
            texto_da_pagina = pagina.extract_text()
            if texto_da_pagina:
                texto_completo += texto_da_pagina + "\n"
                
        if not texto_completo.strip():
            return "O PDF foi lido, mas parece estar em branco ou contém apenas imagens (sem texto extraível)."
            
        # Retorna os primeiros 4000 caracteres para não estourar os tokens por segurança
        return texto_completo[:4000]
        
    except Exception as e:
        return f"Ocorreu um erro ao tentar ler o arquivo PDF: {e}"

# # Inicializa a busca na web
# Reduzimos max_results para 1 e focamos em respostas diretas e curtas
search_tool = TavilySearch(
    max_results=1, 
    search_depth="advanced",
    include_answer=True # Se o Tavily já achar a resposta direta, ele envia apenas ela resumida
)

# 2. Inicializa o motor da Wikipédia configurado para trazer respostas em português
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000)
wikipedia_tool = WikipediaQueryRun(api_wrapper=api_wrapper)


# 3. EXPÕE AS DUAS FERRAMENTAS NA LISTA CENTRAL
# O LangGraph e o Gemini/Groq vão ler essa lista automaticamente!
tools = [search_tool, wikipedia_tool, ler_conteudo_pdf_local] # Adiciona a ferramenta customizada à lista de ferramentas

