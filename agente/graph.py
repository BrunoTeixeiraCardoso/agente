# graph.py
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from tools import tools
import nodes  # IMPORTAÇÃO CRUCIAL: Traz todas as funções limpas do nodes.py

# 1. DEFINIÇÃO DO ESTADO CENTRAL (Mantido idêntico para o app.py ler)
class State(TypedDict):
    messages: Annotated[list, add_messages]
    proxima_ia: str  # Armazena se a tarefa vai para "gemini" ou "groq"

# =====================================================================
# SELEÇÃO CONDICIONAL DE CAMINHOS (Lógica de Fluxo)
# =====================================================================
def decidir_caminho(state: State) -> Literal["no_gemini", "no_groq"]:
    """Lê o Estado do grafo e joga o fluxo na seta correta."""
    if state["proxima_ia"] == "groq":
        return "no_groq"
    return "no_gemini"

# =====================================================================
# CONSTRUÇÃO E ORQUESTRAÇÃO DO GRAFO
# =====================================================================
workflow = StateGraph(State)

# ADICIONANDO OS NÓS REFERENCIANDO O ARQUIVO NODES.PY
workflow.add_node("roteador", nodes.roteador_inicial_node)
workflow.add_node("no_gemini", nodes.no_gemini)
workflow.add_node("no_groq", nodes.no_groq)
workflow.add_node("tools", ToolNode(tools))

# Criação das conexões e estradas inteligentes
workflow.add_edge(START, "roteador")
workflow.add_conditional_edges("roteador", decidir_caminho)

# Configuração de loops de ferramentas para o nó do Gemini
workflow.add_conditional_edges("no_gemini", tools_condition, {"tools": "tools", "__end__": "__end__"})
workflow.add_edge("tools", "no_gemini")

# A Groq encerra o fluxo diretamente sem passar por buscas
workflow.add_edge("no_groq", "__end__")

# Compila o agente pronto para reuso na interface do Streamlit
agente_app = workflow.compile()

# =====================================================================
# CONFIGURAÇÕES E EXTRAÇÕES EXPORTADAS PARA O APP.PY
# =====================================================================
CONFIG_PADRAO = {
    "recursion_limit": 10,
    "max_tokens": 6,
}

def extrair_resposta_do_evento(chunk) -> dict:
    """Varre os dados brutos e extrai os tokens e o texto de qualquer uma das duas IAs."""
    dados_resposta = {"texto": "", "tokens_input": 0, "tokens_output": 0}
    
    # Descobre qual dos dois nós do arquivo externo respondeu neste ciclo
    no_ativo = "no_gemini" if "no_gemini" in chunk else "no_groq" if "no_groq" in chunk else None
    
    if no_ativo:
        mensagens_do_no = chunk[no_ativo]["messages"]
        if mensagens_do_no:
            mensagem_ia = mensagens_do_no[-1]
            dados_resposta["texto"] = mensagem_ia.content
            
            # Captura os metadados de consumo enviados pela IA ativa
            metadata = getattr(mensagem_ia, "response_metadata", {})
            token_usage = metadata.get("token_usage", {})
            
            if token_usage:
                dados_resposta["tokens_input"] = token_usage.get("prompt_tokens", 0)
                dados_resposta["tokens_output"] = token_usage.get("completion_tokens", 0)
                
    return dados_resposta
