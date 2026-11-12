# Changelog

## 1.0.0 — initial build

- Built from the React/Vite clone of the portfolio (11 routes) and its measured rendering.
- Tokens: 19 colours (histogram + canvas-only colours cited from source), 19 type styles, 34 spacing
  steps, 4 radii, 4 breakpoints + hover query, easing/duration/scroll motion, 17 motion patterns.
  Elevation is intentionally empty (no shadows in the source).
- 20 section contracts with source/semantic split, `retrievalEligible` (5 runtime utilities
  ineligible, pinned in code), word budgets from observed maxima, motion + reduced-motion fallback,
  structured responsive changes cited to CSS.
- 2 templates (home, case-study incl. the password-gated case), 11 routes mapped once,
  12 graph rules whose ids and severities match the validator.
- PageSpec schema v1.0.0 with required `mode` (reference | generated); semantic validator with
  template cross-check, graph rules, token policy, retrieval/availability pins and
  generated-mode leakage rules (brand, person, CTA, recognition, URL, asset, copy, route).
- 19 asset roles with three-way availability pinned in code, generation-safe substitutes, and
  licensing guidance for a real person's live site.
- Examples: 2 generated (fictional studio), 3 reference, 11 per-route reference specs.
- Verification: verify_all (28 checks), adversarial suite (61 mutations, 18 controls),
  prove_drift (27 drift cases + control), wrapper gate, policy hash.
- Parity measured twice against the live site (0.9731 / 0.9730 average); 5 physics-hero
  exceptions recorded as pending human approval.
- Not verified from a fresh git clone (the project is not a git repository); see README.
