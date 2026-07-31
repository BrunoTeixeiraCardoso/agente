import streamlit as st
from graph import extrair_resposta_do_evento

def executar_agente_com_logs_copilot(agente_app, query, CONFIG_PADRAO):
    """
    Gerenciador visual estilo VS Code Copilot avançado com telemetria,
    inspeção de payloads de ferramentas, análise de RAG e monitoramento de Fallback.
    """
    resposta_final = ""
    total_input_tokens = 0
    total_output_tokens = 0
    numero_de_requisicoes = 0

    if "parar_agente" not in st.session_state:
        st.session_state.parar_agente = False

    def interromper():
        st.session_state.parar_agente = True

    st.button("🛑 Interromper Agente", key="btn_cancelar", type="primary", on_click=interromper)
    st.session_state.parar_agente = False

    with st.status("Iniciando o agente modular...", expanded=True) as status:
        try:
            for chunk in agente_app.stream(query, CONFIG_PADRAO, stream_mode="updates"):
                numero_de_requisicoes += 1
                
                # Checagem de interrupção
                if st.session_state.parar_agente:
                    status.update(label="⛔ Processamento cancelado pelo usuário!", state="error")
                    st.warning("A execução do grafo foi interrompida no meio do caminho.")
                    st.stop()
                
                # 🔀 NÓ: ROTEADOR INICIAL
                if "roteador" in chunk:
                    ia_escolhida = chunk["roteador"].get("proxima_ia", "desconhecida").upper()
                    status.update(label=f"🔀 Roteador: Direcionando para {ia_escolhida}...", state="running")
                    st.write(f"🔹 **Roteador**: Intenção classificada. Encaminhando fluxo para o cérebro **{ia_escolhida}**.")
                
                # 📚 NÓ: RECUPERAÇÃO DO RAG (LIVROS DE RPG)
                elif "no_rag_gemini" in chunk:
                    status.update(label="📚 RAG: Consultando base vetorial ChromaDB...", state="running")
                    contexto = chunk["no_rag_gemini"].get("contexto_documentos", "")
                    if contexto:
                        st.write("✅ **RAG**: Documentos históricos e regras de RPG localizados com sucesso!")
                        # Exibe detalhes profundos dos documentos recuperados de forma organizada
                        with st.expander("🔍 Inspecionar trechos extraídos dos PDFs"):
                            st.caption("Abaixo estão os blocos de texto injetados no contexto da IA:")
                            st.code(contexto[:1500] + "\n\n[... Conteúdo truncado para exibição ...]" if len(contexto) > 1500 else contexto, language="text")
                    else:
                        st.write("🔸 **RAG**: Nenhuma regra correspondente encontrada no banco local para esta pergunta.")

                # 🧠 NÓ: GEMINI (E DETECÇÃO DE FALLBACKS)
                elif "no_gemini" in chunk:
                    status.update(label="🧠 Gemini: Processando e gerando resposta...", state="running")
                    
                    # Verifica se o modelo acionou ou sugeriu uma ferramenta antes de responder por completo
                    mensagens_gemini = chunk["no_gemini"].get("messages", [])
                    if mensagens_gemini and hasattr(mensagens_gemini[-1], "tool_calls") and mensagens_gemini[-1].tool_calls:
                        chamada = mensagens_gemini[-1].tool_calls[0]
                        st.write(f"⚙️ **Gemini**: Solicitou ativação da ferramenta **`{chamada['name']}`**.")
                        with st.expander(f"🛠️ Argumentos enviados para `{chamada['name']}`"):
                            st.json(chamada.get("args", {}))
                    
                    dados_ia = extrair_resposta_do_evento(chunk)
                    if dados_ia["texto"]:
                        resposta_final = dados_ia["texto"]
                        total_input_tokens += dados_ia["tokens_input"]
                        total_output_tokens += dados_ia["tokens_output"]
                        
                        # Detecção e log detalhado caso a Groq tenha assumido devido a falha interna do nó
                        if "x_groq" in str(chunk) or (dados_ia["tokens_input"] == 0 and dados_ia["tokens_output"] > 0):
                            st.write("🚨 **Mecanismo de Fallback Ativado**:")
                            st.error("O cérebro principal (Gemini) falhou ou estourou o tempo limite de 10s. O cluster secundário **Groq/Llama 3.3** assumiu e concluiu a tarefa.")
                        else:
                            st.write("🔹 **Gemini**: Resposta sintetizada com base nas regras fornecidas.")
                
                # ⚡ NÓ: GROQ (CAMINHO DIRETO)
                elif "no_groq" in chunk:
                    status.update(label="⚡ Groq: Processando lógica e código corporativo...", state="running")
                    
                    mensagens_groq = chunk["no_groq"].get("messages", [])
                    if mensagens_groq and hasattr(mensagens_groq[-1], "tool_calls") and mensagens_groq[-1].tool_calls:
                        chamada = mensagens_groq[-1].tool_calls[0]
                        st.write(f"⚙️ **Groq**: Solicitou ativação da ferramenta **`{chamada['name']}`**.")
                        with st.expander(f"🛠️ Argumentos enviados para `{chamada['name']}`"):
                            st.json(chamada.get("args", {}))

                    dados_ia = extrair_resposta_do_evento(chunk)
                    if dados_ia["texto"]:
                        resposta_final = dados_ia["texto"]
                        total_input_tokens += dados_ia["tokens_input"]
                        total_output_tokens += dados_ia["tokens_output"]
                        st.write("🔹 **Groq/Llama 3.3**: Resposta estruturada de alto desempenho concluída.")
                
                # 🌐 NÓ GLOBAL: EXECUÇÃO DE FERRAMENTAS (TOOLNODE)
                elif "tools" in chunk:
                    status.update(label="🌐 Executando ferramentas no servidor...", state="running")
                    mensagem_ferramenta = chunk["tools"]["messages"][-1]
                    nome_ferramenta = getattr(mensagem_ferramenta, "name", "desconhecida")
                    resultado_bruto = getattr(mensagem_ferramenta, "content", "")
                    
                    st.write(f"🛠️ **Ferramenta executada**: Módulo **`{nome_ferramenta}`**.")
                    with st.expander(f"📥 Retorno bruto gerado pela ferramenta `{nome_ferramenta}`"):
                        if isinstance(resultado_bruto, str) and (resultado_bruto.startswith("{") or resultado_bruto.startswith("[")):
                            st.json(resultado_bruto)
                        else:
                            st.code(resultado_bruto[:1000] + "..." if len(str(resultado_bruto)) > 1000 else resultado_bruto)

            # Resumo da Telemetria Final
            st.markdown("---")
            st.markdown("**📊 Telemetria detalhada de consumo desta rodada:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tokens de Entrada (Prompt)", f"{total_input_tokens:,}")
            with col2:
                st.metric("Tokens de Saída (Resposta)", f"{total_output_tokens:,}")
            with col3:
                st.metric("Ciclos do Grafo (Nós)", numero_de_requisicoes)
            
            status.update(label="✅ Grafo processado com sucesso!", state="complete", expanded=False)
            
        except Exception as e:
            status.update(label="❌ Falha crítica encontrada na execução do fluxo!", state="error", expanded=True)
            st.error(f"Erro detalhado de depuração: {e}")
            st.stop()

    return resposta_final
