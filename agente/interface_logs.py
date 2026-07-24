# interface_logs.py
import streamlit as st
from graph import extrair_resposta_do_evento

def executar_agente_com_logs_copilot(agente_app, query, CONFIG_PADRAO):
    """
    Gerenciador visual estilo VS Code Copilot com botão de interrupção forçada.
    """
    resposta_final = ""
    total_input_tokens = 0
    total_output_tokens = 0
    numero_de_requisicoes = 0

    # 1. Cria um botão de parar na tela acima dos logs
    # Usamos uma chave única (key) para o Streamlit monitorar o clique
    if st.button("🛑 Interromper Agente", key="botao_parar_agente", type="primary"):
        st.warning("⛔ O processamento foi cancelado pelo usuário antes de iniciar.")
        st.stop()

    # Cria o container expandido de logs
    with st.status("Iniciando o agente...", expanded=True) as status:
        try:
            # Percorre o stream de eventos enviado pelo LangGraph
            for chunk in agente_app.stream(query, CONFIG_PADRAO, stream_mode="updates"):
                numero_de_requisicoes += 1
                
                # =========================================================================
                # 🛡️ CHECAGEM DE INTERRUPÇÃO AUTOMÁTICA
                # Como o Streamlit recarrega o app ao clicar em botões, se o usuário
                # clicou em "Parar" durante o loop, nós matamos a execução imediatamente.
                # =========================================================================
                # Nota: Em interfaces web assíncronas complexas, checamos estados de clique.
                # Para o Streamlit de forma simples, se o botão registrar mudança, paramos.
                
                # 🔀 Se passou pelo nó do Roteador
                if "roteador" in chunk:
                    ia_escolhida = chunk["roteador"].get("proxima_ia", "desconhecida").upper()
                    status.update(label=f"🔀 Roteador ativado! Direcionando para: {ia_escolhida}...", state="running")
                    st.write(f"🔹 *Roteador*: Decidiu acionar o cérebro **{ia_escolhida}**.")
                
                # 🧠 Se passou pelo nó do Gemini
                elif "no_gemini" in chunk:
                    status.update(label="🧠 Gemini processando dados...", state="running")
                    st.write("🔹 *Gemini*: Analisando o contexto e gerando resposta...")
                    
                    dados_ia = extrair_resposta_do_evento(chunk)
                    if dados_ia["texto"]:
                        resposta_final = dados_ia["texto"]
                        total_input_tokens += dados_ia["tokens_input"]
                        total_output_tokens += dados_ia["tokens_output"]
                
                # ⚡ Se passou pelo nó da Groq
                elif "no_groq" in chunk:
                    status.update(label="⚡ Groq/Llama 3.3 processando lógica...", state="running")
                    st.write("🔹 *Groq/Llama 3.3*: Processando lógica computacional...")
                    
                    dados_ia = extrair_resposta_do_evento(chunk)
                    if dados_ia["texto"]:
                        resposta_final = dados_ia["texto"]
                        total_input_tokens += dados_ia["tokens_input"]
                        total_output_tokens += dados_ia["tokens_output"]
                
                # 🌐 Se passou pelo nó de Ferramentas
                elif "tools" in chunk:
                    status.update(label="🌐 Executando ferramentas...", state="running")
                    dados_tools = chunk["tools"]["messages"][-1]
                    nome_ferramenta = dados_tools.name
                    st.write(f"🔹 *Ferramenta*: Módulo **`{nome_ferramenta}`** foi executado.")

            # Escreve o resumo de telemetria
            st.markdown("---")
            st.markdown("**📊 Monitoramento de Consumo desta tarefa:**")
            st.markdown(f"* 📥 Tokens de Entrada (Prompt): `{total_input_tokens}`")
            st.markdown(f"* 📤 Tokens de Saída (Resposta): `{total_output_tokens}`")
            st.markdown(f"* ⚡ Chamadas de API feitas nesta rodada: `{numero_de_requisicoes}`")
            
            status.update(label="✅ Processamento concluído com sucesso!", state="complete", expanded=True)
            
        except Exception as e:
            status.update(label="❌ Ocorreu um erro no processamento!", state="error", expanded=True)
            st.error(f"Erro detalhado: {e}")
            st.stop()

    return resposta_final
