#!/usr/bin/env python3
"""Single entry point that proves this design-repo is internally consistent.

    python3 extraction/verify_all.py            # exit 1 on any FAIL

Runs inside design-repo/ alone (self-contained). When the sibling clone source (../src)
is present it also re-reads every cited source range and checks the cited tag is there;
without it those checks WARN instead of failing. Standard library + jsonschema.
"""
import importlib.util, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJ = ROOT.parent
HAS_SRC = (PROJ / "src").is_dir() and (PROJ / "src/styles/original.css").exists()
results = []
def rec(name, ok, detail="", warn=False): results.append((name, "PASS" if ok else ("WARN" if warn else "FAIL"), detail))
def J(rel): return json.loads((ROOT / rel).read_text())
def load_module(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

# Pins duplicated deliberately (BASELINE R3/R8): a registry edit alone cannot loosen them.
PINNED_AVAILABILITY = {
    "case.featured-image": "reference-only", "case.screenshot": "reference-only", "case.phone-screen": "reference-only",
    "case.video": "reference-only", "client.logo": "blocked-for-generation", "brand.wordmark": "blocked-for-generation",
    "person.intro-video": "blocked-for-generation", "decor.mascot-3d": "reference-only", "decor.lettered-shape": "reference-only",
    "decor.geometric-shape": "generation-safe", "ui.rive-icon": "reference-only",
    "placeholder.brand-mark": "generation-safe", "fictional.person-media": "generation-safe", "generated.case-visual": "generation-safe",
    "generated.product-visual": "generation-safe", "generated.motion-loop": "generation-safe", "generated.decorative-illustration": "generation-safe",
    "generated.lettering": "generation-safe", "generated.ui-icon": "generation-safe",
}
RETRIEVAL_INELIGIBLE = {"utility.preloader", "utility.page-transition", "utility.video-modal", "utility.back-button", "utility.password-gate"}
RUNTIME_RX = re.compile(r"preloader|loader|modal|dialog|overlay|drawer|transition|gate|toast|cursor|cookie|consent|banner|back-button", re.I)

# ------------------------------------------------------------------ 1. parse everything
bad_json = []
for p in ROOT.rglob("*.json"):
    try: json.loads(p.read_text())
    except Exception as e: bad_json.append(f"{p.relative_to(ROOT)}: {e}")
rec("json parses", not bad_json, bad_json[:3] or f"{len(list(ROOT.rglob('*.json')))} files")

man = J("registry.manifest.json"); allow = J("tokens/llm/component-allowlist.json")
contracts = {p.stem: json.loads(p.read_text()) for p in (ROOT / "sections").glob("*.json")}
templates = J("templates/templates.json")["templates"]; routes = J("templates/routes.json")["routes"]
roles = J("assets/asset-roles.json")["roles"]; graph = J("compatibility/graph.json")["rules"]
patterns = J("tokens/00-foundation/motion-patterns.json")["patterns"]

# ------------------------------------------------------------------ 2. schemas + semantic validation of every spec
from jsonschema import Draft7Validator
schema = J("schema/pagespec.schema.json"); Draft7Validator.check_schema(schema); V = Draft7Validator(schema)
CV = Draft7Validator(J("schema/section-contract.schema.json"))
sem = load_module("schema/semantic_validate.py", "semantic_validate")
specs = sorted((ROOT / "schema/examples").rglob("*.json"))
schema_errs, sem_errs = [], []
for f in specs:
    d = json.loads(f.read_text())
    schema_errs += [f"{f.name}: {e.message[:90]}" for e in V.iter_errors(d)]
    sem_errs += [f"{f.name}: {e['rule']} {e['message'][:80]}" for e in sem.errors(d)]
rec("pagespec schema (Draft-07)", not schema_errs, schema_errs[:3] or f"{len(specs)} specs, 0 errors")
rec("semantic validation", not sem_errs, sem_errs[:3] or f"{len(specs)} specs, 0 errors")
modes = {json.loads(f.read_text())["mode"] for f in specs}
rec("examples cover both modes", modes == {"reference", "generated"}, sorted(modes))
gen_tpls = {json.loads(f.read_text())["template"] for f in specs if json.loads(f.read_text())["mode"] == "generated"}
rec("generated example per template family", gen_tpls == set(templates), sorted(gen_tpls))
cerr = [f"{n}: {e.message[:90]}" for n, c in contracts.items() for e in CV.iter_errors(c)]
rec("section contracts (closed schema)", not cerr, cerr[:3] or f"{len(contracts)} contracts")

# ------------------------------------------------------------------ 3. provenance vs taxonomy
bad = [n for n, c in contracts.items() if c["semantic"]["id"] != c["id"] or c["source"]["id"] == c["id"] or c["id"] != n]
rec("source/semantic split", not bad, bad or "semantic.id == id, source.id != id for every contract")

# ------------------------------------------------------------------ 4. citations (re-read the real files)
def cites(o, path=""):
    if isinstance(o, dict):
        if "cite" in o and "tag" in o: yield path, o["cite"], o["tag"]
        if "evidence" in o and "evidenceTag" in o and isinstance(o["evidence"], str): yield path, o["evidence"], o["evidenceTag"]
        if {"file", "lines", "tag"} <= set(o): yield path, f"{o['file']}:{o['lines']}", o["tag"]
        for k, v in o.items(): yield from cites(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from cites(v, f"{path}[{i}]")
all_cites = []
for p in sorted(ROOT.rglob("*.json")):
    if p.relative_to(ROOT).parts[0] == "schema": continue   # schemas/examples are contracts, not evidence
    all_cites += [(str(p.relative_to(ROOT)) + c[0], c[1], c[2]) for c in cites(json.loads(p.read_text()))]
plain = J("extraction/measured-values.json")["citations"]
for k, v in plain.items():
    for c in (v if isinstance(v, list) else [v]):
        if re.match(r"^[\w./-]+:\d+(-\d+)?$", c): all_cites.append((f"measured-values.citations.{k}", c, None))
if HAS_SRC:
    cbad = []
    for where, c, tag in all_cites:
        m = re.match(r"^([\w./-]+):(\d+)(?:-(\d+))?$", c)
        if not m: cbad.append(f"{where}: malformed {c}"); continue
        f, a, b = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
        fp = PROJ / f
        if not fp.exists(): cbad.append(f"{where}: {f} missing"); continue
        ls = fp.read_text().splitlines()
        if b > len(ls) or a < 1 or a > b: cbad.append(f"{where}: {c} out of range ({len(ls)} lines)"); continue
        if tag and tag not in "\n".join(ls[a - 1:b]): cbad.append(f"{where}: tag {tag!r} not in {c}")
    rec("citations resolve + tag at cited lines", not cbad, cbad[:4] or f"{len(all_cites)} citations re-read against ../")
else:
    rec("citations resolve + tag at cited lines", False, f"no sibling clone source; {len(all_cites)} citations not re-read (standalone copy)", warn=True)

# ------------------------------------------------------------------ 5. allowlist parity + versions + counts
files = {"sections": {p.stem for p in (ROOT / "sections").glob("*.json")}, "components": {p.stem for p in (ROOT / "components").glob("*.json")}, "primitives": {p.stem for p in (ROOT / "primitives").glob("*.json")}}
par = []
for k in ("sections", "components", "primitives"):
    a = set(allow[k]) if isinstance(allow[k], list) else set(allow[k].keys())
    if a - files[k]: par.append(f"{k}: phantom allowlist ids {sorted(a - files[k])}")
    if files[k] - a: par.append(f"{k}: contracts missing from allowlist {sorted(files[k] - a)}")
if set(allow["assetRoles"]) != set(roles): par.append("assetRoles differ from assets/asset-roles.json")
for sid, e in allow["sections"].items():
    c = contracts.get(sid)
    if not c: continue
    want = ["content." + k for k in c["content"]] + (["variant"] if c["variants"] else []) + ["motion.pattern", "motion.reducedMotionFallback"] + ["style." + k for k in c["styleSlots"]]
    if e["settable"] != want: par.append(f"{sid}: settable differs from contract")
    if e["retrievalEligible"] != c["retrievalEligible"]: par.append(f"{sid}: retrievalEligible differs from contract")
rec("allowlist parity", not par, par[:3] or "sections/components/primitives/assetRoles all match")
vp = []
if man["allowlistVersion"] != allow["allowlistVersion"]: vp.append(f"manifest allowlistVersion {man['allowlistVersion']} != {allow['allowlistVersion']}")
if man["pageSpecVersion"] != schema["properties"]["pageSpecVersion"]["const"]: vp.append("pageSpecVersion != schema const")
rec("version parity (machine-checked fields)", not vp, vp or "allowlistVersion + pageSpecVersion")
cat = J("tokens/llm/token-catalog.json")
real = {"sections": len(files["sections"]), "templates": len(templates), "routes": len(routes), "primitives": len(files["primitives"]), "components": len(files["components"]),
        "assetRoles": len(roles), "colorTokens": len(cat["color"]), "typeStyles": len(cat["fontSize"]), "spacingTokens": len(cat["spacing"]), "motionPatterns": len(patterns),
        "graphRules": len(graph), "exampleSpecs": len(list((ROOT / "schema/examples").glob("*.json"))), "routeSpecs": len(list((ROOT / "schema/examples/routes").glob("*.json")))}
cd = [f"{k}: manifest {man['counts'].get(k)} != disk {v}" for k, v in real.items() if man["counts"].get(k) != v]
rec("manifest counts recomputed", not cd, cd[:3] or real)
rd = []
readme = (ROOT / "README.md").read_text() if (ROOT / "README.md").exists() else ""
for k, v in real.items():
    m = re.search(rf"\|\s*{k}\s*\|\s*(\d+)\s*\|", readme)
    if not m or int(m.group(1)) != v: rd.append(f"README {k}")
rec("README counts match disk", not rd, rd[:4] or "count table matches")
ep = man["entryPoints"]; epb = [f"{k}: {v}" for k, v in ep.items() if v.startswith("..") or v.startswith("/") or not (ROOT / v).exists()]
rec("entryPoints exist inside package", not epb, epb[:3] or f"{len(ep)} entry points")
rec("manifest approval flags", man.get("status") == "design-review-pending" and man.get("productionApproved") is False and man.get("category"), f"status={man.get('status')} productionApproved={man.get('productionApproved')} category={man.get('category')}")

# ------------------------------------------------------------------ 6. asset availability pins
ap = []
for r, v in roles.items():
    if r not in PINNED_AVAILABILITY: ap.append(f"{r}: not pinned in code")
    elif v["availability"] != PINNED_AVAILABILITY[r]: ap.append(f"{r}: registry {v['availability']} != pin {PINNED_AVAILABILITY[r]}")
    if v["availability"] != "generation-safe":
        subs = v.get("generationSafeSubstitutes", [])
        if not subs or any(PINNED_AVAILABILITY.get(s) != "generation-safe" for s in subs): ap.append(f"{r}: substitutes missing / not generation-safe")
for r in PINNED_AVAILABILITY:
    if r not in roles: ap.append(f"{r}: pinned but missing from registry")
if sem.PINNED_AVAILABILITY != PINNED_AVAILABILITY: ap.append("semantic_validate.PINNED_AVAILABILITY differs from verify_all")
for n, c in contracts.items():
    for g in c["generatedAssetRoles"]:
        if PINNED_AVAILABILITY.get(g) != "generation-safe": ap.append(f"{n}: generatedAssetRoles has non-generation-safe {g}")
    for g in c["assetRoles"]:
        if PINNED_AVAILABILITY.get(g) == "generation-safe" and g not in c["generatedAssetRoles"]: ap.append(f"{n}: {g} listed as reference role only")
rec("asset availability pinned + substitutes", not ap, ap[:3] or f"{len(roles)} roles pinned in both verify_all and semantic_validate")

# ------------------------------------------------------------------ 7. retrieval eligibility pins
rp = []
false_set = {n for n, c in contracts.items() if c["retrievalEligible"] is False}
if false_set != RETRIEVAL_INELIGIBLE: rp.append(f"contracts false={sorted(false_set)} != pin")
if sem.RETRIEVAL_INELIGIBLE != RETRIEVAL_INELIGIBLE: rp.append("semantic_validate.RETRIEVAL_INELIGIBLE differs")
for n, c in contracts.items():
    if RUNTIME_RX.search(n + " " + c["title"]) and n not in RETRIEVAL_INELIGIBLE: rp.append(f"{n} looks like runtime UI but is not pinned ineligible")
    if c["retrievalEligible"] is False and len(c.get("retrievalReason", "")) < 30: rp.append(f"{n}: reason < 30 chars")
rec("retrievalEligible pinned", not rp, rp[:3] or f"{len(RETRIEVAL_INELIGIBLE)} runtime sections ineligible, rest eligible")

# ------------------------------------------------------------------ 8. graph <-> validator agreement, templates, routes
gids = {r["id"]: r["severity"] for r in graph}
gv = [f"{k}: graph {s} vs validator {sem.RULE_SEVERITY.get(k)}" for k, s in gids.items() if sem.RULE_SEVERITY.get(k) != s]
gv += [f"{k}: in validator, not in graph" for k in sem.GRAPH_RULE_IDS - set(gids)]
src_txt = (ROOT / "schema/semantic_validate.py").read_text()
gv += [f"{k}: never raised by validator code" for k in gids if f'"{k}"' not in src_txt.split("RULE_SEVERITY = {", 1)[1].split("GRAPH_RULE_IDS", 1)[1]]
rec("graph rules == validator rules", not gv, gv[:3] or f"{len(gids)} rules agree")
tb = []
used = set()
for t, v in templates.items():
    for nd in v["nodes"]:
        for s in ([nd["section"]] if "section" in nd else nd["oneOf"]):
            used.add(s)
            if s not in contracts: tb.append(f"{t}: unknown section {s}")
            elif t not in contracts[s]["templates"]: tb.append(f"{s}: contract does not list {t}")
tb += [f"{s}: in no template" for s in set(contracts) - used]
paths = [r["path"] for r in routes]
if len(paths) != len(set(paths)): tb.append("duplicate route")
for r in routes:
    if r["template"] not in templates: tb.append(f"{r['path']}: unknown template")
    if r["path"] not in templates.get(r["template"], {}).get("routes", []): tb.append(f"{r['path']}: not listed in its template")
    slug = "home" if r["path"] == "/" else r["path"].split("/")[2]
    if not (ROOT / f"schema/examples/routes/{slug}.pagespec.json").exists(): tb.append(f"{r['path']}: no reference spec")
if sum(len(v["routes"]) for v in templates.values()) != len(routes): tb.append("template route lists != routes.json")
rec("templates/routes 1:1", not tb, tb[:3] or f"{len(routes)} routes each mapped once; every section used")

# ------------------------------------------------------------------ 9. tokens: catalog derived from foundation; policy consistent
tk = []
col = J("tokens/00-foundation/color.json")["tokens"]; ty = J("tokens/00-foundation/typography.json"); sp = J("tokens/00-foundation/spacing.json")["tokens"]; ra = J("tokens/00-foundation/radius.json")["tokens"]
if cat["color"] != {k: v["value"] + (f"@{v['alpha']}" if "alpha" in v else "") for k, v in col.items()}: tk.append("catalog.color drifted from foundation/color.json")
if cat["fontSize"] != {k: v["fontSize"] for k, v in ty["scale"].items()}: tk.append("catalog.fontSize drifted")
if cat["fontWeight"] != ty["fontWeights"]: tk.append("catalog.fontWeight drifted")
if cat["spacing"] != {k: v["value"] for k, v in sp.items()}: tk.append("catalog.spacing drifted")
if cat["radius"] != {k: v["value"] for k, v in ra.items()}: tk.append("catalog.radius drifted")
pol = J("tokens/llm/token-policy.json")
if pol["pageSpecTokenSlots"]["node.style.accent"]["allowed"] != sorted(k for k in cat["color"] if k.startswith("color.accent.")): tk.append("policy accent list != catalog accents")
for k in pol["rawValueRestrictions"]:
    if k not in cat: tk.append(f"policy category {k} is not a catalog key")
if {t: v["theme"] for t, v in templates.items()} != {k: v for k, v in pol["themeBinding"].items() if k.startswith("template.")}: tk.append("theme binding != templates")
for n, c in contracts.items():
    for t in c["uses"]["tokens"]:
        if not any(t in (cat.get(g) or {}) for g in ("color", "fontSize", "spacing", "radius")): tk.append(f"{n}: unknown token {t}")
rec("token catalog + policy derived/consistent", not tk, tk[:3] or "catalog matches foundation files; policy keys resolve")
reg = json.dumps(man["entryPoints"])
rec("token catalog/policy registered", "token-catalog" in reg and "token-policy" in reg and "motion-patterns" in reg and "component-allowlist" in reg, "entryPoints")

# ------------------------------------------------------------------ 10. motion
mo = []
for n, c in contracts.items():
    for m in c["motion"]["allowed"]:
        if m not in patterns: mo.append(f"{n}: unknown pattern {m}")
        elif c["motion"]["reducedMotionFallback"].get(m) != patterns[m]["fallback"]: mo.append(f"{n}: fallback for {m}")
    if c["motion"]["default"] not in c["motion"]["allowed"]: mo.append(f"{n}: default not allowed")
rec("motion patterns + reduced-motion fallbacks", not mo, mo[:3] or f"{len(patterns)} patterns")

# ------------------------------------------------------------------ 11. wrapper gate (R9)
wg = load_module("extraction/wrapper_gate.py", "wrapper_gate")
we, ww = wg.run(ROOT)
rec("wrapper gate (measured heights @1440)", not we, we[:3] or f"0 errors, {len(ww)} warnings")

# ------------------------------------------------------------------ 12. policy binding + hash (R15)
ph = load_module("extraction/policy_hash.py", "policy_hash").compute(ROOT)
dp = man.get("designPolicy", {}); pf = J("policy/design-policy.json")
pb = []
if dp.get("contentHash") != ph: pb.append(f"manifest contentHash stale ({dp.get('contentHash')[:20]} vs {ph[:20]})")
if pf.get("contentHash") != ph: pb.append("policy/design-policy.json contentHash stale")
if pf.get("enforcedBy") != load_module("extraction/policy_hash.py", "policy_hash2").ENFORCED_BY: pb.append("enforcedBy != hashed files")
if pf["approval"].get("architectureDecisionRecorded") is not False and not pf["approval"].get("decidedBy"): pb.append("approval recorded without a named human decision")
rec("design policy hash + approval", not pb, pb or ph)

# ------------------------------------------------------------------ 13. source identity registry + copy index in sync
mv = J("extraction/measured-values.json"); idx = J("extraction/source-copy-index.json")
ci = []
fulls = set(idx["fullStrings"])
for f in (ROOT / "schema/examples").glob("reference.*.json"):
    for path, s in sem.copy_strings([n["content"] for n in json.loads(f.read_text())["nodes"]]):
        w = sem.words(s)
        if len(w) >= 4 and sem.h16(" ".join(w)) not in fulls: ci.append(f"{f.name}{path}: not in copy index")
rec("source-copy index covers reference copy", not ci, ci[:3] or f"{len(idx['shingles'])} shingles, {len(fulls)} full strings")
if HAS_SRC:
    corpus = "\n".join(p.read_text() for p in list((PROJ / "src").rglob("*.js")) + list((PROJ / "src").rglob("*.jsx")) + list((PROJ / "src").rglob("*.json")) + [PROJ / "index.html"]).lower().replace("\u2019", "'")
    norm = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", corpus).replace("\\n", " ").replace("{'", " ").replace("'}", " "))
    miss = [p for v in mv["sourceIdentity"]["patterns"].values() for p in v if p.lower().replace("\u2019", "'") not in corpus and re.sub(r"\s+", " ", p.lower().replace("\u2019", "'")) not in norm]
    rec("identity patterns occur in real source", not miss, miss[:3] or f"{sum(len(v) for v in mv['sourceIdentity']['patterns'].values())} patterns verified")
else:
    rec("identity patterns occur in real source", False, "no sibling source; not re-checked", warn=True)

# ------------------------------------------------------------------ 14. hygiene
junk = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file() and (p.name in (".DS_Store", "Thumbs.db", "desktop.ini") or "__MACOSX" in p.parts or "__pycache__" in p.parts or p.suffix == ".pyc")]
rec("no junk files", not junk, junk[:3] or "none")
absr = re.compile(r"/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+/|/private/(tmp|var)/|C:\\\\Users\\\\")
absp = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file() and p.suffix in (".json", ".md", ".py", ".mjs") and absr.search(p.read_text(errors="ignore"))]
rec("no absolute machine paths", not absp, absp[:3] or "none")
par_f = ROOT / "extraction/parity-results.json"
if par_f.exists():
    pr = json.loads(par_f.read_text()); selfap = [e for e in pr.get("exceptions", []) if e.get("approvedBy")]
    rec("parity results recorded, no self-approved exceptions", not selfap, f"avg {pr.get('summary', {}).get('averageScore')}; {len(pr.get('exceptions', []))} exceptions pending human approval")
else:
    rec("parity results recorded, no self-approved exceptions", False, "extraction/parity-results.json missing", warn=True)

w = max(len(n) for n, _, _ in results)
for n, r, d in results: print(f"{r:4}  {n.ljust(w)}  {d}")
f = sum(1 for _, r, _ in results if r == "FAIL"); wn = sum(1 for _, r, _ in results if r == "WARN")
print(f"\nverify_all: {len(results) - f - wn} pass, {f} fail, {wn} warn")
sys.exit(1 if f else 0)
