#!/usr/bin/env python3
"""Semantic validator for PageSpecs: everything Draft-07 cannot express.

    python3 schema/semantic_validate.py path/to/spec.json [...]      # exit 1 on any error

Rule ids match compatibility/graph.json (verify_all.py checks both directions) plus the
contract, token-policy and generated-mode rules below. Standard library only; the repo
root is derived from this file's location (no absolute paths).
"""
import hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
def J(rel): return json.loads((ROOT / rel).read_text())

CONTRACTS = {p.stem: json.loads(p.read_text()) for p in (ROOT / "sections").glob("*.json")}
TEMPLATES = J("templates/templates.json")["templates"]
ROUTES = {r["path"]: r for r in J("templates/routes.json")["routes"]}
GRAPH = {r["id"]: r for r in J("compatibility/graph.json")["rules"]}
CATALOG = J("tokens/llm/token-catalog.json")
POLICY = J("tokens/llm/token-policy.json")
PATTERNS = J("tokens/00-foundation/motion-patterns.json")["patterns"]
ROLES = J("assets/asset-roles.json")["roles"]
COPY = J("extraction/source-copy-index.json")
IDENTITY = J("extraction/measured-values.json")["sourceIdentity"]["patterns"]

# Pinned in code (BASELINE R3/R8): editing a registry file alone cannot loosen these.
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
RUNTIME_AFTER_FOOTER = {"utility.page-transition", "utility.preloader"}
BODY_SECTIONS = {"content.media-text", "content.title-text", "content.text", "media.image", "media.video", "media.carousel", "layout.gray-band"}

RULE_SEVERITY = {
    # compatibility/graph.json rules
    "TEMPLATE_SEQUENCE": "error", "SHELL_HEADER_FIRST": "error", "SHELL_FOOTER_LAST_IN_FLOW": "error", "ONE_HERO": "error",
    "HERO_TEMPLATE_BINDING": "error", "GRAY_BAND_MAX_ONE": "error", "GRAY_BAND_NEEDS_FOLLOWER": "error", "PASSWORD_GATE_ACCESS": "error",
    "CASE_INDEX_NUMBERING": "error", "BODY_OPENS_WITH_MEDIA_TEXT": "warn", "PHYSICS_BUDGET": "warn", "THEME_TEMPLATE": "error",
}
GRAPH_RULE_IDS = set(RULE_SEVERITY)
LOCAL_RULES = {
    "UNKNOWN_SECTION", "ROUTE_TEMPLATE", "REFERENCE_ROUTE_UNKNOWN", "CONSTRAINT_ONE_PER_PAGE", "CONSTRAINT_MAX_PER_PAGE", "MAX_WORDS", "HIGHLIGHT_NOT_IN_TEXT",
    "MOTION_FALLBACK_MISMATCH", "RETRIEVAL_FLAG", "ASSET_ROLE_SECTION", "RAW_COLOR", "UNKNOWN_TOKEN", "TOKEN_SLOT_FAMILY", "THEME_TOKEN",
    "GENERATED_MODE_BRAND", "GENERATED_MODE_PERSON", "GENERATED_MODE_CTA", "GENERATED_MODE_RECOGNITION", "GENERATED_MODE_URL",
    "GENERATED_MODE_ASSET", "GENERATED_MODE_COPY", "GENERATED_MODE_ROUTE",
}

def strip(h): return re.sub(r"<[^>]+>", " ", h or "")
def wc(s): return len(strip(s).split())
def words(s): return re.findall(r"[a-z0-9]+", strip(s).lower().replace("’", "'"))
def h16(s): return hashlib.sha256(s.encode()).hexdigest()[:16]
SHINGLES, FULLS, K = set(COPY["shingles"]), set(COPY["fullStrings"]), COPY["shingleSize"]

STRUCTURAL_KEYS = {"section", "variant", "motion", "style", "role", "pageSpecVersion", "mode", "template", "theme", "access", "retrievalEligible"}
def copy_strings(o, path="$"):
    """Human-readable copy only (structural ids, asset roles/srcs and hrefs excluded)."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k not in STRUCTURAL_KEYS | {"src", "href", "route"}: yield from copy_strings(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from copy_strings(v, f"{path}[{i}]")
    elif isinstance(o, str): yield path, o

def strings_in(o, path="$"):
    if isinstance(o, dict):
        for k, v in o.items(): yield from strings_in(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from strings_in(v, f"{path}[{i}]")
    elif isinstance(o, str): yield path, o

def assets_in(o, path="$"):
    if isinstance(o, dict):
        if set(o) >= {"role", "src"}: yield path, o
        for k, v in o.items(): yield from assets_in(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from assets_in(v, f"{path}[{i}]")

def pat_re(p):
    e = re.escape(p.lower().replace("’", "'"))
    return re.compile(rf"(?<![a-z0-9]){e}(?![a-z0-9])" if re.match(r"^[\w ]+$", p) else e)
ID_RES = {k: [(p, pat_re(p)) for p in v] for k, v in IDENTITY.items()}

def match_template(nodes, tnodes):
    """Greedy sequence match of node section ids against a template node list."""
    i = 0
    for t in tnodes:
        ok = (lambda s: s in t["oneOf"]) if "oneOf" in t else (lambda s, x=t["section"]: s == x)
        n = 0
        while i < len(nodes) and ok(nodes[i]) and (t["repeatable"] or n == 0):
            i += 1; n += 1
        if t["required"] and n == 0:
            return f"required template node {t.get('section') or 'slot:' + t['slot']} missing at position {i}"
    if i != len(nodes):
        return f"node {i} ({nodes[i]}) does not fit the template sequence"
    return None

def validate(spec):
    out = []
    def err(rule, path, msg):
        sev = RULE_SEVERITY.get(rule, "error")
        out.append({"rule": rule, "severity": sev, "path": path, "message": msg})
    nodes = spec.get("nodes", []); secs = [n.get("section") for n in nodes]
    tpl = TEMPLATES.get(spec.get("template"))
    mode = spec.get("mode")

    for i, s in enumerate(secs):
        if s not in CONTRACTS: err("UNKNOWN_SECTION", f"$.nodes[{i}]", f"unknown section {s}")
    if not tpl: return out + [{"rule": "TEMPLATE_SEQUENCE", "severity": "error", "path": "$.template", "message": "unknown template"}]

    # --- template / graph structure
    m = match_template(secs, tpl["nodes"])
    if m: err("TEMPLATE_SEQUENCE", "$.nodes", m)
    if not secs or secs[0] != "shell.header": err("SHELL_HEADER_FIRST", "$.nodes[0]", "shell.header must be first")
    if "shell.footer" in secs:
        after = secs[secs.index("shell.footer") + 1:]
        if any(s not in RUNTIME_AFTER_FOOTER for s in after): err("SHELL_FOOTER_LAST_IN_FLOW", "$.nodes", f"only runtime utilities may follow the footer, found {after}")
    heroes = [s for s in secs if s and s.startswith("hero.")]
    if len(heroes) != 1: err("ONE_HERO", "$.nodes", f"expected exactly one hero, found {len(heroes)}")
    for h in heroes:
        if (h == "hero.home") != (spec["template"] == "template.home"): err("HERO_TEMPLATE_BINDING", "$.nodes", f"{h} not allowed on {spec['template']}")
    bands = [i for i, s in enumerate(secs) if s == "layout.gray-band"]
    if len(bands) > 1: err("GRAY_BAND_MAX_ONE", "$.nodes", f"{len(bands)} gray bands")
    for i in bands:
        if i + 1 >= len(secs) or secs[i + 1] not in BODY_SECTIONS - {"layout.gray-band"}: err("GRAY_BAND_NEEDS_FOLLOWER", f"$.nodes[{i}]", "gray band must be followed by a body block")
    gate = "utility.password-gate" in secs
    if gate != (spec.get("access") == "password-gated"): err("PASSWORD_GATE_ACCESS", "$.access", f"access={spec.get('access')} but gate present={gate}")
    idx = [n.get("content", {}).get("index") for n in nodes if n.get("section") == "content.case-index-item"]
    if idx and idx != [f"{k + 1:02d}" for k in range(len(idx))]: err("CASE_INDEX_NUMBERING", "$.nodes", f"index sequence {idx}")
    body = [s for s in secs if s in BODY_SECTIONS]
    if spec["template"] == "template.case-study" and body and body[0] != "content.media-text": err("BODY_OPENS_WITH_MEDIA_TEXT", "$.nodes", f"body opens with {body[0]}")
    phys = sum(1 for n in nodes if n.get("motion", {}).get("pattern") == "physics-drop")
    if phys > 2: err("PHYSICS_BUDGET", "$.nodes", f"{phys} physics-drop nodes")
    if POLICY["themeBinding"].get(spec["template"]) != spec.get("theme"): err("THEME_TEMPLATE", "$.theme", f"{spec['template']} requires theme {POLICY['themeBinding'].get(spec['template'])}")

    # --- route
    route = spec.get("route", "")
    if (route == "/") != (spec["template"] == "template.home"): err("ROUTE_TEMPLATE", "$.route", f"route {route} vs template {spec['template']}")
    if mode == "reference":
        r = ROUTES.get(route)
        if not r: err("REFERENCE_ROUTE_UNKNOWN", "$.route", f"{route} is not a route of the source")
        elif (r["template"], r["theme"], r["access"]) != (spec["template"], spec.get("theme"), spec.get("access")):
            err("REFERENCE_ROUTE_UNKNOWN", "$.route", f"route table says {r['template']}/{r['theme']}/{r['access']}")
    elif route in ROUTES and route != "/":
        err("GENERATED_MODE_ROUTE", "$.route", "generated page reuses a source case slug")

    # --- per-node contract checks
    counts = {}
    for i, n in enumerate(nodes):
        s = n.get("section"); c = CONTRACTS.get(s)
        if not c: continue
        p = f"$.nodes[{i}]"; counts[s] = counts.get(s, 0) + 1
        mw = c["content"]
        for k, f in mw.items():
            v = n.get("content", {}).get(k)
            if v is None: continue
            kind = f["kind"]
            if kind == "text" and wc(v) > f["maxWords"]: err("MAX_WORDS", f"{p}.content.{k}", f"{wc(v)} words > {f['maxWords']}")
            if kind == "rich":
                total = sum(wc(x.get("text", "")) for x in v)
                if total > f["maxWords"]: err("MAX_WORDS", f"{p}.content.{k}", f"{total} words > {f['maxWords']}")
                for j, para in enumerate(v):
                    for h in para.get("highlights", []) + para.get("strong", []):
                        if h not in para.get("text", ""): err("HIGHLIGHT_NOT_IN_TEXT", f"{p}.content.{k}[{j}]", f"'{h}' not in paragraph")
            if kind in ("link",) and wc(v.get("label", "")) > f["labelMaxWords"]: err("MAX_WORDS", f"{p}.content.{k}.label", "label too long")
            if kind == "links":
                for j, l in enumerate(v):
                    if wc(l.get("label", "")) > f["labelMaxWords"]: err("MAX_WORDS", f"{p}.content.{k}[{j}].label", "label too long")
        hl, ti = n.get("content", {}).get("highlight"), n.get("content", {}).get("title") or n.get("content", {}).get("statement")
        if hl and ti and hl not in ti: err("HIGHLIGHT_NOT_IN_TEXT", f"{p}.content.highlight", f"'{hl}' not in title")
        mo = n.get("motion", {})
        if mo.get("pattern") in PATTERNS and mo.get("reducedMotionFallback") != PATTERNS[mo["pattern"]]["fallback"]:
            err("MOTION_FALLBACK_MISMATCH", f"{p}.motion", f"{mo['pattern']} requires fallback {PATTERNS[mo['pattern']]['fallback']}")
        pinned_ok = s not in RETRIEVAL_INELIGIBLE
        if c.get("retrievalEligible") != pinned_ok: err("RETRIEVAL_FLAG", p, f"contract retrievalEligible={c.get('retrievalEligible')} contradicts pin {pinned_ok}")
        if "retrievalEligible" in n and n["retrievalEligible"] != pinned_ok: err("RETRIEVAL_FLAG", f"{p}.retrievalEligible", f"must be {pinned_ok}")
        allowed_ref = set(c["assetRoles"]); allowed_gen = set(c["generatedAssetRoles"])
        for ap, a in assets_in(n.get("content", {}), f"{p}.content"):
            role = a["role"]
            if role not in (allowed_ref | allowed_gen): err("ASSET_ROLE_SECTION", ap, f"role {role} not allowed in {s}")
            if mode == "generated":
                if PINNED_AVAILABILITY.get(role) != "generation-safe" or role not in allowed_gen: err("GENERATED_MODE_ASSET", ap, f"role {role} is not generation-safe here")
                if not re.match(r"^(placeholder|generated|user-supplied):", a["src"]): err("GENERATED_MODE_ASSET", f"{ap}.src", "generated pages may not point at source asset files")
            elif mode == "reference" and role in allowed_gen - allowed_ref:
                pass
        # tokens
        for slot, v in (n.get("style") or {}).items():
            if v not in CATALOG["color"]: err("UNKNOWN_TOKEN", f"{p}.style.{slot}", f"{v} is not in the token catalog")
            elif not v.startswith(c.get("styleSlots", {}).get(slot, {}).get("tokenFamily", "\0") + "."): err("TOKEN_SLOT_FAMILY", f"{p}.style.{slot}", f"{v} is not a {c['styleSlots'].get(slot, {}).get('tokenFamily')} token")
            for r in POLICY["themeTokenRules"]:
                if spec.get("theme") == r["theme"] and any(v.startswith(f + ".") for f in r["forbiddenFamilies"]): err("THEME_TOKEN", f"{p}.style.{slot}", f"{v} not allowed on {r['theme']} theme")
    for s, k in counts.items():
        con = CONTRACTS[s]["constraints"]
        if con.get("onePerPage") and k > 1: err("CONSTRAINT_ONE_PER_PAGE", "$.nodes", f"{s} x{k}")
        if con.get("maxPerPage") and k > con["maxPerPage"]: err("CONSTRAINT_MAX_PER_PAGE", "$.nodes", f"{s} x{k}")

    # --- raw values anywhere
    for path, s in strings_in(spec):
        if re.search(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(", s) and not path.endswith(".href"):
            err("RAW_COLOR", path, f"raw colour literal in '{s[:40]}'")

    # --- generated mode: no source identity, copy, URLs or assets (BASELINE R2)
    if mode == "generated":
        for path, s in strings_in(spec):
            low = s.lower().replace("’", "'")
            for cat, rule in (("brand", "GENERATED_MODE_BRAND"), ("person", "GENERATED_MODE_PERSON"), ("cta", "GENERATED_MODE_CTA"), ("recognition", "GENERATED_MODE_RECOGNITION"), ("domains", "GENERATED_MODE_URL")):
                for pat, rx in ID_RES[cat]:
                    if rx.search(low): err(rule, path, f"source {cat} pattern '{pat}'")
            for u in re.findall(r"(?:https?://|www\.)([^/\s?#]+)|mailto:[^@\s]+@([^\s?]+)", s):
                host = (u[0] or u[1]).lower()
                if not re.search(r"\.(example|invalid)$", host): err("GENERATED_MODE_URL", path, f"host {host} is not a reserved .example/.invalid domain")
        for path, s in copy_strings(spec):
            w = words(s)
            if len(w) >= 4 and h16(" ".join(w)) in FULLS: err("GENERATED_MODE_COPY", path, "string reproduces source copy")
            elif any(h16(" ".join(w[i:i + K])) in SHINGLES for i in range(len(w) - K + 1)): err("GENERATED_MODE_COPY", path, f"contains a {K}-word run of source copy")
    return out

def errors(spec): return [e for e in validate(spec) if e["severity"] == "error"]

if __name__ == "__main__":
    bad = 0
    for f in sys.argv[1:]:
        res = validate(json.loads(Path(f).read_text()))
        e = [r for r in res if r["severity"] == "error"]; w = [r for r in res if r["severity"] == "warn"]
        print(f"{'FAIL' if e else 'ok  '} {f}: {len(e)} error(s), {len(w)} warning(s)")
        for r in res: print(f"     {r['severity']:5} {r['rule']}: {r['path']} {r['message']}")
        bad += bool(e)
    sys.exit(1 if bad else 0)
