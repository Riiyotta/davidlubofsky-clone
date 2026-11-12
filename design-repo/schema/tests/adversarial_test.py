#!/usr/bin/env python3
"""Adversarial suite: every mutation must be rejected with the named rule; every control must pass.

    python3 schema/tests/adversarial_test.py      # exit 1 if any mutation slips through or a control fails
"""
import copy, importlib.util, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec_ = importlib.util.spec_from_file_location("semantic_validate", ROOT / "schema/semantic_validate.py")
sem = importlib.util.module_from_spec(spec_); spec_.loader.exec_module(sem)
from jsonschema import Draft7Validator
V = Draft7Validator(json.loads((ROOT / "schema/pagespec.schema.json").read_text()))
EX = ROOT / "schema/examples"
def load(n): return json.loads((EX / n).read_text())
REF_HOME, REF_CASE, REF_GATED = load("reference.home.pagespec.json"), load("reference.case-study.pagespec.json"), load("reference.case-study-gated.pagespec.json")
GEN_HOME, GEN_CASE = load("generated.home.pagespec.json"), load("generated.case-study.pagespec.json")

def check(spec):
    """Return set of rule ids (semantic errors) plus 'SCHEMA' if Draft-07 fails."""
    rules = {e["rule"] for e in sem.errors(spec)}
    if list(V.iter_errors(spec)): rules.add("SCHEMA")
    return rules

def idx(spec, section, n=0): return [i for i, x in enumerate(spec["nodes"]) if x["section"] == section][n]
def mut(base, fn):
    s = copy.deepcopy(base); fn(s); return s
def node(s, section, n=0): return s["nodes"][idx(s, section, n)]

CASES = []
def case(name, base, fn, expect): CASES.append((name, base, fn, expect))

# ---------------- schema layer
case("unknown template", REF_CASE, lambda s: s.update(template="template.landing"), "SCHEMA")
case("missing mode", REF_CASE, lambda s: s.pop("mode"), "SCHEMA")
case("invalid mode value", REF_CASE, lambda s: s.update(mode="draft"), "SCHEMA")
case("invented section type", REF_CASE, lambda s: s["nodes"].insert(2, {"section": "content.testimonials", "content": {}, "motion": {"pattern": "none", "reducedMotionFallback": "none"}}), "SCHEMA")
case("missing reducedMotionFallback", REF_CASE, lambda s: node(s, "hero.case")["motion"].pop("reducedMotionFallback"), "SCHEMA")
case("invented motion field", REF_CASE, lambda s: node(s, "hero.case")["motion"].update(inventedAnimation="spin"), "SCHEMA")
case("motion pattern not allowed for section", REF_CASE, lambda s: node(s, "media.image")["motion"].update(pattern="physics-drop", reducedMotionFallback="static-composition"), "SCHEMA")
case("invented content field", REF_CASE, lambda s: node(s, "content.media-text")["content"].update(subtitle="x"), "SCHEMA")
case("invented asset role", REF_CASE, lambda s: node(s, "media.image")["content"]["image"].update(role="hero.photo"), "SCHEMA")
case("missing variant", REF_CASE, lambda s: node(s, "media.image").pop("variant"), "SCHEMA")
case("font override field", REF_CASE, lambda s: node(s, "hero.case")["style"].update(fontFamily="Inter"), "SCHEMA")
case("spacing override field", REF_CASE, lambda s: node(s, "content.text").update(spacing={"top": "13px"}), "SCHEMA")
case("carousel below observed minimum", REF_CASE, lambda s: node(s, "media.carousel")["content"].update(images=node(s, "media.carousel")["content"]["images"][:2]), "SCHEMA")

# ---------------- structure / graph
case("template node sequence mismatch (hero after body)", REF_CASE, lambda s: s["nodes"].insert(idx(s, "navigation.next-case"), s["nodes"].pop(idx(s, "hero.case"))), "TEMPLATE_SEQUENCE")
case("required node removed (next-case)", REF_CASE, lambda s: s["nodes"].pop(idx(s, "navigation.next-case")), "TEMPLATE_SEQUENCE")
case("home section on case template", REF_CASE, lambda s: s["nodes"].insert(3, copy.deepcopy(node(REF_HOME, "conversion.connect"))), "TEMPLATE_SEQUENCE")
case("header not first", REF_CASE, lambda s: s["nodes"].insert(1, s["nodes"].pop(0)), "SHELL_HEADER_FIRST")
case("content after footer", REF_CASE, lambda s: s["nodes"].append(copy.deepcopy(node(s, "media.image"))), "SHELL_FOOTER_LAST_IN_FLOW")
case("two heroes", REF_CASE, lambda s: s["nodes"].insert(3, copy.deepcopy(node(s, "hero.case"))), "ONE_HERO")
case("home hero on case page", REF_CASE, lambda s: s["nodes"].__setitem__(idx(s, "hero.case"), copy.deepcopy(node(REF_HOME, "hero.home"))), "HERO_TEMPLATE_BINDING")
case("two gray bands", REF_CASE, lambda s: s["nodes"].insert(idx(s, "layout.gray-band"), copy.deepcopy(node(s, "layout.gray-band"))), "GRAY_BAND_MAX_ONE")
case("gray band without follower", REF_CASE, lambda s: s["nodes"].insert(idx(s, "navigation.next-case"), s["nodes"].pop(idx(s, "layout.gray-band"))), "GRAY_BAND_NEEDS_FOLLOWER")
case("gate without gated access", REF_GATED, lambda s: s.update(access="public"), "PASSWORD_GATE_ACCESS")
case("gated access without gate", REF_GATED, lambda s: s["nodes"].pop(idx(s, "utility.password-gate")), "PASSWORD_GATE_ACCESS")
case("index numbering out of order", REF_HOME, lambda s: node(s, "content.case-index-item", 1)["content"].update(index="05"), "CASE_INDEX_NUMBERING")
case("dark theme on case page", REF_CASE, lambda s: s.update(theme="dark"), "THEME_TEMPLATE")
case("home template on case route", REF_HOME, lambda s: s.update(route="/case/new-thing/"), "ROUTE_TEMPLATE")
case("reference route not in source", REF_CASE, lambda s: s.update(route="/case/not-a-real-case/"), "REFERENCE_ROUTE_UNKNOWN")
case("onePerPage footer twice", REF_CASE, lambda s: s["nodes"].insert(idx(s, "shell.footer"), copy.deepcopy(node(s, "shell.footer"))), "CONSTRAINT_ONE_PER_PAGE")

# ---------------- content budgets / consistency
case("maxWords overflow (hero title)", REF_CASE, lambda s: node(s, "hero.case")["content"].update(title=node(s, "hero.case")["content"]["title"] + " and then some more words here"), "MAX_WORDS")
case("maxWords overflow (rich body)", REF_CASE, lambda s: node(s, "content.title-text")["content"]["body"][0].update(text=" ".join(["word"] * 200)), "MAX_WORDS")
case("highlight not in title", REF_CASE, lambda s: node(s, "hero.case")["content"].update(highlight="zebra"), "HIGHLIGHT_NOT_IN_TEXT")
case("wrong reduced-motion fallback", REF_CASE, lambda s: node(s, "hero.case")["motion"].update(reducedMotionFallback="static-composition"), "MOTION_FALLBACK_MISMATCH")
case("asset role from another section", REF_CASE, lambda s: node(s, "media.image")["content"]["image"].update(role="client.logo"), "ASSET_ROLE_SECTION")

# ---------------- retrieval eligibility (R8)
case("runtime node flipped eligible", REF_CASE, lambda s: node(s, "utility.back-button").update(retrievalEligible=True), "RETRIEVAL_FLAG")
case("content node marked ineligible", REF_CASE, lambda s: node(s, "content.media-text").update(retrievalEligible=False), "RETRIEVAL_FLAG")
case("modal flipped eligible", REF_HOME, lambda s: node(s, "utility.video-modal").update(retrievalEligible=True), "RETRIEVAL_FLAG")

# ---------------- tokens (R10)
case("raw hex accent", REF_CASE, lambda s: node(s, "hero.case")["style"].update(accent="#FF0000"), "SCHEMA")
case("raw rgb in copy", REF_CASE, lambda s: node(s, "hero.case")["content"].update(roles="rgb(255, 0, 0)"), "RAW_COLOR")
case("raw hex in copy", GEN_CASE, lambda s: node(s, "hero.case")["content"].update(roles="Colour #00AFBC"), "RAW_COLOR")
case("unknown token", REF_CASE, lambda s: node(s, "hero.case")["style"].update(accent="color.accent.neon"), "UNKNOWN_TOKEN")
case("token from wrong family", REF_CASE, lambda s: node(s, "hero.case")["style"].update(accent="color.neutral.900"), "TOKEN_SLOT_FAMILY")

# ---------------- generated-mode leakage (R2/R5) — all start from the passing generated controls
case("brand leakage (owner name)", GEN_HOME, lambda s: node(s, "shell.header")["content"].update(ownerName="David Lubofsky"), "GENERATED_MODE_BRAND")
case("brand leakage (client)", GEN_CASE, lambda s: node(s, "hero.case")["content"].update(roles="ESPN interaction"), "GENERATED_MODE_BRAND")
case("person identity leakage", GEN_CASE, lambda s: node(s, "content.text")["content"]["text"][0].update(text="Inspired by Calvin Johnson and his hands."), "GENERATED_MODE_PERSON")
case("source CTA leakage", GEN_HOME, lambda s: node(s, "shell.header")["content"]["cta"].update(label="Let’s work together"), "GENERATED_MODE_CTA")
case("recognition / press leakage", GEN_CASE, lambda s: node(s, "content.media-text")["content"]["body"][0].update(text="Featured on Awwwards as site of the day."), "GENERATED_MODE_RECOGNITION")
case("store / marketplace link leakage", GEN_CASE, lambda s: node(s, "content.media-text")["content"].update(cta={"label": "Buy the book", "href": "https://www.amazon.com/dp/B0BTRW3DD8"}), "GENERATED_MODE_URL")
case("source URL leakage", GEN_HOME, lambda s: node(s, "shell.footer")["content"]["links"][1].update(href="https://findworkhappiness.com"), "GENERATED_MODE_URL")
case("non-reserved domain", GEN_HOME, lambda s: node(s, "shell.footer")["content"]["links"][1].update(href="https://my-real-studio.com"), "GENERATED_MODE_URL")
case("source email", GEN_HOME, lambda s: node(s, "conversion.connect")["content"]["cta"].update(href="mailto:me@davidlubofsky.com"), "GENERATED_MODE_URL")
case("source copy leakage (paragraph)", GEN_CASE, lambda s: node(s, "content.title-text")["content"]["body"][0].update(text=node(REF_CASE, "content.title-text")["content"]["body"][1]["text"]), "GENERATED_MODE_COPY")
case("source copy leakage (6-word run)", GEN_CASE, lambda s: node(s, "content.media-text")["content"]["body"][0].update(text="Our users loved it: the league has evolved to become pass-happy, they said."), "GENERATED_MODE_COPY")
case("source headline reuse", GEN_HOME, lambda s: node(s, "hero.home")["content"].update(headline="UX, Strategy, Design, and Development"), "GENERATED_MODE_COPY")
case("proprietary media reuse (screenshot)", GEN_CASE, lambda s: node(s, "media.image")["content"].update(image={"role": "case.screenshot", "src": "/images/1694791377-screen.jpg"}), "GENERATED_MODE_ASSET")
case("proprietary media via safe role", GEN_CASE, lambda s: node(s, "media.image")["content"].update(image={"role": "generated.product-visual", "src": "/images/1694791377-screen.jpg"}), "GENERATED_MODE_ASSET")
case("real logo in generated page", GEN_HOME, lambda s: node(s, "content.case-index-item")["content"].update(clientLogo={"role": "client.logo", "src": "placeholder:espn"}), "GENERATED_MODE_ASSET")
case("owner likeness in generated page", GEN_HOME, lambda s: node(s, "hero.home")["content"].update(video={"role": "person.intro-video", "src": "/intro-short.mp4"}), "GENERATED_MODE_ASSET")
case("3D mascot reuse", GEN_HOME, lambda s: node(s, "shell.footer")["content"].update(mascot={"role": "decor.mascot-3d", "src": "/lama.glb"}), "GENERATED_MODE_ASSET")
case("source case slug reused", GEN_CASE, lambda s: s.update(route="/case/dl-brand/"), "GENERATED_MODE_ROUTE")
case("brand in meta title", GEN_HOME, lambda s: s["meta"].update(title="DL | The portfolio of someone"), "GENERATED_MODE_BRAND")

failed = 0
for name, base, fn, expect in CASES:
    got = check(mut(base, fn))
    ok = expect in got
    failed += not ok
    print(f"{'ok  ' if ok else 'MISS'} reject  {name:44s} expect {expect:28s} got {sorted(got)[:4]}")

# ---------------- controls: real examples + every real route + one synthesized minimal spec per template
controls = [(f.relative_to(EX), json.loads(f.read_text())) for f in sorted(EX.rglob("*.json"))]
CONTR = {p.stem: json.loads(p.read_text()) for p in (ROOT / "sections").glob("*.json")}
TPL = json.loads((ROOT / "templates/templates.json").read_text())["templates"]
def minimal(tname):
    """Synthesize a minimal valid generated spec from the template's own node list (auto-covers new templates)."""
    base = GEN_HOME if tname == "template.home" else GEN_CASE
    keep = []
    for nd in TPL[tname]["nodes"]:
        if not nd["required"]: continue
        sid = nd.get("section") or "content.media-text"
        keep.append(copy.deepcopy(node(base, sid)))
    s = copy.deepcopy(base); s["nodes"] = keep; return s
for t in TPL: controls.append((f"synthesized-minimal:{t}", minimal(t)))
for name, sp in controls:
    got = check(sp)
    failed += bool(got)
    print(f"{'ok  ' if not got else 'FAIL'} control {str(name):44s} {sorted(got) if got else 'passes'}")
print(f"\nadversarial: {len(CASES)} mutations, {len(controls)} controls, {failed} failure(s)")
sys.exit(1 if failed else 0)
