# 1. IMPORTAÇÕES (Sempre no topo do arquivo)
import os
from typing import Annotated, Dict, TypedDict
from langchain_core.messages import trim_messages, SystemMessage  # Adicionado SystemMessage
from langgraph.graph.message import add_messages
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Importamos os modelos e a configuração que você criou
from config import get_llms, CONFIG_PADRAO
from tools import tools as default_tools
from utils import injetar_contexto_temporal

# 2. DEFINIÇÃO DO ESTADO
class State(TypedDict):
    messages: Annotated[list, add_messages]
    proxima_ia: str
    contexto_documentos: str

# 3. FUNÇÃO DE SUPORTE
def criar_trimmador(max_tokens: int, modelo_contador):
    """Centraliza a política de trimming de mensagens para reduzir tokens."""
    return trim_messages(
        max_tokens=max_tokens,
        strategy="last",
        token_counter=modelo_contador,
        include_system=False,
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

    # [CORREÇÃO CRÍTICA]: Prepara AMBOS os modelos com as ferramentas. 
    # Se o fallback acionar o Groq, ele também saberá executar ferramentas!
    llm_gemini_com_tools = llm_gemini.bind_tools(ferramentas)
    llm_groq_com_tools = llm_groq.bind_tools(ferramentas)

    # Configuração do Banco de Dados local e Embeddings
    PASTA_DO_BANCO_DADOS = "./banco_vetorial_rpg"
    embeddings = OpenAIEmbeddings()
    
    # Instancia o banco uma única vez na inicialização dos nós, se a pasta existir
    banco_vetorial = None
    if os.path.exists(PASTA_DO_BANCO_DADOS):
        try:
            banco_vetorial = Chroma(
                persist_directory=PASTA_DO_BANCO_DADOS, 
                embedding_function=embeddings
            )
        except Exception as e:
            print(f"⚠️ [RAG] Falha ao pré-carregar o ChromaDB: {e}")

    # --- FUNÇÕES INTERNAS (OS NÓS DO GRAFO) ---

    def classificar_intencao(mensagem: str) -> str:
        palavras_logica = ["programar", "codigo", "python", "calcular", "matematica", "algoritmo", "script"]
        return "groq" if any(palavra in mensagem for palavra in palavras_logica) else "gemini"

    def roteador_inicial_node(state: State):
        """Nó classificador: decide qual IA resolve melhor a intenção do usuário."""
        ultima_mensagem = state["messages"][-1].content.lower()
        return {"proxima_ia": classificar_intencao(ultima_mensagem)}

    def no_recuperar_dados_rag(state: State):
        """Busca regras e lore nos PDFs de RPG com base na pergunta do usuário."""
        if not banco_vetorial:
            print("⚠️ [RAG] Banco de dados indisponível ou pasta não encontrada. Pulando busca.")
            return {"contexto_documentos": ""}

        try:
            print("🔍 [RAG] Consultando a biblioteca de livros de RPG...")
            ultima_mensagem = state["messages"][-1].content
            documentos_proximos = banco_vetorial.similarity_search(ultima_mensagem, k=3)
            conteudo_filtrado = "\n\n---\n\n".join([doc.page_content for doc in documentos_proximos])
            
            print(f"✅ Encontrados {len(documentos_proximos)} trechos relevantes nos seus PDFs!")
            return {"contexto_documentos": conteudo_filtrado}
            
        except Exception as e:
            print(f"⚠️ [RAG] Erro ao acessar o ChromaDB na busca: {e}")
            return {"contexto_documentos": ""}

    def no_gemini(state: State):
        """Nó do Gemini: usa ferramentas e possui fallback automático para a Groq."""
        system_prompt = injetar_contexto_temporal(CONFIG_PADRAO["system_prompt"])
        
        # [PROMPT ENGINE]: Comando explícito obrigando a IA a chamar funções quando necessário
        system_prompt += (
            "\n\n[INSTRUÇÃO OBRIGATÓRIA DE CAPACIDADE]: Você possui ferramentas ativas integradas ao seu sistema "
            "(como rolar dados de RPG, pesquisar na internet ou indexar novos PDFs). Se o comando do usuário "
            "exigir o uso de alguma dessas ações físicas ou buscas externas, invoque a ferramenta apropriada imediatamente."
        )
        
        contexto_rag = state.get("contexto_documentos", "")
        if contexto_rag:
            system_prompt += f"\n\n[CONTEÚDO ADICIONAL DE SUPORTE (RAG)]:\nUse as informações abaixo para responder ao usuário sempre que aplicável:\n{contexto_rag}"
        
        mensagens_otimizadas = trimmador.invoke(state["messages"])
        
        # [CORREÇÃO CRÍTICA]: Tipagem explícita usando SystemMessage nativo do LangChain
        historico_completo = [SystemMessage(content=system_prompt)] + mensagens_otimizadas
        
        try:
            print("🤖 [Grafo] Tentando responder com o Gemini...")
            response = llm_gemini_com_tools.invoke(historico_completo, config={"timeout": 10})
            return {"messages": [response]}
            
        except Exception as erro_gemini:
            print(f"⚠️ [FALHA GEMINI] Modelo indisponível ou demorou demais! Erro: {erro_gemini}")
            print("🚀 [FALLBACK] Redirecionando requisição para a Groq imediatamente...")
            
            # Executa o Groq com suporte a ferramentas também no plano B
            response_fallback = llm_groq_com_tools.invoke(historico_completo)
            return {"messages": [response_fallback]}

    def no_groq(state: State):
        """Nó da Groq: foca em lógica, matemática e programação."""
        system_prompt = injetar_contexto_temporal(CONFIG_PADRAO["system_prompt"])
        
        system_prompt += (
            "\n\n[INSTRUÇÃO OBRIGATÓRIA DE CAPACIDADE]: Você tem acesso a ferramentas de execução real. "
            "Invoque-as caso a solicitação do usuário dependa delas."
        )
        
        mensagens_otimizadas = trimmador.invoke(state["messages"])
        historico_completo = [SystemMessage(content=system_prompt)] + mensagens_otimizadas
        
        # [OTIMIZAÇÃO]: Habilita chamadas de ferramenta também para o fluxo nativo da Groq
        response = llm_groq_com_tools.invoke(historico_completo)
        return {"messages": [response]}

    # Retorna o dicionário com os nós prontos
    return {
        "roteador_inicial_node": roteador_inicial_node,
        "no_recuperar_dados_rag": no_recuperar_dados_rag,
        "no_gemini": no_gemini,
        "no_groq": no_groq,
    }

# 5. EXECUÇÃO E EXPORTAÇÃO (No final do arquivo)
_node_handlers = criar_handlers()
roteador_inicial_node = _node_handlers["roteador_inicial_node"]
no_recuperar_dados_rag = _node_handlers["no_recuperar_dados_rag"]
no_gemini = _node_handlers["no_gemini"]
no_groq = _node_handlers["no_groq"]
