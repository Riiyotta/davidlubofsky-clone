#!/usr/bin/env python3
"""Build-time generator for this design-repo.

Regenerates every derived JSON file from the real clone source (the sibling project:
src/, src/styles/original.css, src/data/site.json) plus the measured geometry in
extraction/measured-values.json (sectionHeights / histograms, captured by
measure_sections.mjs). Citations are resolved by *needle* (a literal string that must
appear in the cited file), so re-running this after the source moves re-points every
citation (BASELINE R16). Requires the sibling source tree; verify_all.py does not.

    python3 extraction/build_repo.py [--measure path/to/measure.json]
"""
import argparse, hashlib, json, re, sys
from pathlib import Path

DR = Path(__file__).resolve().parent.parent          # design-repo/
PROJ = DR.parent                                       # cloned project root
REPO_VERSION = "1.0.0"
PAGESPEC_VERSION = "1.0.0"
ALLOWLIST_VERSION = "1.0.0"

ap = argparse.ArgumentParser()
ap.add_argument("--measure", help="raw output of measure_sections.mjs to fold into measured-values.json")
args = ap.parse_args()

if not (PROJ / "src").is_dir():
    sys.exit("build_repo.py needs the sibling clone source (../src). verify_all.py does not.")

def rd(rel): return (PROJ / rel).read_text()
def lines(rel): return rd(rel).splitlines()
def dump(rel, obj):
    p = DR / rel; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")

def cite(rel, needle, span=1, nth=1):
    """Return 'rel:L1-L2' where L1 is the nth line containing needle."""
    ls = lines(rel); hits = [i for i, l in enumerate(ls, 1) if needle in l]
    if len(hits) < nth: sys.exit(f"needle not found: {rel} :: {needle!r}")
    a = hits[nth - 1]; b = min(len(ls), a + span - 1)
    return f"{rel}:{a}-{b}" if b > a else f"{rel}:{a}"

def css(needle, span=8, nth=1): return {"cite": cite("src/styles/original.css", needle, span, nth), "tag": needle}
def src(rel, needle, span=1, nth=1): return {"cite": cite(rel, needle, span, nth), "tag": needle}

site = json.loads(rd("src/data/site.json"))
CASES = site["cases"]; HOME = site["home"]

# ---------------------------------------------------------------- foundation tokens
CSSF = "src/styles/original.css"
color = {
    "color.neutral.900": {"value": "#161617", "evidence": ["computed:color rgb(22,22,23) x512", css(".bg-black {", 4)]},
    "color.neutral.0": {"value": "#FFFFFF", "evidence": ["computed:color rgb(255,255,255) x65", css(".bg-white {", 4)]},
    "color.neutral.700": {"value": "#303133", "evidence": ["source:home hero physics fill (canvas, not in DOM histogram)", src("src/components/home/ShapesHeroHome.jsx", "const theme = ['#303133', '#161617'];")]},
    "color.neutral.600": {"value": "#5A5B5E", "evidence": [css(".bg-gray-modal {", 4)]},
    "color.neutral.400": {"value": "#BBBBBB", "evidence": ["computed:fill #BBBBBB x22", src("src/components/Header.jsx", 'fill="#BBBBBB"')]},
    "color.neutral.200": {"value": "#DDDCDB", "evidence": ["computed:backgroundColor rgb(221,220,219) x14", css(".bg-gray-fill {", 4)]},
    "color.neutral.150": {"value": "#D9D9D9", "alpha": 0.2, "evidence": ["computed:backgroundColor rgba(217,217,217,0.2) x6", css(".bg-gray-case", 3)]},
    "color.neutral.100": {"value": "#F1F1F1", "evidence": ["computed:backgroundColor rgb(241,241,241) x1", css(".bg-gray-light {", 4)]},
    "color.brand.yellow": {"value": "#FFD600", "evidence": ["computed:backgroundColor rgb(255,214,0) x33; fill #FFD600 x97", css(".bg-yellow {", 4)]},
    "color.brand.yellow-stroke": {"value": "#FFDA18", "evidence": ["computed:stroke #FFDA18 x45", src("src/data/case.js", "stroke=\"#FFDA18\"")]},
    "color.brand.yellow-light": {"value": "#FFE146", "evidence": [css(".foot {", 4)]},
}
ACCENTS = {"#F9CCA2": "peach", "#95CEA5": "mint", "#F0ACAD": "rose", "#B0D7E6": "sky", "#7AB0CE": "steel", "#00AFBC": "teal", "#FFDA18": "sun", "#438CC3": "azure"}
acc_seen = sorted({c["color"]["hex"] for c in CASES.values()})
assert set(acc_seen) == set(ACCENTS), acc_seen
for hx, name in ACCENTS.items():
    users = sorted(s for s, c in CASES.items() if c["color"]["hex"] == hx)
    color[f"color.accent.{name}"] = {"value": hx, "evidence": [f"data:site.json cases[*].color.hex used by {len(users)} case(s)", src("src/components/CaseHero.jsx", "color={info.color?.hex}")]}

TYPE_SCALE = {
    "type.display-xl": {"fontSize": {"base": "48px", "s": "102px"}, "fontWeight": 544, "lineHeight": 1.01, "letterSpacing": "-0.04em", "trap": 90, "evidence": [css(".case-hero__title {", 7), css(".ls-2 {", 3)]},
    "type.display-l": {"fontSize": {"base": "48px", "s": "90px"}, "fontWeight": 544, "lineHeight": 1.08, "letterSpacing": "-0.04em", "trap": 90, "evidence": [css(".home-hero__title {", 7)]},
    "type.display-m": {"fontSize": {"base": "38px", "s": "73px"}, "fontWeight": 509, "lineHeight": 1.03, "letterSpacing": "-0.04em", "trap": 90, "evidence": [css(".title-2 {", 8)]},
    "type.display-m-index": {"fontSize": {"base": "38px", "s": "73px"}, "fontWeight": 509, "lineHeight": 1.04, "letterSpacing": "-0.04em", "trap": 90, "evidence": [css(".home-item__title {", 6)]},
    "type.display-m-footer": {"fontSize": {"base": "35px", "s": "73px"}, "fontWeight": 509, "lineHeight": {"base": 1.05, "s": 0.97}, "letterSpacing": "-0.04em", "trap": 90, "evidence": [css(".foot__title {", 6)]},
    "type.lettering-xxl": {"fontSize": {"base": "161px"}, "fontWeight": 526, "letterSpacing": "-0.053em", "trap": 100, "evidence": [css(".connect-text {", 6)], "note": "rendered as SVG lettering in the source; size kept for reference"},
    "type.body-l": {"fontSize": {"base": "18px", "s": "23px"}, "fontWeight": 491, "lineHeight": 1.4, "letterSpacing": "-0.01em", "evidence": [css(".media-text__text * {", 6)]},
    "type.body-l-trap": {"fontSize": {"base": "20px", "s": "23px"}, "fontWeight": 491, "lineHeight": 1.4, "letterSpacing": "-0.01em", "trap": 23, "evidence": [css(".title-text__text {", 7)]},
    "type.body": {"fontSize": {"base": "16px", "s": "18px"}, "fontWeight": 476, "lineHeight": {"base": 1.5, "s": 1.65}, "letterSpacing": "-0.01em", "evidence": [css(".content__text * {", 6)]},
    "type.lede": {"fontSize": {"base": "16px", "s": "23px"}, "fontWeight": 500, "lineHeight": 1.4, "letterSpacing": "-0.01em", "trap": 23, "evidence": [css(".case-hero__desc {", 6)]},
    "type.ui": {"fontSize": {"base": "16px", "s": "18px"}, "fontWeight": 500, "letterSpacing": "-0.035em", "evidence": ["computed:fontWeight 500 x230", css(".ls-1 {", 3)]},
    "type.button": {"fontSize": {"base": "16px", "s": "18px"}, "fontWeight": 550, "letterSpacing": "-0.035em", "evidence": [css(".btn {", 8)]},
    "type.nav": {"fontSize": {"base": "14px", "s": "18px"}, "fontWeight": 500, "lineHeight": 1.1, "letterSpacing": "-0.035em", "evidence": [css(".site-head__links,", 8)]},
    "type.subhead": {"fontSize": {"base": "24px"}, "fontWeight": 500, "lineHeight": 1.4, "letterSpacing": "-0.01em", "evidence": [css(".next__title {", 6)]},
    "type.annotation": {"fontSize": {"base": "28px"}, "fontWeight": 528, "lineHeight": 1.2, "trap": 55, "evidence": [css(".home-items__title {", 7)]},
    "type.callout": {"fontSize": {"base": "28px"}, "fontWeight": 526, "lineHeight": 1.2, "letterSpacing": "-0.04em", "trap": 55, "evidence": [css(".media-cta__text {", 6)]},
    "type.label": {"fontSize": {"base": "12px"}, "fontWeight": 626, "lineHeight": 1.9, "letterSpacing": "-0.02em", "textTransform": "uppercase", "evidence": [css(".case-hero__label {", 6)]},
    "type.small": {"fontSize": {"base": "14px"}, "fontWeight": 500, "evidence": [css(".text-14 {", 3)]},
    "type.meta": {"fontSize": {"base": "12px"}, "fontWeight": 500, "letterSpacing": "-0.03em", "evidence": [css(".timeline__time {", 5)]},
}
FONT = {"font.family.primary": {"value": "pleasure", "kind": "variable", "weightRange": [300, 900], "axes": {"TRAP": "custom axis, observed values 23/50/55/80/90/100"}, "file": "/fonts/pleasure-variable-latin-v1.woff2", "evidence": [css("@font-face {", 6), "computed:fontFamily pleasure x577 (only family observed)"]}}
WEIGHTS = sorted({476, 491, 500, 509, 526, 528, 544, 550, 600, 626, 650, 680})
LETTER = {"tracking.ui": "-0.035em", "tracking.display": "-0.04em", "tracking.label": "-0.02em", "tracking.body": "-0.01em", "tracking.lettering": "-0.053em"}

# Spacing: every numeric spacing utility used by the clone's markup, resolved via CSS.
markup = "\n".join(p.read_text() for p in (PROJ / "src").rglob("*.jsx"))
used = set(re.findall(r"(?<![\w-])(?:[a-z]+:)?-?(?:p|px|py|pt|pb|pl|pr|m|mx|my|mt|mb|ml|mr)-(\d+)(?![\w\[])", markup))
cssall = rd(CSSF)
spacing = {}
for n in sorted(used, key=int):
    if re.search(rf"\.(?:[a-z]+\\:)?-?(?:p|px|py|pt|pb|pl|pr|m|mx|my|mt|mb|ml|mr)-{n}\s*\{{", cssall):
        spacing[f"space.{n}"] = {"value": f"{int(n) / 10:g}rem", "pxAt1440": int(n), "evidence": f"utility *-{n} used in markup and defined in {CSSF}"}
RADIUS = {
    "radius.pill": {"value": "2.75rem", "computed": "27.5px", "evidence": [css(".btn {", 8), "computed:borderRadius 27.5px x21"]},
    "radius.full": {"value": "9999px", "evidence": ["computed:borderRadius 9999px x15", css(".rounded-full {", 3)]},
    "radius.card-l": {"value": "3rem", "computed": "30px", "evidence": ["computed:borderRadius 30px x2", src("src/components/home/ShapesConnect.jsx", "rounded-[3rem]")]},
    "radius.card-m": {"value": "2.3rem", "computed": "23px", "evidence": ["computed:borderRadius 23px x1", src("src/components/home/ShapesHeroHome.jsx", "rounded-[2.3rem]")]},
}
BREAK = {
    "bp.s": {"minWidth": "650px", "evidence": css("@media (min-width: 650px)", 2)},
    "bp.m": {"minWidth": "769px", "evidence": css("@media (min-width: 769px)", 2)},
    "bp.l": {"minWidth": "1024px", "evidence": css("@media (min-width: 1024px)", 2)},
    "bp.xl": {"minWidth": "1280px", "evidence": css("@media (min-width: 1280px)", 2)},
    "bp.hover": {"query": "(hover: hover) and (pointer: fine)", "evidence": css("@media (hover: hover) and (pointer: fine)", 2)},
}
EASE = {
    "ease.snappy": {"type": "custom-path", "value": "M0,0 C0.094,0.026 0.124,0.127 0.157,0.29 0.197,0.486 0.254,0.8 0.348,0.884 0.42,0.949 0.374,1 1,1", "evidence": src("src/lib/gsap.js", "'snappy',")},
    "ease.expo-in-out": {"type": "named", "value": "expo.inOut", "evidence": src("src/components/Loader.jsx", "ease: 'expo.inOut'")},
    "ease.expo-out": {"type": "named", "value": "expo.out", "evidence": src("src/components/ButtonBack.jsx", "ease: 'expo'")},
    "ease.power1-out": {"type": "named", "value": "power1.out", "evidence": src("src/components/Footer.jsx", "ease: 'power1'")},
    "ease.power3-in-out": {"type": "named", "value": "power3.inOut", "evidence": src("src/components/Loader.jsx", "ease: 'power3.inOut'")},
    "ease.power3-in": {"type": "named", "value": "power3.in", "evidence": src("src/lib/router.js", "ease: 'power3.in'")},
    "ease.css-quart": {"type": "cubic-bezier", "value": "cubic-bezier(.77,0,.175,1)", "evidence": css(".btn-mask {", 8, nth=2)},
    "ease.css-uline": {"type": "cubic-bezier", "value": "cubic-bezier(.785,.135,.15,.86)", "evidence": css(".uline:before {", 6)},
    "ease.css-fade": {"type": "cubic-bezier", "value": "cubic-bezier(.25,.46,.45,.94)", "evidence": css(".lazy img.is-loaded", 4)},
}
DUR = {"duration.instant": "0.22s", "duration.fast": "0.35s", "duration.base": "0.5s", "duration.button": "0.55s", "duration.fall": "0.7s", "duration.slow": "1s", "duration.underline": "1.25s", "duration.reveal": "1.5s"}

motion_patterns = {
    "physics-drop": {"desc": "Matter.js rigid bodies (SVG paths) drop under gravity into the section and settle; DOM proxies follow body transforms.", "fallback": "static-composition", "evidence": [src("src/lib/physics.js", "export class PhysicsLoop"), src("src/components/ShapesHeroCase.jsx", "Bodies.fromVertices(")]},
    "line-reveal": {"desc": "Text split into lines (double split, overflow hidden); lines translate from yPercent 100 with 0.15s stagger, 1.5s snappy ease.", "fallback": "instant-visible", "evidence": [src("src/components/CaseHero.jsx", "tl.from(lines, { yPercent: 100, stagger: 0.15 }, 0)")]},
    "underline-draw": {"desc": "Yellow underline under <em> scales X 0->1 over 1.25s cubic-bezier(.77,0,.175,1), tilted +/-3.3deg at random, triggered 25% into viewport.", "fallback": "static-underline", "evidence": [css("em:after {", 9), src("src/lib/usePageUnderlines.js", "start: 'top bottom-=25%'")]},
    "image-fade-in": {"desc": "Lazy image fades opacity 0->1 over 0.5s once loaded.", "fallback": "instant-visible", "evidence": [css(".lazy img.is-loaded", 4)]},
    "drag-carousel": {"desc": "Horizontal drag (2.5x speed) with lerp 0.1 per tick; touch devices use native scroll-snap.", "fallback": "native-scroll", "evidence": [src("src/components/blocks/Blocks.jsx", "speed: 2.5")]},
    "mask-reveal-follow": {"desc": "Featured image revealed through an elliptical clip-path on hover; clip follows the cursor via quickTo (1s expo).", "fallback": "hidden-until-focus", "evidence": [src("src/components/home/HomeItems.jsx", "clipPath: 'ellipse(50% 50% at 50% 100%)'")]},
    "scroll-scrub-clip": {"desc": "Touch devices: item image scales 0.5->1 and drifts yPercent 12.5->-12.5 scrubbed to scroll.", "fallback": "static-image", "evidence": [src("src/components/home/HomeItems.jsx", "scrollTrigger: { trigger: el.current, scrub: 0.1 }")]},
    "parallax-up": {"desc": "Footer content translates yPercent -35->0 scrubbed while the footer scrolls in (hover devices).", "fallback": "static", "evidence": [src("src/components/Footer.jsx", "{ yPercent: -35 }")]},
    "video-in-view": {"desc": "Muted looping video plays while its section is in view, resets when it leaves.", "fallback": "poster-frame", "evidence": [src("src/components/blocks/Blocks.jsx", "v.currentTime = 0;")]},
    "draw-annotation": {"desc": "Hand-drawn SVG annotation strokes draw on (DrawSVG 1.5s power3.inOut) with arrowhead pop and rotated line reveal.", "fallback": "static-annotation", "evidence": [src("src/components/home/HomeItems.jsx", "drawSVG: gsap.utils.wrap(['100% 100%', 0]),")]},
    "pop-in-label-slide": {"desc": "Circle button scales in (1.25s expo) and its label slides up; label hides after first scroll, circle scales out near the footer.", "fallback": "static-visible", "evidence": [src("src/components/ButtonBack.jsx", ".from(canvas.current, { scale: 0, duration: 1.25 }, 0.8)")]},
    "preloader-sequence": {"desc": "Ring draws, logo parts pop in then fall away; emits start of hero physics.", "fallback": "skip", "evidence": [src("src/components/Loader.jsx", ".from(circle1.current, { drawSVG: 0, ease: 'power3.inOut' })")]},
    "mask-wipe-transition": {"desc": "Route change: black mask wipes up (1s snappy), or clicked image falls (0.7s power3.in) while a white mask wipes down.", "fallback": "instant-swap", "evidence": [src("src/lib/router.js", "fromTo(a, { yPercent: 100 }, { yPercent: 0, duration: 1, ease: 'snappy' })")]},
    "flip-modal": {"desc": "Video card Flip-animates into a centred modal (1s snappy); scrubber scales in; cursor-following play/pause.", "fallback": "instant-open", "evidence": [src("src/components/home/IntroModal.jsx", "Flip.from(state, { duration: 1, ease: 'snappy', scale: true })")]},
    "gate-reveal": {"desc": "Password field and submit circle reveal via clip-path inset/circle (1.5s expo.inOut).", "fallback": "instant-visible", "evidence": [src("src/components/KnockKnock.jsx", "{ clipPath: 'inset(0 0 0 100% round 5.5rem)' },")]},
    "tilt-3d": {"desc": "3D mascot tilts toward the cursor (lerp 0.075) and advances a position/rotation timeline with downward scroll.", "fallback": "static-render", "evidence": [src("src/components/TheLama.jsx", "ease: 0.075")]},
    "none": {"desc": "No motion.", "fallback": "none", "evidence": ["no animation code bound to this section in the source"]},
}

# ---------------------------------------------------------------- word budgets (observed maxima)
def strip(h): return re.sub(r"<[^>]+>", " ", h or "")
def wc(h): return len(strip(h).split())
def obs(key, vals): return {"maxWords": max(vals), "observedMax": max(vals), "evidence": f"data:src/data/site.json {key} (max over {len(vals)} values)"}
blocks = [(s, b) for s, c in CASES.items() for b in c["blocks"]]
B = lambda t, f: [wc(b.get(f)) for _, b in blocks if b["type"] == t and b.get(f)]
BUDGET = {
    "case.title": obs("cases[*].titleFormated", [wc(c["titleFormated"]) for c in CASES.values()]),
    "case.shortDesc": obs("cases[*].shortDesc", [wc(c["shortDesc"]) for c in CASES.values()]),
    "case.roles": obs("cases[*].roles", [wc(c["roles"]) for c in CASES.values()]),
    "media_text.title": obs("case_media_text.title", B("case_media_text", "title")),
    "media_text.text": obs("case_media_text.text", B("case_media_text", "text")),
    "media_text.cta": obs("case_media_text.ctaLabel", B("case_media_text", "ctaLabel")),
    "title_text.title": obs("case_title_text.title", B("case_title_text", "title")),
    "title_text.text": obs("case_title_text.text", B("case_title_text", "text")),
    "text.text": obs("case_text.text", B("case_text", "text")),
    "home.title": obs("home.featuredCases[*].titleFormated", [wc(c["titleFormated"]) for c in HOME["featuredCases"]]),
    "home.desc": obs("home.featuredCases[*].shortDesc", [wc(c["shortDesc"]) for c in HOME["featuredCases"]]),
}
PARAS = {t: max(b[f].count("<p") for _, b in blocks if b["type"] == t and b.get(f)) for t, f in (("case_media_text", "text"), ("case_title_text", "text"), ("case_text", "text"))}
CAROUSEL_MAX = max(len(b["images"]) for _, b in blocks if b["type"] == "case_carousel")
CAROUSEL_MIN = min(len(b["images"]) for _, b in blocks if b["type"] == "case_carousel")

# ---------------------------------------------------------------- asset roles
ASSET_ROLES = {
    "case.featured-image": {"availability": "reference-only", "generationPolicy": "must-not-reuse", "desc": "Case featured photo/illustration (hero semicircle, next-case image, home index reveal).", "evidence": src("src/components/ShapesHeroCase.jsx", "<img src={image.jpg}"), "generationSafeSubstitutes": ["generated.case-visual"]},
    "case.screenshot": {"availability": "reference-only", "generationPolicy": "must-not-reuse", "desc": "Real product screenshots, device mockups and storyboards from client work.", "evidence": src("src/components/blocks/Blocks.jsx", "<LazyPicture image={block.image} />"), "generationSafeSubstitutes": ["generated.product-visual"]},
    "case.phone-screen": {"availability": "reference-only", "generationPolicy": "must-not-reuse", "desc": "Real mobile screen captures (750x1624) in carousels.", "evidence": src("src/components/blocks/Blocks.jsx", "className=\"carousel-slide mr-24 s:mr-30\""), "generationSafeSubstitutes": ["generated.product-visual"]},
    "case.video": {"availability": "reference-only", "generationPolicy": "must-not-reuse", "desc": "Real screen-recording / case videos.", "evidence": src("src/components/blocks/Blocks.jsx", "<video ref={media} src={block.videoUrl}"), "generationSafeSubstitutes": ["generated.motion-loop"]},
    "client.logo": {"availability": "blocked-for-generation", "generationPolicy": "must-not-fabricate", "desc": "Real client / company logos shown on the home index.", "evidence": src("src/components/home/HomeItems.jsx", "alt={`${homeCase.company || 'Client'} logo`}"), "generationSafeSubstitutes": ["placeholder.brand-mark"]},
    "brand.wordmark": {"availability": "blocked-for-generation", "generationPolicy": "must-not-fabricate", "desc": "The source owner's own logo mark (header, footer, loader).", "evidence": src("src/components/Header.jsx", 'aria-label="Go to homepage"'), "generationSafeSubstitutes": ["placeholder.brand-mark"]},
    "person.intro-video": {"availability": "blocked-for-generation", "generationPolicy": "must-not-fabricate", "desc": "Video and poster of the real site owner (a real person's likeness).", "evidence": src("src/components/home/ShapesHeroHome.jsx", 'src="/intro-short.mp4"'), "generationSafeSubstitutes": ["fictional.person-media"]},
    "decor.mascot-3d": {"availability": "reference-only", "generationPolicy": "must-not-reuse", "desc": "Proprietary 3D mascot model rendered in the footer.", "evidence": src("src/components/TheLama.jsx", "loader.load('/lama.glb'"), "generationSafeSubstitutes": ["generated.decorative-illustration"]},
    "decor.lettered-shape": {"availability": "reference-only", "generationPolicy": "must-not-reuse", "desc": "Source copy rendered as SVG lettering for physics (e.g. the next-case and connect words).", "evidence": src("src/components/ShapesNext.jsx", 'className="absolute bottom-full left-0 js-text z-2"'), "generationSafeSubstitutes": ["generated.lettering"]},
    "decor.geometric-shape": {"availability": "generation-safe", "generationPolicy": "may-reuse-shape", "desc": "Plain geometric physics shapes (triangle, semicircle, bar) defined as SVG paths.", "evidence": src("src/components/ShapesHeroCase.jsx", '<path d="M0,0l0,473.3h299.8L0,0z" />')},
    "ui.rive-icon": {"availability": "reference-only", "generationPolicy": "must-not-reuse", "desc": "The source's own Rive UI animations (arrow, play, play/pause, close).", "evidence": src("src/lib/rive.js", "export const createArrow"), "generationSafeSubstitutes": ["generated.ui-icon"]},
    "placeholder.brand-mark": {"availability": "generation-safe", "generationPolicy": "may-generate-new", "desc": "Placeholder, user-supplied or newly generated brand mark for the new site owner."},
    "fictional.person-media": {"availability": "generation-safe", "generationPolicy": "may-generate-new", "desc": "Fictional person portrait/video loop (no real person's likeness)."},
    "generated.case-visual": {"availability": "generation-safe", "generationPolicy": "may-generate-new", "desc": "Newly generated featured visual for a fictional project."},
    "generated.product-visual": {"availability": "generation-safe", "generationPolicy": "may-generate-new", "desc": "Newly generated UI/product visual for a fictional project."},
    "generated.motion-loop": {"availability": "generation-safe", "generationPolicy": "may-generate-new", "desc": "Newly generated short muted video loop."},
    "generated.decorative-illustration": {"availability": "generation-safe", "generationPolicy": "may-generate-new", "desc": "Newly generated decorative illustration / 3D object."},
    "generated.lettering": {"availability": "generation-safe", "generationPolicy": "may-generate-new", "desc": "Original copy set as lettering shapes."},
    "generated.ui-icon": {"availability": "generation-safe", "generationPolicy": "may-generate-new", "desc": "Generic arrow / play / close icon."},
}

# ---------------------------------------------------------------- content field helpers
T = lambda mw, **k: {"kind": "text", "maxWords": mw, **k}
def TL(*lits, **k):
    """Budget = word count of the real source literal(s) this field carries (no guessed budgets)."""
    return {"kind": "text", "maxWords": max(wc(l) for l in lits), "evidenceLiterals": len(lits), **k}
EM_MAX = max(len(x.split()) for c in list(CASES.values()) + HOME["featuredCases"] for x in re.findall(r"<em>(.*?)</em>", c["titleFormated"]))
EM_BLOCK = max([len(x.split()) for _, b in blocks for f in ("title",) for x in re.findall(r"<em>(.*?)</em>", b.get(f) or "")] or [1])
LINK = lambda mw: {"kind": "link", "labelMaxWords": mw}
RICH = lambda mw, paras: {"kind": "rich", "maxWords": mw, "maxParagraphs": paras}
ASSET = lambda roles, gen, **k: {"kind": "asset", "roles": roles, "generatedRoles": gen, **k}

RUNTIME_REASON = {
    "utility.preloader": "First-load intro overlay shown before any content; it carries no page content and is removed after the sequence.",
    "utility.page-transition": "Full-viewport mask that only exists to cover a route change; it is invisible at rest and carries no content.",
    "utility.video-modal": "Overlay dialog opened from a video card; it duplicates media already present and is not page content.",
    "utility.back-button": "Fixed floating navigation control that sits over the page; it is chrome, not a content section.",
    "utility.password-gate": "Runtime access gate (password form) shown before a protected case renders; it is not page content.",
}

SECTIONS = [
  dict(id="shell.header", category="SHELL", title="Site header", source=src("src/components/Header.jsx", 'className="site-head fixed', 40), sid="src:Header",
       desc="Fixed header: logo mark + owner name (left), three text links centred, yellow pill CTA (right). Links fade out after 50px of scroll.",
       content={"ownerName": TL("David Lubofsky"), "navLinks": {"kind": "links", "min": 3, "max": 3, "labelMaxWords": max(wc(x) for x in ("My Work", "My Book", "in"))}, "cta": LINK(wc("Let’s work together")), "logo": ASSET(["brand.wordmark"], ["placeholder.brand-mark"])},
       motion=["none"], defaultMotion="none", constraints={"onePerPage": True, "mustBeFirst": True},
       responsive=[{"at": "bp.s", "change": "hide-to-show", "detail": "owner name and CTA label appear; below 650px the CTA collapses to its circle", "evidence": css(".site-head__cta .btn-mask__text,", 4)}],
       primitives=["logo.wordmark", "link.underline", "button.pill"], tokens=["type.nav", "color.brand.yellow"]),
  dict(id="shell.footer", category="SHELL", title="Site footer", source=src("src/components/Footer.jsx", 'className="foot relative', 60), sid="src:Footer",
       desc="Yellow gradient footer: large statement with one white-underlined word, availability date, three contact links, legal line, logo; 3D mascot behind; content parallaxes up on scroll-in.",
       content={"statement": TL("Putting the human back into humankind"), "highlight": TL("human"), "availabilityLabel": TL("Next availability:"), "availabilityValue": TL(site["global"]["available"]), "links": {"kind": "links", "min": 3, "max": 3, "labelMaxWords": max(wc(x) for x in ("Shoot me a message", "Connect on LinkedIn", "Check out my book"))}, "legal": TL("UX, Strategy, Design, and Dev. ©2026 David Lubofsky"), "mascot": ASSET(["decor.mascot-3d"], ["generated.decorative-illustration"], optional=True)},
       motion=["parallax-up", "tilt-3d"], defaultMotion="parallax-up", constraints={"onePerPage": True, "mustBeLast": True},
       responsive=[{"at": "bp.s", "change": "layout-shift", "detail": "contact list moves beside the statement; footer height 65rem -> 71rem", "evidence": src("src/components/Footer.jsx", "h-[65rem] s:h-[71rem]")}],
       primitives=["link.underline", "logo.wordmark"], components=["mascot.3d"], tokens=["type.display-m-footer", "color.brand.yellow", "color.brand.yellow-light"]),
  dict(id="utility.preloader", category="UTILITY", title="Intro preloader", source=src("src/components/Loader.jsx", "bg-black z-10", 20), sid="src:Loader",
       desc="First-load overlay: ring draws, logo pieces pop in and fall away.", content={}, motion=["preloader-sequence"], defaultMotion="preloader-sequence",
       constraints={"maxPerPage": 1}, responsive=[], runtime=True, primitives=["logo.wordmark"], tokens=["color.neutral.900", "color.brand.yellow"]),
  dict(id="utility.page-transition", category="UTILITY", title="Route transition mask", source=src("src/App.jsx", "js-mask", 1), sid="src:App.js-mask",
       desc="Fixed full-viewport masks used only during route changes (black wipe; white wipe from the home index).", content={}, motion=["mask-wipe-transition"], defaultMotion="mask-wipe-transition",
       constraints={"maxPerPage": 1}, responsive=[], runtime=True, tokens=["color.neutral.900", "color.neutral.0"]),
  dict(id="utility.video-modal", category="UTILITY", title="Intro video modal", source=src("src/components/home/IntroModal.jsx", "<aside className", 40), sid="src:IntroModal",
       desc="Dialog that Flip-animates a video card to centre with a scrubber, timecode and cursor-following play/pause.", content={"video": ASSET(["person.intro-video"], ["fictional.person-media"])},
       motion=["flip-modal"], defaultMotion="flip-modal", constraints={"maxPerPage": 1}, responsive=[{"at": "bp.s", "change": "layout-shift", "detail": "portrait: card width 75%; landscape: card height 75vh", "evidence": src("src/components/home/IntroModal.jsx", "portrait:w-full")}], runtime=True,
       components=["scrubber.timeline"], primitives=["button.circle-icon"], tokens=["color.neutral.600", "type.meta"]),
  dict(id="utility.back-button", category="UTILITY", title="Back to index button", source=src("src/components/ButtonBack.jsx", 'className="back inline-flex', 20), sid="src:ButtonBack",
       desc="Fixed bottom-left yellow circle with arrow and label linking back to the index.", content={"label": TL("Back to cases")},
       motion=["pop-in-label-slide"], defaultMotion="pop-in-label-slide", constraints={"maxPerPage": 1},
       responsive=[{"at": "bp.s", "change": "hide-to-show", "detail": "label shows from 650px; below, circle only and right-aligned", "evidence": src("src/components/ButtonBack.jsx", "hidden s:inline-flex ml-13")}], runtime=True,
       primitives=["button.circle-icon"], tokens=["color.brand.yellow"]),
  dict(id="utility.password-gate", category="UTILITY", title="Password gate", source=src("src/components/KnockKnock.jsx", 'id="login"', 20), sid="src:KnockKnock",
       desc="Centred password field with yellow submit circle; inline error under the field.", content={"placeholder": TL("Enter Password"), "errorMessage": TL("Incorrect Password")},
       motion=["gate-reveal"], defaultMotion="gate-reveal", constraints={"maxPerPage": 1}, responsive=[], runtime=True,
       primitives=["input.password", "button.circle-icon"], tokens=["color.neutral.100", "radius.full"]),
  dict(id="hero.home", category="HERO", title="Index hero", source=src("src/components/home/HomeHero.jsx", 'className="home-hero relative', 18), sid="src:HomeHero",
       desc="Dark opener: multi-line discipline statement with yellow period, scroll cue bottom-left, physics shapes (triangle, bar, wedge) plus a falling portrait video card with hand-drawn callout.",
       content={"headline": TL("UX, Strategy, Design, and Development"), "scrollCue": TL("Scroll to view my work"), "videoCallout": TL("Get to know me a bit better"), "video": ASSET(["person.intro-video"], ["fictional.person-media"])},
       motion=["physics-drop", "underline-draw"], defaultMotion="physics-drop", constraints={"onePerPage": True},
       responsive=[{"at": "bp.s", "change": "font-size-step", "detail": "headline 48px -> 90px; scroll cue label appears", "evidence": css(".home-hero__title {", 7)}],
       components=["shape-field.physics", "card.video"], primitives=["mark.period"], tokens=["type.display-l", "color.neutral.700"]),
  dict(id="content.case-index-intro", category="INDEX", title="Index annotation", source=src("src/components/home/HomeItems.jsx", "left-[62rem] js-t-fade", 20), sid="src:HomeItems.annotation",
       desc="Rotated hand-written style note with drawn loop and arrow that introduces the project list.", content={"annotation": TL("Web experiences and products I’ve been lucky enough to help build.")},
       motion=["draw-annotation"], defaultMotion="draw-annotation", constraints={"onePerPage": True},
       responsive=[], primitives=[], tokens=["type.annotation", "color.brand.yellow-stroke"]),
  dict(id="content.case-index-item", category="INDEX", title="Index project entry", source=src("src/components/home/HomeItems.jsx", "<article ref={el}", 50), sid="src:HomeItem",
       desc="One project: number in a step shape, optional client logo, large title with highlighted word and yellow period, one-line description, 'check it out' link; featured image revealed under the cursor.",
       content={"index": T(1), "title": T(BUDGET["home.title"]["maxWords"]), "highlight": T(EM_MAX), "description": T(BUDGET["home.desc"]["maxWords"]), "linkLabel": TL("Check it out"), "href": {"kind": "href"},
                "clientLogo": ASSET(["client.logo"], ["placeholder.brand-mark"], optional=True), "featuredImage": ASSET(["case.featured-image"], ["generated.case-visual"])},
       motion=["mask-reveal-follow", "scroll-scrub-clip", "underline-draw"], defaultMotion="mask-reveal-follow", constraints={"minPerPage": 1},
       responsive=[{"at": "bp.s", "change": "layout-shift", "detail": "entries alternate left/right (odd entries margin-left auto); below 650px they stack with 22.5rem gaps", "evidence": src("src/components/home/HomeItems.jsx", "t % 2 === 0 ? '' : 's:ml-auto'")},
                   {"at": "bp.hover", "change": "interaction-swap", "detail": "hover devices: cursor-following mask reveal; touch: scroll-scrubbed clip", "evidence": src("src/components/home/HomeItems.jsx", "if (!app.hasMouse) {")}],
       components=["card.case-index", "mask.reveal-ellipse"], primitives=["shape.step-marker", "text.highlight", "mark.period", "link.underline", "icon.arrow-small"], tokens=["type.display-m-index", "type.ui"]),
  dict(id="conversion.connect", category="CONVERSION", title="Contact invitation", source=src("src/components/home/ShapesConnect.jsx", "relative pb-175", 25), sid="src:ShapesConnect",
       desc="Words of an invitation fall as physics bodies around a centred video card with play button and a pill 'message' CTA.",
       content={"lettering": {"kind": "words", "min": 1, "max": len("Want to partner together".split())}, "video": ASSET(["person.intro-video"], ["fictional.person-media"]), "cta": LINK(wc("Shoot me a message"))},
       motion=["physics-drop"], defaultMotion="physics-drop", constraints={"onePerPage": True},
       responsive=[{"at": "bp.s", "change": "size-step", "detail": "video card 17.5rem -> 29.5rem wide; physics scale x2 below 650px", "evidence": src("src/components/home/ShapesConnect.jsx", "w-[17.5rem] s:w-[29.5rem]")}],
       components=["card.video", "lettering.physics"], primitives=["button.pill"], tokens=["type.lettering-xxl", "radius.card-l"]),
  dict(id="hero.case", category="HERO", title="Case hero", source=src("src/components/CaseHero.jsx", 'className="case-hero relative', 24), sid="src:CaseHero",
       desc="Light opener: huge title with highlighted word and yellow period, 'roles' label + roles, short description bottom-right; accent-coloured physics shapes and the featured image in a semicircle mask.",
       content={"title": T(BUDGET["case.title"]["maxWords"]), "highlight": T(EM_MAX), "rolesLabel": TL("Roles"), "roles": T(BUDGET["case.roles"]["maxWords"]), "description": T(BUDGET["case.shortDesc"]["maxWords"]), "featuredImage": ASSET(["case.featured-image"], ["generated.case-visual"])},
       styleSlots={"accent": {"tokenFamily": "color.accent", "required": True}},
       motion=["physics-drop", "line-reveal"], defaultMotion="line-reveal", constraints={"onePerPage": True},
       responsive=[{"at": "bp.s", "change": "font-size-step", "detail": "title 48px -> 102px; description 16px -> 23px; physics scale ww/800 -> ww/1680", "evidence": css(".case-hero__title {", 12)}],
       components=["shape-field.physics"], primitives=["text.highlight", "mark.period"], tokens=["type.display-xl", "type.lede", "type.label"]),
  dict(id="content.media-text", category="CONTENT", title="Image + statement", source=src("src/components/blocks/Blocks.jsx", 'className="media-text relative', 18), sid="src:MediaText",
       desc="Half-width image (grey fill) beside a display title with highlighted word and yellow period, 1-2 large paragraphs and an optional underlined external link.",
       content={"title": T(BUDGET["media_text.title"]["maxWords"]), "highlight": T(EM_BLOCK, optional=True), "body": RICH(BUDGET["media_text.text"]["maxWords"], PARAS["case_media_text"]), "cta": {**LINK(BUDGET["media_text.cta"]["maxWords"]), "optional": True}, "image": ASSET(["case.screenshot"], ["generated.product-visual"])},
       motion=["image-fade-in", "underline-draw"], defaultMotion="image-fade-in", constraints={},
       responsive=[{"at": "bp.s", "change": "stack-to-row", "detail": "image above text below 650px; side-by-side from 650px, text margin 9.9rem (18rem from 1024px)", "evidence": css(".s\\:flex-row {", 3)}],
       components=["media.figure"], primitives=["text.highlight", "mark.period", "link.underline"], tokens=["type.display-m", "type.body-l", "color.neutral.200"]),
  dict(id="content.title-text", category="CONTENT", title="Title + long text", source=src("src/components/blocks/Blocks.jsx", 'className="content px-24', 16), sid="src:TitleText",
       desc="Display title (left half) and up to three body paragraphs (right half) with highlighted words and optional bold paragraph.",
       content={"title": T(BUDGET["title_text.title"]["maxWords"]), "highlight": T(EM_BLOCK, optional=True), "body": RICH(BUDGET["title_text.text"]["maxWords"], PARAS["case_title_text"])},
       motion=["underline-draw"], defaultMotion="underline-draw", constraints={},
       responsive=[{"at": "bp.s", "change": "stack-to-row", "detail": "title above text below 650px; two columns from 650px", "evidence": css(".s\\:flex-row {", 3)}],
       primitives=["text.highlight", "mark.period"], tokens=["type.display-m", "type.body"]),
  dict(id="content.text", category="CONTENT", title="Numbered note / statement", source=src("src/components/blocks/Blocks.jsx", 'className="title-text px-24', 24), sid="src:TextBlock",
       desc="Variant 'numbered': step number in a drawn triangle above one paragraph. Variant 'statement': one display line with yellow period. Variant 'note': one paragraph without a number.",
       variants=["numbered", "statement", "note"],
       content={"index": T(1, optional=True), "text": RICH(BUDGET["text.text"]["maxWords"], PARAS["case_text"])},
       motion=["underline-draw"], defaultMotion="underline-draw", constraints={},
       responsive=[{"at": "bp.s", "change": "gutter-step", "detail": "left inset 2.4rem -> 17.3rem from 650px", "evidence": src("src/components/blocks/Blocks.jsx", 's:pl-[17.3rem] s:pr-0 flex flex-col pb-40')}],
       primitives=["shape.step-marker", "text.highlight", "mark.period"], tokens=["type.body-l-trap", "type.display-m"]),
  dict(id="media.image", category="MEDIA", title="Image", source=src("src/components/blocks/Blocks.jsx", 'className="block-media relative pb-75 s:pb-150 last:pb-0 site-max">', 8), sid="src:BlockImage",
       desc="Variant 'inset': image offset right (31.4rem left inset at 1024px+). Variant 'full-width': edge-to-gutter image. Consecutive images overlap upward by 7rem.",
       variants=["inset", "full-width"], content={"image": ASSET(["case.screenshot"], ["generated.product-visual"])},
       motion=["image-fade-in"], defaultMotion="image-fade-in", constraints={},
       responsive=[{"at": "bp.l", "change": "gutter-step", "detail": "inset variant: 2.4rem -> 4.4rem (650px) -> 17.3rem (769px) -> 31.4rem left / 15rem right (1024px)", "evidence": src("src/components/blocks/Blocks.jsx", "l:pl-[31.4rem] l:pr-150'")}],
       components=["media.figure"], tokens=["space.75", "space.150"]),
  dict(id="media.video", category="MEDIA", title="Video", source=src("src/components/blocks/Blocks.jsx", "last:pb-0 media-cover px-24 s:px-44", 8), sid="src:BlockVideo",
       desc="16:9 muted looping video, inset like the image block; plays only while in view.", content={"video": ASSET(["case.video"], ["generated.motion-loop"])},
       motion=["video-in-view"], defaultMotion="video-in-view", constraints={},
       responsive=[{"at": "bp.l", "change": "gutter-step", "detail": "same inset steps as media.image inset", "evidence": src("src/components/blocks/Blocks.jsx", "last:pb-0 media-cover px-24 s:px-44")}],
       primitives=["video.inline"], tokens=[]),
  dict(id="media.carousel", category="MEDIA", title="Screen carousel", source=src("src/components/blocks/Blocks.jsx", "carousel extend", 20), sid="src:Carousel",
       desc="Full-bleed row of tall phone screens; drag to scroll (hover devices) or native snap scroll (touch).",
       content={"images": {"kind": "assets", "min": CAROUSEL_MIN, "max": CAROUSEL_MAX, "roles": ["case.phone-screen"], "generatedRoles": ["generated.product-visual"]}},
       motion=["drag-carousel", "image-fade-in"], defaultMotion="drag-carousel", constraints={},
       responsive=[{"at": "bp.s", "change": "slides-per-view", "detail": "slide width 85% -> 50%-3rem (650px) -> 33.33%-3rem (1024px)", "evidence": css(".carousel {", 4)}],
       components=["media.figure"], tokens=[]),
  dict(id="layout.gray-band", category="LAYOUT", title="Grey background band", source=src("src/components/blocks/Blocks.jsx", "bg-gray-case/20", 3), sid="src:GrayStart",
       desc="Out-of-flow light-grey band that starts at the vertical middle of the next block and runs to the next-case section.", content={},
       motion=["none"], defaultMotion="none", constraints={"maxPerPage": 1},
       responsive=[], tokens=["color.neutral.150"]),
  dict(id="navigation.next-case", category="NAVIGATION", title="Next case", source=src("src/components/ShapesNext.jsx", 'className="next relative bg-white"', 30), sid="src:ShapesNext",
       desc="White band linking to the next case: small title + pill button top-left, lettered words and an arrow fall as physics bodies onto a rotated semicircle holding the next case's image.",
       content={"title": T(BUDGET["case.title"]["maxWords"]), "ctaLabel": TL("Check it out"), "href": {"kind": "href"}, "lettering": {"kind": "words", "min": 1, "max": len("View next brand".split())}, "featuredImage": ASSET(["case.featured-image"], ["generated.case-visual"])},
       motion=["physics-drop"], defaultMotion="physics-drop", constraints={"onePerPage": True},
       responsive=[{"at": "bp.s", "change": "height-step", "detail": "height 60rem -> 77rem; text column moves to 17.3rem", "evidence": src("src/components/ShapesNext.jsx", "h-[60rem] s:h-[77rem]")}],
       components=["lettering.physics"], primitives=["button.pill"], tokens=["type.subhead"]),
]
SEC = {s["id"]: s for s in SECTIONS}

PRIMITIVES = {
  "button.pill": ("Yellow pill button; on hover the mask collapses onto the arrow circle and the label slides.", src("src/components/ButtonMain.jsx", 'className={`btn relative', 20), ["label", "href"]),
  "button.circle-icon": ("Yellow circle with an animated icon (arrow / play / pause / close).", src("src/components/home/Buttons.jsx", "export const ButtonPlay"), ["icon"]),
  "link.underline": ("Text link with a yellow (or white) underline that wipes out and back in on hover.", css(".uline:before {", 6), ["label", "href", "tone"]),
  "text.highlight": ("Emphasised word with a tilted yellow marker underline drawn in on scroll.", css("em:after {", 9), ["text"]),
  "mark.period": ("Yellow semicircle used as a full stop after display titles.", src("src/data/case.js", "export const PERIOD_SVG"), []),
  "shape.step-marker": ("Thin yellow outline triangle/semicircle/bar framing a step number.", src("src/data/case.js", "export const SMALL_SHAPES"), ["shape"]),
  "icon.arrow-small": ("Small yellow arrow after index links.", src("src/components/home/HomeItems.jsx", 'viewBox="0 0 18 10"'), []),
  "logo.wordmark": ("Three-part logo mark (half-disc, bar, wedge).", src("src/components/Header.jsx", 'viewBox="0 0 60 49"'), []),
  "input.password": ("Pill text field on light grey.", src("src/components/KnockKnock.jsx", 'type="password"'), ["placeholder"]),
  "video.inline": ("Muted, looping, inline video element.", src("src/components/blocks/Blocks.jsx", "loop muted playsInline"), ["src"]),
}
COMPONENTS = {
  "card.case-index": ("Index entry card: number + logo row, title, description, link.", src("src/components/home/HomeItems.jsx", "<article ref={el}", 50), ["index", "title", "description", "href"]),
  "card.video": ("Rounded video card with play circle; opens the video modal.", src("src/components/home/ShapesHeroHome.jsx", "play-hover absolute inset-0 media-cover rounded-[2.3rem]"), ["video"]),
  "media.figure": ("Aspect-ratio figure with lazy picture that fades in.", src("src/components/LazyPicture.jsx", "export default function LazyPicture", 30), ["image"]),
  "lettering.physics": ("SVG words plus convex hull shapes that fall as physics bodies.", src("src/components/ShapesNext.jsx", "const shape = (i = 0, x = 1, yMul = 1, av = 0) => {", 15), ["words"]),
  "shape-field.physics": ("Canvas of geometric physics bodies in a theme colour.", src("src/components/ShapesHeroCase.jsx", "const shapes = small", 12), ["color"]),
  "mascot.3d": ("WebGL mascot model with cursor tilt and scroll timeline.", src("src/components/TheLama.jsx", "export default function TheLama()", 20), ["model"]),
  "scrubber.timeline": ("Thin progress track with yellow handle and timecode.", src("src/components/home/IntroModal.jsx", 'className="timeline relative'), []),
  "mask.reveal-ellipse": ("Elliptical clip mask that follows the cursor.", src("src/components/home/HomeItems.jsx", "home-item__clip-mask absolute inset-0"), []),
}

# ---------------------------------------------------------------- templates
BODY = ["content.media-text", "content.title-text", "content.text", "media.image", "media.video", "media.carousel", "layout.gray-band"]
TEMPLATES = {
  "template.home": {"desc": "Dark index page: hero, annotated project list, contact invitation.", "theme": "dark",
    "evidence": src("src/pages/HomePage.jsx", '<div ref={ref} className="text-white site-max z-2">', 8),
    "nodes": [
      {"section": "shell.header", "required": True, "repeatable": False},
      {"section": "hero.home", "required": True, "repeatable": False},
      {"section": "content.case-index-intro", "required": True, "repeatable": False},
      {"section": "content.case-index-item", "required": True, "repeatable": True},
      {"section": "conversion.connect", "required": True, "repeatable": False},
      {"section": "utility.video-modal", "required": False, "repeatable": False},
      {"section": "shell.footer", "required": True, "repeatable": False},
      {"section": "utility.page-transition", "required": False, "repeatable": False},
      {"section": "utility.preloader", "required": False, "repeatable": False}]},
  "template.case-study": {"desc": "Light case study: hero, a free sequence of content/media blocks, next-case link. One family for public and password-gated cases.", "theme": "light",
    "evidence": src("src/pages/CasePage.jsx", "export default function CasePage", 40),
    "nodes": [
      {"section": "shell.header", "required": True, "repeatable": False},
      {"section": "utility.password-gate", "required": False, "repeatable": False},
      {"section": "hero.case", "required": True, "repeatable": False},
      {"slot": "body", "oneOf": BODY, "required": True, "repeatable": True},
      {"section": "navigation.next-case", "required": True, "repeatable": False},
      {"section": "utility.back-button", "required": True, "repeatable": False},
      {"section": "shell.footer", "required": True, "repeatable": False},
      {"section": "utility.page-transition", "required": False, "repeatable": False},
      {"section": "utility.preloader", "required": False, "repeatable": False}]},
}
routes = json.loads((DR / "templates/routes.json").read_text())["routes"]
for r in routes:
    assert r["template"] in TEMPLATES
    if r["path"] != "/":
        assert r["path"].split("/")[2] in CASES, r["path"]
assert len(routes) == len(CASES) + 1

# ---------------------------------------------------------------- source identity registry (R2)
corpus_parts = [json.dumps(site, ensure_ascii=False), rd("index.html")]
for p in sorted(list((PROJ / "src").rglob("*.jsx")) + list((PROJ / "src").rglob("*.js"))): corpus_parts.append(p.read_text())
corpus = "\n".join(corpus_parts)
def norm_corpus(t):
    t = re.sub(r"<[^>]+>", " ", t).replace("\\n", " ").replace("{'", " ").replace("'}", " ")
    return re.sub(r"\s+", " ", t).lower().replace("’", "'")
corpus_l = norm_corpus(corpus)
corpus_raw = corpus.lower().replace("’", "'")
def in_corpus(x): return norm_corpus(x) in corpus_l or x.lower().replace("’", "'") in corpus_raw
SOURCE_BRAND = {
  "brand": ["David Lubofsky", "Lubofsky", "davidlubofsky", "DL | The portfolio", "builtkindly", "seewhateyesee", "Work Happiness", "findworkhappiness", "ESPN", "Detroit Lions"],
  "person": ["David", "Calvin Johnson", "davidalubofsky"],
  "cta": ["Let’s work together", "Shoot me a message", "Back to cases", "Scroll to view my work", "Get to know me a bit better", "Connect on LinkedIn", "Check out my book", "Putting the human back into humankind"],
  "recognition": ["Awwwards", "commarts", "Communication Arts", "amazon.com", "spotify", "youtube.com"],
  "domains": ["davidlubofsky.com", "findworkhappiness.com", "linkedin.com/in/davidalubofsky", "seewhateyesee.org", "builtkindly.com", "espn.com", "awwwards.com", "commarts.com", "amazon.com", "spotify.com", "youtube.com"],
}
missing = [(k, p) for k, v in SOURCE_BRAND.items() for p in v if not in_corpus(p)]
if missing: sys.exit(f"source-identity patterns not found in source corpus (would be invented): {missing}")

# ---------------------------------------------------------------- write tokens
def ev(x): return x if isinstance(x, list) else [x]
dump("tokens/00-foundation/color.json", {"$comment": "Foundation colours. Every value is in the computed histogram or cited in source (canvas-only colours).", "tokens": color})
dump("tokens/00-foundation/typography.json", {"fontFamily": FONT, "fontWeights": WEIGHTS, "tracking": LETTER, "scale": TYPE_SCALE, "rootSize": {"rule": "html font-size = 1000vw / 1440 at >=650px (10px at 1440), 1000vw / 375 below", "evidence": css("html {", 6, nth=3)}})
dump("tokens/00-foundation/spacing.json", {"$comment": "Spacing scale: 1 unit = 0.1rem (1px at the 1440px reference width). Only utilities actually used by the clone's markup.", "tokens": spacing})
dump("tokens/00-foundation/radius.json", {"tokens": RADIUS})
dump("tokens/00-foundation/breakpoint.json", {"tokens": BREAK})
dump("tokens/00-foundation/motion.json", {"easing": EASE, "duration": DUR, "scroll": {"lerp": 0.12, "wheelMultiplier": {"mac": 0.3, "windows": 0.7}, "evidence": src("src/lib/smoothScroll.js", "ease: 0.12,")}, "reducedMotion": {"sourceSupport": False, "evidence": "grep -rl prefers-reduced-motion src -> 0 files; fallbacks in section contracts are requirements for generated pages, not observed behaviour"}})
dump("tokens/00-foundation/elevation.json", {"tokens": {}, "evidence": "no box-shadow other than CSS resets in src/styles/original.css (grep box-shadow -> reset lines only); the design uses flat surfaces"})
dump("tokens/00-foundation/motion-patterns.json", {"patternsVersion": "1.0.0", "patterns": motion_patterns})
SEM = {
  "text.primary": {"light": "color.neutral.900", "dark": "color.neutral.0"},
  "text.inverse": {"light": "color.neutral.0", "dark": "color.neutral.900"},
  "surface.page": {"light": "color.neutral.0", "dark": "color.neutral.900"},
  "surface.brand": {"light": "color.brand.yellow", "dark": "color.brand.yellow"},
  "surface.footer-start": {"light": "color.brand.yellow-light", "dark": "color.brand.yellow-light"},
  "surface.media-fill": {"light": "color.neutral.200", "dark": "color.neutral.200"},
  "surface.band": {"light": "color.neutral.150", "dark": "color.neutral.150"},
  "surface.input": {"light": "color.neutral.100", "dark": "color.neutral.100"},
  "surface.modal-track": {"light": "color.neutral.600", "dark": "color.neutral.600"},
  "shape.fill": {"light": "accent (per-page style.accent)", "dark": "color.neutral.700"},
  "mark.highlight": {"light": "color.brand.yellow", "dark": "color.brand.yellow"},
  "stroke.annotation": {"light": "color.brand.yellow-stroke", "dark": "color.brand.yellow-stroke"},
  "logo.secondary": {"light": "color.neutral.400", "dark": "color.neutral.400"},
}
dump("tokens/10-semantic/semantic.json", {"$comment": "Semantic roles. The case hero's physics fill is the page's accent token.", "roles": SEM, "evidence": [css("html:not(.is-dark) body", 4), css(".is-dark body", 4)]})
for th in ("light", "dark"):
    dump(f"tokens/themes/{th}.json", {"theme": th, "templates": [t for t, v in TEMPLATES.items() if v["theme"] == th], "resolves": {k: v[th] for k, v in SEM.items()}})
dump("tokens/20-component/component.json", {"button.pill": {"height": "5.5rem", "radius": "radius.pill", "fill": "color.brand.yellow", "type": "type.button", "evidence": css(".btn {", 8)},
     "button.circle-icon": {"size": "5.5rem", "fill": "color.brand.yellow", "evidence": src("src/components/ButtonBack.jsx", "h-[5.5rem] w-[5.5rem]")},
     "card.video": {"radius": ["radius.card-m", "radius.card-l"], "aspectRatio": "300/500", "evidence": src("src/components/home/ShapesConnect.jsx", "aspectRatio: '300/500'")}})
dump("tokens/30-layout/layout.json", {"siteMax": {"value": "144rem", "evidence": css(".site-max {", 4)}, "gutter": {"base": "2.4rem", "s": {"left": "4.14rem", "right": "4.4rem"}, "evidence": css(".site-gutter {", 4)},
     "caseInset": {"s": "17.3rem", "l": "31.4rem", "evidence": src("src/components/blocks/Blocks.jsx", "l:pl-[31.4rem] l:pr-150'")}})

catalog = {"catalogVersion": "1.0.0", "derivedFrom": "tokens/00-foundation/*.json + tokens/10-semantic/semantic.json (regenerated by extraction/build_repo.py; verify_all.py re-derives and diffs)",
  "color": {k: v["value"] + (f"@{v['alpha']}" if "alpha" in v else "") for k, v in color.items()},
  "fontSize": {k: v["fontSize"] for k, v in TYPE_SCALE.items()}, "fontWeight": WEIGHTS, "fontFamily": ["pleasure"],
  "spacing": {k: v["value"] for k, v in spacing.items()}, "radius": {k: v["value"] for k, v in RADIUS.items()},
  "breakpoint": {k: v.get("minWidth", v.get("query")) for k, v in BREAK.items()}, "elevation": {},
  "easing": {k: v["value"] for k, v in EASE.items()}, "duration": DUR, "semantic": SEM}
dump("tokens/llm/token-catalog.json", catalog)
policy = {"policyVersion": "1.0.0",
  "pageSpecTokenSlots": {"node.style.accent": {"sections": ["hero.case"], "family": "color.accent", "allowed": sorted(k for k in color if k.startswith("color.accent.")), "rule": "TOKEN_SLOT_FAMILY"}},
  "themeBinding": {"template.home": "dark", "template.case-study": "light", "rule": "THEME_TEMPLATE", "evidence": src("src/lib/router.js", "document.documentElement.classList.toggle('is-dark', state.route.name === 'index');")},
  "themeTokenRules": [{"theme": "dark", "forbiddenFamilies": ["color.accent"], "reason": "accents are only used by the light case hero"}],
  "rawValueRestrictions": {"color": "RAW_COLOR: no #hex / rgb() / hsl() literal anywhere in a PageSpec", "spacing": "no spacing field exists on a PageSpec node (schema additionalProperties:false); spacing is owned by section contracts", "fontFamily": "no font field exists on a PageSpec node; the only family is pleasure", "fontSize": "owned by section contracts", "fontWeight": "owned by section contracts"},
  "overrides": "PageSpecs carry exactly one token slot (hero.case style.accent). Spacing, type and radius are fixed by section contracts; there is no per-instance override mechanism in the source, so none is offered."}
dump("tokens/llm/token-policy.json", policy)

# ---------------------------------------------------------------- assets, sections, primitives, components
dump("assets/asset-roles.json", {"rolesVersion": "1.0.0", "$comment": "Closed asset-role vocabulary. availability is also pinned in code (PINNED_AVAILABILITY in schema/semantic_validate.py and extraction/verify_all.py). The source is a real person's live portfolio with real client work: generated pages must never reproduce its logos, likeness, screenshots, videos or 3D model.",
     "srcSchemes": {"reference": "site-relative path to the clone's own asset (e.g. /images/...)", "generated": "placeholder:<slug> | generated:<slug> | user-supplied:<slug>"},
     "roles": {k: {kk: (vv["cite"] if kk == "evidence" else vv) for kk, vv in v.items()} | ({"evidenceTag": v["evidence"]["tag"]} if "evidence" in v else {}) for k, v in ASSET_ROLES.items()}})

contract_files = []
for s in SECTIONS:
    gen_roles = sorted({r for f in s["content"].values() if isinstance(f, dict) for r in f.get("generatedRoles", [])})
    ref_roles = sorted({r for f in s["content"].values() if isinstance(f, dict) for r in f.get("roles", [])})
    c = {"id": s["id"], "title": s["title"], "description": s["desc"],
         "source": {"id": s["sid"], "file": s["source"]["cite"].split(":")[0], "lines": s["source"]["cite"].split(":")[1], "tag": s["source"]["tag"]},
         "semantic": {"id": s["id"], "category": s["category"]},
         "retrievalEligible": not s.get("runtime", False),
         **({"retrievalReason": RUNTIME_REASON[s["id"]]} if s.get("runtime") else {}),
         "variants": s.get("variants", []), "content": s["content"], "styleSlots": s.get("styleSlots", {}),
         "assetRoles": ref_roles, "generatedAssetRoles": gen_roles,
         "constraints": s["constraints"],
         "motion": {"allowed": s["motion"], "default": s["defaultMotion"], "reducedMotionFallback": {m: motion_patterns[m]["fallback"] for m in s["motion"]}},
         "responsive": [{**r, "evidence": r["evidence"]["cite"], "evidenceTag": r["evidence"]["tag"]} for r in s["responsive"]],
         "uses": {"primitives": s.get("primitives", []), "components": s.get("components", []), "tokens": s.get("tokens", [])},
         "templates": [t for t, v in TEMPLATES.items() if any(n.get("section") == s["id"] or s["id"] in n.get("oneOf", []) for n in v["nodes"])]}
    fn = f"sections/{s['id']}.json"; dump(fn, c); contract_files.append(fn)
for k, (d, e, props) in PRIMITIVES.items(): dump(f"primitives/{k}.json", {"id": k, "description": d, "props": props, "source": {"file": e["cite"].split(":")[0], "lines": e["cite"].split(":")[1], "tag": e["tag"]}})
for k, (d, e, props) in COMPONENTS.items(): dump(f"components/{k}.json", {"id": k, "description": d, "props": props, "source": {"file": e["cite"].split(":")[0], "lines": e["cite"].split(":")[1], "tag": e["tag"]}})
dump("templates/templates.json", {"templatesVersion": "1.0.0", "templates": {k: {"description": v["desc"], "theme": v["theme"], "nodes": v["nodes"], "evidence": v["evidence"]["cite"], "evidenceTag": v["evidence"]["tag"], "routes": [r["path"] for r in routes if r["template"] == k]} for k, v in TEMPLATES.items()}})

# ---------------------------------------------------------------- allowlist
allow = {"allowlistVersion": ALLOWLIST_VERSION, "$comment": "Closed list of every section/component/primitive an AI may place, and the node properties it may set. Parity with sections/, components/, primitives/ is checked by verify_all.py.",
  "nodeProperties": ["section", "variant", "content", "motion", "retrievalEligible", "style"],
  "sections": {s["id"]: {"settable": ["content." + k for k in s["content"]] + (["variant"] if s.get("variants") else []) + ["motion.pattern", "motion.reducedMotionFallback"] + ["style." + k for k in s.get("styleSlots", {})],
                         "retrievalEligible": not s.get("runtime", False), "assetRoles": sorted({r for f in s["content"].values() if isinstance(f, dict) for r in f.get("roles", []) + f.get("generatedRoles", [])})} for s in SECTIONS},
  "components": sorted(COMPONENTS), "primitives": sorted(PRIMITIVES), "assetRoles": sorted(ASSET_ROLES)}
dump("tokens/llm/component-allowlist.json", allow)

# ---------------------------------------------------------------- compatibility graph (rule ids == validator rule ids)
graph = {"graphVersion": "1.0.0", "rules": [
  {"id": "TEMPLATE_SEQUENCE", "severity": "error", "rule": "Node sequence must match the declared template's node list (order, required, repeatable, body slot membership).", "evidence": "templates/templates.json"},
  {"id": "SHELL_HEADER_FIRST", "severity": "error", "rule": "shell.header is the first node."},
  {"id": "SHELL_FOOTER_LAST_IN_FLOW", "severity": "error", "rule": "shell.footer is the last non-runtime node; only utility.page-transition / utility.preloader may follow it."},
  {"id": "ONE_HERO", "severity": "error", "rule": "Exactly one hero.* node per page.", "exception": "none: both templates have exactly one hero (templates/templates.json)"},
  {"id": "HERO_TEMPLATE_BINDING", "severity": "error", "rule": "hero.home only on template.home; hero.case only on template.case-study."},
  {"id": "GRAY_BAND_MAX_ONE", "severity": "error", "rule": "At most one layout.gray-band per page (observed max 1 across 10 cases).", "evidence": "data:src/data/site.json case_gray_start counts"},
  {"id": "GRAY_BAND_NEEDS_FOLLOWER", "severity": "error", "rule": "layout.gray-band must be followed by another body block: it positions itself from its next sibling.", "evidence": src("src/components/blocks/Blocks.jsx", "const next = node?.nextElementSibling;")["cite"]},
  {"id": "PASSWORD_GATE_ACCESS", "severity": "error", "rule": "utility.password-gate is present if and only if access = password-gated."},
  {"id": "CASE_INDEX_NUMBERING", "severity": "error", "rule": "content.case-index-item indexes run 01, 02, ... in node order (zero-padded position).", "evidence": src("src/components/home/HomeItems.jsx", "String(index + 1).padStart(2, '0')")["cite"]},
  {"id": "BODY_OPENS_WITH_MEDIA_TEXT", "severity": "warn", "rule": "A case body usually opens with content.media-text (9 of 10 cases; the gated case opens with content.text)."},
  {"id": "PHYSICS_BUDGET", "severity": "warn", "rule": "At most two physics-drop nodes per page (both templates use exactly two)."},
  {"id": "THEME_TEMPLATE", "severity": "error", "rule": "template.home uses theme dark; template.case-study uses theme light.", "evidence": policy["themeBinding"]["evidence"]["cite"]},
]}
dump("compatibility/graph.json", graph)

# ---------------------------------------------------------------- PageSpec schema (generated from the same section table)
def field_schema(f):
    k = f["kind"]
    if k == "text": return {"type": "string", "minLength": 1}
    if k == "href": return {"$ref": "#/definitions/href"}
    if k == "link": return {"$ref": "#/definitions/link"}
    if k == "links": return {"type": "array", "minItems": f["min"], "maxItems": f["max"], "items": {"$ref": "#/definitions/link"}}
    if k == "rich": return {"type": "array", "minItems": 1, "maxItems": f["maxParagraphs"], "items": {"$ref": "#/definitions/paragraph"}}
    if k == "words": return {"type": "array", "minItems": f["min"], "maxItems": f["max"], "items": {"type": "string", "pattern": "^\\S+$"}}
    if k == "asset": return {"$ref": "#/definitions/asset"}
    if k == "assets": return {"type": "array", "minItems": f["min"], "maxItems": f["max"], "items": {"$ref": "#/definitions/asset"}}
    raise ValueError(k)
branches = []
for s in SECTIONS:
    props = {k: field_schema(f) for k, f in s["content"].items()}
    req = [k for k, f in s["content"].items() if not f.get("optional")]
    node_props = {"section": {"const": s["id"]}, "content": {"type": "object", "additionalProperties": False, "properties": props, "required": req},
                  "motion": {"type": "object", "additionalProperties": False, "required": ["pattern", "reducedMotionFallback"],
                             "properties": {"pattern": {"enum": s["motion"]}, "reducedMotionFallback": {"enum": sorted({motion_patterns[m]["fallback"] for m in s["motion"]})}}},
                  "retrievalEligible": {"type": "boolean"}}
    if s.get("variants"): node_props["variant"] = {"enum": s["variants"]}
    if s.get("styleSlots"): node_props["style"] = {"type": "object", "additionalProperties": False, "required": ["accent"], "properties": {"accent": {"type": "string", "pattern": "^color\\.[a-z0-9.-]+$"}}}
    nreq = ["section", "content", "motion"] + (["variant"] if s.get("variants") else []) + (["style"] if s.get("styleSlots") else [])
    branches.append({"type": "object", "additionalProperties": False, "required": nreq, "properties": node_props})
schema = {"$schema": "http://json-schema.org/draft-07/schema#", "$id": "pagespec.schema.json", "title": "PageSpec", "type": "object", "additionalProperties": False,
  "required": ["pageSpecVersion", "mode", "template", "route", "theme", "access", "meta", "nodes"],
  "properties": {
    "pageSpecVersion": {"const": PAGESPEC_VERSION},
    "mode": {"enum": ["reference", "generated"], "description": "reference = faithful reconstruction of the source; generated = new page that must contain no source identity, copy, URLs or assets."},
    "template": {"enum": sorted(TEMPLATES)},
    "route": {"type": "string", "pattern": "^/(case/[a-z0-9-]+/)?$"},
    "theme": {"enum": ["light", "dark"]},
    "access": {"enum": ["public", "password-gated"]},
    "meta": {"type": "object", "additionalProperties": False, "required": ["title"], "properties": {"title": {"type": "string", "minLength": 1}}},
    "nodes": {"type": "array", "minItems": 1, "items": {"oneOf": branches}}},
  "definitions": {
    "href": {"type": "string", "pattern": "^(/[a-z0-9/#-]*|https?://[^\\s]+|mailto:[^\\s]+)$"},
    "link": {"type": "object", "additionalProperties": False, "required": ["label", "href"], "properties": {"label": {"type": "string", "minLength": 1}, "href": {"$ref": "#/definitions/href"}}},
    "paragraph": {"type": "object", "additionalProperties": False, "required": ["text"], "properties": {"text": {"type": "string", "minLength": 1}, "highlights": {"type": "array", "items": {"type": "string", "minLength": 1}}, "strong": {"type": "array", "items": {"type": "string", "minLength": 1}}}},
    "asset": {"type": "object", "additionalProperties": False, "required": ["role", "src"], "properties": {"role": {"enum": sorted(ASSET_ROLES)}, "src": {"type": "string", "pattern": "^(/[A-Za-z0-9._/-]+|(placeholder|generated|user-supplied):[a-z0-9-]+)$"}, "alt": {"type": "string"}}}}}
dump("schema/pagespec.schema.json", schema)

# ---------------------------------------------------------------- reference example PageSpecs built from the real data
def paras(h):
    out = []
    for p in re.findall(r"<p>(.*?)</p>", h or "", re.S):
        text = re.sub(r"<[^>]+>", "", p).strip()
        d = {"text": text}
        hl = [re.sub(r"<[^>]+>", "", x) for x in re.findall(r"<em>(.*?)</em>", p)]
        st = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<strong>(.*?)</strong>", p, re.S)]
        if hl: d["highlights"] = hl
        if st: d["strong"] = st
        out.append(d)
    return out
def title_parts(h):
    hl = re.findall(r"<em>(.*?)</em>", h)
    return re.sub(r"<[^>]+>", "", h).strip(), (hl[0] if hl else None)
def img(i, role): return {"role": role, "src": i.get("jpg") or i.get("svg")}
def M(sec, pattern=None):
    p = pattern or SEC[sec]["defaultMotion"]; return {"pattern": p, "reducedMotionFallback": motion_patterns[p]["fallback"]}
def nxt(slug):
    order = [c["slug"] for c in site["order"] if not c["protected"]]
    return CASES[order[(order.index(slug) + 1) % len(order)]] if slug in order else CASES[order[0]]
HEADER = {"section": "shell.header", "content": {"ownerName": "David Lubofsky", "navLinks": [{"label": "My Work", "href": "/#work"}, {"label": "My Book", "href": "https://findworkhappiness.com"}, {"label": "in", "href": "https://www.linkedin.com/in/davidalubofsky/"}], "cta": {"label": "Let’s work together", "href": "mailto:me@davidlubofsky.com"}, "logo": {"role": "brand.wordmark", "src": "/favicon.svg"}}, "motion": M("shell.header")}
FOOTER = {"section": "shell.footer", "content": {"statement": "Putting the human back into humankind", "highlight": "human", "availabilityLabel": "Next availability:", "availabilityValue": site["global"]["available"], "links": [{"label": "Shoot me a message", "href": "mailto:me@davidlubofsky.com"}, {"label": "Connect on LinkedIn", "href": "https://www.linkedin.com/in/davidalubofsky/"}, {"label": "Check out my book", "href": "https://findworkhappiness.com"}], "legal": "UX, Strategy, Design, and Dev. ©2026 David Lubofsky", "mascot": {"role": "decor.mascot-3d", "src": "/lama.glb"}}, "motion": M("shell.footer")}
LITERALS = ["Let’s work together", "My Work", "My Book", "Putting the human back into humankind", "Next availability:", "Shoot me a message", "Connect on LinkedIn", "Check out my book", "UX, Strategy, Design, and Dev.", "Enter Password", "Incorrect Password", "Roles", "Check it out", "Back to cases", "UX, Strategy, Design, and Development", "Scroll to view my work", "Get to", "know me a", "bit better", "Web experiences and products I’ve been lucky enough to help build.", "Want", "partner", "together"]
bad = [l for l in LITERALS if not in_corpus(l)]
if bad: sys.exit(f"reference literals not found in source: {bad}")
def case_spec(slug):
    c = CASES[slug]; title, hl = title_parts(c["titleFormated"]); nodes = [HEADER]
    if c.get("protected"): nodes.append({"section": "utility.password-gate", "content": {"placeholder": "Enter Password", "errorMessage": "Incorrect Password"}, "motion": M("utility.password-gate")})
    nodes.append({"section": "hero.case", "content": {"title": title, "highlight": hl, "rolesLabel": "Roles", "roles": c["roles"], "description": c["shortDesc"], "featuredImage": img(c["featuredImage"], "case.featured-image")}, "style": {"accent": "color.accent." + ACCENTS[c["color"]["hex"]]}, "motion": M("hero.case")})
    for b in c["blocks"]:
        t = b["type"]
        if t == "case_media_text":
            tt, h = title_parts(b["title"]); ct = {"title": tt, "body": paras(b["text"]), "image": img(b["image"], "case.screenshot")}
            if h: ct["highlight"] = h
            if b.get("ctaLabel"): ct["cta"] = {"label": b["ctaLabel"], "href": b["ctaLink"]}
            nodes.append({"section": "content.media-text", "content": ct, "motion": M("content.media-text")})
        elif t == "case_title_text":
            tt, h = title_parts(b["title"]); ct = {"title": tt, "body": paras(b["text"])}
            if h: ct["highlight"] = h
            nodes.append({"section": "content.title-text", "content": ct, "motion": M("content.title-text")})
        elif t == "case_text":
            v = "statement" if b.get("bigText") else ("numbered" if b.get("index") else "note"); ct = {"text": paras(b["text"])}
            if b.get("index"): ct["index"] = b["index"]
            nodes.append({"section": "content.text", "variant": v, "content": ct, "motion": M("content.text")})
        elif t == "case_image": nodes.append({"section": "media.image", "variant": "full-width" if b.get("fullWidth") else "inset", "content": {"image": img(b["image"], "case.screenshot")}, "motion": M("media.image")})
        elif t == "case_video": nodes.append({"section": "media.video", "content": {"video": {"role": "case.video", "src": b["videoUrl"]}}, "motion": M("media.video")})
        elif t == "case_carousel": nodes.append({"section": "media.carousel", "content": {"images": [img(i, "case.phone-screen") for i in b["images"]]}, "motion": M("media.carousel")})
        elif t == "case_gray_start": nodes.append({"section": "layout.gray-band", "content": {}, "motion": M("layout.gray-band")})
    n = nxt(slug)
    nodes += [{"section": "navigation.next-case", "content": {"title": n["title"], "ctaLabel": "Check it out", "href": f"/case/{n['slug']}/", "lettering": ["View", "next", "brand"], "featuredImage": img(n["featuredImage"], "case.featured-image")}, "motion": M("navigation.next-case")},
              {"section": "utility.back-button", "content": {"label": "Back to cases"}, "motion": M("utility.back-button"), "retrievalEligible": False}, FOOTER]
    return {"pageSpecVersion": PAGESPEC_VERSION, "mode": "reference", "template": "template.case-study", "route": f"/case/{slug}/", "theme": "light", "access": "password-gated" if c.get("protected") else "public", "meta": {"title": "DL | The portfolio of David Lubofsky"}, "nodes": nodes}
def home_spec():
    nodes = [HEADER, {"section": "hero.home", "content": {"headline": "UX, Strategy, Design, and Development", "scrollCue": "Scroll to view my work", "videoCallout": "Get to know me a bit better", "video": {"role": "person.intro-video", "src": "/intro-short.mp4"}}, "motion": M("hero.home")},
             {"section": "content.case-index-intro", "content": {"annotation": "Web experiences and products I’ve been lucky enough to help build."}, "motion": M("content.case-index-intro")}]
    for i, fc in enumerate(HOME["featuredCases"]):
        tt, h = title_parts(fc["titleFormated"]); ct = {"index": f"{i + 1:02d}", "title": tt, "highlight": h, "description": fc["shortDesc"], "linkLabel": "Check it out", "href": f"/case/{fc['slug']}/", "featuredImage": img(fc["featuredImage"], "case.featured-image")}
        if fc.get("companyLogo"): ct["clientLogo"] = img(fc["companyLogo"], "client.logo")
        nodes.append({"section": "content.case-index-item", "content": ct, "motion": M("content.case-index-item")})
    nodes += [{"section": "conversion.connect", "content": {"lettering": ["Want", "to", "partner", "together"], "video": {"role": "person.intro-video", "src": "/intro-short.mp4"}, "cta": {"label": "Shoot me a message", "href": "mailto:me@davidlubofsky.com"}}, "motion": M("conversion.connect")},
              {"section": "utility.video-modal", "content": {"video": {"role": "person.intro-video", "src": "/videos/intro-full.mp4"}}, "motion": M("utility.video-modal"), "retrievalEligible": False}, FOOTER,
              {"section": "utility.page-transition", "content": {}, "motion": M("utility.page-transition"), "retrievalEligible": False},
              {"section": "utility.preloader", "content": {}, "motion": M("utility.preloader"), "retrievalEligible": False}]
    return {"pageSpecVersion": PAGESPEC_VERSION, "mode": "reference", "template": "template.home", "route": "/", "theme": "dark", "access": "public", "meta": {"title": "DL | The portfolio of David Lubofsky"}, "nodes": nodes}
for sl in CASES: pass
dump("schema/examples/reference.home.pagespec.json", home_spec())
dump("schema/examples/reference.case-study.pagespec.json", case_spec("espn-who-can-break-calvins-record"))
dump("schema/examples/reference.case-study-gated.pagespec.json", case_spec("restricted-work"))
# every real route as a reference spec, used by the adversarial suite's route-coverage control
for r in routes:
    slug = r["path"].split("/")[2] if r["path"] != "/" else None
    dump(f"schema/examples/routes/{'home' if not slug else slug}.pagespec.json", home_spec() if not slug else case_spec(slug))

def norm_words(s): return re.findall(r"[a-z0-9]+", strip(s).lower().replace("’", "'"))
strings = []
def walk(o):
    if isinstance(o, dict): [walk(v) for k, v in o.items() if k not in ("id", "slug", "url", "jpg", "webp", "svg", "password", "videoUrl", "ctaLink", "type")]
    elif isinstance(o, list): [walk(v) for v in o]
    elif isinstance(o, str): strings.append(o)
walk(site)
def walk_copy(o):
    if isinstance(o, dict): [walk_copy(v) for k, v in o.items() if k not in ("section", "variant", "motion", "style", "role", "src", "href", "retrievalEligible", "index")]
    elif isinstance(o, list): [walk_copy(v) for v in o]
    elif isinstance(o, str): strings.append(o)
for ex in sorted((DR / "schema/examples").glob("reference.*.json")): walk_copy([n["content"] for n in json.loads(ex.read_text())["nodes"]])
for p in sorted((PROJ / "src/components").rglob("*.jsx")):
    strings += re.findall(r">\s*([A-Z][^<>{}]{8,}?)\s*<", p.read_text())
    strings += re.findall(r"'([A-Z][^'\n]{12,})'", p.read_text())
shingles, fulls = set(), set()
for s in strings:
    w = norm_words(s)
    if len(w) >= 4: fulls.add(hashlib.sha256(" ".join(w).encode()).hexdigest()[:16])
    for i in range(len(w) - 5): shingles.add(hashlib.sha256(" ".join(w[i:i + 6]).encode()).hexdigest()[:16])
dump("extraction/source-copy-index.json", {"$comment": "Text-free index of the source's copy: sha256[:16] of every normalised 6-word shingle and of every full string of 4+ words. Used by GENERATED_MODE_COPY. Normalisation: strip tags, lowercase, [a-z0-9]+ words, curly apostrophe -> straight.", "shingleSize": 6, "hashLength": 16, "shingles": sorted(shingles), "fullStrings": sorted(fulls), "counts": {"sourceStrings": len(strings), "shingles": len(shingles), "fullStrings": len(fulls)}})


# ---------------------------------------------------------------- measured values
mv_path = DR / "extraction/measured-values.json"
mv = json.loads(mv_path.read_text()) if mv_path.exists() else {}
if args.measure:
    raw = json.loads(Path(args.measure).read_text())
    mv["sectionHeights"] = {"viewport": 1440, "unit": "px", "measuredWith": raw["measuredWith"], "settleMs": raw["settleMs"], "source": "local clone (npm run dev), every route",
        "routes": {p: {"pageHeight": v["1440"]["pageHeight"], "sections": v["1440"]["sections"]} for p, v in raw["routes"].items()}}
    mv["responsiveHeights"] = {"viewports": [768, 390], "routes": {p: {vw: {"pageHeight": v[vw]["pageHeight"], "sectionCount": len(v[vw]["sections"])} for vw in ("768", "390")} for p, v in raw["routes"].items()}}
    mv["histograms"] = {"viewport": 1440, "scope": "all 11 routes, visible elements", "values": raw["histograms"]}
mv["wordBudgets"] = BUDGET
mv["paragraphBudgets"] = PARAS
mv["carousel"] = {"minImages": CAROUSEL_MIN, "maxImages": CAROUSEL_MAX}
mv["citations"] = {
    "routes": [cite("src/lib/router.js", "export function parse(pathname)", 5), cite("src/data/case.js", "export function nextCaseFor(slug)", 6)],
    "sourceStackEvidence": [cite("package.json", '"react"'), cite("package.json", '"gsap"'), cite("package.json", '"matter-js"'), cite("package.json", '"three"'), cite("package.json", '"@rive-app/canvas"')],
    "themeBinding": policy["themeBinding"]["evidence"]["cite"],
    "reducedMotion": "grep -rl prefers-reduced-motion src -> 0 files (no reduced-motion handling in the source)",
}
mv["sourceIdentity"] = {"$comment": "R2 registry: literal patterns, each verified to occur in the real source corpus (src/**/*.jsx + src/data/site.json) at build time.", "patterns": SOURCE_BRAND}
mv_path.write_text(json.dumps(mv, indent=2, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------- manifest (counts recomputed from disk)
def count(globp): return len(list(DR.glob(globp)))
manifest = {"repositoryId": "dl-portfolio-design-repo", "repositoryVersion": REPO_VERSION, "pageSpecVersion": PAGESPEC_VERSION, "allowlistVersion": ALLOWLIST_VERSION,
  "versionFieldNote": "allowlistVersion is machine-checked by verify_all.py against tokens/llm/component-allowlist.json; pageSpecVersion is machine-checked against schema/pagespec.schema.json's const; repositoryVersion is documentation-only.",
  "status": "design-review-pending", "productionApproved": False,
  "category": "portfolio", "categoryEvidence": "single person's personal site: index of their own client case studies, a book link, contact CTA and availability date; no pricing, sign-up, accounts or product UI (src/pages/HomePage.jsx, src/pages/CasePage.jsx)",
  "designPolicy": {"policyId": "n0-design-constraints-common", "policyVersion": "0.1.0", "commonIrVersion": "0.5", "enforcementMode": "hard-and-soft", "domain": "personal-portfolio", "localExtension": "policy/design-policy.json", "contentHash": "sha256:PENDING"},
  "sourceStack": "documentation only: React 18 + Vite 5 SPA; GSAP 3.13 (ScrollTrigger, SplitText, Flip, DrawSVG, CustomEase); matter-js 0.18 physics; Rive canvas runtime; three.js footer model. Original site: Nuxt 2 + DatoCMS. Nothing in contracts depends on this.",
  "defaultTheme": "light", "schemaValidatedThemes": ["light", "dark"],
  "counts": {"sections": count("sections/*.json"), "templates": len(TEMPLATES), "routes": len(routes), "primitives": count("primitives/*.json"), "components": count("components/*.json"),
             "assetRoles": len(ASSET_ROLES), "colorTokens": len(color), "typeStyles": len(TYPE_SCALE), "spacingTokens": len(spacing), "motionPatterns": len(motion_patterns), "graphRules": len(graph["rules"]),
             "exampleSpecs": count("schema/examples/*.json"), "routeSpecs": count("schema/examples/routes/*.json")},
  "entryPoints": {"readme": "README.md", "changelog": "CHANGELOG.md", "schema": "schema/pagespec.schema.json", "sectionContractSchema": "schema/section-contract.schema.json",
    "semanticValidator": "schema/semantic_validate.py", "adversarialTests": "schema/tests/adversarial_test.py", "templates": "templates/templates.json", "routes": "templates/routes.json",
    "compatibilityGraph": "compatibility/graph.json", "assetRoles": "assets/asset-roles.json", "allowlist": "tokens/llm/component-allowlist.json", "tokenCatalog": "tokens/llm/token-catalog.json",
    "tokenPolicy": "tokens/llm/token-policy.json", "motionPatterns": "tokens/00-foundation/motion-patterns.json", "measuredValues": "extraction/measured-values.json",
    "verifyAll": "extraction/verify_all.py", "wrapperGate": "extraction/wrapper_gate.py", "proveDrift": "extraction/prove_drift.py", "policy": "policy/design-policy.json", "policyHash": "extraction/policy_hash.py",
    "sourceCopyIndex": "extraction/source-copy-index.json", "parityResults": "extraction/parity-results.json"}}
prev = DR / "registry.manifest.json"
if prev.exists():
    old = json.loads(prev.read_text()); manifest["designPolicy"]["contentHash"] = old.get("designPolicy", {}).get("contentHash", "sha256:PENDING")
dump("registry.manifest.json", manifest)
print("built:", {k: v for k, v in manifest["counts"].items()})
