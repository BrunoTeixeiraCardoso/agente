# 1. IMPORTAÇÕES (Sempre no topo do arquivo)
from typing import Annotated
from langchain_core.messages import trim_messages
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

# Importamos os modelos e a configuração que você criou
from config import get_llms, CONFIG_PADRAO
from tools import tools as default_tools
from utils import injetar_contexto_temporal


# 2. DEFINIÇÃO DO ESTADO
class State(TypedDict):
    messages: Annotated[list, add_messages]
    proxima_ia: str


# 3. FUNÇÃO DE SUPORTE (Deve vir ANTES de criar_handlers para poder ser usada lá dentro)
def criar_trimmador(max_tokens: int, modelo_contador):
    """Centraliza a política de trimming de mensagens para reduzir tokens."""
    return trim_messages(
        max_tokens=max_tokens,
        strategy="last",
        token_counter=modelo_contador,  # Usa o LLM para contar os tokens corretamente
        include_system=False,          # O System Prompt será injetado manualmente depois
        start_on="human",
    )


# 4. FUNÇÃO PRINCIPAL CONSTRUTORA
def criar_handlers(llm_gemini=None, llm_groq=None, ferramentas=None, trimmador=None):
    """Constrói os handlers de cada nó de forma reutilizável e testável."""
    
    # Inicializa as instâncias necessárias
    llm_gemini = llm_gemini or get_llms()["gemini"]
    llm_groq = llm_groq or get_llms()["groq"]
    ferramentas = ferramentas or default_tools
    
    # Captura o limite de tokens da configuração e monta o trimmador dinamicamente
    limite_tokens = CONFIG_PADRAO.get("max_tokens", 2048)
    trimmador = trimmador or criar_trimmador(max_tokens=limite_tokens, modelo_contador=llm_groq)

    # Prepara o Gemini com as ferramentas
    llm_gemini_com_tools = llm_gemini.bind_tools(ferramentas)

    # --- FUNÇÕES INTERNAS (OS NÓS DO GRAFO) ---

    def classificar_intencao(mensagem: str) -> str:
        palavras_logica = ["programar", "codigo", "python", "calcular", "matematica", "algoritmo", "script"]
        return "groq" if any(palavra in mensagem for palavra in palavras_logica) else "gemini"

    def roteador_inicial_node(state: State):
        """Nó classificador: decide qual IA resolve melhor a intenção do usuário."""
        ultima_mensagem = state["messages"][-1].content.lower()
        return {"proxima_ia": classificar_intencao(ultima_mensagem)}

    def no_gemini(state: State):
        """Nó do Gemini: usa ferramentas e contexto mais amplo."""
        # 1. Pega o prompt modular lido do arquivo externo txt
        system_prompt = injetar_contexto_temporal(CONFIG_PADRAO["system_prompt"])
        
        # 2. Poda o histórico da conversa baseado no limite de tokens configurado
        mensagens_otimizadas = trimmador.invoke(state["messages"])
        
        # 3. Junta o System Prompt no início das mensagens limpas
        historico_completo = [{"role": "system", "content": system_prompt}] + mensagens_otimizadas
        
        # 4. Executa o modelo
        response = llm_gemini_com_tools.invoke(historico_completo)
        return {"messages": [response]}

    def no_groq(state: State):
        """Nó da Groq: foca em lógica, matemática e programação."""
        # 1. Pega o mesmo prompt modular lido do arquivo externo txt
        system_prompt = injetar_contexto_temporal(CONFIG_PADRAO["system_prompt"])
        
        # 2. Poda o histórico da conversa baseado no limite de tokens
        mensagens_otimizadas = trimmador.invoke(state["messages"])
        
        # 3. Injeta o System Prompt de forma segura no topo
        historico_completo = [{"role": "system", "content": system_prompt}] + mensagens_otimizadas
        
        # 4. Executa o modelo
        response = llm_groq.invoke(historico_completo)
        return {"messages": [response]}

    # Retorna o dicionário com os nós prontos
    return {
        "roteador_inicial_node": roteador_inicial_node,
        "no_gemini": no_gemini,
        "no_groq": no_groq,
    }


# 5. EXECUÇÃO E EXPORTAÇÃO (No final do arquivo)
# Executa a função construtora e distribui os nós para o seu graph.py importar com sucesso
_node_handlers = criar_handlers()
roteador_inicial_node = _node_handlers["roteador_inicial_node"]
no_gemini = _node_handlers["no_gemini"]
no_groq = _node_handlers["no_groq"]
