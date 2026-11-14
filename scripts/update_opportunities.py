#!/usr/bin/env python3
"""Radar História RJ — varredura recorrente orientativa.

O robô NUNCA declara uma inscrição aberta: novos achados permanecem 'Em apuração'
até o responsável conferir o edital e promovê-los para opportunities.
Usa páginas institucionais públicas + RSS de notícias como descoberta auxiliar.
Falhas de uma fonte não apagam registros curados.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote, urljoin, urlparse
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'opportunities.json'
TZ = timezone(timedelta(hours=-3))
NOW = datetime.now(TZ)
UA = 'RadarHistoriaRJ/2.0 (+public opportunity indexer; honors source policies)'
SOURCES = [
    ('UERJ - PROSSIM', 'https://prossim.uerj.br/public/carregar_selecao', 'Rio de Janeiro'),
    ('UFRJ - PR4', 'https://concursos.pr4.ufrj.br/category/concursos/', 'Rio de Janeiro'),
    ('UFRRJ', 'https://servicos.ufrrj.br/concursos/index.php?acao=concursos_abertos', 'Seropédica'),
    ('Prefeitura do Rio', 'https://concurso.prefeitura.rio/', 'Rio de Janeiro'),
    ('SEEDUC-RJ', 'https://www.seeduc.rj.gov.br/professor/contrata%C3%A7%C3%A3o-tempor%C3%A1ria', 'Estado do Rio'),
    ('Fundação Casa de Rui Barbosa', 'https://www.gov.br/casaruibarbosa/pt-br/a-fundacao/editais-e-oportunidades/selecoes_publicas', 'Rio de Janeiro'),
    ('Secretaria Municipal de Cultura', 'https://cultura.prefeitura.rio/', 'Rio de Janeiro'),
    ('Secretaria Estadual de Cultura', 'https://cultura.rj.gov.br/', 'Estado do Rio'),
    ('Elite Rede de Ensino - carreiras', 'https://elite.gupy.io/', 'Estado do Rio'),
]
# RSS serve como pista, NÃO como verificação de abertura ou elegibilidade.
QUERIES = [
    '"professor de história" (concurso OR edital OR seleção) "RJ"',
    '"historiador" (concurso OR seleção OR edital) "Rio de Janeiro"',
    '"professor história" "processo seletivo" "Rio de Janeiro"',
    '"educação patrimonial" (vaga OR edital OR seleção) "RJ"',
    '"professor de história" "vaga" "colégio" "Rio de Janeiro"',
    '"professor de história" (Elite OR Gupy OR escola) "RJ"',
    '"historiador" (museu OR arquivo OR patrimônio) "Rio de Janeiro" vaga',
    '"pesquisador de acervo" (vaga OR seleção) "Rio de Janeiro"',
    '"historiador" "clube" (vaga OR seleção) "Rio de Janeiro"',
    '"professor de história" (CLT OR contratação) "Rio de Janeiro"',
]
STRONG = re.compile(r'\b(historiador(?:a|es)?|professor(?:a|es)?.{0,55}hist[oó]ria|docente.{0,55}hist[oó]ria|hist[oó]ria\s+(?:antiga|moderna|do\s+brasil|da\s+am[eé]rica)|teoria\s+e\s+metodologia\s+da\s+hist[oó]ria|educa[cç][aã]o\s+patrimonial|mem[oó]ria\s+institucional)\b', re.I)
EXCLUDE = re.compile(r'\b(resultado\s+final|homologa[cç][aã]o|gabarito\s+definitivo|classifica[cç][aã]o\s+final|prorroga[cç][aã]o\s+do\s+concurso\s+de\s+20[01])\b', re.I)


def normalized(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')


def meaningful(text: str) -> bool:
    t = re.sub(r'\s+', ' ', text).strip()
    return 17 <= len(t) <= 220 and bool(STRONG.search(t)) and not EXCLUDE.search(t)


def hash_id(url: str, title: str) -> str:
    return 'radar-' + hashlib.sha1((normalized(title) + '|' + url).encode('utf-8')).hexdigest()[:14]


def get(url: str) -> requests.Response:
    r = requests.get(url, headers={'User-Agent': UA}, timeout=18)
    r.raise_for_status()
    return r


def matches_known(title: str, verified: list[dict]) -> bool:
    # Suprime especialidades idênticas já curadas, mesmo em endereços diferentes.
    a = normalized(title)
    terms = ['historiador', 'historia do brasil', 'historia moderna', 'historia da america',
             'teoria e metodologia da historia', 'historia antiga']
    for item in verified:
        b = normalized(item.get('title', ''))
        if a == b or (min(len(a), len(b)) > 25 and (a in b or b in a)):
            return True
        for term in terms:
            if term in a and term in b:
                org = normalized(item.get('org', ''))
                if ('uerj' in normalized(title) and 'uerj' in org) or ('ufrj' in normalized(title) and 'universidade federal do rio de janeiro' in org):
                    return True
    return False


def category(title: str):
    s = normalized(title)
    if 'professor' in s or 'historia antiga' in s or 'historia moderna' in s or 'historia do brasil' in s:
        return 'professor'
    if 'historiador' in s:
        return 'historiador'
    return 'cultura'


def new_candidate(title, url, source, city, record_kind):
    title = re.sub(r'\s+', ' ', title).strip()[:210]
    return {
        'id': hash_id(url, title), 'title': title,
        'org': source, 'city': city, 'region': 'A confirmar',
        'category': category(title), 'type': 'A confirmar', 'modality': 'A confirmar',
        'start': None, 'end': None, 'deadlineTime': None, 'slots': 'Verificar edital',
        'salary': None, 'education': 'Consultar fonte e requisitos específicos',
        'description': 'Achado na varredura automática de fontes públicas. Verifique se o cargo atende à formação em História, se o edital está vigente e quais são os prazos.',
        'tags': ['Novo achado', 'Conferir edital', record_kind],
        'url': url, 'sourceName': source, 'verifiedAt': NOW.date().isoformat(),
        'firstSeenAt': NOW.date().isoformat(), 'origin': 'descoberta', 'sector': 'a confirmar'
    }


def scan_official(name, url, city):
    response = get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for tag in soup(['script', 'style', 'nav', 'footer']):
        tag.decompose()
    collected = []
    # Examine links and their local text, never whole page (reduces false positives).
    for anchor in soup.find_all('a', href=True):
        label = anchor.get_text(' ', strip=True)
        if meaningful(label):
            href = urljoin(url, anchor.get('href', ''))
            if urlparse(href).scheme in ('http', 'https'):
                collected.append(new_candidate(label, href, name, city, 'Portal institucional'))
    # Some portais place listings as unlinked headings/paragraphs.
    for el in soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6', 'li']):
        label = el.get_text(' ', strip=True)
        if meaningful(label):
            link = el.find('a', href=True)
            href = urljoin(url, link['href']) if link else url
            collected.append(new_candidate(label, href, name, city, 'Portal institucional'))
    # UFRJ has some specific subject rows rendered as plain text separated by newlines.
    if 'UFRJ - PR4' == name:
        for line in soup.get_text('\n', strip=True).splitlines():
            if re.search(r'PSS-\d+', line) and meaningful(line):
                collected.append(new_candidate(line, url, name, city, 'UFRJ / normas complementares'))
    return collected


def scan_rss(query):
    url = 'https://news.google.com/rss/search?q=' + quote(query + ' when:45d') + '&hl=pt-BR&gl=BR&ceid=BR:pt-419'
    raw = get(url).content
    root = ET.fromstring(raw)
    results = []
    for item in root.findall('.//channel/item')[:25]:
        title = (item.findtext('title') or '').strip()
        href = item.findtext('link') or ''
        pub = item.findtext('pubDate') or ''
        if not meaningful(title):
            continue
        # Notícias antigas não devem virar novidades só porque foram reindexadas.
        if pub:
            try:
                from email.utils import parsedate_to_datetime
                published = parsedate_to_datetime(pub)
                if published.tzinfo is None:
                    published = published.replace(tzinfo=timezone.utc)
                if published < NOW.astimezone(timezone.utc) - timedelta(days=21):
                    continue
            except (TypeError, ValueError):
                continue
        if len(href) > 2000 or not href.startswith('https://'):
            continue
        # Google News RSS can reference broad state-wide news; candidate NOT asserted valid.
        results.append(new_candidate(title, href, 'Google Notícias · publicação a confirmar', 'Estado do Rio', 'Notícia a conferir'))
    return results


def main():
    if not DATA.is_file():
        raise SystemExit(f'Arquivo inexistente: {DATA}')
    data = json.loads(DATA.read_text(encoding='utf-8'))
    verified = data.get('opportunities', [])
    previous = data.get('discovered', [])
    all_ids = {x['id'] for x in verified + previous}
    all_urls = {x.get('url') for x in verified}
    found = 0
    succeeded = 0
    errors = []
    potential = []
    for source in SOURCES:
        try:
            vals = scan_official(*source)
            potential.extend(vals)
            succeeded += 1
        except Exception as exc:
            errors.append(f'{source[0]}: {exc}')
    for query in QUERIES:
        try:
            vals = scan_rss(query)
            potential.extend(vals)
            succeeded += 1
        except Exception as exc:
            errors.append(f'RSS: {exc}')
    # No successful fetch means we must not mark a new successful scan.
    if succeeded == 0:
        print('Nenhuma fonte acessível. Arquivo preservado.\n' + '\n'.join(errors), file=sys.stderr)
        return 1
    for candidate in potential:
        if len(previous) >= 60:
            break
        if candidate['id'] in all_ids or candidate['url'] in all_urls:
            continue
        if matches_known(candidate['title'], verified):
            continue
        # Stable dedup by source and normalized title.
        key = (normalized(candidate['org']), normalized(candidate['title']))
        if any((normalized(x.get('org', '')), normalized(x.get('title', ''))) == key for x in previous):
            continue
        previous.append(candidate)
        all_ids.add(candidate['id'])
        found += 1
    # Remove old unreviewed leads to keep the interface useful. Verified curation is untouched.
    cutoff = (NOW - timedelta(days=21)).date().isoformat()
    previous = [x for x in previous if x.get('firstSeenAt', x.get('verifiedAt', '9999-12-31')) >= cutoff]
    data['discovered'] = previous
    data['meta']['automaticScanAt'] = NOW.isoformat(timespec='seconds')
    data['meta']['updatedAt'] = NOW.isoformat(timespec='seconds')
    data['meta']['scanStatus'] = f'{succeeded} fontes/consultas acessadas, {found} novos achados sem confirmação'
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(data['meta']['scanStatus'])
    if errors:
        print('Fontes indisponíveis (mantidas para próxima execução):\n' + '\n'.join(errors), file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
