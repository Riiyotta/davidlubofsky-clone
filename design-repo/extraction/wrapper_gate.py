#!/usr/bin/env python3
"""Whole-page-wrapper quality gate (BASELINE R9), called from verify_all.py.

Reads measured section heights (extraction/measured-values.json -> sectionHeights, 1440px)
and the section contracts' semantic categories. Thresholds are pinned here in code.

  HERO > 1800px  -> warn;   HERO > 3000px -> error unless whitelisted
  one in-flow section > 50% of its page -> warn; > 60% -> error unless whitelisted
  (pages with < 3 in-flow sections are skipped; fixed/absolute elements take no page height;
   SHELL sections are excluded from the share check)
  missing measurement / wrong viewport / unknown section id -> error
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIEWPORT = 1440
HERO_WARN_PX, HERO_ERROR_PX = 1800, 3000
SHARE_WARN, SHARE_ERROR = 0.50, 0.60
MIN_INFLOW_FOR_SHARE = 3

def run(root=ROOT):
    errors, warns = [], []
    mv = json.loads((root / "extraction/measured-values.json").read_text())
    routes = [r["path"] for r in json.loads((root / "templates/routes.json").read_text())["routes"]]
    cats = {p.stem: json.loads(p.read_text())["semantic"]["category"] for p in (root / "sections").glob("*.json")}
    wl_path = root / "extraction/wrapper-whitelist.json"
    whitelist = json.loads(wl_path.read_text()).get("entries", []) if wl_path.exists() else []
    for w in whitelist:
        if len(w.get("justification", "")) < 30: errors.append(f"whitelist {w.get('route')}::{w.get('section')}: justification < 30 chars")
        if not w.get("reviewedBy"): errors.append(f"whitelist {w.get('route')}::{w.get('section')}: missing reviewedBy")
        elif "agent" in w["reviewedBy"].lower() and "not a human sign-off" not in w["reviewedBy"].lower():
            errors.append(f"whitelist {w.get('route')}::{w.get('section')}: agent attestation must say 'not a human sign-off'")
    wl = {(w.get("route"), w.get("section")): w for w in whitelist}

    sh = mv.get("sectionHeights")
    if not sh: return [f"no sectionHeights in measured-values.json"], warns
    if sh.get("viewport") != VIEWPORT: errors.append(f"sectionHeights measured at {sh.get('viewport')}px, gate requires {VIEWPORT}px")
    for route in routes:
        page = sh.get("routes", {}).get(route)
        if not page: errors.append(f"{route}: missing measurement"); continue
        ph = page["pageHeight"]; secs = page["sections"]
        for s in secs:
            if s["id"] not in cats: errors.append(f"{route}: measured unknown section id {s['id']}")
        inflow = [s for s in secs if s["flow"] == "in-flow" and cats.get(s["id"]) != "SHELL"]
        for s in secs:
            key = (route, s["id"]); w = wl.get(key)
            if cats.get(s["id"]) == "HERO":
                if s["height"] > HERO_ERROR_PX:
                    if not w: errors.append(f"{route}: {s['id']} {s['height']}px > {HERO_ERROR_PX}px")
                    elif s["height"] > w.get("maxHeightPx", 0): errors.append(f"{route}: {s['id']} {s['height']}px exceeds whitelist cap {w.get('maxHeightPx')}")
                    else: warns.append(f"{route}: {s['id']} {s['height']}px (whitelisted)")
                elif s["height"] > HERO_WARN_PX: warns.append(f"{route}: {s['id']} {s['height']}px > {HERO_WARN_PX}px")
        if len(inflow) >= MIN_INFLOW_FOR_SHARE:
            for s in inflow:
                share = s["height"] / ph; w = wl.get((route, s["id"]))
                if share > SHARE_ERROR:
                    if not w: errors.append(f"{route}: {s['id']} holds {share:.0%} of the page")
                    elif s["height"] > w.get("maxHeightPx", 0): errors.append(f"{route}: {s['id']} exceeds whitelist cap")
                    else: warns.append(f"{route}: {s['id']} {share:.0%} (whitelisted)")
                elif share > SHARE_WARN: warns.append(f"{route}: {s['id']} holds {share:.0%} of the page")
    for (route, sec), w in wl.items():
        page = sh.get("routes", {}).get(route, {})
        if not any(s["id"] == sec for s in page.get("sections", [])): errors.append(f"stale whitelist entry {route}::{sec}")
    return errors, warns

if __name__ == "__main__":
    e, w = run()
    for x in w: print("WARN ", x)
    for x in e: print("ERROR", x)
    print(f"wrapper gate: {len(e)} error(s), {len(w)} warning(s)")
    sys.exit(1 if e else 0)
