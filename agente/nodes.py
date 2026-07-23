# nodes.py
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import trim_messages

# Importações vindas dos seus arquivos de infraestrutura
from config import llm_gemini, llm_groq
from tools import tools

# 1. Configuração de corte de memória interno para os nós economizarem tokens
trimmador_de_memoria = trim_messages(
    max_tokens=6, 
    strategy="last",
    token_counter=len, 
    include_system=True,
    start_on="human"
)

# 2. Vincula as ferramentas de busca ao Gemini
llm_gemini_com_tools = llm_gemini.bind_tools(tools)

# 3. Definição do Estado espelhada para validação de tipo das funções
class State(TypedDict):
    messages: Annotated[list, add_messages]
    proxima_ia: str

# =====================================================================
# FUNÇÕES PURAS DOS NÓS (LOGICA INDIVIDUAL DE CADA CÉREBRO)
# =====================================================================

def roteador_inicial_node(state: State):
    """Nó Classificador: Analisa o texto e decide qual IA resolve melhor."""
    ultima_mensagem = state["messages"][-1].content.lower()
    
    # Lista de termos que exigem raciocínio lógico estruturado ou código
    palavras_logica = ["programar", "codigo", "python", "calcular", "matematica", "algoritmo", "script"]
    
    # Triagem inteligente por intenção
    if any(palavra in ultima_mensagem for palavra in palavras_logica):
        escolha = "groq"
    else:
        escolha = "gemini"
        
    return {"proxima_ia": escolha}

def no_gemini(state: State):
    """Nó do Gemini: Especialista em buscas na web e contextos longos."""
    system_prompt = "Você é o especialista em buscas e textos longos. Use ferramentas sempre que precisar de dados atuais."
    historico_completo = [{"role": "system", "content": system_prompt}] + state["messages"]
    
    # Aplica o trimming antes de disparar a API do Google
    mensagens_otimizadas = trimmador_de_memoria.invoke(historico_completo)
    response = llm_gemini_com_tools.invoke(mensagens_otimizadas)
    return {"messages": [response]}

def no_groq(state: State):
    """Nó da Groq: Especialista em lógica computacional, códigos e matemática."""
    system_prompt = "Você é o especialista em lógica, matemática e programação. Seja direto e preciso."
    historico_completo = [{"role": "system", "content": system_prompt}] + state["messages"]
    
    # Aplica o trimming antes de disparar a API da Groq
    mensagens_otimizadas = trimmador_de_memoria.invoke(historico_completo)
    response = llm_groq.invoke(mensagens_otimizadas)
    return {"messages": [response]}
