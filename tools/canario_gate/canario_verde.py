"""Canário verde: este teste TEM QUE PASSAR.

O controle negativo do canário vermelho. Sem ele, um ambiente onde *tudo* reprova
(dependência quebrada, coleta falhando, interpretador errado) faria o vermelho reprovar
"como esperado" e o veredito ficaria verde por acidente — sensor que mede uma direção
só não mede nada.
"""


def canario_verde():
    """Uma aprovação genuína."""
    esperado, obtido = "aprovado", "aprovado"
    assert obtido == esperado
