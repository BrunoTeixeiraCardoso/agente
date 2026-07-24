import streamlit as st
import os
from pathlib import Path
from graph import agente_app, CONFIG_PADRAO
# IMPORTAÇÃO DO NOVO COMPONENTE DE LOGS MODULAR
from interface_logs import executar_agente_com_logs_copilot

# 1. Configurações visuais da página
st.set_page_config(page_title="Agente de IA Modular", page_icon="🤖", layout="centered")
st.title("🤖 Agente Estilo VS Code Copilot")
st.caption("Interface limpa com gerenciador de logs modularizado")

# Barra lateral para gerenciamento de memória e Upload de PDF
with st.sidebar:
    st.header("⚙️ Configurações")
    if st.button("🗑️ Limpar Histórico do Chat"):
        st.session_state.historico_chat = []
        st.rerun()
        
    st.markdown("---")
    st.header("📂 Enviar Documento")
    arquivo_enviado = st.file_uploader("Escolha um arquivo PDF para o agente ler:", type=["pdf"])
    
    if arquivo_enviado:
        caminho_temporario = os.path.join(Path(__file__).parent, arquivo_enviado.name)
        with open(caminho_temporario, "wb") as f:
            f.write(arquivo_enviado.getbuffer())
        st.success(f"✅ Arquivo '{arquivo_enviado.name}' carregado!")
        st.session_state.caminho_pdf_atual = caminho_temporario

# 2. Inicialização do Histórico na Sessão
if "historico_chat" not in st.session_state:
    st.session_state.historico_chat = []

# 3. Exibe mensagens anteriores salvas na tela
for mensagem in st.session_state.historico_chat:
    with st.chat_message(mensagem["role"]):
        st.write(mensagem["content"])

# 4. Processamento do Input do Usuário
if prompt_usuario := st.chat_input("Como posso te ajudar hoje?"):
    with st.chat_message("user"):
        st.write(prompt_usuario)
    
    st.session_state.historico_chat.append({"role": "user", "content": prompt_usuario})

    # Abre o balão de resposta do assistente
    with st.chat_message("assistant"):
        placeholder_resposta = st.empty()
        query = {"messages": [("user", prompt_usuario)]}
        
        # =========================================================================
        # 🔥 A MÁGICA DA MODULARIZAÇÃO AQUI:
        # Chamamos a função externa que cuida de desenhar todos os logs na tela!
        # =========================================================================
        resposta_final = executar_agente_com_logs_copilot(agente_app, query, CONFIG_PADRAO)
            
        # 5. Exibe a resposta final em texto logo abaixo dos logs fixos
        if resposta_final:
            placeholder_resposta.write(resposta_final)
            st.session_state.historico_chat.append({"role": "assistant", "content": resposta_final})
        else:
            placeholder_resposta.write("O agente concluiu o fluxo, mas não retornou texto.")
