from common import (esc, rel, fmt_time, GENRES, recipe_card, layout, SITE_URL, REPO_URL,
                    heat_dots, base_axis)
import urllib.parse

def build_recipe_page(r, all_recipes, kitchen=None):
    depth = 1
    p = rel(depth)
    imgs = r["images"]
    hero = imgs[0]["file"] if imgs else "assets/img/chrome-ember-2.jpg"
    tags_html = "".join(f'<a class="chip" href="{p}recipes.html?tag={esc(t)}">{esc(t)}</a>' for t in r["tags"])
    ing_rows = "".join(
        f'''<li><label class="ing"><input type="checkbox" data-ing="{esc(r['slug'])}"><span class="ing-box" aria-hidden="true"></span><span class="ing-amount">{esc(i['amount'])}</span><span class="ing-item">{esc(i['item'])}{(' <em>' + esc(i['note']) + '</em>') if i.get('note') else ''}</span></label></li>'''
        for i in r["ingredients"])
    steps_html = "".join(
        f'''<li class="step"><div class="step-num">{n}</div><div class="step-body"><h4>{esc(s['title'])}</h4><p>{esc(s['text'])}</p></div></li>'''
        for n, s in enumerate(r["steps"], 1))
    notes_html = "".join(f"<li>{esc(n)}</li>" for n in r["notes"])
    gallery_html = ""
    if len(imgs) > 1:
        figs = "".join(
            f'''<figure class="gal-item" data-lb><img src="{p}{esc(im['file'])}" alt="{esc(im.get('alt') or r['title'])}" loading="lazy"><figcaption>{esc(im.get('source','web'))}</figcaption></figure>'''
            for im in imgs[1:])
        srcs = sorted({im.get("src_url", "") for im in imgs[1:] if im.get("src_url")})
        src_list = "".join(f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(u)}</a>' for u in srcs[:8])
        extra = ""
        creators = [im for im in imgs[1:] if im.get("creator")]
        if creators:
            extra = "<p>CC-licensed images: " + "; ".join(
                f"{esc(im['creator'])} ({esc(im.get('license','cc')).upper()})" for im in creators[:8]) + ".</p>"
        gallery_html = f'''<section class="recipe-section" id="gallery">
<h2 class="section-title"><span>Gallery</span></h2>
<div class="gallery">{figs}</div>
<details class="credits"><summary>Image sources &amp; credits</summary><p>Images are web-sourced via image search and self-hosted. Original sources:</p>{extra}{src_list}</details>
</section>'''
    videos_html = ""
    if r["videos"]:
        vcards = "".join(
            f'''<div class="video-card" data-yt="{esc(v['id'])}" tabindex="0" role="button" aria-label="Play: {esc(v['title'])}">
<div class="video-thumb"><img src="https://i.ytimg.com/vi/{esc(v['id'])}/hqdefault.jpg" alt="" loading="lazy"><div class="video-play">▶</div></div>
<div class="video-meta"><h4>{esc(v['title'])}</h4><p>{esc(v['channel'])}</p></div>
</div>'''
            for v in r["videos"])
        videos_html = f'''<section class="recipe-section" id="watch">
<h2 class="section-title"><span>Watch it made</span></h2>
<p class="section-sub">Verified working videos — click a card to load the embed.</p>
<div class="video-grid">{vcards}</div>
</section>'''
    links_html = "".join(
        f'''<a class="ext-link" href="{esc(l['url'])}" target="_blank" rel="noopener"><div class="ext-body"><h4>{esc(l['title'])}</h4><p>{esc(l['desc'])}</p></div><span class="ext-domain">{esc(l['url'].split('/')[2].replace('www.',''))} ↗</span></a>'''
        for l in r["links"])
    pairings_html = ""
    pairs = [x for x in all_recipes if x["slug"] in r["pairings"]]
    if pairs:
        pair_cards = "".join(recipe_card(x, p) for x in pairs)
        pairings_html = f'''<section class="recipe-section" id="pairings">
<h2 class="section-title"><span>Pairs well with</span></h2>
<div class="pair-grid">{pair_cards}</div>
</section>'''
    equipment_html = ""
    eq = r.get("equipment", [])
    if eq:
        tool_cards = "".join(
            f'''<a class="tool-link" href="{esc(kitchen['tools'][e['t']]['url'] if kitchen else '#')}" target="_blank" rel="noopener">
<div class="tool-link-head"><span class="tool-name">{esc(kitchen['tools'][e['t']]['name'] if kitchen else e['t'])}</span><span class="tool-domain">wikipedia ↗</span></div>
{('<p class="tool-note">' + esc(e['n']) + '</p>') if e.get('n') else ''}
</a>'''
            for e in eq)
        equipment_html = f'''<section class="recipe-section" id="equipment">
<h2 class="section-title"><span>The tool wall</span></h2>
<p class="section-sub">Every tool this recipe leans on — click any tool for its full story. The whole catalog lives on <a href="{p}kitchen.html">the Tool Wall</a>.</p>
<div class="equip-grid">{tool_cards}</div>
</section>'''
    f = r.get("facts", {})
    dots, hlabel = heat_dots(f.get("heat", 0))
    facts_rows = [
        ("Course", f.get("course", "—")),
        ("Base", f.get("base", "—")),
        ("Origin", f.get("origin", "—")),
        ("First recorded", f.get("first_recorded", "—")),
        ("Name means", f.get("name_means", "—")),
        ("Key technique", f.get("technique", "—")),
        ("Heat", f'<span class="heat-dots">{dots}</span> {esc(hlabel)}'),
        ("Budget", f'{esc(f.get("budget", "—"))}<span class="budget-hint">{" pocket change" if f.get("budget")=="$" else " fair" if f.get("budget")=="$$" else " occasion"}</span>'),
        ("Best season", f.get("season", "—")),
        ("Signature", f.get("signature", "—")),
        ("Serve it", f.get("serve_at", "—")),
        ("Pour", f.get("pour", "—")),
    ]
    facts_html = "".join(
        f'<div class="fact-row"><div class="fact-k">{esc(k)}</div><div class="fact-v">{v}</div></div>'
        for k, v in facts_rows)
    datasheet_html = f'''<section class="recipe-section" id="datasheet">
<h2 class="section-title"><span>Data sheet</span></h2>
<p class="section-sub">The dish at a glance — twelve field notes for the collectors.</p>
<div class="facts-table">{facts_html}
<div class="fact-row fact-link"><div class="fact-k">Wikipedia</div><div class="fact-v"><a href="{esc(f.get('wiki','#'))}" target="_blank" rel="noopener">{esc(urllib.parse.unquote(f.get('wiki','#').split('/wiki/')[-1]).replace('_',' '))} ↗</a></div></div>
</div>
</section>'''
    rels = r.get("relations", {})
    by_slug = {x["slug"]: x for x in all_recipes}
    def rel_row(x, note):
        rx = by_slug.get(x["s"] if isinstance(x, dict) else x)
        if not rx: return ""
        n = note(x) if note else ""
        return f'''<a class="rel-item" href="{p}recipe/{rx['slug']}.html">
<img src="{p}{esc(rx['hero_image'])}" alt="" loading="lazy">
<div class="rel-body"><div class="rel-genre">{esc(rx['genre'])}</div><h4>{esc(rx['title'])}</h4>
{('<p>' + esc(n) + '</p>') if n else ''}</div><span class="rel-arrow">→</span>
</a>'''
    ft_parts = []
    if rels.get("used_in"):
        rows = "".join(rel_row(x, lambda x: x.get("n", "")) for x in rels["used_in"])
        ft_parts.append(f'<div class="ft-block"><h4 class="ft-title">Used in</h4><p class="ft-sub">Other dishes in this kitchen that lean on this recipe.</p>{rows}</div>')
    if rels.get("uses"):
        rows = "".join(rel_row(x, lambda x: x.get("n", "")) for x in rels["uses"])
        ft_parts.append(f'<div class="ft-block"><h4 class="ft-title">Uses from the pantry</h4><p class="ft-sub">Recipes this dish quietly depends on.</p>{rows}</div>')
    if rels.get("variants"):
        note = rels.get("cluster_note", "")
        sub = f'<p class="ft-sub">{esc(note)}</p>' if note else ""
        rows = "".join(rel_row(x, lambda x: "") for x in rels["variants"])
        ft_parts.append(f'<div class="ft-block"><h4 class="ft-title">Versions of the idea</h4>{sub}{rows}</div>')
    if rels.get("similar"):
        rows = "".join(rel_row(x, lambda x: x.get("n", "")) for x in rels["similar"][:3])
        ft_parts.append(f'<div class="ft-block"><h4 class="ft-title">Similar in spirit</h4><p class="ft-sub">If this one works for you, the neighbors probably will too.</p>{rows}</div>')
    family_html = ""
    if ft_parts:
        family_html = f'''<section class="recipe-section" id="family">
<h2 class="section-title"><span>The family tree</span></h2>
<div class="family-tree">{"".join(ft_parts)}</div>
</section>'''
    side_jump = f'''<li><a href="#story">The story</a></li>
<li><a href="#ingredients">Ingredients</a></li>
{('<li><a href="#equipment">The tool wall</a></li>' if equipment_html else '')}
<li><a href="#method">Method</a></li>
{('<li><a href="#gallery">Gallery</a></li>' if gallery_html else '')}
{('<li><a href="#watch">Videos</a></li>' if videos_html else '')}
<li><a href="#notes">Chef's notes</a></li>
<li><a href="#datasheet">Data sheet</a></li>
<li><a href="#links">Related links</a></li>
<li><a href="#comments">Comments</a></li>
{('<li><a href="#pairings">Pairs with</a></li>' if pairings_html else '')}
{('<li><a href="#family">Family tree</a></li>' if family_html else '')}'''
    body = f'''<article class="recipe-hero">
<div class="recipe-hero-bg" style="background-image:url('{p}{esc(hero)}')"></div>
<div class="recipe-hero-veil"></div>
<div class="wrap recipe-hero-inner">
<a class="crumb" href="{p}collection/{GENRES[r['genre']]['slug']}.html">← {esc(r['genre'])}</a>
<h1 class="recipe-title">{esc(r['title'])}</h1>
<p class="recipe-kicker">{esc(r['kicker'])}</p>
<div class="recipe-meta">
<span class="meta-pill">⏱ {esc(r['time']['total_label'])}</span>
<span class="meta-pill">◆ {esc(r['difficulty'].title())}</span>
<span class="meta-pill">🍽 serves {esc(r['servings'])}</span>
</div>
<div class="recipe-tags">{tags_html}</div>
</div>
</article>

<div class="wrap recipe-layout">
<aside class="recipe-side">
<div class="side-card jump-card">
<h4>On this page</h4>
<ul class="jump">{side_jump}</ul>
</div>
<div class="side-card timer-card">
<h4>Kitchen timer</h4>
<div class="timer-display" id="timerDisplay">00:00</div>
<div class="timer-quick"><button class="btn btn-tiny" data-timer="10">10m</button><button class="btn btn-tiny" data-timer="20">20m</button><button class="btn btn-tiny" data-timer="{max(5, (r['time']['total_min'] or 30) // 2)}">½ recipe</button></div>
<div class="timer-input"><input id="timerMin" type="number" min="0" max="600" placeholder="min"> <button class="btn btn-tiny" id="timerSet">Set</button></div>
<div class="timer-ctrl"><button class="btn btn-tiny btn-primary" id="timerStart">Start</button><button class="btn btn-tiny" id="timerReset">Reset</button></div>
</div>
<div class="side-card print-card">
<h4>Recipe card</h4>
<p>Print this page — the layout folds into a real recipe card.</p>
<button class="btn btn-ghost btn-block" onclick="window.print()">🖨 Print recipe</button>
</div>
</aside>

<div class="recipe-main">
<section class="recipe-section" id="story">
<p class="dropcap">{esc(r['story'][0])}</p>
<p>{esc(r['story'][1])}</p>
<div class="funfact"><span class="funfact-ic">✦</span><div><strong>Kitchen wisdom.</strong> {esc(r['fun_fact'])}</div></div>
</section>

<section class="recipe-section" id="ingredients">
<h2 class="section-title"><span>Ingredients</span></h2>
<p class="section-sub">serves {esc(r['servings'])} — tick items off as you shop; it saves as you go</p>
<ul class="ing-list">{ing_rows}</ul>
</section>

{equipment_html}

<section class="recipe-section" id="method">
<h2 class="section-title"><span>Method</span></h2>
<ol class="steps">{steps_html}</ol>
</section>

{gallery_html}
{videos_html}

<section class="recipe-section" id="notes">
<h2 class="section-title"><span>Chef's notes</span></h2>
<ul class="notes-list">{notes_html}</ul>
<div class="storage"><strong>Keeping it:</strong> {esc(r['storage'])}</div>
</section>

{datasheet_html}

<section class="recipe-section" id="links">
<h2 class="section-title"><span>Go deeper</span></h2>
<div class="ext-links">{links_html}</div>
</section>

<section class="recipe-section" id="comments">
<h2 class="section-title"><span>Comments</span></h2>
<p class="section-sub">Powered by GitHub Issues — the backup kitchen. One issue per recipe; your comment lands in the repo.</p>
<div id="ghComments" data-slug="{esc(r['slug'])}" data-title="{esc(r['title'])}" data-repo="HAKORADev/site-test-test-super-test">
<div class="comment-loading">Checking the comment box…</div>
</div>
<a class="btn btn-primary btn-block" id="ghNewComment" href="#" target="_blank" rel="noopener">💬 Leave a comment on GitHub</a>
</section>

{pairings_html}

{family_html}
</div>
</div>'''
    desc = r["kicker"]
    return layout(r["title"], desc, depth, body, active="recipes", og_image=hero)
