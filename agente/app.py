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
        
        # Executa o agente obtendo o retorno do fluxo através dos logs
        resposta_bruta = executar_agente_com_logs_copilot(agente_app, query, CONFIG_PADRAO)


   # --- FILTRO INTELIGENTE ANTI-POLUIÇÃO (VERSÃO ANTIESTRUTURADA) ---
        if hasattr(resposta_bruta, "content"):
            texto_bruto = str(resposta_bruta.content)
        else:
            texto_bruto = str(resposta_bruta)

        texto_limpo = ""

        # Verifica se a resposta veio poluída com a estrutura da API do Gemini
        if '"text":' in texto_bruto or "extras" in texto_bruto:
            import re
            
            # REGRAS DE REGEX EXTRA-PRECISAS:
            # 1. Procura pelo padrão "text":"CONTEÚDO" ou "text" : "CONTEÚDO"
            padrao_aspas_duplas = re.search(r'"text"\s*:\s*"([^"]+)"', texto_bruto)
            # 2. Procura pelo padrão caso venha com aspas simples
            padrao_aspas_simples = re.search(r"'text'\s*:\s*'([^']+)'", texto_bruto)
            
            if padrao_aspas_duplas:
                texto_limpo = padrao_aspas_duplas.group(1)
            elif padrao_aspas_simples:
                texto_limpo = padrao_aspas_simples.group(1)
            else:
                # Se a Regex falhar, limpa na força bruta removendo tudo a partir da palavra "extras"
                import json
                try:
                    # Adiciona chaves para tentar ler como JSON se necessário
                    if not texto_bruto.strip().startswith("{"):
                        texto_bruto = f"{{{texto_bruto}}}"
                    dados_json = json.loads(texto_bruto)
                    texto_limpo = dados_json.get("text", texto_bruto)
                except Exception:
                    # Corta a string antes de aparecer a palavra "extras" se ela estiver no final
                    if "extras" in texto_bruto:
                        texto_limpo = texto_bruto.split('"extras"')[0].split("'extras'")[0]
                        # Remove chaves ou vírgulas que sobraram do corte
                        texto_limpo = re.sub(r'["\'\{\}\s,:]*(text|type)*["\'\{\}\s,:]*', '', texto_limpo)
                    else:
                        texto_limpo = texto_bruto
        else:
            # Se já veio limpo de fábrica, apenas atribui
            texto_limpo = texto_bruto

        # Resolve problemas de codificação de quebras de linha textuais literais (\n)
        texto_limpo = texto_limpo.replace("\\n", "\n")
        
        # Limpa possíveis aspas residuais que sobram no início ou final do texto extraído
        texto_limpo = texto_limpo.strip().strip('"').strip("'")

        # Mostra a resposta 100% purificada e direta para o usuário
        if texto_limpo.strip():
            placeholder_resposta.write(texto_limpo)
            st.session_state.historico_chat.append({"role": "assistant", "content": texto_limpo})
        else:
            placeholder_resposta.write("O agente concluiu o fluxo, mas não retornou texto.")