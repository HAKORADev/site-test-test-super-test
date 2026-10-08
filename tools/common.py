import json, os, html, unicodedata

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE_NAME = "Salt & Ember"
SITE_TAGLINE = "A test kitchen with a pot always on."
SITE_URL = "https://hakoradev.github.io/site-test-test-super-test/"
REPO_URL = "https://github.com/HAKORADev/site-test-test-super-test"
BUILT_NOTE = "Built overnight by an AI sous-chef while the owner slept."

GENRES = {
    "Italian Classics": {
        "slug": "italian-classics",
        "blurb": "Four-ingredient sauces, blistered crusts, and the rice that wants to be stirred. The cuisine that turned restraint into abundance.",
        "cover_key": "classic-margherita-pizza",
    },
    "French Bistro": {
        "slug": "french-bistro",
        "blurb": "Onions that take an hour, wine that goes in the pot and the cook, and cheese lids with structural ambition.",
        "cover_key": "french-onion-soup",
    },
    "Asian Kitchen": {
        "slug": "asian-kitchen",
        "blurb": "Broths built in layers, woks at full scream, and bowls that teach you to slurp without apology.",
        "cover_key": "shoyu-ramen",
    },
    "Spice Route": {
        "slug": "spice-route",
        "blurb": "Yogurt marinades, bloomed spices, and gravies you plan to wipe up with bread. The warmest aisle in the kitchen.",
        "cover_key": "butter-chicken",
    },
    "Mediterranean Sun": {
        "slug": "mediterranean-sun",
        "blurb": "Olive oil as a seasoning, lemons as a finishing move, and vegetables treated like main characters.",
        "cover_key": "seafood-paella",
    },
    "Street Food": {
        "slug": "street-food",
        "blurb": "Crusts, crackles and drips. The food that tastes best standing up, eaten with intent, over a napkin you have abandoned.",
        "cover_key": "smash-burger",
    },
    "Comfort Food": {
        "slug": "comfort-food",
        "blurb": "Golden tops, spoon-tender meat, and the specific silence of a table full of people eating their feelings.",
        "cover_key": "baked-mac-and-cheese",
    },
    "Sweet & Baked": {
        "slug": "sweet-baked",
        "blurb": "Caramelized sugar glass, molten centers, and bread that needs a whole day of patience. Dessert is not optional.",
        "cover_key": "chocolate-lava-cake",
    },
}

def load_recipes():
    rdir = os.path.join(REPO, "data", "recipes")
    out = []
    for f in sorted(os.listdir(rdir)):
        if f.endswith(".json"):
            out.append(json.load(open(os.path.join(rdir, f), encoding="utf-8")))
    media = json.load(open(os.path.join(REPO, "assets", "data", "media.json"), encoding="utf-8"))
    for r in out:
        m = media.get(r["slug"], {"images": [], "videos": []})
        r["images"] = m["images"]
        r["videos"] = m["videos"]
        if not r.get("hero_image"):
            r["hero_image"] = r["images"][0]["file"] if r["images"] else fallback_hero(r)
    return out

def fallback_hero(r):
    chrome = {"Sweet & Baked": "assets/img/chrome-hands-1.jpg"}
    return chrome.get(r["genre"], "assets/img/chrome-ember-2.jpg")

def genre_slug(name):
    return GENRES[name]["slug"]

def esc(s):
    return html.escape(str(s), quote=True)

def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    out = ""
    for ch in s.lower():
        if ch.isalnum():
            out += ch
        elif out and out[-1] != "-":
            out += "-"
    return out.strip("-")

def rel(depth):
    return "../" * depth

def fmt_time(mins):
    if mins is None:
        return "—"
    if mins < 60:
        return f"{mins} min"
    h, m = divmod(mins, 60)
    if m:
        return f"{h} hr {m} min"
    return f"{h} hr"

def recipe_card(r, p=""):
    img = r["hero_image"]
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in r["tags"][:3])
    return f'''<a class="card recipe-card" href="{p}recipe/{r['slug']}.html" data-genre="{esc(r['genre'])}" data-tags="{esc(','.join(r['tags']))}" data-title="{esc(r['title'].lower())}">
  <div class="card-media"><img src="{esc(p)}{esc(img)}" alt="{esc(r['title'])}" loading="lazy"></div>
  <div class="card-body">
    <div class="card-genre">{esc(r['genre'])}</div>
    <h3 class="card-title">{esc(r['title'])}</h3>
    <p class="card-kicker">{esc(r['kicker'])}</p>
    <div class="card-meta"><span class="meta-item">⏱ {esc(r['time']['total_label'])}</span><span class="meta-item">◆ {esc(r['difficulty'].title())}</span></div>
    <div class="card-tags">{tags}</div>
  </div>
</a>'''

def head(title, desc, depth, og_image=None, extra_css="", page_class=""):
    p = rel(depth)
    og_img = SITE_URL + (og_image or "assets/img/chrome-ember-1.jpg")
    full_title = title if title == SITE_NAME else f"{title} — {SITE_NAME}"
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{esc(og_img)}">
<meta property="og:site_name" content="{SITE_NAME}">
<link rel="icon" type="image/svg+xml" href="{p}assets/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400;9..144,500;9..144,600;9..144,700;9..144,900&family=Inter:wght@400;500;600;700&family=Caveat:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{p}assets/style.css">
{extra_css}'''

def nav(depth, active=""):
    p = rel(depth)
    items = [("index.html", "Home", "home"), ("recipes.html", "All Recipes", "recipes"), ("collections.html", "Collections", "collections"), ("search.html", "Search", "search"), ("about.html", "About", "about")]
    links = "".join(f'<a href="{p}{href}" class="{"active" if key == active else ""}">{label}</a>' for href, label, key in items)
    return f'''<header class="site-header" id="siteHeader">
  <div class="wrap nav-wrap">
    <a class="logo" href="{p}index.html" id="logoLink" title="Salt &amp; Ember — click the pot, it sizzles">
      <svg class="logo-pot" viewBox="0 0 48 48" aria-hidden="true"><path d="M10 20h28v3c0 9-5 16-14 16S10 32 10 23v-3z" fill="currentColor"/><rect x="6" y="17" width="36" height="4" rx="2" fill="currentColor"/><path d="M17 14c0-3 3-3 3-6M24 14c0-3 3-3 3-6M31 14c0-3 3-3 3-6" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" fill="none"/></svg>
      <span class="logo-word">Salt <em>&amp;</em> Ember</span>
    </a>
    <nav class="nav-links">{links}</nav>
    <div class="nav-actions">
      <a class="btn btn-ghost btn-dice" id="surpriseBtn" href="#" title="Surprise me">🎲 <span>Surprise me</span></a>
      <form class="nav-search" action="{p}search.html" method="get">
        <input type="search" name="q" placeholder="Search 30 recipes…" autocomplete="off" aria-label="Search recipes">
        <kbd>/</kbd>
      </form>
    </div>
  </div>
</header>'''

def footer(depth):
    p = rel(depth)
    year = "2026"
    genre_links = "".join(f'<a href="{p}collection/{g["slug"]}.html">{esc(name)}</a>' for name, g in GENRES.items())
    return f'''<footer class="site-footer">
  <div class="wrap footer-grid">
    <div class="footer-brand">
      <div class="footer-logo">Salt <em>&amp;</em> Ember</div>
      <p>{SITE_TAGLINE} A scratch-built test kitchen — 30 recipes, {BUILT_NOTE.lower()}</p>
      <p class="footer-note">All recipes written with love and exact temperatures. Images sourced from the web with credits on each page.</p>
    </div>
    <div class="footer-col">
      <h4>Collections</h4>
      {genre_links}
    </div>
    <div class="footer-col">
      <h4>Kitchen</h4>
      <a href="{p}recipes.html">All recipes</a>
      <a href="{p}search.html">Search the pantry</a>
      <a href="{p}about.html">About this test</a>
      <a href="{REPO_URL}" target="_blank" rel="noopener">Source on GitHub ↗</a>
    </div>
  </div>
  <div class="wrap footer-bottom">
    <span>© {year} {SITE_NAME} — a throwaway test site that got too real.</span>
    <span class="footer-egg">the pot is listening 👀</span>
  </div>
</footer>
<script>window.__SE_DATA__ = {{ prefix: "{rel(depth)}" }};</script>
<script src="{p}assets/site.js" defer></script>'''

def layout(title, desc, depth, body, active="", og_image=None, page_class=""):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
{head(title, desc, depth, og_image)}
</head>
<body class="{page_class}">
{nav(depth, active)}
<main>
{body}
</main>
{footer(depth)}
</body>
</html>'''
