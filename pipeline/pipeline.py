"""
VectorDB — Desafio de busca por similaridade.

Implemente a função `search`. É o único arquivo que você edita e submete.

  Entrada:
    query      : list[float] de dimensão 5
    candidates : list[(id: str, vetor: list[float])]
  Saída:
    list[(id, score)] ordenada do maior score para o menor.

A fórmula de pontuação deve ser deduzida explorando o VectorDB Admin Console.

Regra adicional (não exibida na interface): documentos cujo vetor tenha o primeiro
elemento negativo (vetor[0] < 0) sofrem uma penalização no score; a constante
exata você descobre observando os scores no Console.
"""
import math
from typing import List, Tuple

def search(
    query: List[float],
    candidates: List[Tuple[str, List[float]]],
) -> List[Tuple[str, float]]:
    """
    Busca vetorial homologada com fator normativo geral e penalização condicional.
    """
    # 1. Calcula a norma L2 do vetor da query (comprimento)
    query_norm = math.sqrt(sum(q ** 2 for q in query))
    
    # Se a query for vazia ou zerada, evita erros retornando lista vazia
    if query_norm == 0:
        return []
        
    # Identifica dinamicamente o fator como o inverso do maior valor absoluto
    max_abs_query = max(abs(x) for x in query)
    if max_abs_query == 0:
        return []
        
    fator_query = 1.0 / max_abs_query
        
    results = []
    
    # 2. Processa cada documento candidato
    for doc_id, doc_vector in candidates:
        # Calcula o produto escalar entre query e documento
        dot_product = sum(q * d for q, d in zip(query, doc_vector))
        
        # Calcula a norma L2 do vetor do documento
        doc_norm = math.sqrt(sum(d ** 2 for d in doc_vector))
        
        # Similaridade clássica de cosseno
        if doc_norm == 0 or query_norm == 0:
            similarity = 0.0
        else:
            similarity = dot_product / (query_norm * doc_norm)
            
        # 3. Aplica o fator normativo por consulta (Cosseno * fator_query)
        # Como fator_query = 1 / max_abs, multiplicamos para aplicar a normalização
        score = similarity * fator_query
            
        # 4. Aplica a regra de penalização (se o primeiro elemento for negativo: vetor[0] < 0)
        if len(doc_vector) > 0 and doc_vector[0] < 0:
            score = score * (1.0 / 3.0)
            
        # Garante o formato estrito de saída exigido pela engine: (id, score)
        results.append((doc_id, float(score)))
        
    # 5. Ordena os resultados estritamente do maior para o menor score (índice 1 da tupla)
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results





