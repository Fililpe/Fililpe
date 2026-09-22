#!/usr/bin/env python3
"""Gera os SVGs do README (header, títulos de seção e cards) em versão dark e light.

Uso: python3 scripts/gerar_svgs.py
Tudo é estático e fica versionado em assets/. Nenhum serviço externo.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
W = 860

TEMAS = {
    "dark": dict(bg="#0d1117", term="#161b22", barra="#21262d", borda="#30363d",
                 texto="#c9d1d9", fraco="#8b949e", verde="#3fb950", azul="#58a6ff",
                 roxo="#bc8cff", amarelo="#d29922"),
    "light": dict(bg="#ffffff", term="#f6f8fa", barra="#eaeef2", borda="#d0d7de",
                  texto="#1f2328", fraco="#656d76", verde="#1a7f37", azul="#0969da",
                  roxo="#8250df", amarelo="#9a6700"),
}

PROJETOS = [
    ("safe-console-c", "C", "#555555",
     ["Sanitização de entrada, mascaramento de", "dados sensíveis e cifras César/XOR."],
     "fgets · validação de senha · xor"),
    ("cifrario", "Python", "#3572A5",
     ["Cifras clássicas com quebra de César por", "força bruta e análise de frequência."],
     "césar · vigenère · atbash"),
    ("grupo4-ansible-guia", "Ansible", "#EE0000",
     ["Guia de Ansible feito em grupo: playbooks,", "roles, Vault e hardening de SSH."],
     "playbooks · vault · jinja2"),
    ("Vagrant-Jenkins", "Shell", "#89e051",
     ["Lab com duas VMs (Jenkins e produção) e", "pipeline CI/CD para uma API Node.js."],
     "vagrant · jenkins · node"),
    ("pipeline-jenkins-nodejs", "Jenkins", "#D24939",
     ["Pipeline com Jenkinsfile e GitHub Actions,", "com build e testes em Jest."],
     "ci/cd · actions · jest"),
    ("Terraform", "HCL", "#844FBA",
     ["Infraestrutura como código: buckets na", "AWS (S3) e no GCP, com outputs."],
     "terraform · aws · gcp"),
]

SECOES = {
    "sobre": "~/sobre",
    "lab": "~/homelab",
    "projetos": "~/projetos",
    "estudando": "~/estudando",
    "stack": "~/stack",
    "contato": "~/contato",
}


def svg(w, h, corpo, estilo, titulo):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(titulo)}">\n'
            f'<title>{escape(titulo)}</title>\n<style>\n{estilo}\n</style>\n{corpo}\n</svg>\n')


def header(c):
    """Janela de terminal com os comandos sendo digitados e a saída aparecendo."""
    h = 250
    tam, cw = 16, 9.6  # tamanho da fonte e largura aproximada de um caractere
    x0, x_cmd = 28, 28 + 2 * cw  # "$ " ocupa dois caracteres
    linhas = [
        # (tipo, texto, início da animação em s)
        ("cmd", "whoami", 0.4),
        ("out", "Filipe Sousa, estudante de Cibersegurança na CESAR School", 1.5),
        ("cmd", "cat foco.txt", 2.2),
        ("out", "AppSec · Pentest · Blue/Red team · DevOps", 3.5),
        ("cmd", "echo $LOCAL", 4.2),
        ("out", "Recife, PE", 5.3),
    ]
    estilo = f"""
text {{ font-family: {FONT}; font-size: {tam}px; }}
.p {{ fill: {c['verde']}; }}
.cmd {{ fill: {c['texto']}; }}
.out {{ fill: {c['fraco']}; opacity: 0; animation: surge .4s ease-out forwards; }}
.capa {{ fill: {c['term']}; animation-fill-mode: forwards; }}
.linha {{ opacity: 0; animation: surge .01s forwards; }}
.cursor {{ fill: {c['verde']}; opacity: 0; animation: surge .01s 6s forwards, pisca 1s steps(1) 6s infinite; }}
@keyframes surge {{ to {{ opacity: 1; }} }}
@keyframes pisca {{ 50% {{ opacity: 0; }} }}
"""
    partes = [
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="10" fill="{c["term"]}" stroke="{c["borda"]}"/>',
        f'<path d="M0.5 36 V10.5 a10 10 0 0 1 10 -10 H{W-10.5} a10 10 0 0 1 10 10 V36 Z" fill="{c["barra"]}" stroke="{c["borda"]}"/>',
        '<circle cx="22" cy="18" r="6" fill="#ff5f57"/>',
        '<circle cx="42" cy="18" r="6" fill="#febc2e"/>',
        '<circle cx="62" cy="18" r="6" fill="#28c840"/>',
        f'<text x="{W/2}" y="23" text-anchor="middle" style="font-size:13px" fill="{c["fraco"]}">filipe@cesar: ~</text>',
    ]
    y = 70
    n = 0
    for tipo, texto, t in linhas:
        if tipo == "cmd":
            largura = len(texto) * cw + 4
            dur = 0.08 * len(texto)
            partes.append(
                f'<g class="linha" style="animation-delay:{t}s">'
                f'<text x="{x0}" y="{y}" class="p">$</text>'
                f'<text x="{x_cmd}" y="{y}" class="cmd">{escape(texto)}</text>'
                f'<rect class="capa" x="{x_cmd}" y="{y-tam}" width="{largura}" height="{tam+6}" '
                f'style="animation-name:dig{n};animation-duration:{dur:.2f}s;'
                f'animation-delay:{t}s;animation-timing-function:steps({len(texto)})"/></g>')
            estilo += f"@keyframes dig{n} {{ to {{ transform: translateX({largura:.1f}px); }} }}\n"
            n += 1
        else:
            partes.append(f'<text x="{x0}" y="{y}" class="out" style="animation-delay:{t}s">{escape(texto)}</text>')
        y += 28
    partes.append(f'<g class="cursor"><text x="{x0}" y="{y}" class="p">$</text>'
                  f'<rect x="{x_cmd}" y="{y-tam+2}" width="{cw}" height="{tam+2}"/></g>')
    return svg(W, h, "\n".join(partes), estilo, "Terminal: Filipe Sousa, estudante de Cibersegurança na CESAR School. AppSec, Pentest, Blue/Red team e DevOps. Recife, PE.")


def secao(c, rotulo):
    """Título de seção: prompt + caminho + linha com um brilho percorrendo."""
    h = 40
    x_linha = 40 + len(rotulo) * 11.4 + 24
    estilo = f"""
text {{ font-family: {FONT}; font-size: 19px; font-weight: 600; }}
.base {{ stroke: {c['borda']}; stroke-width: 1.5; }}
.brilho {{ stroke: {c['verde']}; stroke-width: 1.5; stroke-dasharray: 90 {W}; animation: corre 6s linear infinite; }}
.cursor {{ fill: {c['verde']}; animation: pisca 1.1s steps(1) infinite; }}
@keyframes corre {{ from {{ stroke-dashoffset: 90; }} to {{ stroke-dashoffset: -{W}; }} }}
@keyframes pisca {{ 50% {{ opacity: 0; }} }}
"""
    corpo = (f'<text x="2" y="27" fill="{c["verde"]}">❯</text>'
             f'<text x="26" y="27" fill="{c["azul"]}">{escape(rotulo)}</text>'
             f'<rect class="cursor" x="{x_linha-18}" y="12" width="9" height="18"/>'
             f'<line class="base" x1="{x_linha}" y1="21" x2="{W}" y2="21"/>'
             f'<line class="brilho" x1="{x_linha}" y1="21" x2="{W}" y2="21"/>')
    return svg(W, h, corpo, estilo, rotulo)


def card(c, nome, lang, cor_lang, desc, tags):
    w, h = 420, 128
    estilo = f"""
text {{ font-family: {FONT}; }}
.nome {{ font-size: 15px; font-weight: 700; fill: {c['azul']}; }}
.desc {{ font-size: 12.5px; fill: {c['texto']}; }}
.tags {{ font-size: 11.5px; fill: {c['fraco']}; }}
.lang {{ font-size: 12px; fill: {c['fraco']}; }}
.moldura {{ fill: {c['term']}; stroke: {c['borda']}; }}
.canto {{ stroke: {c['verde']}; stroke-width: 2; fill: none; stroke-dasharray: 70 1030; animation: corre 9s linear infinite; }}
@keyframes corre {{ from {{ stroke-dashoffset: 0; }} to {{ stroke-dashoffset: -1100; }} }}
"""
    perimetro = f"M8.5 0.5 H{w-8.5} a8 8 0 0 1 8 8 V{h-8.5} a8 8 0 0 1 -8 8 H8.5 a8 8 0 0 1 -8 -8 V8.5 a8 8 0 0 1 8 -8 Z"
    corpo = [
        f'<rect class="moldura" x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="8"/>',
        f'<path class="canto" d="{perimetro}"/>',
        f'<text x="20" y="34" fill="{c["verde"]}" style="font-size:15px;font-weight:700">▸</text>',
        f'<text x="38" y="34" class="nome">{escape(nome)}</text>',
        f'<circle cx="{w-20-len(lang)*7.2-14}" cy="29.5" r="5" fill="{cor_lang}"/>',
        f'<text x="{w-20}" y="34" text-anchor="end" class="lang">{escape(lang)}</text>',
        f'<text x="20" y="64" class="desc">{escape(desc[0])}</text>',
        f'<text x="20" y="83" class="desc">{escape(desc[1])}</text>',
        f'<text x="20" y="110" class="tags"># {escape(tags)}</text>',
    ]
    return svg(w, h, "\n".join(corpo), estilo, f"{nome}: {' '.join(desc)}")


def main():
    OUT.mkdir(exist_ok=True)
    for tema, c in TEMAS.items():
        (OUT / f"header-{tema}.svg").write_text(header(c), encoding="utf-8")
        for chave, rotulo in SECOES.items():
            (OUT / f"secao-{chave}-{tema}.svg").write_text(secao(c, rotulo), encoding="utf-8")
        for nome, lang, cor, desc, tags in PROJETOS:
            (OUT / f"card-{nome}-{tema}.svg").write_text(card(c, nome, lang, cor, desc, tags), encoding="utf-8")
    print(f"SVGs gerados em {OUT}")


if __name__ == "__main__":
    main()
