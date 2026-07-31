import config
from typing import Annotated, Literal, TypedDict # Otimizado: TypedDict nativo

from langgraph.graph import START, END, StateGraph # Corrigido: Importando o END oficial
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

import nodes
from tools import tools

# Estrutura do estado do grafo: guarda o histórico e a decisão de qual modelo usar.
class State(TypedDict):
    messages: Annotated[list, add_messages]
    proxima_ia: str
    contexto_documentos: str

def decidir_caminho(state: State) -> Literal["no_rag_gemini", "no_groq"]:
    """Seleciona o próximo nó. Se for Gemini, passa primeiro pelo RAG."""
    return "no_groq" if state["proxima_ia"] == "groq" else "no_rag_gemini"

def construir_workflow():
    workflow = StateGraph(State)

    # 1. Cadastra todos os nós (incluindo o novo nó de RAG)
    workflow.add_node("roteador", nodes.roteador_inicial_node)
    workflow.add_node("no_rag_gemini", nodes.no_recuperar_dados_rag)
    workflow.add_node("no_gemini", nodes.no_gemini)
    workflow.add_node("no_groq", nodes.no_groq)
    workflow.add_node("tools", ToolNode(tools))

    # 2. O fluxo começa no roteador
    workflow.add_edge(START, "roteador")
    
    # 3. O roteador decide o caminho usando a nova regra do decidir_caminho
    workflow.add_conditional_edges("roteador", decidir_caminho)
    
    # 4. Depois que o RAG acha os documentos, ele passa o bastão para o Gemini
    workflow.add_edge("no_rag_gemini", "no_gemini")

    # 5. O Gemini mantém a lógica original de usar ferramentas se precisar
    # Corrigido: Usando a constante END em vez da string "__end__"
    workflow.add_conditional_edges("no_gemini", tools_condition, {"tools": "tools", END: END})
    workflow.add_edge("tools", "no_gemini")
    workflow.add_edge("no_groq", END)

    return workflow


def criar_agente_app():
    """Compila o workflow para uso na interface."""
    return construir_workflow().compile()


agente_app = criar_agente_app()
CONFIG_PADRAO = config.get_default_config()


def extrair_resposta_do_evento(chunk) -> dict:
    """Extrai texto e métricas de tokens de forma robusta e multiplataforma."""
    dados_resposta = {"texto": "", "tokens_input": 0, "tokens_output": 0}

    no_ativo = "no_gemini" if "no_gemini" in chunk else "no_groq" if "no_groq" in chunk else None

    if no_ativo:
        mensagens_do_no = chunk[no_ativo].get("messages", [])
        if mensagens_do_no:
            mensagem_ia = mensagens_do_no[-1]
            dados_resposta["texto"] = mensagem_ia.content

            # Acessa os metadados da mensagem de IA
            metadata = getattr(mensagem_ia, "response_metadata", {})
            
            # Tenta pegar o token_usage padrão (Gemini / OpenAI padrão)
            token_usage = metadata.get("token_usage", {})
            
            # Se o token_usage vier vazio (comum na Groq), busca em metadados da Groq
            if not token_usage and "x_groq" in metadata:
                token_usage = metadata["x_groq"].get("usage", {})

            if token_usage:
                # Busca pelas chaves tradicionais ou chaves alternativas comuns
                dados_resposta["tokens_input"] = token_usage.get("prompt_tokens") or token_usage.get("input_tokens") or 0
                dados_resposta["tokens_output"] = token_usage.get("completion_tokens") or token_usage.get("output_tokens") or 0

    return dados_resposta
