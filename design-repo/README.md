# DL portfolio — design-repo

A machine-validated description of what the cloned portfolio **renders and how it behaves**
(tokens, section contracts, page shapes, motion), so an LLM can produce new PageSpecs for a
*different* person or studio without inventing colours, copy budgets or structure, and
without reproducing the source owner's identity, client work or media.

Status: **design-review-pending**, `productionApproved: false`. Policy binding and every
parity exception are awaiting a human decision (see below). Nothing here has been ratified
by the site owner.

## What the source is

- A one-person portfolio: a dark index page and ten light case-study pages, one of them
  password-gated (`templates/routes.json`). Category `portfolio`, bound to the generic common
  policy `n0-design-constraints-common` 0.1.0 with a local extension (`policy/design-policy.json`).
- It is a **real, live site with real client work** (logos, screenshots, videos, the owner's
  own face and voice). Those are evidence for `reference` PageSpecs only. In `generated` mode
  they are blocked by `assets/asset-roles.json` (availability pinned in code) and by the
  `GENERATED_MODE_*` rules in `schema/semantic_validate.py`.
- Source stack (documentation only, see `registry.manifest.json` → `sourceStack`): a React +
  Vite rebuild of a Nuxt/DatoCMS site. No contract depends on it.

## Counts (recomputed from disk by `extraction/verify_all.py`)

| item | count |
|---|---|
| sections | 20 |
| templates | 2 |
| routes | 11 |
| primitives | 10 |
| components | 8 |
| assetRoles | 19 |
| colorTokens | 19 |
| typeStyles | 19 |
| spacingTokens | 34 |
| motionPatterns | 17 |
| graphRules | 12 |
| exampleSpecs | 5 |
| routeSpecs | 11 |

## Layout

```
registry.manifest.json      status, counts, versions, entry points, category + policy binding
tokens/00-foundation/       color, typography, spacing, radius, breakpoint, motion, elevation (empty: no shadows), motion-patterns
tokens/10-semantic/         semantic roles; tokens/themes/{light,dark}.json resolve them
tokens/20-component/, 30-layout/
tokens/llm/                 component-allowlist, token-catalog, token-policy
primitives/  components/    10 primitives, 8 components (each cites its source)
sections/                   20 section contracts (source/semantic split, retrievalEligible, budgets, motion, responsive)
templates/                  templates.json (2 page shapes) + routes.json (11 routes, each mapped once)
compatibility/graph.json    12 rhythm/structure rules; ids identical to the validator's
assets/asset-roles.json     19 roles with reference-only / generation-safe / blocked-for-generation
schema/                     pagespec.schema.json, section-contract.schema.json, semantic_validate.py,
                            examples/ (2 generated + 3 reference + 11 per-route reference specs), tests/adversarial_test.py
policy/design-policy.json   classification, local rules, approval state, content hash
extraction/                 measured-values.json (heights @1440, histograms, budgets, identity registry),
                            source-copy-index.json (text-free hashes), parity-results.json,
                            verify_all.py, wrapper_gate.py, prove_drift.py, policy_hash.py,
                            build_repo.py, measure_sections.mjs, parity_capture.mjs, parity_score.py
```

## PageSpec in one paragraph

`{pageSpecVersion, mode: reference|generated, template, route, theme, access, meta, nodes[]}`.
Each node is `{section, variant?, content, motion{pattern, reducedMotionFallback}, style?, retrievalEligible?}`.
`template.home` is dark: header, hero, annotation, 1+ index entries, contact invitation, footer.
`template.case-study` is light: header, optional password gate, hero, a free body of
media-text / title-text / text / image / video / carousel / one grey band, next-case, back button,
footer. The only per-page token slot is `hero.case.style.accent` (one of eight `color.accent.*`);
spacing, type and radius are fixed by the contracts because the source has no per-instance override.

## Verify

```bash
python3 extraction/verify_all.py          # 28 checks; exit 1 on any FAIL
python3 schema/tests/adversarial_test.py  # every mutation rejected, every control passes
python3 extraction/prove_drift.py         # injects drift into temp copies; every case must be caught
python3 extraction/wrapper_gate.py        # height gate alone
```

Python 3 + `jsonschema` (Draft-07). Parity tooling additionally needs Pillow and a Playwright
install (pointed to with `PLAYWRIGHT_DIR`). Run from a clean install of the clone with
`npm ci && npm run build` (the lockfile is the source of truth; never ship `node_modules`).
Citation checks re-read `../src` when the design-repo sits inside the clone, and degrade to a
WARN when the folder is used standalone.

## Evidence and measurements

- Heights: every route measured at 1440px (plus page heights at 768 / 390) from the running
  clone with `extraction/measure_sections.mjs`. Largest in-flow section: 2569px (16% of its
  page); every hero is 900px; the wrapper gate reports 0 errors and 0 warnings.
- Tokens: computed-style histograms over all 11 routes. Colours only drawn on canvas
  (physics fills, case accents) are cited from source instead.
- Word budgets are observed maxima from the real content, or the word count of the real UI
  literal a field carries. Nothing was guessed.
- Reduced motion: the source has **no** `prefers-reduced-motion` handling (grep: 0 files). The
  `reducedMotionFallback` values are requirements for generated pages, not observed behaviour.

## Parity (live site vs clone, measured, two runs)

| run | average | sections scored | below 0.80 gate |
|---|---|---|---|
| 1 | 0.9731 | 171 | 6 (all `hero.case`) |
| 2 | 0.9730 | 160 | 5 (all `hero.case`) |

Content sections agree between runs within 0.0053 (129 frozen sections). The sections below the
gate are all physics heroes: Matter.js bodies get `Math.random()` angular velocity on every load
on both sides, so the photo and shapes land differently each time. This was diagnosed from the
live / clone / diff images: text, header and layout are identical. They are recorded in
`extraction/parity-results.json` as exceptions with `status: "pending human approval"` and
`approvedBy: null`. Which routes dip below the gate changes from run to run. Screenshots are not
committed; `parity_capture.mjs` + `parity_score.py` reproduce the numbers.

## Not done / needs a human

- **Fresh `git clone` verification was not possible:** the project folder is not a git
  repository. The design-repo was verified in an isolated temp copy instead. When the project is
  put under git, add `design-repo.zip`, `node_modules/`, `dist/`, `.DS_Store`, `__pycache__/` and
  the saved original-site folder to `.gitignore`, then re-run every check from a fresh clone.
- Policy classification (`portfolio`) and binding are `defined-pending-architecture-review`.
- The 5 parity exceptions need a human approver.
- No IR was generated (none requested).
