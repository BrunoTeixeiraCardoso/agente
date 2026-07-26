# rpg_tools.py
import random
from langchain_core.tools import tool


@tool
def rolar_dados_rpg(quantidade: int, lados: int, modificador: int = 0) -> str:
    """Rola dados de RPG (como d4, d6, d8, d10, d12, d20, d100) com base na quantidade, lados e modificadores.
    
    Use essa ferramenta SEMPRE que o usuário pedir para rolar dados, testar perícias ou atributos no RPG.
    Exemplo: para '2d20 + 5', passe quantidade=2, lados=20, modificador=5.
    """
    try:
        if quantidade <= 0 or quantidade > 50:
            return "Erro: A quantidade de dados deve ser entre 1 e 50."
        if lados <= 1 or lados > 1000:
            return "Erro: O número de lados do dado deve ser entre 2 e 1000."
            
        resultados = [random.randint(1, lados) for _ in range(quantidade)]
        soma_dados = sum(resultados)
        total_final = soma_dados + modificador
        
        resposta = f"🎲 Rolagem: {quantidade}d{lados}"
        if modificador != 0:
            resposta += f" {'+' if modificador > 0 else '-'} {abs(modificador)}"
            
        resposta += f"\nResultados individuais: {resultados}"
        resposta += f"\nTotal: {total_final}"
        
        return resposta
        
    except Exception as e:
        return f"Falha ao rolar os dados: {str(e)}"
