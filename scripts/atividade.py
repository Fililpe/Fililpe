#!/usr/bin/env python3
"""Gera o painel "tail -f atividade.log" com meus últimos commits públicos.

Uso: GITHUB_TOKEN=... python3 scripts/atividade.py
Roda na GitHub Action (.github/workflows/atividade.yml), mas funciona local também.
Só usa a biblioteca padrão do Python, sem dependências externas.

Três travas para nunca mostrar repositório privado:
  1. a busca já pede só commits públicos (is:public);
  2. cada resultado é descartado se o repositório não vier com private == false;
  3. o GITHUB_TOKEN da Action só enxerga este repositório, então nem teria acesso
     a repositórios privados de outras contas.
"""
import json
import os
import sys
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gerar_svgs import FONT, OUT, TEMAS, W, svg  # noqa: E402

USUARIO = "Fililpe"
QTD = 5
API = "https://api.github.com/search/commits"
RECIFE = timezone(timedelta(hours=-3))


def buscar_commits():
    q = f"author:{USUARIO} is:public merge:false"
    url = API + "?" + urllib.parse.urlencode(
        {"q": q, "sort": "author-date", "order": "desc", "per_page": 30})
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": f"{USUARIO}-readme-atividade",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)["items"]


def filtrar(itens):
    vistos, commits = set(), []
    for it in itens:
        repo = it.get("repository") or {}
        if repo.get("private") is not False:  # trava 2: na dúvida, fica de fora
            continue
        if it["sha"] in vistos:  # o mesmo commit pode aparecer no fork e no original
            continue
        vistos.add(it["sha"])
        dono, nome = repo["owner"]["login"], repo["name"]
        commits.append({
            "repo": nome if dono == USUARIO else f"{dono}/{nome}",
            "msg": it["commit"]["message"].splitlines()[0] if it["commit"]["message"] else "",
            "data": datetime.fromisoformat(it["commit"]["author"]["date"]),
        })
        if len(commits) == QTD:
            break
    return commits


def limpar(texto, limite):
    """Tira caracteres de controle e corta o texto para caber na coluna."""
    texto = "".join(ch for ch in texto if unicodedata.category(ch)[0] != "C").strip()
    return texto if len(texto) <= limite else texto[:limite - 1] + "…"


def relativa(data, agora):
    """Data relativa em dias, contados no fuso de Recife (UTC-3, sem horário de verão)."""
    dias = (agora.astimezone(RECIFE).date() - data.astimezone(RECIFE).date()).days
    if dias <= 0:
        return "hoje"
    if dias == 1:
        return "ontem"
    if dias < 14:
        return f"há {dias} dias"
    if dias < 60:
        return f"há {dias // 7} semanas"
    if dias < 365:
        return f"há {dias // 30} meses"
    return f"há {dias // 365} ano{'s' if dias >= 730 else ''}"


def painel(c, commits, agora):
    tam, cw = 14, 8.4  # tamanho da fonte e largura aproximada de um caractere
    x_data, x_repo, x_msg = 28, 28 + 15 * cw, 28 + 44 * cw
    lim_repo, lim_msg = 27, int((W - 28 - x_msg) // cw)
    h = 62 + len(commits) * 26 + 34
    estilo = f"""
text {{ font-family: {FONT}; font-size: {tam}px; }}
.data {{ fill: {c['fraco']}; }}
.repo {{ fill: {c['azul']}; }}
.msg {{ fill: {c['texto']}; }}
.linha {{ opacity: 0; animation: surge .4s ease-out forwards; }}
.cursor {{ fill: {c['verde']}; opacity: 0; animation: surge .01s {0.3 + len(commits) * 0.35:.2f}s forwards,
  pisca 1s steps(1) {0.3 + len(commits) * 0.35:.2f}s infinite; }}
@keyframes surge {{ to {{ opacity: 1; }} }}
@keyframes pisca {{ 50% {{ opacity: 0; }} }}
"""
    partes = [
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="10" fill="{c["term"]}" stroke="{c["borda"]}"/>',
        f'<path d="M0.5 36 V10.5 a10 10 0 0 1 10 -10 H{W-10.5} a10 10 0 0 1 10 10 V36 Z" fill="{c["barra"]}" stroke="{c["borda"]}"/>',
        '<circle cx="22" cy="18" r="6" fill="#ff5f57"/>',
        '<circle cx="42" cy="18" r="6" fill="#febc2e"/>',
        '<circle cx="62" cy="18" r="6" fill="#28c840"/>',
        f'<text x="{W/2}" y="23" text-anchor="middle" style="font-size:13px" fill="{c["fraco"]}">atividade.log</text>',
    ]
    y = 66
    for i, cm in enumerate(commits):
        partes.append(
            f'<g class="linha" style="animation-delay:{0.3 + i * 0.35:.2f}s">'
            f'<text x="{x_data}" y="{y}" class="data">[{escape(relativa(cm["data"], agora))}]</text>'
            f'<text x="{x_repo:.1f}" y="{y}" class="repo">{escape(limpar(cm["repo"], lim_repo))}</text>'
            f'<text x="{x_msg:.1f}" y="{y}" class="msg">{escape(limpar(cm["msg"], lim_msg))}</text></g>')
        y += 26
    partes.append(f'<rect class="cursor" x="{x_data}" y="{y-tam+2}" width="{cw}" height="{tam+2}"/>')
    resumo = "; ".join(f'{cm["repo"]}: {limpar(cm["msg"], 120)}' for cm in commits)
    return svg(W, h, "\n".join(partes), estilo, f"Meus últimos commits públicos. {resumo}")


def main():
    commits = filtrar(buscar_commits())
    if not commits:
        # Melhor falhar do que sobrescrever o painel com uma lista vazia.
        sys.exit("Nenhum commit público encontrado, SVG mantido como está.")
    agora = datetime.now(timezone.utc)
    for tema, c in TEMAS.items():
        (OUT / f"atividade-{tema}.svg").write_text(painel(c, commits, agora), encoding="utf-8")
    for cm in commits:
        print(f'[{relativa(cm["data"], agora)}] {cm["repo"]}: {cm["msg"]}')


if __name__ == "__main__":
    main()
