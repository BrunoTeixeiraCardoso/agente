import config
from typing import Annotated, Literal

from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

import nodes
from tools import tools


# Estrutura do estado do grafo: guarda o histórico e a decisão de qual modelo usar.
class State(TypedDict):
    messages: Annotated[list, add_messages]
    proxima_ia: str


def decidir_caminho(state: State) -> Literal["no_gemini", "no_groq"]:
    """Seleciona o próximo nó com base na decisão do roteador."""
    return "no_groq" if state["proxima_ia"] == "groq" else "no_gemini"


def construir_workflow():
    """Monta e configura o grafo do agente com nós e conexões."""
    # Cria o grafo que define o fluxo do agente entre os nós de decisão e resposta.
    workflow = StateGraph(State)

    # Cada nó representa uma etapa do processo: decidir, responder e usar ferramentas.
    workflow.add_node("roteador", nodes.roteador_inicial_node)
    workflow.add_node("no_gemini", nodes.no_gemini)
    workflow.add_node("no_groq", nodes.no_groq)
    workflow.add_node("tools", ToolNode(tools))

    # O fluxo começa no roteador e depois segue para o modelo escolhido.
    workflow.add_edge(START, "roteador")
    workflow.add_conditional_edges("roteador", decidir_caminho)
    workflow.add_conditional_edges("no_gemini", tools_condition, {"tools": "tools", "__end__": "__end__"})
    workflow.add_edge("tools", "no_gemini")
    workflow.add_edge("no_groq", "__end__")

    return workflow


def criar_agente_app():
    """Compila o workflow para uso na interface."""
    # Compila o grafo em um objeto pronto para ser executado pela interface.
    return construir_workflow().compile()


agente_app = criar_agente_app()
CONFIG_PADRAO = config.get_default_config()


# def extrair_resposta_do_evento(chunk) -> dict:
#     """Extrai texto e métricas de tokens dos eventos retornados pelo grafo."""
#     # Pega a resposta final do nó ativo e também os contadores de tokens usados.
#     dados_resposta = {"texto": "", "tokens_input": 0, "tokens_output": 0}

#     no_ativo = "no_gemini" if "no_gemini" in chunk else "no_groq" if "no_groq" in chunk else None

#     if no_ativo:
#         mensagens_do_no = chunk[no_ativo].get("messages", [])
#         if mensagens_do_no:
#             mensagem_ia = mensagens_do_no[-1]
#             dados_resposta["texto"] = mensagem_ia.content

#             metadata = getattr(mensagem_ia, "response_metadata", {})
#             token_usage = metadata.get("token_usage", {})

#             if token_usage:
#                 dados_resposta["tokens_input"] = token_usage.get("prompt_tokens", 0)
#                 dados_resposta["tokens_output"] = token_usage.get("completion_tokens", 0)

#     return dados_resposta

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
            
            # [MELHORIA MULTIPLATAFORMA]: Se o token_usage vier vazio (comum na Groq),
            # tenta buscar em metadados alternativos ou aninhados da Groq
            if not token_usage and "x_groq" in metadata:
                token_usage = metadata["x_groq"].get("usage", {})

            if token_usage:
                # Busca pelas chaves tradicionais ou chaves alternativas comuns
                dados_resposta["tokens_input"] = token_usage.get("prompt_tokens") or token_usage.get("input_tokens") or 0
                dados_resposta["tokens_output"] = token_usage.get("completion_tokens") or token_usage.get("output_tokens") or 0

    return dados_resposta
