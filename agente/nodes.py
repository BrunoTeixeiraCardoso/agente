# nodes.py
import os
from typing import Annotated, Dict, TypedDict
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langgraph.graph.message import add_messages

from config import CONFIG_PADRAO
from utils import injetar_contexto_temporal
# IMPORTAÇÃO DO NOVO AUXILIAR
from helpers_grafo import inicializar_dependencias_grafo

# 1. DEFINIÇÃO DO ESTADO
class State(TypedDict):
    messages: Annotated[list, add_messages]
    proxima_ia: str
    contexto_documentos: str

# 2. FUNÇÃO PRINCIPAL CONSTRUTORA
def criar_handlers():
    """Constrói os handlers de cada nó consumindo dependências externas organizadas."""
    
    # Executa o helper para puxar os modelos e o banco vetorial configurados
    deps = inicializar_dependencias_grafo()
    
    llm_gemini_com_tools = deps["gemini_tools"]
    llm_groq_com_tools = deps["groq_tools"]
    trimmador = deps["trimmador"]
    banco_vetorial = deps["banco_vetorial"]

    # --- FUNÇÕES INTERNAS (OS NÓS DO GRAFO) ---

    def classificar_intencao(mensagem: str) -> str:
        palavras_logica = ["programar", "codigo", "python", "calcular", "matematica", "algoritmo", "script"]
        return "groq" if any(palavra in mensagem for palavra in palavras_logica) else "gemini"

    def roteador_inicial_node(state: State):
        ultima_mensagem = state["messages"][-1].content.lower()
        return {"proxima_ia": classificar_intencao(ultima_mensagem)}

    def no_recuperar_dados_rag(state: State):
        if not banco_vetorial:
            print("⚠️ [RAG] Banco de dados indisponível ou pasta não encontrada. Pulando busca.")
            return {"contexto_documentos": ""}
        try:
            print("🔍 [RAG] Consultando a biblioteca de livros de RPG...")
            ultima_mensagem = state["messages"][-1].content
            documentos_proximos = banco_vetorial.similarity_search(ultima_mensagem, k=3)
            conteudo_filtrado = "\n\n---\n\n".join([doc.page_content for doc in documentos_proximos])
            return {"contexto_documentos": conteudo_filtrado}
        except Exception as e:
            print(f"⚠️ [RAG] Erro ao acessar o ChromaDB na busca: {e}")
            return {"contexto_documentos": ""}

    def no_gemini(state: State):
        system_prompt = injetar_contexto_temporal(CONFIG_PADRAO["system_prompt"])
        system_prompt += (
            "\n\n[INSTRUÇÃO OBRIGATÓRIA DE CAPACIDADE]: Você possui ferramentas ativas integradas... "
            "Se o comando exigir o uso delas, invoque-as imediatamente."
        )
        
        contexto_rag = state.get("contexto_documentos", "")
        if contexto_rag:
            system_prompt += f"\n\n[CONTEÚDO ADICIONAL DE SUPORTE (RAG)]:\n{contexto_rag}"
        
        mensagens_otimizadas = trimmador.invoke(state["messages"])
        historico_completo = [SystemMessage(content=system_prompt)] + mensagens_otimizadas
        
        try:
            print("🤖 [Grafo] Tentando responder com o Gemini...")
            response = llm_gemini_com_tools.invoke(historico_completo, config={"timeout": 10})
            return {"messages": [response]}
        except Exception as erro_gemini:
            print(f"⚠️ [FALLBACK] Redirecionando requisição para a Groq...")
            # Implementação da higienização anti-erro 400 que corrigimos antes
            historico_sanitizado = [
                msg for msg in historico_completo 
                if not (hasattr(msg, "tool_calls") and msg.tool_calls)
            ]
            response_fallback = llm_groq_com_tools.invoke(historico_sanitizado)
            return {"messages": [response_fallback]}

    def no_groq(state: State):
        system_prompt = injetar_contexto_temporal(CONFIG_PADRAO["system_prompt"])
        mensagens_otimizadas = trimmador.invoke(state["messages"])
        historico_completo = [SystemMessage(content=system_prompt)] + mensagens_otimizadas
        response = llm_groq_com_tools.invoke(historico_completo)
        return {"messages": [response]}

    return {
        "roteador_inicial_node": roteador_inicial_node,
        "no_recuperar_dados_rag": no_recuperar_dados_rag,
        "no_gemini": no_gemini,
        "no_groq": no_groq,
    }

# 3. EXECUÇÃO E EXPORTAÇÃO NATIVA
_node_handlers = criar_handlers()
roteador_inicial_node = _node_handlers["roteador_inicial_node"]
no_recuperar_dados_rag = _node_handlers["no_recuperar_dados_rag"]
no_gemini = _node_handlers["no_gemini"]
no_groq = _node_handlers["no_groq"]
