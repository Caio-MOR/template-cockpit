"""Gate do CI: actions pinadas NO SHA que este repo revisou, e permissões mínimas.

Validar só a *forma* do pin (`uses: x@<40 hex> # vN`) deixa passar SHA trocado por
outro dono com o comentário de versão mantido. Por isso a tabela PINS: (action, tag) ->
SHA. Atualizar a tabela no mesmo PR que atualiza o workflow é justamente a revisão que
se quer forçar. O glob é `*.y*ml` porque o GitHub aceita `.yml` e `.yaml`.

O parse do `permissions` é por linha, e desde T3 isso é escolha e não restrição:
`pyyaml` entrou no `requirements.txt` para o runner de eval. Trocar este parse por
`yaml.safe_load` é melhoria possível, deixada de fora do escopo de T3.
"""
import ast
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SETTINGS = RAIZ / ".claude" / "settings.json"
REQUIREMENTS = RAIZ / "requirements.txt"
TOOLS = RAIZ / "tools"
WORKFLOWS = sorted((RAIZ / ".github" / "workflows").glob("*.y*ml"))

# (action, tag) -> SHA revisado. Par fora da tabela reprova; par na tabela que nenhum
# workflow usa também reprova (tabela limpa).
PINS = {
    ("actions/checkout", "v7.0.1"): "3d3c42e5aac5ba805825da76410c181273ba90b1",
    ("actions/setup-python", "v7.0.0"): "5fda3b95a4ea91299a34e894583c3862153e4b97",
}

USES = re.compile(
    r"^\s*(?:-\s+)?uses:\s*(?P<action>[^@\s]+)@(?P<sha>[0-9a-f]{40})\s+#\s*(?P<tag>v[\w.\-]+)\s*$"
)


def _permissions_contents(texto: str) -> str | None:
    """Valor de `contents:` dentro do bloco `permissions:` de topo, ou None."""
    linhas = texto.splitlines()
    for i, linha in enumerate(linhas):
        if linha.rstrip() != "permissions:":
            continue
        for seguinte in linhas[i + 1:]:
            if seguinte.strip() and not seguinte.startswith((" ", "\t")):
                break  # acabou o bloco indentado
            achado = re.match(r"\s+contents:\s*(\S+)\s*$", seguinte)
            if achado:
                return achado.group(1)
    return None


def _divergencias(nome: str, texto: str, pins: dict) -> list[str]:
    """Linhas `uses:` fora da forma pinada ou com SHA diferente da tabela. Função pura:
    é o que permite provar com texto sintético que o contrato reprova."""
    problemas = []
    for n, linha in enumerate(texto.splitlines(), 1):
        if "uses:" not in linha:
            continue
        achado = USES.match(linha)
        if not achado:
            problemas.append(f"{nome}:{n} action não pinada por SHA: {linha.strip()}")
            continue
        chave = (achado.group("action"), achado.group("tag"))
        esperado = pins.get(chave)
        if esperado is None:
            problemas.append(f"{nome}:{n} usa {chave[0]}@{chave[1]}, par não declarado em PINS")
        elif esperado != achado.group("sha"):
            problemas.append(
                f"{nome}:{n} {chave[0]} {chave[1]} pinada em {achado.group('sha')}, esperado {esperado}"
            )
    return problemas


def _pares_usados(texto: str) -> set:
    return {
        (m.group("action"), m.group("tag"))
        for m in (USES.match(l) for l in texto.splitlines()) if m
    }


# ---------------------------------------------------------------- workflows reais


def test_existe_workflow_de_ci():
    assert WORKFLOWS, "nenhum workflow em .github/workflows/"


def test_toda_action_pinada_no_sha_da_tabela():
    problemas = []
    vistos = set()
    for wf in WORKFLOWS:
        texto = wf.read_text(encoding="utf-8")
        problemas += _divergencias(wf.name, texto, PINS)
        vistos |= _pares_usados(texto)
    assert not problemas, "\n".join(problemas)
    orfas = sorted(PINS.keys() - vistos)
    assert not orfas, f"PINS declara par que nenhum workflow usa (limpar a tabela): {orfas}"


def test_todo_workflow_declara_permissions_contents_read():
    """Workflow sem `permissions` herda o token amplo do repositório."""
    faltando = [
        wf.name for wf in WORKFLOWS
        if _permissions_contents(wf.read_text(encoding="utf-8")) != "read"
    ]
    assert not faltando, (
        "workflow sem `permissions:` de topo com `contents: read`: " + ", ".join(faltando)
    )


def test_ci_chama_o_veredito_e_nao_o_pytest_direto():
    """Quem julga a suíte não pode ser o próprio pytest: o job da suíte invoca
    `tools/gate_veredito.py`, e nenhum step roda `pytest` a seco."""
    texto = (RAIZ / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
    assert "tools/gate_veredito.py" in texto
    corridas = [l.split("run:", 1)[1].strip() for l in texto.splitlines() if "run:" in l]
    assert not any(c in ("pytest -q", "pytest") for c in corridas), corridas
    assert "working-directory" not in texto, "gate rodado de subpasta não mede a árvore inteira"


def test_settings_json_parseavel():
    """settings.json quebrado derrubaria os hooks em silêncio."""
    dados = json.loads(SETTINGS.read_text(encoding="utf-8"))
    assert isinstance(dados, dict) and "hooks" in dados


# ---------------------------------------------------------------- sintético: reprova


def test_sintetico_uses_por_tag_ou_sha_de_outro_dono_reprova():
    por_tag = "steps:\n  - uses: actions/checkout@v4\n"
    assert _divergencias("x.yml", por_tag, PINS) == [
        "x.yml:2 action não pinada por SHA: - uses: actions/checkout@v4"
    ]
    sha_falso = "  - uses: actions/checkout@" + "0" * 40 + " # v7.0.1\n"
    [problema] = _divergencias("x.yml", sha_falso, PINS)
    assert "pinada em " + "0" * 40 in problema
    fora_da_tabela = "  - uses: alguem/acao@" + "a" * 40 + " # v1.0.0\n"
    assert "par não declarado em PINS" in _divergencias("x.yml", fora_da_tabela, PINS)[0]
    assert _permissions_contents("name: x\njobs:\n  a: {}\n") is None
    assert _permissions_contents("permissions:\n  contents: read\njobs: {}\n") == "read"


# ------------------------------------------------- dependência externa declarada


# Import de terceiro -> nome da distribuição no `requirements.txt`. Módulo importado
# fora deste mapa reprova: acrescentar a entrada é a revisão que se quer forçar.
MODULO_PARA_DISTRIBUICAO = {"yaml": "pyyaml"}
RE_NOME_DE_PACOTE = re.compile(r"[A-Za-z0-9._-]+")


def _imports_de_terceiro(arquivo: Path, locais: set[str]) -> set[str]:
    raizes: set[str] = set()
    for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8"))):
        if isinstance(no, ast.Import):
            raizes.update(a.name.split(".")[0] for a in no.names)
        elif isinstance(no, ast.ImportFrom) and no.level == 0 and no.module:
            raizes.add(no.module.split(".")[0])
    return {r for r in raizes if r not in sys.stdlib_module_names and r not in locais}


def _distribuicoes_declaradas() -> set[str]:
    nomes: set[str] = set()
    for linha in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        sem_comentario = linha.split("#")[0].strip()
        casado = RE_NOME_DE_PACOTE.match(sem_comentario)
        if casado:
            nomes.add(casado.group(0).lower())
    return nomes


def test_toda_dependencia_externa_de_tools_declarada_no_requirements():
    """Todo import de terceiro em `tools/` aparece no `requirements.txt`.

    O furo que fecha: o runner de eval passou a importar `yaml` numa cópia vinda
    de outro repo, onde a dependência era declarada — aqui não era. Venv limpa
    quebraria no import e a suíte local passaria, porque a máquina do autor já
    tinha o pacote instalado por outro caminho.
    """
    declaradas = _distribuicoes_declaradas()
    locais = {f.stem for f in TOOLS.glob("*.py")}
    faltando = []
    for arquivo in sorted(TOOLS.glob("*.py")):
        for modulo in sorted(_imports_de_terceiro(arquivo, locais)):
            distribuicao = MODULO_PARA_DISTRIBUICAO.get(modulo)
            if distribuicao is None:
                faltando.append(
                    f"{arquivo.name}: import `{modulo}` sem entrada em "
                    "MODULO_PARA_DISTRIBUICAO deste teste"
                )
            elif distribuicao.lower() not in declaradas:
                faltando.append(
                    f"{arquivo.name}: import `{modulo}` exige `{distribuicao}` "
                    "declarado no requirements.txt"
                )
    assert faltando == [], "; ".join(faltando)


def test_sintetico_import_nao_declarado_reprova(tmp_path):
    """O gate acima morde: arquivo sintético que importa pacote fora do requirements."""
    falso = tmp_path / "usa_requests.py"
    falso.write_text("""import requests
import json
""", encoding="utf-8")
    assert _imports_de_terceiro(falso, set()) == {"requests"}
    assert "requests" not in _distribuicoes_declaradas()
    assert "pyyaml" in _distribuicoes_declaradas()
