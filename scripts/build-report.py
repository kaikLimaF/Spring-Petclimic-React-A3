#!/usr/bin/env python3
"""A3 / QA - Gera docs/RELATORIO-A3.html (e .pdf via LibreOffice, se disponivel) a partir dos Markdown em docs/.
Conversor Markdown -> HTML minimo, sem dependencias externas (cabecalhos, paragrafos, listas, tabelas,
blocos de codigo, citacoes, negrito/italico/codigo inline, links, regras horizontais).
Uso: python3 scripts/build-report.py
"""
import html, re, subprocess, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / 'docs'
ORDER = ['RELATORIO-FINAL.md', '01-arquitetura.md', '02-plano-de-testes.md', '03-matriz-de-rastreabilidade.md',
         '04-analise-de-riscos.md', '05-casos-de-teste-caixa-preta.md', '06-casos-de-teste-caixa-branca.md',
         '07-testes-automatizados.md', '08-inspecao-e-analise-estatica.md', '09-metricas-e-cobertura.md',
         '10-gestao-de-defeitos.md', '11-quality-decision.md', '12-melhorias-e-licoes-aprendidas.md', '13-anexo-resultados-por-teste.md']

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'`([^`]+)`', lambda m: '<code>' + m.group(1) + '</code>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)', r'<i>\1</i>', s)
    s = re.sub(r'(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?!\w)', r'<i>\1</i>', s)
    s = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img alt="\1" src="\2">', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    s = s.replace('\\|', '|')
    return s

def convert(md):
    out, i, lines = [], 0, md.splitlines()
    para = []
    def flush():
        if para:
            out.append('<p>' + inline(' '.join(para)) + '</p>'); para.clear()
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('```'):
            flush(); lang = ln[3:].strip(); buf = []; i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                buf.append(lines[i]); i += 1
            out.append('<pre class="%s">' % html.escape(lang) + html.escape('\n'.join(buf)) + '</pre>'); i += 1; continue
        m = re.match(r'^(#{1,6})\s+(.*)$', ln)
        if m:
            flush(); lvl = len(m.group(1)); out.append('<h%d>%s</h%d>' % (lvl, inline(m.group(2)), lvl)); i += 1; continue
        if re.match(r'^\s*(-{3,}|\*{3,}|_{3,})\s*$', ln):
            flush(); out.append('<hr>'); i += 1; continue
        if ln.startswith('|'):
            flush(); rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append(lines[i]); i += 1
            cells = lambda r: [c.strip() for c in re.split(r'(?<!\\)\|', r.strip().strip('|'))]
            head = cells(rows[0]); body = [cells(r) for r in rows[2:]] if len(rows) > 1 and re.match(r'^\|?\s*:?-', rows[1]) else [cells(r) for r in rows[1:]]
            t = ['<table><thead><tr>' + ''.join('<th>%s</th>' % inline(c) for c in head) + '</tr></thead><tbody>']
            for r in body:
                t.append('<tr>' + ''.join('<td>%s</td>' % inline(c) for c in r) + '</tr>')
            t.append('</tbody></table>'); out.append(''.join(t)); continue
        if ln.startswith('>'):
            flush(); buf = []
            while i < len(lines) and lines[i].startswith('>'):
                buf.append(lines[i][1:].strip()); i += 1
            out.append('<blockquote>' + ''.join('<p>%s</p>' % inline(b) for b in buf if b) + '</blockquote>'); continue
        m = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)$', ln)
        if m:
            flush(); kind = 'ol' if m.group(2)[0].isdigit() else 'ul'; items = []
            while i < len(lines):
                m2 = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)$', lines[i])
                if m2 and (m2.group(2)[0].isdigit()) == (kind == 'ol'):
                    items.append(m2.group(3)); i += 1
                elif lines[i].startswith('    ') and items:
                    items[-1] += ' ' + lines[i].strip(); i += 1
                else: break
            out.append('<%s>' % kind + ''.join('<li>%s</li>' % inline(it) for it in items) + '</%s>' % kind); continue
        if not ln.strip():
            flush(); i += 1; continue
        para.append(ln.strip()); i += 1
    flush()
    return '\n'.join(out)

CSS = """
body{font-family:'Liberation Sans',Arial,Helvetica,sans-serif;font-size:10.5pt;line-height:1.35;color:#111;margin:0}
h1{font-size:20pt;color:#1a3d7c;border-bottom:2px solid #1a3d7c;padding-bottom:4px;margin-top:0}
h2{font-size:14pt;color:#1a3d7c;margin-top:18pt} h3{font-size:12pt;margin-top:14pt} h4{font-size:11pt}
table{border-collapse:collapse;width:100%;margin:8pt 0;font-size:9pt} th,td{border:1px solid #999;padding:3pt 5pt;vertical-align:top;text-align:left}
th{background:#e8eef8} pre{background:#f3f4f6;border:1px solid #ccc;padding:6pt;font-size:8pt;white-space:pre-wrap;font-family:'Liberation Mono',monospace}
code{font-family:'Liberation Mono',monospace;font-size:9pt;background:#f3f4f6} blockquote{border-left:4px solid #1a3d7c;margin:8pt 0;padding:4pt 10pt;background:#f7f9fc}
.cover{text-align:center;padding-top:160pt} .cover h1{border:none;font-size:26pt} .cover p{font-size:13pt}
.break{page-break-before:always}
"""
parts = ['<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>Relatório A3 — QA Spring PetClinic (React)</title><style>%s</style></head><body>' % CSS]
parts.append('<div class="cover"><h1>Projeto A3 — Gestão da Qualidade de Software</h1><p><b>Quality Assurance em Sistemas Open Source</b></p><p>Sistema avaliado: Spring PetClinic (React)<br>spring-petclinic/spring-petclinic-reactjs · Spring Boot 3.2.1 · Java 21</p><p>Universidade Anhembi Morumbi · Ânima Educação</p><p>Relatório técnico — 16/11/2026</p><p style="font-size:10pt;color:#555">Integrantes: ______________________________________</p></div>')
for n, name in enumerate(ORDER):
    md = (DOCS / name).read_text(encoding='utf-8')
    parts.append('<div class="break"></div>' + convert(md))
parts.append('</body></html>')
out_html = DOCS / 'RELATORIO-A3.html'
out_html.write_text('\n'.join(parts), encoding='utf-8')
print('HTML:', out_html, out_html.stat().st_size, 'bytes')
soffice = shutil.which('soffice') or shutil.which('libreoffice')
if soffice:
    r = subprocess.run([soffice, '--headless', '--convert-to', 'pdf:writer_web_pdf_Export', '--outdir', str(DOCS), str(out_html)], capture_output=True, text=True, timeout=300)
    pdf = DOCS / 'RELATORIO-A3.pdf'
    print('PDF:', pdf if pdf.exists() else 'FALHOU', r.stdout.strip()[-200:], r.stderr.strip()[-200:])
else:
    print('LibreOffice nao encontrado; converta o HTML para PDF manualmente (Ctrl+P no navegador).')
