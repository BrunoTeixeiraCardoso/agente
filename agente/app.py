import os
from pathlib import Path
import streamlit as st

from graph import CONFIG_PADRAO, agente_app
from interface_logs import executar_agente_com_logs_copilot

# Configura a aparência inicial da página da interface do agente.
st.set_page_config(page_title="Agente de IA Modular", page_icon="🤖", layout="centered")
st.title("🤖 Agente Estilo VS Code Copilot")
st.caption("Interface limpa com gerenciador de logs modularizado")

# Configuração de caminhos do RAG local
PASTA_DOS_LIVROS = "./meus_livros_rpg"

# Inicializa o histórico de mensagens para manter o chat persistente na sessão.
if "historico_chat" not in st.session_state:
    st.session_state.historico_chat = []

# Barra lateral com opções de controle e upload de PDF.
with st.sidebar:
    st.header("⚙️ Configurações")
    if st.button("🗑️ Limpar Histórico do Chat"):
        st.session_state.historico_chat = []
        st.rerun()
        
    st.markdown("---")
    st.header("📂 Enviar Documento para o RAG")
    
    # Permite ao usuário enviar um novo livro de RPG ou documento para a pasta monitorada
    arquivo_enviado = st.file_uploader("Escolha um arquivo PDF para o agente ler:", type=["pdf"])

    if arquivo_enviado:
        # [CORREÇÃO RAG]: Garante que a pasta destino existe e salva o PDF no local correto do RAG
        os.makedirs(PASTA_DOS_LIVROS, exist_ok=True)
        caminho_final_pdf = os.path.join(PASTA_DOS_LIVROS, arquivo_enviado.name)
        
        with open(caminho_final_pdf, "wb") as f:
            f.write(arquivo_enviado.getbuffer())
            
        st.success(f"✅ '{arquivo_enviado.name}' salvo na biblioteca de RPG!")
        st.info("💡 Lembre-se de rodar o script 'indexar_rpg.py' no terminal para atualizar o banco de dados!")

# Reexibe as mensagens já armazenadas para a interface parecer contínua.
for mensagem in st.session_state.historico_chat:
    with st.chat_message(mensagem["role"]):
        st.write(mensagem["content"])

# Captura a mensagem digitada pelo usuário e a envia para o agente.
if prompt_usuario := st.chat_input("Como posso te ajudar hoje?"):
    with st.chat_message("user"):
        st.write(prompt_usuario)
    
    st.session_state.historico_chat.append({"role": "user", "content": prompt_usuario})

    # Exibe o espaço de resposta do assistente e executa o fluxo do agente.
    with st.chat_message("assistant"):
        placeholder_resposta = st.empty()
        
        # [CORREÇÃO MEMÓRIA]: Extrai as mensagens anteriores do session_state 
        # para que o LangGraph e o trimmador analisem o contexto completo da conversa
        historico_formatado = []
        for msg in st.session_state.historico_chat:
            historico_formatado.append((msg["role"], msg["content"]))
            
        query = {"messages": historico_formatado}
        
        # Executa o agente obtendo o retorno do fluxo através dos logs (Texto já vem limpo)
        texto_limpo = executar_agente_com_logs_copilot(agente_app, query, CONFIG_PADRAO)

        # [OTIMIZAÇÃO COMPLETA]: Removemos 40 linhas de Regex redundantes. 
        # A função executar_agente_com_logs_copilot já utiliza a extração purificada do graph.py.
        texto_limpo = texto_limpo.strip().strip('"').strip("'")

        # Mostra a resposta purificada e direta para o usuário
        if texto_limpo:
            placeholder_resposta.write(texto_limpo)
            st.session_state.historico_chat.append({"role": "assistant", "content": texto_limpo})
        else:
            placeholder_resposta.write("O agente concluiu o fluxo, mas não retornou texto.")
