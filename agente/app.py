import os
from pathlib import Path
import streamlit as st

from graph import CONFIG_PADRAO, agente_app
from interface_logs import executar_agente_com_logs_copilot

# Configura a aparência inicial da página da interface do agente.
st.set_page_config(page_title="Agente de IA Modular", page_icon="🤖", layout="centered")
st.title("🤖 Agente Estilo VS Code Copilot")
st.caption("Interface de Chat limpa com painel lateral de monitoramento e telemetria")

# Inicializa o histórico de mensagens para manter o chat persistente na sessão.
if "historico_chat" not in st.session_state:
    st.session_state.historico_chat = []

# Barra lateral contendo opções administrativas e a área de streaming de logs
with st.sidebar:
    st.header("⚙️ Painel de Controle")
    if st.button("🗑️ Limpar Histórico do Chat", use_container_width=True):
        st.session_state.historico_chat = []
        st.rerun()
        
    st.markdown("---")
    st.header("📊 Console de Execução (Logs)")
    st.caption("Acompanhe o comportamento interno dos nós do grafo e consumo de APIs abaixo:")

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
        
        # Extrai as mensagens anteriores do session_state para análise de contexto completa
        historico_formatado = []
        for msg in st.session_state.historico_chat:
            historico_formatado.append((msg["role"], msg["content"]))
            
        query = {"messages": historico_formatado}
        
        # [MUDANÇA VISUAL & OTIMIZAÇÃO]: Envia os logs dinâmicos e a telemetria do RAG 
        # diretamente para o container da barra lateral, corrigindo também a chamada dupla anterior.
        with st.sidebar:
            resposta_bruta = executar_agente_com_logs_copilot(agente_app, query, CONFIG_PADRAO)

        # [CORREÇÃO CRÍTICA ANTI-LISTA]: Garante a extração do texto se vier um objeto ou lista do Grafo
        if isinstance(resposta_bruta, list) and len(resposta_bruta) > 0:
            ultima_msg = resposta_bruta[-1]
            texto_limpo = getattr(ultima_msg, "content", str(ultima_msg))
        elif hasattr(resposta_bruta, "content"):
            texto_limpo = resposta_bruta.content
        else:
            texto_limpo = str(resposta_bruta)

        # Higienização de strings garantida contra aspas residuais
        texto_limpo = texto_limpo.strip().strip('"').strip("'")

        # Mostra a resposta purificada e direta na tela central do usuário
        if texto_limpo:
            placeholder_resposta.write(texto_limpo)
            st.session_state.historico_chat.append({"role": "assistant", "content": texto_limpo})
        else:
            placeholder_resposta.write("O agente concluiu o fluxo, mas não retornou texto.")
