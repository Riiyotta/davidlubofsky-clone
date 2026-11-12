#!/usr/bin/env python3
"""Score a parity capture (see parity_capture.mjs) per section and write text-free results.

    python3 extraction/parity_score.py <PARITY_OUT dir> [--write]

Per section: similarity = share of pixels (grayscale) whose live/clone difference <= 40,
over every captured frame row that overlaps the section. Gate: every section >= 0.80 and
report the average. Sections below the gate are listed as exceptions with the measured
score, the diagnosed cause and status "pending human approval" (approvedBy: null) — an
agent never approves its own exception. Requires Pillow.
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
GATE, THRESH, VH = 0.80, 40, 900
# Diagnosed, evidence-backed causes for sections that cannot be frozen identically.
KNOWN_CAUSES = {
    "hero.case": "Matter.js physics bodies get Math.random() angular velocity on every load (src/components/ShapesHeroCase.jsx) on BOTH sides; shape and photo positions differ per load by design.",
    "hero.home": "Matter.js physics bodies (incl. the falling video card) settle differently per load and per frame timing on both sides (src/components/home/ShapesHeroHome.jsx).",
    "navigation.next-case": "Falling lettered words get Math.random() angular velocity (src/components/ShapesNext.jsx); landing positions differ per load on both sides.",
    "conversion.connect": "Falling words settle at frame-timing-dependent positions; the trigger fires at a slightly different scroll moment on each side (src/components/home/ShapesConnect.jsx).",
    "shell.footer": "3D mascot pose depends on accumulated wheel input and cursor position (src/components/TheLama.jsx); the scrubbed parallax also differs by the scroll path taken.",
}

def score(out):
    cap = json.loads((out / "capture.json").read_text())
    res = {}
    for route, r in cap["routes"].items():
        secs = []
        for i, b in enumerate(r["boxes"]):
            same, total = 0, 0
            for f in r["frames"]:
                y0 = f["scrollY"]["clone"]
                if f["scrollY"]["live"] != y0: continue
                a, z = max(b["top"], y0), min(b["top"] + b["height"], y0 + VH)
                if z <= a: continue
                live = Image.open(out / f"live-{r['slug']}-{f['y']}.png").convert("L").crop((0, a - y0, 1440, z - y0))
                clone = Image.open(out / f"clone-{r['slug']}-{f['y']}.png").convert("L").crop((0, a - y0, 1440, z - y0))
                d = ImageChops.difference(live, clone).point(lambda p: 255 if p > THRESH else 0)
                n = live.size[0] * live.size[1]; diff = d.histogram()[255]
                same += n - diff; total += n
            if total: secs.append({"section": b["id"], "order": i, "score": round(same / total, 4), "pixels": total})
        res[route] = {"pageHeight": r["pageHeight"], "sections": secs}
    return res

if __name__ == "__main__":
    out = Path(sys.argv[1]); res = score(out)
    allsec = [s for r in res.values() for s in r["sections"]]
    avg = round(sum(s["score"] * s["pixels"] for s in allsec) / sum(s["pixels"] for s in allsec), 4)
    below = [(route, s) for route, r in res.items() for s in r["sections"] if s["score"] < GATE]
    for route, r in res.items():
        print(route, " ".join(f"{s['section']}={s['score']:.3f}" for s in r["sections"]))
    print(f"average {avg}; {len(below)} section(s) below {GATE}")
    if "--write" in sys.argv:
        p = ROOT / "extraction/parity-results.json"
        prev = json.loads(p.read_text()) if p.exists() else {}
        runs = prev.get("runs", [])[-1:] + [{"average": avg, "belowGate": len(below), "perSection": {route: {f"{s['order']}:{s['section']}": s["score"] for s in r["sections"]} for route, r in res.items()}}]
        exceptions = [{"route": route, "section": s["section"], "order": s["order"], "score": s["score"], "cause": KNOWN_CAUSES.get(s["section"], "UNDIAGNOSED - investigate live/clone/diff images before treating as an exception"), "status": "pending human approval", "approvedBy": None} for route, s in below]
        doc = {"$comment": "Text-free parity evidence (BASELINE R12). Screenshots are not committed; re-run parity_capture.mjs + parity_score.py to reproduce.",
               "method": {"viewport": [1440, 900], "frameStep": 900, "pixelThreshold": THRESH, "sectionGate": GATE, "capture": "extraction/parity_capture.mjs", "score": "extraction/parity_score.py",
                          "determinism": "fonts.ready + networkidle + 6.5s settle, full scroll pass for lazy images, videos paused at t=0 (seek awaited) before every frame, identical waits both sides, no clicks", "liveSide": "the original site", "cloneSide": "local clone dev server"},
               "summary": {"averageScore": avg, "sections": len(allsec), "sectionsBelowGate": len(below)},
               "routes": res, "runs": runs, "exceptions": exceptions}
        p.write_text(json.dumps(doc, indent=2) + "\n")
