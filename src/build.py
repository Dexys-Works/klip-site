#!/usr/bin/env python3
"""Builds the static Dexys Klip landing page for GitHub Pages: one page per language, plus 404, robots and sitemap.

Run from anywhere:  python3 src/build.py
Inputs: src/strings.json (translations, kept in step with the app's catalogs) and the constants below.
Outputs (committed, served as is by GitHub Pages): index.html, pt-br/index.html, nl/index.html, 404.html,
robots.txt, sitemap.xml. No dependencies beyond the Python standard library.
"""
import json
import pathlib
from html import escape
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = "https://klip.dexysworks.com"
APP = "https://app.klip.dexysworks.com"  # the Klip app: sign-in, sign-up, billing, legal pages

# False until the app is deployed at APP: "Sign in" / "Start free" become "Get early access" (a pre-filled email to
# CONTACT, in the visitor's language, naming the plan), and links into the app (legal pages) are left out.
# Set to True and rebuild once APP works.
APP_LIVE = False
CONTACT = "paulo.cardoso@outlook.com"  # already public on dexysworks.com

# Languages: catalog code, URL path, <html lang>, Open Graph locale, name in its own language, short label.
LANGS = [
    {"code": "en", "path": "/", "lang": "en", "og": "en_US", "name": "English", "short": "EN"},
    {"code": "pt-BR", "path": "/pt-br/", "lang": "pt-BR", "og": "pt_BR", "name": "Português (Brasil)", "short": "PT"},
    {"code": "nl", "path": "/nl/", "lang": "nl", "og": "nl_NL", "name": "Nederlands", "short": "NL"},
]

# Plan limits mirror PLANS in the app (worker/clipper/billing.py). Prices are monthly, VAT included, and must match
# CLIPPER_PRICE_PRO_EUR / CLIPPER_PRICE_BUSINESS_EUR in the app's deployment.
PLANS = [
    {"id": "free", "price": 0, "minutes": 30, "max_length": 20, "hd": False, "jobs": 1, "watermark": True},
    {"id": "pro", "price": 19, "minutes": 600, "max_length": 180, "hd": True, "jobs": 3, "watermark": False},
    {"id": "business", "price": 79, "minutes": 3000, "max_length": 360, "hd": True, "jobs": 8, "watermark": False},
]

# Strings only the static site needs (the rest come from the app's catalogs via strings.json).
EXTRA = {
    "en": {"nf_title": "Page not found", "nf_body": "This page doesn’t exist. It may have moved.", "nf_home": "Back to the home page",
           "early": "Get early access", "early_short": "Early access",
           "early_note": "Opening soon. Free plan: 30 minutes of video a month, no card needed.",
           "early_hint": "Opens your email app. We only use your address to tell you when you can start.",
           "early_cta_title": "Be among the first to try it",
           "early_cta_body": "Dexys Klip opens soon. Send us a short email and we’ll let you know when your account is ready.",
           "early_pricing": "Plans start when Dexys Klip opens.",
           "mail_subject": "Early access to Dexys Klip",
           "mail_body": "Hi,\n\nI’d like early access to Dexys Klip.\n\nPlan I’m interested in: {plan}\nWhat I want to make clips from (podcast, streams, talks, gameplay…): \n\nThanks!",
           "mail_any": "not sure yet", "early_alt": "No email app? Write to {email}.",
           "hero_pill": "Early access · opening soon", "link_label": "Video link (optional)",
           "link_placeholder": "Paste a YouTube, Vimeo or Twitch link",
           "early_free": "Free plan: 30 minutes of video a month, no card needed.",
           "mail_body_link": "Hi,\n\nI’d like early access to Dexys Klip.\n\nA video I’d like to clip: {link}\n\nThanks!",
           "chips_label": "Highlights", "chip_moments": "Best moments", "chip_reframe": "Face tracking", "chip_langs": "15 video languages",
           "styles_title": "Captions in five styles",
           "styles_lead": "Pick a style per clip, or set one in your brand kit with your own font and colours.",
},
    "pt-BR": {"nf_title": "Página não encontrada", "nf_body": "Esta página não existe. Ela pode ter mudado de lugar.",
              "nf_home": "Voltar para o início",
              "early": "Pedir acesso antecipado", "early_short": "Acesso antecipado",
              "early_note": "Em breve. Plano grátis: 30 minutos de vídeo por mês, sem cartão.",
              "early_hint": "Abre seu app de e-mail. Usamos seu endereço só para avisar quando você puder começar.",
              "early_cta_title": "Seja um dos primeiros a experimentar",
              "early_cta_body": "O Dexys Klip abre em breve. Mande um e-mail curto e avisaremos quando sua conta estiver pronta.",
              "early_pricing": "Os planos começam quando o Dexys Klip abrir.",
              "mail_subject": "Acesso antecipado ao Dexys Klip",
              "mail_body": "Olá,\n\nQuero acesso antecipado ao Dexys Klip.\n\nPlano que me interessa: {plan}\nDe onde quero fazer clipes (podcast, lives, palestras, gameplay…): \n\nObrigado!",
              "mail_any": "ainda não sei", "early_alt": "Sem app de e-mail? Escreva para {email}.",
              "hero_pill": "Acesso antecipado · em breve", "link_label": "Link do vídeo (opcional)",
              "link_placeholder": "Cole um link do YouTube, Vimeo ou Twitch",
              "early_free": "Plano grátis: 30 minutos de vídeo por mês, sem cartão.",
              "mail_body_link": "Olá,\n\nQuero acesso antecipado ao Dexys Klip.\n\nUm vídeo que eu gostaria de recortar: {link}\n\nObrigado!",
              "chips_label": "Destaques", "chip_moments": "Melhores momentos", "chip_reframe": "Rastreamento de rosto", "chip_langs": "15 idiomas de vídeo",
              "styles_title": "Legendas em cinco estilos",
              "styles_lead": "Escolha um estilo por clipe, ou defina um no seu kit de marca com sua fonte e cores."},
    "nl": {"nf_title": "Pagina niet gevonden", "nf_body": "Deze pagina bestaat niet. Misschien is hij verplaatst.",
           "nf_home": "Terug naar de homepage",
           "early": "Vroege toegang aanvragen", "early_short": "Vroege toegang",
           "early_note": "Binnenkort beschikbaar. Gratis abonnement: 30 minuten video per maand, geen creditcard nodig.",
           "early_hint": "Opent je e-mailprogramma. We gebruiken je adres alleen om je te laten weten wanneer je kunt beginnen.",
           "early_cta_title": "Probeer het als een van de eersten",
           "early_cta_body": "Dexys Klip gaat binnenkort open. Stuur ons een korte e-mail en we laten je weten wanneer je account klaar is.",
           "early_pricing": "De abonnementen starten zodra Dexys Klip opengaat.",
           "mail_subject": "Vroege toegang tot Dexys Klip",
           "mail_body": "Hoi,\n\nIk wil graag vroege toegang tot Dexys Klip.\n\nAbonnement dat me interesseert: {plan}\nWaar ik clips van wil maken (podcast, streams, presentaties, gameplay…): \n\nBedankt!",
           "mail_any": "weet ik nog niet", "early_alt": "Geen e-mailprogramma? Schrijf naar {email}.",
           "hero_pill": "Vroege toegang · binnenkort", "link_label": "Videolink (optioneel)",
           "link_placeholder": "Plak een link van YouTube, Vimeo of Twitch",
           "early_free": "Gratis abonnement: 30 minuten video per maand, geen creditcard nodig.",
           "mail_body_link": "Hoi,\n\nIk wil graag vroege toegang tot Dexys Klip.\n\nEen video waar ik clips van wil maken: {link}\n\nBedankt!",
           "chips_label": "Hoogtepunten", "chip_moments": "Beste momenten", "chip_reframe": "Gezichtsvolging", "chip_langs": "15 videotalen",
           "styles_title": "Ondertitels in vijf stijlen",
           "styles_lead": "Kies per clip een stijl, of leg er een vast in je huisstijlkit met je eigen lettertype en kleuren."},
}

STRINGS = json.loads((ROOT / "src/strings.json").read_text())

ICONS = {
    "arrow": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "scissors": '<circle cx="6" cy="6" r="3"/><path d="M8.12 8.12 12 12"/><path d="M20 4 8.12 15.88"/><circle cx="6" cy="18" r="3"/><path d="M14.8 14.8 20 20"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/>',
    "link": '<path d="M9 17H7A5 5 0 0 1 7 7h2"/><path d="M15 7h2a5 5 0 1 1 0 10h-2"/><path d="M8 12h8"/>',
    "crop": '<path d="M6 2v14a2 2 0 0 0 2 2h14"/><path d="M18 22V8a2 2 0 0 0-2-2H2"/>',
    "captions": '<rect width="18" height="14" x="3" y="5" rx="2"/><path d="M7 15h4M15 15h2M7 11h2M13 11h4"/>',
    "hash": '<path d="M4 9h16M4 15h16M10 3 8 21M16 3l-2 18"/>',
    "sliders": '<path d="M21 4h-7M10 4H3M21 12h-9M8 12H3M21 20h-5M12 20H3M14 2v4M8 10v4M16 18v4"/>',
    "palette": '<circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/>'
               '<circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/>'
               '<path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.93 0 1.65-.75 1.65-1.69 0-.44-.18-.83-.44-1.12-.29-.29-.44-.65-.44-1.13a1.64 1.64 0 0 1 1.67-1.67h2c3.05 0 5.55-2.5 5.55-5.55C21.97 6.01 17.46 2 12 2z"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "eyeoff": '<path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.4 10.4 0 0 1 12 5c7 0 10 7 10 7a13.2 13.2 0 0 1-1.67 2.68"/>'
              '<path d="M6.61 6.61A13.5 13.5 0 0 0 2 12s3 7 10 7a9.7 9.7 0 0 0 5.39-1.61"/><path d="m2 2 20 20"/>',
    "trend": '<path d="m22 7-8.5 8.5-5-5L2 17"/><path d="M16 7h6v6"/>',
    "monitor": '<rect width="20" height="14" x="2" y="3" rx="2"/><path d="M8 21h8M12 17v4"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>',
    "moon": '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
}


def icon(name: str, size: int = 18, cls: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{ICONS[name]}</svg>')


def speaker(cls: str) -> str:
    return (f'<svg class="{cls}" viewBox="0 0 100 100" aria-hidden="true" focusable="false">'
            '<circle cx="50" cy="40" r="15" fill="currentColor"/><path d="M20 100c0-24 13-38 30-38s30 14 30 38z" fill="currentColor"/></svg>')


def translator(code: str):
    cat = STRINGS[code]
    one = (lambda n: n == 1)  # en, pt-BR and nl all use "one" for exactly 1 in these strings

    def t(key: str, **params) -> str:
        if key in EXTRA[code]:
            text = EXTRA[code][key]
        else:
            section, name = key.split(".", 1)
            node = cat[section]
            if "count" in params:
                name = f"{name}_one" if one(params["count"]) and f"{name}_one" in node else (f"{name}_other" if f"{name}_other" in node else name)
            text = node[name]
        for k, v in params.items():
            text = text.replace("{" + k + "}", str(v))
        return text

    # Escaped for HTML text and attributes.
    return lambda key, **p: escape(t(key, **p))


def eur(code: str, n: int) -> str:
    return f"€{n}" if code == "en" else f"€ {n}"


def early_href(code: str, plan: str = "") -> str:
    """mailto: link with a subject and body in the visitor's language (escaped for an HTML attribute)."""
    raw = EXTRA[code]
    body = raw["mail_body"].replace("{plan}", plan or raw["mail_any"])
    return escape(f"mailto:{CONTACT}?subject={quote(raw['mail_subject'])}&body={quote(body)}")


def start_link(code: str, t, plan_name: str = "") -> tuple:
    """(href, label) for the main call to action: sign-up while the app is live, early access before."""
    if APP_LIVE:
        return f"{APP}/sign-up", t("landing.start")
    return early_href(code, plan_name), t("early")


def capture_form(code: str, t, variant: str, label: str) -> str:
    """Link field + early-access button. Without JavaScript the browser opens mailto: with the link as the body;
    site.js builds the full message in the visitor's language (with or without a link)."""
    raw = EXTRA[code]
    body_empty = raw["mail_body"].replace("{plan}", raw["mail_any"])
    return f'''<form class="capture capture-{variant}" action="mailto:{CONTACT}" method="get" data-capture data-to="{CONTACT}"
  data-subject="{escape(raw["mail_subject"])}" data-body="{escape(raw["mail_body_link"])}" data-body-empty="{escape(body_empty)}">
  <input type="hidden" name="subject" value="{escape(raw["mail_subject"])}">
  <label class="sr-only" for="link-{variant}">{t("link_label")}</label>
  <span class="capture-icon">{icon("link", 18)}</span>
  <input id="link-{variant}" name="body" type="text" inputmode="url" autocomplete="url" spellcheck="false" placeholder="{t("link_placeholder")}">
  <button class="btn btn-primary" type="submit">{label}</button>
</form>'''


# The app's five caption styles (worker/clipper/pipeline/captions.py): words shown, which word is active, colours.
CAPTION_STYLES = [
    {"id": "bold", "name": "Bold Pop", "words": 3, "active": 1},
    {"id": "karaoke", "name": "Karaoke", "words": 4, "active": 2},
    {"id": "minimal", "name": "Minimal", "words": 7, "active": -1},
    {"id": "boxed", "name": "Boxed", "words": 5, "active": 1},
    {"id": "neon", "name": "Neon", "words": 2, "active": 1},
]


def caption_gallery(code: str, t) -> str:
    sample = STRINGS[code]["landing"]["mock_hook"].strip("“”\"„ ").rstrip(".")
    words = sample.split()
    cards = []
    for i, st in enumerate(CAPTION_STYLES):
        ws = words[: st["words"]]
        cap = " ".join(f'<span class="{"on" if j == st["active"] else ""}">{escape(w)}</span>' for j, w in enumerate(ws))
        cards.append(f'''<li class="style-card style-{st["id"]}"><div class="style-frame" aria-hidden="true">
      <div class="style-speaker">{speaker("sp")}</div><p class="style-caption">{cap}</p></div>
      <p class="style-name">{st["name"]}</p></li>''')
    return f'''<section id="captions" class="section band" aria-labelledby="captions-title"><div class="wrap">
    {section_head("captions-title", t("styles_title"), t("styles_lead"))}
    <ul class="styles">{"".join(cards)}</ul>
  </div></section>'''


BARS = [38, 52, 30, 64, 46, 72, 58, 88, 94, 80, 70, 44, 36, 50, 62, 40, 34, 56, 48, 76, 90, 84, 66, 42,
        32, 46, 58, 38, 52, 70, 86, 96, 78, 60, 44, 36, 54, 40, 30, 48]
PICKED = [(6, 10), (19, 22), (29, 33)]


def hero_visual(t) -> str:
    bars = "".join(f'<span class="{"on" if any(a <= i <= b for a, b in PICKED) else ""}" style="height:{h}%"></span>' for i, h in enumerate(BARS))
    words = "".join(f'<span class="word" style="animation-delay:{i}s">{t(k)}</span>' for i, k in enumerate(["landing.mock_w1", "landing.mock_w2", "landing.mock_w3"]))
    back = lambda cls, score, sp: (f'<div class="phone {cls}"><div class="phone-speaker">{speaker("sp " + sp)}</div>'
                                   f'<span class="score">{icon("trend", 12)}{score}</span></div>')
    return f'''<div class="hero-visual" role="img" aria-label="{t("landing.hero_figure")}">
  <div aria-hidden="true">
    <div class="source">
      <div class="speakers">{speaker("sp sp-a")}{speaker("sp sp-b")}</div>
      <div class="crop"></div>
      <span class="source-label">{t("landing.mock_source")}</span>
    </div>
    <div class="timeline card">
      <div class="bars">{bars}</div>
      <div class="moments"><span>#1</span><span>#2</span><span>#3</span></div>
    </div>
    {back("phone-back phone-left", 88, "sp-b")}
    {back("phone-back phone-right", 85, "sp-a")}
    <div class="phone phone-front">
      <div class="phone-speaker">{speaker("sp")}</div>
      <div class="track"></div>
      <span class="score">{icon("trend", 12)}92</span>
      <p class="caption">{words}</p>
    </div>
  </div>
</div>'''


def score_card(t) -> str:
    metrics = [("editor.metric_hook", 95), ("editor.metric_payoff", 90), ("editor.metric_standalone", 88), ("editor.metric_pace", 84)]
    rows = "".join(f'<div class="metric"><span class="metric-label">{t(k)}</span><span class="metric-bar"><span style="width:{v}%"></span></span>'
                   f'<span class="metric-value">{v}</span></div>' for k, v in metrics)
    return f'''<div class="score-card card" role="img" aria-label="{t("landing.score_figure")}">
  <div aria-hidden="true">
    <div class="score-head">
      <div><p class="muted small">{t("editor.whyThisClip")}</p><p class="hook">{t("landing.mock_hook")}</p></div>
      <div class="score-total"><p class="score-number">92</p><p class="muted xsmall">{t("common.viralityScore")}</p></div>
    </div>
    <div class="metrics">{rows}</div>
  </div>
</div>'''


def head(lang: dict, t, title: str, description: str, path: str, index: bool = True) -> str:
    alternates = "".join(f'<link rel="alternate" hreflang="{l["lang"]}" href="{SITE}{l["path"]}">' for l in LANGS)
    robots = "" if index else '<meta name="robots" content="noindex">'
    redirect = ""
    if lang["code"] == "en" and index:
        # First visit to "/": send Portuguese and Dutch browsers to their page. A language picked on the site wins.
        redirect = ('<script>(function(){try{if(localStorage.getItem("klip-lang"))return;var l=(navigator.languages||[navigator.language||""])[0].toLowerCase();'
                    'if(l.indexOf("pt")===0)location.replace("/pt-br/");else if(l.indexOf("nl")===0)location.replace("/nl/");}catch(e){}})();</script>')
    return f'''<!doctype html>
<html lang="{lang["lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
{robots}<link rel="canonical" href="{SITE}{path}">
{alternates if index else ""}{f'<link rel="alternate" hreflang="x-default" href="{SITE}/">' if index else ""}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Dexys Klip">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:locale" content="{lang["og"]}">
<meta property="og:image" content="{SITE}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Dexys Klip: long videos in, short clips out">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#171a1c" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/manrope-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css">
<script>(function(){{try{{var t=localStorage.getItem("klip-theme");if(t==="light"||t==="dark")document.documentElement.dataset.theme=t;}}catch(e){{}}}})();</script>
{redirect}<script src="/assets/site.js" defer></script>
</head>'''


def header(lang: dict, t) -> str:
    href, label = start_link(lang["code"], t)
    signin = (f'<a class="signin-text" href="{APP}/sign-in">{t("landing.signIn")}</a>'
              f'<a class="btn btn-ghost signin-btn" href="{APP}/sign-in">{t("landing.signIn")}</a>') if APP_LIVE else ""
    links = [("#how", "landing.nav_how"), ("#features", "landing.nav_features"), ("#privacy", "landing.nav_privacy"),
             ("#pricing", "landing.nav_pricing"), ("#faq", "landing.nav_faq")]
    nav = "".join(f'<li><a href="{h}">{t(k)}</a></li>' for h, k in links)
    return f'''<header class="site-header">
  <div class="wrap header-inner">
    {brand(lang, t)}
    <nav class="header-nav" aria-label="{t("landing.nav_label")}"><ul>{nav}</ul></nav>
    <div class="header-actions">
      {signin}
      <a class="btn btn-primary btn-compact" href="{href}">{label if APP_LIVE else t("early_short")}</a>
    </div>
  </div>
</header>'''


def brand(lang: dict, t) -> str:
    return (f'<a class="brand" href="{lang["path"]}" aria-label="{t("landing.home")}"><span class="brand-tile">{icon("scissors", 16)}</span>'
            f'<span class="brand-name">Dexys Klip</span></a>')


def lang_switch(lang: dict, t) -> str:
    current = ' aria-current="page"'
    items = "".join(
        f'<li><a href="{l["path"]}" hreflang="{l["lang"]}" lang="{l["lang"]}" data-lang="{l["code"]}"'
        f'{current if l is lang else ""}>{escape(l["name"])}</a></li>' for l in LANGS)
    return f'<nav class="lang-switch" aria-label="{t("language.label")}">{icon("globe", 14)}<ul>{items}</ul></nav>'


def theme_switch(t) -> str:
    opts = [("system", "theme.system", "monitor"), ("light", "theme.light", "sun"), ("dark", "theme.dark", "moon")]
    btns = "".join(f'<button type="button" data-theme-value="{v}" aria-label="{t(k)}" title="{t(k)}" aria-pressed="{"true" if v == "system" else "false"}">{icon(i, 14)}</button>'
                   for v, k, i in opts)
    return f'<div class="theme-switch" role="group" aria-label="{t("theme.group")}" hidden>{btns}</div>'


def footer(lang: dict, t, year: int = 2026) -> str:
    href, label = start_link(lang["code"], t)
    account = (f'<li><a href="{APP}/sign-in">{t("landing.signIn")}</a></li>' if APP_LIVE else "") + f'<li><a href="{href}">{label}</a></li>'
    legal = f'''<nav aria-labelledby="footer-legal"><h2 id="footer-legal">{t("landing.footer_legal")}</h2><ul>
      <li><a href="{APP}/privacy">{t("legal.p_title")}</a></li>
      <li><a href="{APP}/terms">{t("legal.t_title")}</a></li>
      <li><a href="{APP}/subprocessors">{t("legal.s_title")}</a></li></ul></nav>''' if APP_LIVE else ""
    return f'''<footer class="site-footer">
  <div class="wrap footer-grid">
    <div class="footer-brand">{brand(lang, t)}<p class="muted">{t("landing.footer_tagline")}</p></div>
    <nav aria-labelledby="footer-product"><h2 id="footer-product">{t("landing.footer_product")}</h2><ul>
      <li><a href="{lang["path"]}#features">{t("landing.nav_features")}</a></li>
      <li><a href="{lang["path"]}#pricing">{t("landing.nav_pricing")}</a></li>
      {account}</ul></nav>
    {legal}
  </div>
  <div class="wrap footer-bottom">
    <p>{t("landing.footer_copy", year="YEAR").replace("YEAR", f'<span data-year>{year}</span>')}</p>
    <div class="footer-settings">{lang_switch(lang, t)}{theme_switch(t)}</div>
  </div>
</footer>'''


def features_list(p: dict, t) -> list:
    return [t("pricing.f_minutes", n=p["minutes"]), t("pricing.f_length", n=p["max_length"]),
            t("pricing.f_hd" if p["hd"] else "pricing.f_sd"), t("pricing.f_jobs", count=p["jobs"]),
            t("pricing.f_watermark" if p["watermark"] else "pricing.f_noWatermark")]


def section_head(id_: str, title: str, lead: str = "") -> str:
    return f'<div class="section-head"><h2 id="{id_}">{title}</h2>{f"<p>{lead}</p>" if lead else ""}</div>'


def landing(lang: dict) -> str:
    code = lang["code"]
    t = translator(code)
    title, description = t("landing.meta_title"), t("landing.meta_description")

    steps = "".join(f'''<li class="card step"><div class="step-top"><span class="tile">{icon(ic)}</span><span class="step-n" aria-hidden="true">0{i + 1}</span></div>
      <h3>{t(f"landing.step{i + 1}_t")}</h3><p class="muted">{t(f"landing.step{i + 1}_b")}</p></li>''' for i, ic in enumerate(["upload", "scissors", "download"]))
    feats = "".join(f'<li><span class="tile">{icon(ic)}</span><h3>{t(f"landing.f_{k}_t")}</h3><p class="muted">{t(f"landing.f_{k}_b")}</p></li>'
                    for k, ic in [("reframe", "crop"), ("captions", "captions"), ("copy", "hash"), ("editor", "sliders"), ("brand", "palette"), ("teams", "users")])
    privacy = "".join(f'<li class="card"><span class="symbol">{icon(ic, 20)}</span><h3>{t(f"landing.{k}_t")}</h3><p class="muted">{t(f"landing.{k}_b")}</p></li>'
                      for k, ic in [("p1", "pin"), ("p2", "eyeoff"), ("p3", "download")])
    plans = []
    for p in PLANS:
        name = t(f"plans.{p['id']}")
        if APP_LIVE:
            href = f"{APP}/sign-up" + (f"?redirect_url=%2Fbilling%3Fplan%3D{p['id']}" if p["price"] else "")
        else:
            href = early_href(code, STRINGS[code]["plans"][p["id"]])
        per = f' <span class="per">{t("landing.per_month")}</span>' if p["price"] else ""
        feats_html = "".join(f"<li>{icon('check', 16)}{f}</li>" for f in features_list(p, t))
        if APP_LIVE:
            cta = t("landing.choose", name=name) if p["price"] else t("landing.start")
        else:
            cta = t("early")
        plans.append(f'''<li class="card plan{" featured" if p["id"] == "pro" else ""}"><h3>{name}</h3><p class="muted small">{t(f"pricing.tag_{p['id']}")}</p>
      <p class="price">{eur(code, p["price"])}{per}</p><ul class="plan-features">{feats_html}</ul>
      <a class="btn {"btn-primary" if p["id"] == "pro" else "btn-ghost"} btn-block" href="{href}">{cta}</a></li>''')
    faq = "".join(f'<details><summary>{t(f"landing.q_{q}")}{icon("chevron", 18, "chev")}</summary><p class="muted">{t(f"landing.a_{q}")}</p></details>'
                  for q in ["minutes", "free", "langs", "training", "data", "cancel", "rights"])
    start_href, start_label = start_link(code, t)
    hero_note = t("landing.hero_note") if APP_LIVE else f'{t("early_free")} {t("early_hint")}'
    hero_action = (f'<div class="hero-ctas"><a class="btn btn-primary btn-large" href="{start_href}">{start_label} {icon("arrow")}</a>'
                   f'<a class="btn btn-ghost btn-large" href="#pricing">{t("landing.hero_plans")}</a></div>') if APP_LIVE \
        else capture_form(code, t, "hero", t("early"))
    chip_items = [("#features", "chip_moments"), ("#features", "common.viralityScore"), ("#features", "chip_reframe"),
                  ("#captions", "landing.f_captions_t"), ("#features", "landing.f_brand_t"), ("#faq", "chip_langs")]
    chips = "".join(f'<li><a href="{h}">{t(k)}</a></li>' for h, k in chip_items)
    dock = "" if APP_LIVE else f'<div class="dock" data-dock hidden>{capture_form(code, t, "dock", t("early_short"))}</div>'
    cta_title = t("landing.cta_title") if APP_LIVE else t("early_cta_title")
    cta_body = t("landing.cta_body") if APP_LIVE else t("early_cta_body")
    cta_alt = "" if APP_LIVE else '<p class="alt">' + t("early_alt", email="EMAIL").replace("EMAIL", f'<a href="mailto:{CONTACT}">{CONTACT}</a>') + "</p>"
    privacy_links = f' <a href="{APP}/subprocessors">{t("landing.privacy_sub")}</a> · <a href="{APP}/privacy">{t("legal.p_title")}</a>' if APP_LIVE else ""
    pricing_note = f'{t("pricing.vatNote")} {t("pricing.lead")}' if APP_LIVE else f'{t("early_pricing")} {t("pricing.vatNote")} {t("pricing.lead")}'
    jsonld = json.dumps({
        "@context": "https://schema.org", "@type": "SoftwareApplication", "name": "Dexys Klip", "url": SITE + lang["path"],
        "inLanguage": lang["lang"], "applicationCategory": "MultimediaApplication", "operatingSystem": "Web",
        "description": STRINGS[code]["landing"]["meta_description"],
        "publisher": {"@type": "Organization", "name": "Dexys Works", "url": "https://dexysworks.com"},
        "offers": [{"@type": "Offer", "name": STRINGS[code]["plans"][p["id"]], "price": p["price"], "priceCurrency": "EUR"} for p in PLANS],
    }, ensure_ascii=False).replace("<", "\\u003c")

    return f'''{head(lang, t, title, description, lang["path"])}
<body>
<a class="skip-link" href="#content">{t("landing.skip")}</a>
{header(lang, t)}
<main id="content">
  <section class="wrap hero" aria-labelledby="hero-title">
    <div class="hero-copy">
      <p class="pill">{t("hero_pill") if not APP_LIVE else t("landing.hero_eyebrow")}</p>
      <h1 id="hero-title">{t("landing.hero_title")}</h1>
      <p class="lead">{t("landing.hero_lead")}</p>
      {hero_action}
      <p class="muted small hero-note">{hero_note}</p>
      <ul class="chips" aria-label="{t("chips_label")}">{chips}</ul>
    </div>
    {hero_visual(t)}
  </section>

  <div class="sources"><p class="wrap">{icon("link", 16, "symbol")}<span>{t("landing.sources_link")}</span>
    <span class="chip">YouTube</span><span class="chip">Vimeo</span><span class="chip">Twitch</span><span>{t("landing.sources_more")},</span>
    <span class="inline">{icon("upload", 16, "symbol")}{t("landing.sources_upload")}</span></p></div>

  <section id="how" class="section band" aria-labelledby="how-title"><div class="wrap">
    {section_head("how-title", t("landing.how_title"), t("landing.how_lead"))}
    <ol class="grid-3">{steps}</ol>
  </div></section>

  <section id="features" class="section" aria-labelledby="features-title"><div class="wrap">
    {section_head("features-title", t("landing.features_title"), t("landing.features_lead"))}
    <div class="showcase"><div><h3>{t("landing.show_title")}</h3><p class="muted">{t("landing.show_body")}</p></div>{score_card(t)}</div>
    <ul class="features">{feats}</ul>
  </div></section>

  {caption_gallery(code, t)}

  <section id="privacy" class="section" aria-labelledby="privacy-title"><div class="wrap">
    {section_head("privacy-title", t("landing.privacy_title"), t("landing.privacy_lead"))}
    <ul class="grid-3">{privacy}</ul>
    <p class="note">{t("landing.privacy_note")}{privacy_links}</p>
  </div></section>

  <section id="pricing" class="section band" aria-labelledby="pricing-title"><div class="wrap">
    {section_head("pricing-title", t("landing.pricing_title"), t("landing.pricing_lead"))}
    <ul class="grid-3 plans">{"".join(plans)}</ul>
    <p class="note">{pricing_note}</p>
  </div></section>

  <section id="faq" class="section faq-section" aria-labelledby="faq-title"><div class="wrap faq-grid">
    <h2 id="faq-title">{t("landing.faq_title")}</h2>
    <div class="faq">{faq}</div>
  </div></section>

  <section class="wrap cta-wrap" aria-labelledby="cta-title"><div class="cta">
    <div class="cta-copy"><h2 id="cta-title">{cta_title}</h2><p>{cta_body}</p>{cta_alt}</div>
    {f'<a class="btn btn-inverse btn-large" href="{start_href}">{start_label} {icon("arrow")}</a>' if APP_LIVE else capture_form(code, t, "cta", t("early_short"))}
  </div></section>
</main>
{footer(lang, t)}
{dock}
<script type="application/ld+json">{jsonld}</script>
</body>
</html>
'''


def not_found() -> str:
    lang = LANGS[0]
    t = translator("en")
    others = "".join(f'<p lang="{l["lang"]}" class="muted">{translator(l["code"])("nf_title")} · <a href="{l["path"]}">{translator(l["code"])("nf_home")}</a></p>'
                     for l in LANGS[1:])
    return f'''{head(lang, t, t("nf_title") + " · Dexys Klip", t("nf_body"), "/404.html", index=False)}
<body>
{header(lang, t)}
<main id="content" class="wrap not-found">
  <h1>{t("nf_title")}</h1>
  <p class="lead">{t("nf_body")}</p>
  <p><a class="btn btn-primary btn-large" href="/">{t("nf_home")} {icon("arrow")}</a></p>
  {others}
</main>
{footer(lang, t)}
</body>
</html>
'''


def sitemap() -> str:
    alts = "".join(f'<xhtml:link rel="alternate" hreflang="{l["lang"]}" href="{SITE}{l["path"]}"/>' for l in LANGS)
    alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/"/>'
    urls = "".join(f"<url><loc>{SITE}{l['path']}</loc>{alts}</url>" for l in LANGS)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            f'xmlns:xhtml="http://www.w3.org/1999/xhtml">{urls}</urlset>\n')


def main() -> None:
    for lang in LANGS:
        out = ROOT / lang["path"].strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(landing(lang))
    (ROOT / "404.html").write_text(not_found())
    (ROOT / "sitemap.xml").write_text(sitemap())
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    print("built:", ", ".join(l["path"] for l in LANGS), "+ 404.html, sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
