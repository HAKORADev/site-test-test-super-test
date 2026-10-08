import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from expand_data import KITCHEN, EQUIPMENT, FACTS, CLUSTERS, USES, SIMILAR_PAIRS

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RDIR = os.path.join(REPO, "data", "recipes")

slugs = sorted(f[:-5] for f in os.listdir(RDIR) if f.endswith(".json"))
errors = []

slug_set = set(slugs)
for s in EQUIPMENT:
    if s not in slug_set: errors.append(f"EQUIPMENT: unknown recipe {s}")
for s in FACTS:
    if s not in slug_set: errors.append(f"FACTS: unknown recipe {s}")
for s in slugs:
    if s not in EQUIPMENT: errors.append(f"missing EQUIPMENT for {s}")
    if s not in FACTS: errors.append(f"missing FACTS for {s}")
for e in EQUIPMENT.values():
    for item in e:
        if item["t"] not in KITCHEN: errors.append(f"unknown tool {item['t']}")
for u in USES:
    if u["recipe"] not in slug_set: errors.append(f"USES unknown recipe {u['recipe']}")
    if u["uses"] not in slug_set: errors.append(f"USES unknown component {u['uses']}")
for p in SIMILAR_PAIRS:
    if p["a"] not in slug_set: errors.append(f"SIMILAR unknown {p['a']}")
    if p["b"] not in slug_set: errors.append(f"SIMILAR unknown {p['b']}")
for c in CLUSTERS.values():
    for m in c["members"]:
        if m not in slug_set: errors.append(f"CLUSTER unknown {m}")

for s, f in FACTS.items():
    need = ["course", "base", "origin", "first_recorded", "name_means", "technique",
            "heat", "budget", "season", "signature", "serve_at", "pour", "wiki"]
    for k in need:
        if k not in f: errors.append(f"FACTS {s} missing {k}")

if errors:
    print("VALIDATION FAILED:")
    for e in errors: print(" -", e)
    sys.exit(1)

slug_to_cluster = {}
for cname, c in CLUSTERS.items():
    for m in c["members"]:
        slug_to_cluster.setdefault(m, []).append(cname)

used_in = {}
for u in USES:
    used_in.setdefault(u["uses"], []).append({"s": u["recipe"], "n": u["note"]})

similar = {}
for p in SIMILAR_PAIRS:
    similar.setdefault(p["a"], []).append({"s": p["b"], "n": p["note"]})
    similar.setdefault(p["b"], []).append({"s": p["a"], "n": p["note"]})

variants = {}
for cname, c in CLUSTERS.items():
    for m in c["members"]:
        variants.setdefault(m, []).extend(x for x in c["members"] if x != m)

for s in slugs:
    path = os.path.join(RDIR, s + ".json")
    r = json.load(open(path, encoding="utf-8"))
    r["equipment"] = EQUIPMENT[s]
    r["facts"] = FACTS[s]
    r["relations"] = {
        "used_in": used_in.get(s, []),
        "uses": [{"s": u["uses"], "n": u["note"]} for u in USES if u["recipe"] == s],
        "variants": [{"s": v, "cluster": slug_to_cluster[s][0]} for v in dict.fromkeys(variants.get(s, []))],
        "cluster_note": CLUSTERS[slug_to_cluster[s][0]]["note"] if s in slug_to_cluster else "",
        "similar": similar.get(s, []),
    }
    json.dump(r, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"injected equipment+facts+relations into {len(slugs)} recipe jsons")

kitchen = {"tools": KITCHEN, "cats": TOOL_CATS if False else None}
used_by = {k: [] for k in KITCHEN}
for s in slugs:
    for item in EQUIPMENT[s]:
        used_by[item["t"]].append(s)
kitchen = {"cats": {}, "tools": {}}
from expand_data import TOOL_CATS
kitchen["cats"] = TOOL_CATS
for k, v in KITCHEN.items():
    kitchen["tools"][k] = {"name": v["name"], "cat": v["cat"], "url": v["url"], "blurb": v["blurb"]}
kitchen["used_by"] = used_by
json.dump(kitchen, open(os.path.join(REPO, "data", "kitchen.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"wrote data/kitchen.json ({len(KITCHEN)} tools)")

n_var = sum(len(dict.fromkeys(variants.get(s, []))) for s in slugs) // 2
n_sim = len(SIMILAR_PAIRS) * 2
print(f"relations: {len(USES)} uses links, {n_var} variant links, {n_sim} similar links")

urls = sorted({v["url"] for v in KITCHEN.values()} | {f["wiki"] for f in FACTS.values()})
with open(os.path.join(REPO, "tools", "urls_to_check.txt"), "w") as f:
    f.write("\n".join(urls))
print(f"{len(urls)} unique URLs to verify -> tools/urls_to_check.txt")
