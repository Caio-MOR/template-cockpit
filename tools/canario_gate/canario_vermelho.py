"""Canário vermelho: este teste TEM QUE REPROVAR.

Não é um teste da suíte — é o instrumento de medição do veredito
(`tools/gate_veredito.py`). O nome fora do padrão `test_*.py` é de propósito: a suíte
normal não o coleta, e ele não entra na contagem da suíte.

Se este arquivo um dia PASSAR, não conserte o arquivo: o que quebrou foi o repo. Passar
aqui significa que alguma coisa entre o pytest e o relatório está forçando resultado —
um hook `pytest_runtest_call`, um `force_result`, um plugin adulterando report — e que
"N passed" deixou de ser evidência de qualquer coisa.
"""


def canario_vermelho():
    """Uma reprovação genuína, sem marker, sem condição, sem plugin."""
    esperado, obtido = "reprovado", "aprovado"
    assert obtido == esperado, (
        "este canário existe para reprovar; se você está lendo isto num relatório de "
        "sucesso, o ambiente de testes está mentindo"
    )
