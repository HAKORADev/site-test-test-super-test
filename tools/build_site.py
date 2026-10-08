import json, os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (REPO, SITE_NAME, SITE_TAGLINE, SITE_URL, REPO_URL, BUILT_NOTE,
                    GENRES, load_recipes, esc, rel, fmt_time, recipe_card, layout)
from recipe import build_recipe_page

recipes = load_recipes()
by_genre = {}
for r in recipes:
    by_genre.setdefault(r["genre"], []).append(r)

OUT = REPO

def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path)

# ---------- index.html ----------
featured = [r for r in recipes if r["slug"] in ("classic-margherita-pizza", "beef-bourguignon", "shoyu-ramen", "smash-burger", "chocolate-lava-cake", "pho-bo")]
coll_cards = "".join(f'''<a class="card coll-card" href="collection/{g['slug']}.html">
<div class="card-media"><img src="{esc(next((x['hero_image'] for x in recipes if x['slug']==g['cover_key']), 'assets/img/chrome-ember-1.jpg'))}" alt="{esc(name)}" loading="lazy"></div>
<div class="card-body"><h3 class="coll-name">{esc(name)}</h3><p class="coll-blurb">{esc(g['blurb'])}</p><span class="coll-count">{len(by_genre[name])} recipe{'s' if len(by_genre[name])>1 else ''} →</span></div>
</a>''' for name, g in GENRES.items())
hero_recipes = random.Random(7).sample(recipes, 3)
hero_strip = "".join(f'''<a class="hero-tile" href="recipe/{r['slug']}.html"><img src="{esc(r['hero_image'])}" alt="{esc(r['title'])}" loading="lazy"><span>{esc(r['title'])}</span></a>''' for r in hero_recipes)
featured_cards = "".join(recipe_card(r) for r in featured)
body = f'''<section class="home-hero">
<div class="home-hero-bg" style="background-image:url('assets/img/chrome-ember-1.jpg')"></div>
<div class="home-hero-veil"></div>
<div class="wrap home-hero-inner">
<p class="hero-eyebrow">est. last night · a test kitchen</p>
<h1 class="hero-title">Cook like someone<br><em>hungry is watching.</em></h1>
<p class="hero-sub">{SITE_TAGLINE} Thirty recipes written like we meant it — exact temperatures, real technique, fun facts at the bottom of every pot.</p>
<div class="hero-cta">
<a class="btn btn-primary btn-big" href="recipes.html">Browse all 30 recipes</a>
<a class="btn btn-ghost btn-big btn-dice" href="#" id="heroSurprise">🎲 Surprise me</a>
</div>
</div>
</section>

<section class="wrap home-strip">
<h2 class="strip-label">Tonight could be —</h2>
<div class="hero-strip">{hero_strip}</div>
</section>

<section class="wrap home-section">
<div class="section-head"><h2>The eight collections</h2><a class="see-all" href="collections.html">Browse them all →</a></div>
<div class="coll-grid">{coll_cards}</div>
</section>

<section class="wrap home-section">
<div class="section-head"><h2>From the kitchen</h2><a class="see-all" href="recipes.html">All recipes →</a></div>
<div class="card-grid">{featured_cards}</div>
</section>

<section class="wrap home-quote">
<blockquote>"Tell me what you eat, and I will tell you what you are."<cite>— Jean Anthelme Brillat-Savarin, who never saw a smash burger</cite></blockquote>
</section>'''
write("index.html", layout(SITE_NAME, SITE_TAGLINE + " Thirty real recipes with galleries, videos, fun facts and custom search.", 0, body, active="home", og_image="assets/img/chrome-ember-1.jpg"))

# ---------- recipes.html ----------
all_cards = "".join(recipe_card(r) for r in recipes)
all_tags = sorted({t for r in recipes for t in r["tags"]})
tag_chips = "".join(f'<button class="chip tag-chip" data-tag="{esc(t)}">{esc(t)}</button>' for t in all_tags)
genre_chips = "".join(f'<button class="chip genre-chip" data-genre="{esc(name)}">{esc(name)}</button>' for name in GENRES)
body = f'''<section class="wrap page-head">
<h1 class="page-title">All recipes</h1>
<p class="page-sub">Thirty dishes. Filter by collection, tag, or just start typing — the grid answers instantly.</p>
</section>
<section class="wrap filter-bar">
<input type="search" id="filterInput" class="filter-input" placeholder="Type to filter — “ramen”, “baking”, “one-pot”…">
<div class="chip-row"><span class="chip-label">Collections</span>{genre_chips}</div>
<div class="chip-row"><span class="chip-label">Tags</span>{tag_chips}</div>
<div class="filter-foot"><span id="filterCount"></span><button class="btn btn-ghost btn-tiny" id="filterClear" hidden>Clear filters</button></div>
</section>
<section class="wrap"><div class="card-grid" id="recipeGrid">{all_cards}</div>
<div class="no-results" id="noResults" hidden><h3>Nothing in the pantry matches.</h3><p>Try “quick”, “vegetarian”, “soup” — or <a href="search.html">open full search</a>.</p></div>
</section>'''
write("recipes.html", layout("All Recipes", "Browse all thirty recipes with live filtering by collection, tag and text.", 0, body, active="recipes"))

# ---------- collections.html ----------
coll_cards2 = "".join(f'''<a class="card coll-card big" href="collection/{g['slug']}.html">
<div class="card-media tall"><img src="{esc(next((x['hero_image'] for x in recipes if x['slug']==g['cover_key']), 'assets/img/chrome-ember-1.jpg'))}" alt="{esc(name)}" loading="lazy"></div>
<div class="card-body"><h3 class="coll-name">{esc(name)}</h3><p class="coll-blurb">{esc(g['blurb'])}</p><span class="coll-count">{len(by_genre[name])} recipe{'s' if len(by_genre[name])>1 else ''} →</span></div>
</a>''' for name, g in GENRES.items())
body = f'''<section class="wrap page-head">
<h1 class="page-title">Collections</h1>
<p class="page-sub">Eight shelves in the pantry. Every recipe lives in exactly one — follow a shelf, or hunt by tag from <a href="recipes.html">the index</a>.</p>
</section>
<section class="wrap"><div class="coll-grid">{coll_cards2}</div></section>'''
write("collections.html", layout("Collections", "Eight recipe collections, from Italian classics to Sweet & Baked.", 0, body, active="collections"))

# ---------- collection/<slug>.html ----------
for name, g in GENRES.items():
    rs = by_genre[name]
    cover = next((x["hero_image"] for x in recipes if x["slug"] == g["cover_key"]), "assets/img/chrome-ember-1.jpg")
    cards = "".join(recipe_card(r, "../") for r in rs)
    tagcloud = sorted({t for r in rs for t in r["tags"]})
    cloud = "".join(f'<a class="chip" href="../recipes.html?tag={esc(t)}">{esc(t)}</a>' for t in tagcloud)
    cbody = f'''<section class="coll-hero">
<div class="coll-hero-bg" style="background-image:url('../{esc(cover)}')"></div><div class="coll-hero-veil"></div>
<div class="wrap coll-hero-inner"><a class="crumb" href="../collections.html">← All collections</a>
<h1 class="page-title">{esc(name)}</h1>
<p class="coll-hero-blurb">{esc(g['blurb'])}</p></div></section>
<section class="wrap"><div class="card-grid">{cards}</div>
<div class="tag-cloud"><span class="chip-label">Tags in this shelf</span>{cloud}</div></section>'''
    write(f"collection/{g['slug']}.html", layout(name, g["blurb"], 1, cbody, active="collections", og_image=cover))

# ---------- search.html ----------
body = f'''<section class="wrap page-head">
<h1 class="page-title">Search the pantry</h1>
<p class="page-sub">Full-text across titles, ingredients, tags and steps. Use <span class="kbd-hint">↑ ↓</span> to move, <span class="kbd-hint">↵</span> to open.</p>
</section>
<section class="wrap search-wrap">
<input type="search" id="searchInput" class="filter-input big-input" placeholder="mushroom… baking… spicy… 30 minutes…" autocomplete="off" autofocus>
<div class="chip-row"><span class="chip-label">Quick</span>
<button class="chip genre-chip" data-q="quick">under an hour</button>
<button class="chip genre-chip" data-q="vegetarian">vegetarian</button>
<button class="chip genre-chip" data-q="soup">soup</button>
<button class="chip genre-chip" data-q="dessert">dessert</button>
<button class="chip genre-chip" data-q="baking">baking</button>
<button class="chip genre-chip" data-q="one-pot">one-pot</button>
</div>
<div id="searchResults" class="search-results"></div>
</section>'''
write("search.html", layout("Search", "Instant full-text search across every recipe, ingredient and tag.", 0, body, active="search"))

# ---------- about.html ----------
about_body = f'''<section class="wrap page-head">
<h1 class="page-title">About this kitchen</h1>
<p class="page-sub">A very specific experiment with a very honest answer.</p>
</section>
<section class="wrap about-grid">
<div class="about-main">
<p class="dropcap">Salt &amp; Ember is a cooking site built overnight as a proof of work. The brief was simple and slightly dangerous: prove that a real, polished content site can be built end to end — thirty recipes, each with galleries of web-sourced photography, verified YouTube videos, custom collections, custom search, related links, and a comment system that costs nothing.</p>
<p>Every recipe here was written from actual kitchen knowledge — real temperatures, real timings, the technique details that separate a dish from a rumor. The photography was sourced from the open web via image search, then self-hosted so nothing rots; every gallery carries its sources. Every video was checked against YouTube's oEmbed endpoint before shipping — if a card is on a page, the video exists and allows embedding.</p>
<p>The whole thing is a static site: a Python generator writes plain HTML from a small JSON "database" of recipes. No framework, no build server, no database daemon. Search runs entirely in your browser against a JSON index. Comments run on GitHub Issues — one issue per recipe, fetched client-side from the public API. It is the cheapest fully-functional backend on the internet, and for a site like this, arguably the most durable.</p>
<p>Why "Salt &amp; Ember"? Because every dish on this site is, at some level, salt applied with heat. Also because the other forty name ideas were worse.</p>
<p class="about-sign">— built between sunset and sunrise, {BUILT_NOTE.lower()}</p>
</div>
<aside class="about-side">
<div class="side-card">
<h4>Under the hood</h4>
<ul class="about-facts">
<li><strong>30</strong> recipes, hand-written</li>
<li><strong>240+</strong> web-sourced photos, self-hosted</li>
<li><strong>70+</strong> verified YouTube videos</li>
<li><strong>8</strong> collections, {len({t for r in recipes for t in r['tags']})} tags</li>
<li><strong>0</strong> frameworks, trackers, or cookies</li>
<li><strong>1</strong> easter egg, if you click the pot</li>
</ul>
</div>
<div class="side-card">
<h4>Try this</h4>
<p>Hit <strong>Surprise me</strong> in the nav. Use the kitchen timer on any recipe page. Tick ingredients off while shopping — the list remembers. And the footer knows you're reading it.</p>
</div>
<div class="side-card">
<h4>Source</h4>
<p>Everything — generator, data, theme — lives in the open:</p>
<a class="btn btn-ghost btn-block" href="{REPO_URL}" target="_blank" rel="noopener">View repository ↗</a>
</div>
</aside>
</section>'''
write("about.html", layout("About", "The story of an overnight cooking-site experiment.", 0, about_body, active="about"))

# ---------- 404.html ----------
body = f'''<section class="wrap notfound">
<h1 class="nf-title">404<span class="nf-flame">🔥</span></h1>
<h2>Something burned.</h2>
<p>This page left the pot on and walked away. The rest of the kitchen is intact:</p>
<div class="nf-actions"><a class="btn btn-primary" href="index.html">Back to the kitchen</a><a class="btn btn-ghost" href="search.html">Search the pantry</a></div>
<div class="nf-random"><a href="#" id="nfSurprise">or let the dice decide →</a></div>
</section>'''
write("404.html", layout("Page not found", "404 — this recipe went missing.", 0, body))

# ---------- search index ----------
idx = []
for r in recipes:
    idx.append({
        "slug": r["slug"], "title": r["title"], "genre": r["genre"], "tags": r["tags"],
        "difficulty": r["difficulty"], "total_min": r["time"]["total_min"], "time_label": r["time"]["total_label"],
        "kicker": r["kicker"], "img": r["hero_image"],
        "text": " ".join([r["title"], r["genre"], r["kicker"], " ".join(r["tags"]),
                          " ".join(i["item"] for i in r["ingredients"]),
                          " ".join(s["text"] for s in r["steps"]), " ".join(r["story"])]).lower(),
    })
json.dump(idx, open(os.path.join(OUT, "assets", "search-index.json"), "w"), ensure_ascii=False)
print("wrote assets/search-index.json")

# ---------- sitemap + robots ----------
urls = ["", "recipes.html", "collections.html", "search.html", "about.html"]
for r in recipes:
    urls.append("recipe/" + r["slug"] + ".html")
for g in GENRES.values():
    urls.append("collection/" + g["slug"] + ".html")
xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
xml += "".join(f"<url><loc>{SITE_URL}{u}</loc></url>\n" for u in urls)
xml += "</urlset>"
write("sitemap.xml", xml)
write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n")

# ---------- recipe pages ----------
for r in recipes:
    write(f"recipe/{r['slug']}.html", build_recipe_page(r, recipes))

print(f"\nDONE: {len(recipes)} recipe pages, {len(GENRES)} collection pages, index/search/about/404/sitemap")
