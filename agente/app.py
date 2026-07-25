import os
from pathlib import Path

import streamlit as st

from graph import CONFIG_PADRAO, agente_app
from interface_logs import executar_agente_com_logs_copilot

# Configura a aparência inicial da página da interface do agente.
st.set_page_config(page_title="Agente de IA Modular", page_icon="🤖", layout="centered")
st.title("🤖 Agente Estilo VS Code Copilot")
st.caption("Interface limpa com gerenciador de logs modularizado")

# Barra lateral com opções de controle e upload de PDF.
with st.sidebar:
    st.header("⚙️ Configurações")
    # Limpa o histórico do chat da sessão atual.
    if st.button("🗑️ Limpar Histórico do Chat"):
        st.session_state.historico_chat = []
        st.rerun()
        
    st.markdown("---")
    st.header("📂 Enviar Documento")
    # Permite ao usuário enviar um PDF para o agente processar.
    arquivo_enviado = st.file_uploader("Escolha um arquivo PDF para o agente ler:", type=["pdf"])

    if arquivo_enviado:
        caminho_temporario = os.path.join(Path(__file__).parent, arquivo_enviado.name)
        with open(caminho_temporario, "wb") as f:
            f.write(arquivo_enviado.getbuffer())
        st.success(f"✅ Arquivo '{arquivo_enviado.name}' carregado!")
        st.session_state.caminho_pdf_atual = caminho_temporario

# Inicializa o histórico de mensagens para manter o chat persistente na sessão.
if "historico_chat" not in st.session_state:
    st.session_state.historico_chat = []

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
        query = {"messages": [("user", prompt_usuario)]}
        
        # Chama a função responsável por executar o agente e mostrar os logs na interface.
        resposta_final = executar_agente_com_logs_copilot(agente_app, query, CONFIG_PADRAO)

        # Mostra a resposta final do agente após o processamento.
        if resposta_final:
            placeholder_resposta.write(resposta_final)
            st.session_state.historico_chat.append({"role": "assistant", "content": resposta_final})
        else:
            placeholder_resposta.write("O agente concluiu o fluxo, mas não retornou texto.")
