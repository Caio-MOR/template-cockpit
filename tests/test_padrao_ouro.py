"""O template passa na própria régua — e o repo instanciado a partir dele também.

`tools/padrao_ouro_audit.py` implementa a norma do padrão ouro (exigências com id, peso
e check mecânico). Este teste roda o auditor sobre a raiz deste repo em modo template
(placeholders `{{...}}` permitidos) e exige placar >= 9. Depois de instanciar e trocar os
placeholders, rode sem `--template`: o mesmo número tem que sair.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
AUDITOR = RAIZ / "tools" / "padrao_ouro_audit.py"
TETO = 120


def _rodar(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(AUDITOR), *args], capture_output=True,
                          text=True, encoding="utf-8", timeout=TETO, check=False)


def test_auditor_da_placar_minimo_9_no_template():
    r = _rodar("--tipo", "cockpit", "--template", str(RAIZ))
    primeira = r.stdout.splitlines()[0] if r.stdout else ""
    assert primeira.startswith("placar: "), r.stdout + r.stderr
    placar = float(primeira.split("placar: ")[1].split("/")[0])
    assert placar >= 9.0, r.stdout


def test_auditor_sai_com_zero_no_template():
    r = _rodar("--tipo", "cockpit", "--template", str(RAIZ))
    assert r.returncode == 0, r.stdout + r.stderr


def test_tipo_e_lido_do_agents_md_sem_flag():
    r = _rodar("--template", str(RAIZ))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "(tipo cockpit," in r.stdout
