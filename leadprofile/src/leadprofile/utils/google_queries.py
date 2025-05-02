import unicodedata
from typing import List, Tuple

SOCIAL_SITES = {
    "linkedin":  "linkedin.com/in",
    "instagram": "instagram.com",
    "facebook":  "facebook.com",
    "x":         "twitter.com",
    "telegram":  "t.me",
    "discord":   "discord.com",
    "youtube":   "youtube.com/channel",
}

# ───────────────────────── helpers ──────────────────────────


def _slug(text: str) -> str:
    """remove acentos, pontuação e espaços → slug compacto"""
    norm = unicodedata.normalize("NFKD", text)
    clean = "".join(c for c in norm if not unicodedata.combining(c))
    return "".join(ch for ch in clean.lower() if ch.isalnum())


def build_queries(name: str, city: str = "", state: str = "") -> List[Tuple[str, str]]:
    """
    Gera até 17 queries (2 LinkedIn + 6 redes + 3 news + 3 lawsuit +
    pdf, intitle, inurl). Devolve lista [(tag, query)].
    """
    parts = name.split()
    first, last = parts[0], parts[-1]
    quoted = f'"{name}"'

    if city and state:
        loc = f'"{city}, {state}"'
    elif city or state:
        loc = f'"{city or state}"'
    else:
        loc = ""

    queries: List[Tuple[str, str]] = []

    # 1) LinkedIn – duas variantes de slug (sem acento / com hífen)
    slug_plain = _slug(name)               # joaomoura
    slug_dash = "-".join(_slug(p) for p in parts)  # joao-moura
    queries += [
        ("linkedin", f'site:{SOCIAL_SITES["linkedin"]}/{slug_plain} {loc}'),
        ("linkedin", f'site:{SOCIAL_SITES["linkedin"]}/{slug_dash} {loc}')
    ]

    # 2) Demais redes (1 cada)
    for tag, dom in SOCIAL_SITES.items():
        if tag == "linkedin":
            continue
        queries.append((tag, f'site:{dom} {quoted} {loc}'))

    # 3) Notícias locais (3 variantes)
    queries += [
        ("news_local", f'{quoted} {loc} intext:notícia'),
        ("news_local", f'"{first} * {last}" {loc} intext:notícia'),
        ("news_local", f'"{first} {last} *" {loc} intext:notícia')
    ]

    # 4) Processos (.jus.br) (3 variantes)
    queries += [
        ("lawsuit", f'{quoted} {loc} site:.jus.br'),
        ("lawsuit", f'"{first} * {last}" {loc} site:.jus.br'),
        ("lawsuit", f'"{first} {last} *" {loc} site:.jus.br')
    ]

    # 5) PDF currículo, intitle, inurl
    queries += [
        ("cv_pdf",  f'{quoted} {loc} filetype:pdf currículo'),
        ("intitle", f'intitle:{quoted} {loc}'),
        ("inurl",   f'inurl:{first.lower()} {loc}')
    ]

    return queries        # não corta mais!
