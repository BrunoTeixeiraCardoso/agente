import streamlit as st
# Importação: Trazendo a configuração e a função de extração limpa do graph.py
from graph import agente_app, CONFIG_PADRAO, extrair_resposta_do_evento

# 1. Configurações visuais da página
st.set_page_config(page_title="Agente de IA Modular", page_icon="🤖", layout="centered")
st.title("🤖 Agente com Logs Estilo Copilot")
st.caption("Bastidores do raciocínio fixos na tela para consulta rápida")

# Barra lateral para gerenciamento de memória
with st.sidebar:
    st.header("⚙️ Configurações")
    if st.button("🗑️ Limpar Histórico do Chat"):
        st.session_state.historico_chat = []
        st.rerun()

# 2. Inicialização do Histórico na Sessão
if "historico_chat" not in st.session_state:
    st.session_state.historico_chat = []

# 3. Exibe mensagens anteriores salvas na tela
for message in st.session_state.historico_chat:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 4. Processamento do Input do Usuário
if prompt_usuario := st.chat_input("Como posso te ajudar hoje?"):
    with st.chat_message("user"):
        st.write(prompt_usuario)
    
    st.session_state.historico_chat.append({"role": "user", "content": prompt_usuario})

    # Abre o bloco de resposta do assistente
    with st.chat_message("assistant"):
        placeholder_resposta = st.empty()
        resposta_final = ""
        
        # CRIANDO O CONTAINER DE LOGS (Estilo Copilot / VS Code)
        with st.status("Iniciando o agente...", expanded=True) as status:
            query = {"messages": [("user", prompt_usuario)]}
            
            try:
                # 📊 Variáveis para acumular o gasto de tokens e requisições desta rodada
                total_input_tokens = 0
                total_output_tokens = 0
                numero_de_requisicoes = 0
                
                # Percorre o stream do LangGraph passando as configurações
                for chunk in agente_app.stream(query, CONFIG_PADRAO, stream_mode="updates"):
                    # Cada nó executado conta como uma requisição para monitorar o seu RPM
                    numero_de_requisicoes += 1
                    
                    # 🔀 MONITORAMENTO DO ROTEADOR: Exibe a triagem de intenção na tela
                    if "roteador" in chunk:
                        ia_escolhida = chunk["roteador"].get("proxima_ia", "desconhecida").upper()
                        status.update(label=f"🔀 Roteador ativado! Direcionando tarefa para a API: {ia_escolhida}...", state="running")
                    
                    # 🧠 MONITORAMENTO DO GEMINI
                    elif "no_gemini" in chunk:
                        status.update(label="🧠 Gemini processando dados e decidindo próximo passo...", state="running")
                        
                        # Extração atualizada vinda do graph.py (lê dinamicamente o nó ativo)
                        dados_ia = extrair_resposta_do_evento(chunk)
                        if dados_ia["texto"]:
                            resposta_final = dados_ia["texto"]
                            total_input_tokens += dados_ia["tokens_input"]
                            total_output_tokens += dados_ia["tokens_output"]
                    
                    # ⚡ MONITORAMENTO DA GROQ
                    elif "no_groq" in chunk:
                        status.update(label="⚡ Groq/Llama 3.3 processando lógica/código e finalizando...", state="running")
                        
                        # Extração atualizada vinda do graph.py (lê dinamicamente o nó ativo)
                        dados_ia = extrair_resposta_do_evento(chunk)
                        if dados_ia["texto"]:
                            resposta_final = dados_ia["texto"]
                            total_input_tokens += dados_ia["tokens_input"]
                            total_output_tokens += dados_ia["tokens_output"]
                    
                    # 🌐 MONITORAMENTO DAS FERRAMENTAS DE BUSCA
                    elif "tools" in chunk:
                        status.update(label="🌐 API de Busca (Tavily) ativada! Varrendo a internet...", state="running")
                
                # 📈 ATUALIZAÇÃO: Desenha o painel de consumo de tokens dentro do log fixo
                st.markdown("---")
                st.markdown("**📊 Monitoramento de Consumo (TPM / RPM):**")
                st.markdown(f"* 📥 Tokens de Entrada (Prompt): `{total_input_tokens}`")
                st.markdown(f"* 📤 Tokens de Saída (Resposta): `{total_output_tokens}`")
                st.markdown(f"* ⚡ Chamadas de API nesta rodada: `{numero_de_requisicoes}`")
                
                # Modificação mantida: A caixa com o histórico de passos continua aberta na tela
                status.update(label="✅ Processamento concluído com sucesso!", state="complete", expanded=True)
                
            except Exception as e:
                status.update(label="❌ Ocorreu um erro no processamento!", state="error", expanded=True)
                st.error(f"Erro detalhado: {e}")
                st.stop()
            
        # 5. Exibe a resposta final na tela após os logs fixos
        if resposta_final:
            placeholder_resposta.write(resposta_final)
            st.session_state.historico_chat.append({"role": "assistant", "content": resposta_final})
        else:
            placeholder_resposta.write("O agente concluiu o fluxo, mas não retornou texto.")
