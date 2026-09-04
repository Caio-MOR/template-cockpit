#!/usr/bin/env python3
"""Hook PreToolUse (matcher `Edit|Write|MultiEdit`) — bloqueia `.env` e segredo em texto.

%% formato: cadeia — lê o JSON do stdin, decide, sai.

Bloqueia (exit 2, motivo em pt-BR no stderr):
  - `tool_input.file_path` com basename `.env` ou começando com `.env.`
    (exceto `.env.example`, que é template público).
  - conteúdo (`content`/`new_string`, inclusive dentro de `edits[]` do MultiEdit)
    casando com padrão de chave/segredo conhecido.

Exceção: arquivo dentro de `tests/` cujo conteúdo contém a palavra `SINTETICO` passa
— é como os próprios testes deste hook geram segredo de mentira sem se autobloquear.

Falha aberta: qualquer exceção interna sai com exit 0 e aviso no stderr.
"""
import json
import re
import sys

PADROES_SEGREDO = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
    re.compile(r"github_pat_"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY"),
    re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.eyJ"),
    re.compile(r"SUPABASE_SERVICE_ROLE_KEY\s*=\s*\S{20,}"),
    re.compile(r"x-api-key\s*[:=]\s*['\"]?[A-Za-z0-9_-]{20,}"),
]


def _basename(path: str) -> str:
    return path.replace("\\", "/").rsplit("/", 1)[-1]


def _e_arquivo_env_proibido(file_path: str) -> bool:
    if not file_path:
        return False
    nome = _basename(file_path)
    if nome == ".env.example":
        return False
    return nome == ".env" or nome.startswith(".env.")


def _conteudos(tool_input: dict) -> str:
    partes = []
    for chave in ("content", "new_string"):
        valor = tool_input.get(chave)
        if isinstance(valor, str):
            partes.append(valor)
    for edicao in tool_input.get("edits", []) or []:
        if isinstance(edicao, dict):
            valor = edicao.get("new_string")
            if isinstance(valor, str):
                partes.append(valor)
    return "\n".join(partes)


def _e_teste_sintetico(file_path: str, texto: str) -> bool:
    caminho = "/" + (file_path or "").replace("\\", "/")
    return "/tests/" in caminho and "SINTETICO" in texto


def _achado_de_segredo(texto: str):
    for padrao in PADROES_SEGREDO:
        if padrao.search(texto):
            return padrao.pattern
    return None


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        tool_input = payload.get("tool_input", {}) or {}
        file_path = tool_input.get("file_path", "") or ""

        if _e_arquivo_env_proibido(file_path):
            print(
                f"Bloqueado: escrita em {file_path or '(.env)'} — segredo só em "
                ".env, nunca gravado por ferramenta automática. Edite manualmente.",
                file=sys.stderr,
            )
            sys.exit(2)

        texto = _conteudos(tool_input)
        if texto and not _e_teste_sintetico(file_path, texto):
            padrao = _achado_de_segredo(texto)
            if padrao:
                print(
                    f"Bloqueado: conteúdo casa com padrão de segredo ({padrao}). "
                    "Remova a credencial do texto antes de gravar.",
                    file=sys.stderr,
                )
                sys.exit(2)

        sys.exit(0)
    except SystemExit:
        raise
    except Exception as exc:  # falha aberta: bug no hook não trava o leigo
        print(f"guarda_segredo: aviso, hook falhou aberto ({exc})", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
