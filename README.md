# DL portfolio clone

React + Vite rebuild of the DL portfolio (home page + 10 case studies). Run it with
`npm ci && npm run dev` (port 5191).

## Information architecture

- `ia.json` is the **only hand-edited IA file**.
- `IA.md` and `matrix.csv` are **generated** from it by `build.mjs`. Never edit them by hand.
- After changing `ia.json`, run:

```bash
node validate.mjs && node build.mjs
```

Section ids match the contracts in `design-repo/sections/`, and every section's
`implementedBy` names the component in `src/` that renders it.

### What the data shows

- **11 routes, 8 templates, 20 sections.** 10 of the 11 routes are case studies. They are
  split into 7 templates only because each case uses a different mix of blocks (computed from
  `src/data/site.json`); they share one purpose. The design-repo models them as a single
  `template.case-study` with a free body. That is the better build target: one case page
  with optional blocks, not seven page types.
- **Every case route has the same frame:** `hero.case`, `content.text`, `navigation.next-case`,
  `utility.back-button`, plus the shell (10/10 routes). `content.media-text` and `media.image`
  are on 9/10. The variation is all in optional media: grey band on 7 routes, video on 5,
  carousel on 5.
- **14 sections are shared and 6 are single-use.** All six single-use sections belong to
  either the home page (hero, index intro, index entries, contact invitation, video modal) or
  the one gated case (password gate). Keep them page-local.
- The password-gated case's template lists the blocks shown **after** unlocking. Before
  unlocking, the rendered page is only the header, the gate and the footer.

## Other folders

- `design-repo/` holds the machine-validated design contracts (tokens, section contracts,
  PageSpec schema, validators). See `design-repo/README.md`.
- `DL _ The portfolio of David Lubofsky*` is the saved copy of the original site used as
  reference. Do not ship it.
