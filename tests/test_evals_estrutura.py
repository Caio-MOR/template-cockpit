"""Gate determinístico dos evals de comportamento no template (R11 adaptado por R17).

Roda sem LLM. O template é MODELO, não produção: exige apenas >= 1 positivo e
>= 1 negativo por skill (o marketplace `caio-mor` exige 3+3 — ver
`tools/eval_runner.py`/`docs/` de lá). A execução real com `claude -p` é gate
local (`python tools/eval_runner.py --skills-dir .claude/skills`), nunca CI.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "tools"))

import eval_runner  # noqa: E402

SKILLS_DIR = RAIZ / ".claude" / "skills"
EVALS_DIR = RAIZ / "evals"

RE_CAMINHO_MAQUINA = re.compile(
    r"(?i)[a-z]:[\\/]users[\\/]"
    r"|(?<![\w/])/(Users|home)/[A-Za-z0-9_.-]+(?=[/\s\"'`)\]]|$)"
)


def _skills():
    return eval_runner.descobrir_skills(SKILLS_DIR)


def _casos_por_skill():
    return {nome: eval_runner.descobrir_casos(EVALS_DIR / nome, None) for nome in _skills()}


def test_toda_skill_tem_pasta_evals():
    faltando = [nome for nome in _skills() if not (EVALS_DIR / nome).is_dir()]
    assert faltando == [], f"skills sem evals/<skill>/: {faltando}"


def test_cada_caso_tem_prompt_valido_e_name_igual_a_pasta():
    problemas = []
    for nome, casos in _casos_por_skill().items():
        for case_dir in casos:
            try:
                caso = eval_runner.parse_caso(case_dir)
            except eval_runner.ErroCasoMalFormado as e:
                problemas.append(str(e))
                continue
            if caso["nome"] != case_dir.name:
                problemas.append(f"{case_dir}: name do frontmatter difere da pasta")
    assert problemas == [], "\n".join(problemas)


def test_cada_skill_tem_ao_menos_1_positivo_e_1_negativo():
    faltando = []
    for nome, casos in _casos_por_skill().items():
        positivos = sum(1 for c in casos if "positivo" in set(eval_runner.parse_caso(c)["tags"]))
        negativos = sum(1 for c in casos if "negativo" in set(eval_runner.parse_caso(c)["tags"]))
        if positivos < 1 or negativos < 1:
            faltando.append(f"{nome}: positivos={positivos} negativos={negativos}")
    assert faltando == [], f"skills sem 1 positivo + 1 negativo: {faltando}"


def test_todo_grader_tool_used_tem_regex_compilavel():
    problemas = []
    for nome, casos in _casos_por_skill().items():
        for case_dir in casos:
            caso = eval_runner.parse_caso(case_dir)
            for g in caso["graders"]:
                if g.get("type") == "tool_used":
                    try:
                        re.compile(g["input_match"])
                    except re.error as e:
                        problemas.append(f"{case_dir}/{g['_arquivo']}: {e}")
    assert problemas == [], "\n".join(problemas)


def test_runs_max_turns_timeout_sao_inteiros_positivos():
    for nome, casos in _casos_por_skill().items():
        for case_dir in casos:
            caso = eval_runner.parse_caso(case_dir)
            for chave in ("runs", "max_turns", "timeout_seconds"):
                assert isinstance(caso[chave], int) and caso[chave] > 0, f"{case_dir}: {chave}"


def test_prompt_sem_caminho_de_maquina():
    problemas = []
    for nome, casos in _casos_por_skill().items():
        for case_dir in casos:
            texto = (case_dir / "prompt.md").read_text(encoding="utf-8")
            for n, linha in enumerate(texto.splitlines(), start=1):
                if RE_CAMINHO_MAQUINA.search(linha):
                    problemas.append(f"{case_dir}/prompt.md:{n}: caminho de máquina")
    assert problemas == [], "\n".join(problemas)
