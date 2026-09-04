#!/usr/bin/env python3
"""Hook PreToolUse (matcher `Bash`) — bloqueia comandos git perigosos.

%% formato: cadeia — lê o JSON do stdin, decide, sai. Sem ramos que dependam de
resultado de etapa anterior; cada checagem é independente das outras.

Bloqueia (exit 2, motivo em pt-BR no stderr):
  a) `git commit` com a branch atual do cwd sendo `main`/`master`.
  b) `git push` com `--force`, `-f` ou `--force-with-lease`.
  c) qualquer comando com `--no-verify`.
  d) `git push` cujo destino explícito é `main`/`master`.

Falha aberta: qualquer exceção interna sai com exit 0 e aviso no stderr — um hook
que trava por bug próprio não pode travar quem não sabe depurar hook.
"""
import json
import re
import subprocess
import sys

TETO_SUBPROC = 10


def _branch_atual(cwd: str):
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd or ".", capture_output=True, text=True, timeout=TETO_SUBPROC,
        )
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return r.stdout.strip()


def _e_git_commit(cmd: str) -> bool:
    return bool(re.search(r"(?<![\w-])git\s+commit\b", cmd))


def _e_git_push(cmd: str) -> bool:
    return bool(re.search(r"(?<![\w-])git\s+push\b", cmd))


def _tem_flag_force(cmd: str) -> bool:
    return bool(re.search(r"(?<!\S)(--force(-with-lease)?|-f)(?!\S)", cmd))


def _tem_no_verify(cmd: str) -> bool:
    return "--no-verify" in cmd


def _push_destino_main_ou_master(cmd: str) -> bool:
    for trecho in re.split(r"&&|\|\||;", cmd):
        if not _e_git_push(trecho):
            continue
        resto = re.sub(r"^.*?(?<![\w-])git\s+push\b", "", trecho, count=1)
        if re.search(r"(?<![\w/-])(HEAD:)?(refs/heads/)?(main|master)(?![\w/-])", resto):
            return True
    return False


def _commit_em_main_ou_master(cmd: str, cwd: str) -> bool:
    if not _e_git_commit(cmd):
        return False
    branch = _branch_atual(cwd)
    return branch in ("main", "master")


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        tool_input = payload.get("tool_input", {}) or {}
        cmd = tool_input.get("command", "") or ""
        cwd = payload.get("cwd") or "."

        if _commit_em_main_ou_master(cmd, cwd):
            print(
                "Bloqueado: commit direto na branch main/master. Crie uma branch de "
                "feature (`git checkout -b ...`) antes de commitar.",
                file=sys.stderr,
            )
            sys.exit(2)

        if _e_git_push(cmd) and _tem_flag_force(cmd):
            print(
                "Bloqueado: `git push` com --force/-f/--force-with-lease reescreve "
                "histórico remoto. Não é permitido por hook — peça ao dono do repo.",
                file=sys.stderr,
            )
            sys.exit(2)

        if _tem_no_verify(cmd):
            print(
                "Bloqueado: --no-verify pula de propósito os hooks de verificação do "
                "git. Não é permitido neste repo.",
                file=sys.stderr,
            )
            sys.exit(2)

        if _push_destino_main_ou_master(cmd):
            print(
                "Bloqueado: push com destino explícito main/master. Abra PR a partir "
                "de uma branch de feature.",
                file=sys.stderr,
            )
            sys.exit(2)

        sys.exit(0)
    except SystemExit:
        raise
    except Exception as exc:  # falha aberta: bug no hook não trava o leigo
        print(f"guarda_bash: aviso, hook falhou aberto ({exc})", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
