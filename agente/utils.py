# # utils.py
# from datetime import datetime


# def obter_data_atual_formatada() -> str:
#     """Retorna a data atual do sistema no formato DD/MM/AAAA."""
#     return datetime.now().strftime("%d/%m/%Y")


# def injetar_contexto_temporal(system_prompt_base: str) -> str:
#     """Acopla a data de hoje como uma diretriz no topo do system prompt."""
#     data_hoje = obter_data_atual_formatada()
    
#     contexto = f"Diretriz Temporal: Hoje é dia {data_hoje}.\n"
#     contexto += "Use essa informação para determinar se as perguntas do usuário exigem dados atuais da internet.\n\n"
    
#     return contexto + system_prompt_base

# utils.py
from datetime import datetime


def obter_data_atual_formatada() -> str:
    """Retorna a data atual do sistema no formato DD/MM/AAAA."""
    return datetime.now().strftime("%d/%m/%Y")


def injetar_contexto_temporal(system_prompt_base: str) -> str:
    """Acopla a data de hoje como uma diretriz no topo do system prompt."""
    data_hoje = obter_data_atual_formatada()
    
    contexto = f"Diretriz Temporal: Hoje é dia {data_hoje}.\n"
    contexto += "Use essa informação para determinar se as perguntas do usuário exigem dados atuais da internet.\n\n"
    
    return contexto + system_prompt_base
