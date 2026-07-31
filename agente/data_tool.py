from langchain_core.tools import tool
import datetime

@tool
def consultar_data_e_hora_atual() -> str:
    """
    Retorna a data e a hora atual exata do sistema (Formato: DD/MM/AAAA HH:MM:SS).
    Use esta ferramenta imediatamente sempre que o usuário perguntar que dia é hoje, 
    qual é a data atual, que horas são ou precisar de um ponto de referência temporal.
    """
    try:
        agora = datetime.datetime.now()
        return agora.strftime("%d/%m/%Y %H:%M:%S")
    except Exception as error:
        return f"Erro ao obter o carimbo de data/hora atual: {error}"
