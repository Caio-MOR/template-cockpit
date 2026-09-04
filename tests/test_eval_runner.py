"""Testes do parser de casos e dos graders do runner de bolso (R12).

Nada aqui chama `claude`: os graders são exercitados sobre transcrições
`stream-json` sintéticas (`tests/fixtures/`). Inclui o teste de mutação (um
grader negativo com um `tool_use` de Skill na transcrição precisa reprovar; sem
ele, aprovar) e o teste do exit code 2 com `claude` ausente do PATH.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
FIXTURES = RAIZ / "tests" / "fixtures"
sys.path.insert(0, str(RAIZ / "tools"))

import eval_runner  # noqa: E402


def _carregar_transcricao(nome: str) -> list[dict]:
    texto = (FIXTURES / nome).read_text(encoding="utf-8")
    return [json.loads(l) for l in texto.splitlines() if l.strip()]


# ---------------------------------------------------------------------------
# Parser de prompt.md / graders/*.md


def test_parse_caso_le_frontmatter_e_graders(tmp_path):
    case_dir = tmp_path / "caso-x"
    (case_dir / "graders").mkdir(parents=True)
    (case_dir / "prompt.md").write_text(
        "---\nname: caso-x\ntags: [positivo]\nruns: 3\nmax_turns: 3\n"
        "timeout_seconds: 180\n---\n\nRoda o os audit no meu projeto.\n",
        encoding="utf-8",
    )
    (case_dir / "graders" / "disparo.md").write_text(
        "---\ntype: tool_used\ntool: Skill\n"
        "input_match: '\"skill\"\\s*:\\s*\"(?:[\\w-]+:)?os-audit\"'\nmin: 1\n---\n\njustificativa\n",
        encoding="utf-8",
    )
    caso = eval_runner.parse_caso(case_dir)
    assert caso["nome"] == "caso-x"
    assert caso["tags"] == ["positivo"]
    assert caso["runs"] == caso["max_turns"] == 3
    assert caso["timeout_seconds"] == 180
    assert caso["prompt"] == "Roda o os audit no meu projeto."
    assert len(caso["graders"]) == 1
    assert caso["graders"][0]["type"] == "tool_used"


def test_parse_caso_sem_frontmatter_reprova(tmp_path):
    case_dir = tmp_path / "caso-y"
    (case_dir / "graders").mkdir(parents=True)
    (case_dir / "prompt.md").write_text("sem frontmatter nenhum\n", encoding="utf-8")
    (case_dir / "graders" / "disparo.md").write_text(
        "---\ntype: tool_used\ntool: Skill\ninput_match: 'x'\nmin: 1\n---\n", encoding="utf-8"
    )
    with pytest.raises(eval_runner.ErroCasoMalFormado):
        eval_runner.parse_caso(case_dir)


def test_parse_caso_com_runs_nao_inteiro_reprova(tmp_path):
    case_dir = tmp_path / "caso-z"
    (case_dir / "graders").mkdir(parents=True)
    (case_dir / "prompt.md").write_text(
        "---\nname: caso-z\ntags: [negativo]\nruns: tres\nmax_turns: 3\n"
        "timeout_seconds: 180\n---\n\nprompt\n", encoding="utf-8",
    )
    (case_dir / "graders" / "disparo.md").write_text(
        "---\ntype: tool_used\ntool: Skill\ninput_match: 'x'\nmin: 0\nmax: 0\n---\n", encoding="utf-8"
    )
    with pytest.raises(eval_runner.ErroCasoMalFormado):
        eval_runner.parse_caso(case_dir)


def test_parse_caso_com_regex_incompilavel_reprova(tmp_path):
    case_dir = tmp_path / "caso-w"
    (case_dir / "graders").mkdir(parents=True)
    (case_dir / "prompt.md").write_text(
        "---\nname: caso-w\ntags: [positivo]\nruns: 3\nmax_turns: 3\n"
        "timeout_seconds: 180\n---\n\nprompt\n", encoding="utf-8",
    )
    (case_dir / "graders" / "disparo.md").write_text(
        "---\ntype: tool_used\ntool: Skill\ninput_match: '(['\nmin: 1\n---\n", encoding="utf-8"
    )
    with pytest.raises(eval_runner.ErroCasoMalFormado):
        eval_runner.parse_caso(case_dir)


# ---------------------------------------------------------------------------
# Graders sobre transcrições sintéticas — mutação (o coração do R12)


def test_grader_negativo_reprova_quando_skill_disparou():
    """Mutação: transcrição COM tool_use de Skill os-audit + grader negativo => reprova."""
    linhas = _carregar_transcricao("transcript_com_skill_os_audit.jsonl")
    grader = {
        "type": "tool_used", "tool": "Skill",
        "input_match": r'"skill"\s*:\s*"(?:[\w-]+:)?os-audit"',
        "min": 0, "max": 0, "_arquivo": "disparo.md",
    }
    veredito = eval_runner.avaliar_grader(grader, linhas, Path("."))
    assert veredito["passou"] is False, "grader negativo deveria reprovar com skill disparada"


def test_grader_negativo_aprova_quando_skill_nao_disparou():
    """Sem mutação: transcrição SEM tool_use de Skill + o mesmo grader negativo => aprova."""
    linhas = _carregar_transcricao("transcript_sem_skill.jsonl")
    grader = {
        "type": "tool_used", "tool": "Skill",
        "input_match": r'"skill"\s*:\s*"(?:[\w-]+:)?os-audit"',
        "min": 0, "max": 0, "_arquivo": "disparo.md",
    }
    veredito = eval_runner.avaliar_grader(grader, linhas, Path("."))
    assert veredito["passou"] is True, "grader negativo deveria aprovar sem skill disparada"


def test_grader_positivo_aprova_quando_skill_disparou():
    linhas = _carregar_transcricao("transcript_com_skill_os_audit.jsonl")
    grader = {
        "type": "tool_used", "tool": "Skill",
        "input_match": r'"skill"\s*:\s*"(?:[\w-]+:)?os-audit"',
        "min": 1, "_arquivo": "disparo.md",
    }
    veredito = eval_runner.avaliar_grader(grader, linhas, Path("."))
    assert veredito["passou"] is True


def test_grader_positivo_reprova_quando_skill_nao_disparou():
    linhas = _carregar_transcricao("transcript_sem_skill.jsonl")
    grader = {
        "type": "tool_used", "tool": "Skill",
        "input_match": r'"skill"\s*:\s*"(?:[\w-]+:)?os-audit"',
        "min": 1, "_arquivo": "disparo.md",
    }
    veredito = eval_runner.avaliar_grader(grader, linhas, Path("."))
    assert veredito["passou"] is False


def test_grader_positivo_nao_confunde_skill_de_nome_parecido():
    """`os-audit` não pode casar com `os-audit-v2` nem o contrário — a regex é ancorada nas aspas."""
    linhas = [{"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Skill", "input": {"skill": "os-audit-v2"}}
    ]}}]
    grader = {
        "type": "tool_used", "tool": "Skill",
        "input_match": r'"skill"\s*:\s*"(?:[\w-]+:)?os-audit"',
        "min": 1, "_arquivo": "disparo.md",
    }
    veredito = eval_runner.avaliar_grader(grader, linhas, Path("."))
    assert veredito["passou"] is False


def test_grader_regex_sobre_ultima_mensagem_do_assistente():
    linhas = _carregar_transcricao("transcript_sem_skill.jsonl")
    grader_ok = {"type": "regex", "pattern": r"sem usar nenhuma skill", "_arquivo": "r.md"}
    grader_fail = {"type": "regex", "pattern": r"isso nao aparece em lugar nenhum", "_arquivo": "r.md"}
    assert eval_runner.avaliar_grader(grader_ok, linhas, Path("."))["passou"] is True
    assert eval_runner.avaliar_grader(grader_fail, linhas, Path("."))["passou"] is False


def test_grader_file_exists(tmp_path):
    (tmp_path / "relatorio.md").write_text("ok", encoding="utf-8")
    grader_ok = {"type": "file_exists", "glob": "relatorio.md", "_arquivo": "f.md"}
    grader_fail = {"type": "file_exists", "glob": "nao-existe.md", "_arquivo": "f.md"}
    assert eval_runner.avaliar_grader(grader_ok, [], tmp_path)["passou"] is True
    assert eval_runner.avaliar_grader(grader_fail, [], tmp_path)["passou"] is False


def test_grader_tipo_nao_suportado_levanta_erro():
    with pytest.raises(eval_runner.ErroCasoMalFormado):
        eval_runner.avaliar_grader({"type": "llm", "_arquivo": "l.md"}, [], Path("."))


# ---------------------------------------------------------------------------
# `claude` ausente do PATH => exit 2


def test_main_sem_claude_no_path_retorna_2(monkeypatch, tmp_path):
    monkeypatch.setattr(eval_runner.shutil, "which", lambda nome: None)
    ret = eval_runner.main(["--all"])
    assert ret == 2


def test_montar_comando_inclui_plugin_dir_quando_presente():
    cmd = eval_runner.montar_comando("claude", "oi", 3, Path("/tmp/plugin-x"))
    assert "--plugin-dir" in cmd
    assert str(Path("/tmp/plugin-x")) in cmd


def test_montar_comando_sem_plugin_dir_no_modo_skills():
    cmd = eval_runner.montar_comando("claude", "oi", 3, None)
    assert "--plugin-dir" not in cmd
