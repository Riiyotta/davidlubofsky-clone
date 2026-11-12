# React/Vite clone of the DL portfolio (src/), routes from src/lib/router.js + src/data/site.json

Source: React/Vite clone of the DL portfolio (src/), routes from src/lib/router.js + src/data/site.json
Status: **measured-from-clone** · production approved: **false**
11 routes · 8 templates · 20 unique sections

> Generated from `ia.json` by `build.mjs`. Edit the JSON, not this file.

## Shape of the site

The largest 3 templates (Case: images + carousel + grey band, Case: video + carousels + images + grey band, Home (dark project index)) account for 6 of 11 routes (55%). The remaining 5 routes span 5 templates.

| template | routes | share |
|---|---:|---:|
| Case: images + carousel + grey band | 3 | 27% |
| Case: video + carousels + images + grey band | 2 | 18% |
| Home (dark project index) | 1 | 9% |
| Case: video + images + grey band | 1 | 9% |
| Case: opening video then numbered images | 1 | 9% |
| Case: numbered images only | 1 | 9% |
| Case: list of image + statement blocks | 1 | 9% |
| Case: password-gated client work | 1 | 9% |

## Page chrome

**1 routes carry chrome = `full · dark`** — Home (dark project index).

**9 routes carry chrome = `full · light`** — Case: images + carousel + grey band, Case: video + carousels + images + grey band, Case: video + images + grey band, Case: opening video then numbered images, Case: numbered images only, Case: list of image + statement blocks.

**1 routes carry chrome = `full · light · gated`** — Case: password-gated client work.

## Sections by reuse

How widely a section is shared determines whether it belongs in a shared
component library or stays local to its page.

| section | category | templates | routes | implementation | scope |
|---|---|---:|---:|---|---|
| `shell.header` | SHELL | 8 | 11 | `src/components/Header.jsx` | Present on all 11 routes. |
| `shell.footer` | SHELL | 8 | 11 | `src/components/Footer.jsx + TheLama.jsx` | Present on all 11 routes. |
| `utility.preloader` | UTILITY | 8 | 11 | `src/components/Loader.jsx` | Mounted on all 11 routes, but only shown on the first load of a session. |
| `utility.page-transition` | UTILITY | 8 | 11 | `src/App.jsx (.js-mask) + src/lib/router.js` | Present on all 11 routes; invisible at rest. |
| `utility.back-button` | UTILITY | 7 | 10 | `src/components/ButtonBack.jsx` | Every case route (10 routes). |
| `hero.case` | HERO | 7 | 10 | `src/components/CaseHero.jsx + ShapesHeroCase.jsx` | Every case route (10 routes). |
| `content.text` | CONTENT | 7 | 10 | `src/components/blocks/Blocks.jsx > TextBlock` | Every case route (10 routes), usually several times per page. |
| `navigation.next-case` | NAVIGATION | 7 | 10 | `src/components/ShapesNext.jsx` | Every case route (10 routes). |
| `content.media-text` | CONTENT | 6 | 9 | `src/components/blocks/Blocks.jsx > MediaText` | 9 case routes (every case except the password-gated one). |
| `media.image` | MEDIA | 6 | 9 | `src/components/blocks/Blocks.jsx > BlockImage` | 9 case routes. |
| `content.title-text` | CONTENT | 5 | 8 | `src/components/blocks/Blocks.jsx > TitleText` | 8 case routes. |
| `layout.gray-band` | LAYOUT | 4 | 7 | `src/components/blocks/Blocks.jsx > GrayStart` | 7 case routes, at most once each. |
| `media.video` | MEDIA | 4 | 5 | `src/components/blocks/Blocks.jsx > BlockVideo` | 5 case routes. |
| `media.carousel` | MEDIA | 2 | 5 | `src/components/blocks/Blocks.jsx > Carousel` | 5 case routes. |
| `utility.video-modal` | UTILITY | 1 | 1 | `src/components/home/IntroModal.jsx` | Home page only (1 route). |
| `utility.password-gate` | UTILITY | 1 | 1 | `src/components/KnockKnock.jsx` | The one password-gated case route. |
| `hero.home` | HERO | 1 | 1 | `src/components/home/HomeHero.jsx + ShapesHeroHome.jsx` | Home page only (1 route). |
| `content.case-index-intro` | INDEX | 1 | 1 | `src/components/home/HomeItems.jsx (annotation)` | Home page only (1 route). |
| `content.case-index-item` | INDEX | 1 | 1 | `src/components/home/HomeItems.jsx > HomeItem` | Home page only (1 route), repeated per project. |
| `conversion.connect` | CONVERSION | 1 | 1 | `src/components/home/ShapesConnect.jsx` | Home page only (1 route). |

**14 shared sections** appear in more than one template and belong in a component library.

**6 single-use sections** appear in exactly one template. Building these
as "reusable" components up front would be speculative — keep them page-local
until a second caller actually appears.

## Templates

### Home (dark project index) — `template.home`

1 route · `/` · chrome: **full · dark**

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.header` | shared ×8 |
| 2 | HERO | `hero.home` | page-local |
| 3 | INDEX | `content.case-index-intro` | page-local |
| 4 | INDEX | `content.case-index-item` | page-local |
| 5 | CONVERSION | `conversion.connect` | page-local |
| 6 | UTILITY | `utility.video-modal` | page-local |
| 7 | SHELL | `shell.footer` | shared ×8 |
| 8 | UTILITY | `utility.page-transition` | shared ×8 |
| 9 | UTILITY | `utility.preloader` | shared ×8 |

### Case: images + carousel + grey band — `template.case-carousel-band`

3 routes · `/case/espn-who-can-break-calvins-record/`, `/case/find-work-happiness/`, `/case/the-search-for-work-happiness-book/` · chrome: **full · light**

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.header` | shared ×8 |
| 2 | HERO | `hero.case` | shared ×7 |
| 3 | CONTENT | `content.media-text` | shared ×6 |
| 4 | CONTENT | `content.title-text` | shared ×5 |
| 5 | MEDIA | `media.carousel` | shared ×2 |
| 6 | CONTENT | `content.text` | shared ×7 |
| 7 | LAYOUT | `layout.gray-band` | shared ×4 |
| 8 | MEDIA | `media.image` | shared ×6 |
| 9 | NAVIGATION | `navigation.next-case` | shared ×7 |
| 10 | UTILITY | `utility.back-button` | shared ×7 |
| 11 | SHELL | `shell.footer` | shared ×8 |
| 12 | UTILITY | `utility.page-transition` | shared ×8 |
| 13 | UTILITY | `utility.preloader` | shared ×8 |

### Case: video + carousels + images + grey band — `template.case-full-mix`

2 routes · `/case/dl-brand/`, `/case/yall-agency/` · chrome: **full · light**

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.header` | shared ×8 |
| 2 | HERO | `hero.case` | shared ×7 |
| 3 | CONTENT | `content.media-text` | shared ×6 |
| 4 | CONTENT | `content.title-text` | shared ×5 |
| 5 | LAYOUT | `layout.gray-band` | shared ×4 |
| 6 | MEDIA | `media.video` | shared ×4 |
| 7 | CONTENT | `content.text` | shared ×7 |
| 8 | MEDIA | `media.carousel` | shared ×2 |
| 9 | MEDIA | `media.image` | shared ×6 |
| 10 | NAVIGATION | `navigation.next-case` | shared ×7 |
| 11 | UTILITY | `utility.back-button` | shared ×7 |
| 12 | SHELL | `shell.footer` | shared ×8 |
| 13 | UTILITY | `utility.page-transition` | shared ×8 |
| 14 | UTILITY | `utility.preloader` | shared ×8 |

### Case: video + images + grey band — `template.case-video-band`

1 route · `/case/understanding-diseases/` · chrome: **full · light**

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.header` | shared ×8 |
| 2 | HERO | `hero.case` | shared ×7 |
| 3 | CONTENT | `content.media-text` | shared ×6 |
| 4 | CONTENT | `content.title-text` | shared ×5 |
| 5 | CONTENT | `content.text` | shared ×7 |
| 6 | LAYOUT | `layout.gray-band` | shared ×4 |
| 7 | MEDIA | `media.video` | shared ×4 |
| 8 | MEDIA | `media.image` | shared ×6 |
| 9 | NAVIGATION | `navigation.next-case` | shared ×7 |
| 10 | UTILITY | `utility.back-button` | shared ×7 |
| 11 | SHELL | `shell.footer` | shared ×8 |
| 12 | UTILITY | `utility.page-transition` | shared ×8 |
| 13 | UTILITY | `utility.preloader` | shared ×8 |

### Case: opening video then numbered images — `template.case-video-images`

1 route · `/case/a-browser-bending-look-at-vision-loss/` · chrome: **full · light**

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.header` | shared ×8 |
| 2 | HERO | `hero.case` | shared ×7 |
| 3 | CONTENT | `content.media-text` | shared ×6 |
| 4 | MEDIA | `media.video` | shared ×4 |
| 5 | CONTENT | `content.title-text` | shared ×5 |
| 6 | CONTENT | `content.text` | shared ×7 |
| 7 | MEDIA | `media.image` | shared ×6 |
| 8 | NAVIGATION | `navigation.next-case` | shared ×7 |
| 9 | UTILITY | `utility.back-button` | shared ×7 |
| 10 | SHELL | `shell.footer` | shared ×8 |
| 11 | UTILITY | `utility.page-transition` | shared ×8 |
| 12 | UTILITY | `utility.preloader` | shared ×8 |

### Case: numbered images only — `template.case-text-images`

1 route · `/case/designing-a-world-full-of-kindness/` · chrome: **full · light**

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.header` | shared ×8 |
| 2 | HERO | `hero.case` | shared ×7 |
| 3 | CONTENT | `content.media-text` | shared ×6 |
| 4 | CONTENT | `content.title-text` | shared ×5 |
| 5 | CONTENT | `content.text` | shared ×7 |
| 6 | MEDIA | `media.image` | shared ×6 |
| 7 | NAVIGATION | `navigation.next-case` | shared ×7 |
| 8 | UTILITY | `utility.back-button` | shared ×7 |
| 9 | SHELL | `shell.footer` | shared ×8 |
| 10 | UTILITY | `utility.page-transition` | shared ×8 |
| 11 | UTILITY | `utility.preloader` | shared ×8 |

### Case: list of image + statement blocks — `template.case-statement-list`

1 route · `/case/speaking-writing-and-features/` · chrome: **full · light**

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.header` | shared ×8 |
| 2 | HERO | `hero.case` | shared ×7 |
| 3 | CONTENT | `content.media-text` | shared ×6 |
| 4 | CONTENT | `content.text` | shared ×7 |
| 5 | NAVIGATION | `navigation.next-case` | shared ×7 |
| 6 | UTILITY | `utility.back-button` | shared ×7 |
| 7 | SHELL | `shell.footer` | shared ×8 |
| 8 | UTILITY | `utility.page-transition` | shared ×8 |
| 9 | UTILITY | `utility.preloader` | shared ×8 |

### Case: password-gated client work — `template.case-gated`

1 route · `/case/restricted-work/` · chrome: **full · light · gated**

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.header` | shared ×8 |
| 2 | UTILITY | `utility.password-gate` | page-local |
| 3 | HERO | `hero.case` | shared ×7 |
| 4 | CONTENT | `content.text` | shared ×7 |
| 5 | MEDIA | `media.image` | shared ×6 |
| 6 | LAYOUT | `layout.gray-band` | shared ×4 |
| 7 | MEDIA | `media.video` | shared ×4 |
| 8 | NAVIGATION | `navigation.next-case` | shared ×7 |
| 9 | UTILITY | `utility.back-button` | shared ×7 |
| 10 | SHELL | `shell.footer` | shared ×8 |
| 11 | UTILITY | `utility.page-transition` | shared ×8 |
| 12 | UTILITY | `utility.preloader` | shared ×8 |

## Section reference

### SHELL

_Site-wide frame present on every route: fixed header and the yellow footer._

**`shell.header`** — Fixed top bar: three-part logo mark and owner name on the left, three underlined text links centred (work, book, LinkedIn), yellow pill CTA with animated arrow on the right; the links fade out after 50px of scroll.

· Present on all 11 routes. · appears on 11 routes · implemented by `src/components/Header.jsx`

**`shell.footer`** — Yellow gradient footer: large statement with a white-underlined word, next-availability date, three contact links, legal line and logo, with a 3D mascot behind; content parallaxes upward as it scrolls in.

· Present on all 11 routes. · appears on 11 routes · implemented by `src/components/Footer.jsx + TheLama.jsx`

### UTILITY

_Runtime UI that is not page content: intro preloader, route-transition masks, modal, floating back control, password gate._

**`utility.preloader`** — Black first-load overlay: a yellow ring draws, the logo's three parts pop in and fall away, then the page's physics start.

· Mounted on all 11 routes, but only shown on the first load of a session. · appears on 11 routes · implemented by `src/components/Loader.jsx`

**`utility.page-transition`** — Full-viewport masks used only while changing route: a black wipe, or (from the home list) a white wipe after the clicked project image falls.

· Present on all 11 routes; invisible at rest. · appears on 11 routes · implemented by `src/App.jsx (.js-mask) + src/lib/router.js`

**`utility.video-modal`** — Dialog that Flip-animates a portrait video card to the centre, with a scrub track, timecode, cursor-following play/pause and a close button.

· Home page only (1 route). · appears on 1 routes · implemented by `src/components/home/IntroModal.jsx`

**`utility.back-button`** — Fixed bottom-left yellow circle with an arrow and a 'back' label linking to the home list; the label hides after the first scroll and the circle shrinks away near the footer.

· Every case route (10 routes). · appears on 10 routes · implemented by `src/components/ButtonBack.jsx`

**`utility.password-gate`** — Centred pill password field with a yellow submit circle and an inline error message, shown before a protected case renders.

· The one password-gated case route. · appears on 1 routes · implemented by `src/components/KnockKnock.jsx`

### HERO

_The page-opening composition (title + physics shapes)._

**`hero.home`** — Dark opener: a discipline statement with a yellow full stop, a scroll cue, dark geometric physics shapes and a falling portrait video card with a hand-drawn 'get to know me' callout.

· Home page only (1 route). · appears on 1 routes · implemented by `src/components/home/HomeHero.jsx + ShapesHeroHome.jsx`

**`hero.case`** — Light opener of a case: very large title with one highlighted word and a yellow full stop, a 'roles' label, a short description, accent-coloured physics shapes and the featured image falling inside a semicircle mask.

· Every case route (10 routes). · appears on 10 routes · implemented by `src/components/CaseHero.jsx + ShapesHeroCase.jsx`

### INDEX

_The home page's list of projects and its hand-drawn introduction._

**`content.case-index-intro`** — Rotated, hand-drawn style note with a looping yellow stroke and arrow that introduces the project list.

· Home page only (1 route). · appears on 1 routes · implemented by `src/components/home/HomeItems.jsx (annotation)`

**`content.case-index-item`** — One project in the home list: a number inside a drawn step shape, optional client logo, large title with a highlighted word, one-line description and a 'check it out' link; the featured image is revealed through an ellipse that follows the cursor. Repeats once per listed project (9 on the live data).

· Home page only (1 route), repeated per project. · appears on 1 routes · implemented by `src/components/home/HomeItems.jsx > HomeItem`

### CONTENT

_Text-led case-study blocks._

**`content.media-text`** — Half-width image on a grey fill beside a display title (highlighted word, yellow full stop), one or two large paragraphs and an optional underlined external link.

· 9 case routes (every case except the password-gated one). · appears on 9 routes · implemented by `src/components/blocks/Blocks.jsx > MediaText`

**`content.title-text`** — Two-column block: display title on the left, up to three body paragraphs with highlighted words (one may be bold) on the right.

· 8 case routes. · appears on 8 routes · implemented by `src/components/blocks/Blocks.jsx > TitleText`

**`content.text`** — Single inset text block in one of three forms: a numbered step (number inside a drawn triangle above a paragraph), a one-line display statement with a yellow full stop, or a plain paragraph.

· Every case route (10 routes), usually several times per page. · appears on 10 routes · implemented by `src/components/blocks/Blocks.jsx > TextBlock`

### MEDIA

_Image-, video- and screen-led case-study blocks._

**`media.image`** — Single image, either inset to the right or full width between the gutters; consecutive images overlap upward slightly.

· 9 case routes. · appears on 9 routes · implemented by `src/components/blocks/Blocks.jsx > BlockImage`

**`media.video`** — Inset 16:9 muted looping video that plays only while it is on screen.

· 5 case routes. · appears on 5 routes · implemented by `src/components/blocks/Blocks.jsx > BlockVideo`

**`media.carousel`** — Full-bleed row of tall phone screens that is dragged sideways with the mouse, or scroll-snapped on touch.

· 5 case routes. · appears on 5 routes · implemented by `src/components/blocks/Blocks.jsx > Carousel`

### LAYOUT

_Out-of-flow background treatments that frame other blocks._

**`layout.gray-band`** — Out-of-flow light grey background band that starts halfway down the block after it and runs to the next-case section.

· 7 case routes, at most once each. · appears on 7 routes · implemented by `src/components/blocks/Blocks.jsx > GrayStart`

### NAVIGATION

_In-page links onward to another case._

**`navigation.next-case`** — White band linking to the next case: small title and pill button top-left while large lettered words and an arrow fall onto a rotated semicircle holding the next case's image.

· Every case route (10 routes). · appears on 10 routes · implemented by `src/components/ShapesNext.jsx`

### CONVERSION

_Invitations to contact the site owner._

**`conversion.connect`** — Large words of an invitation fall as physics bodies around a centred portrait video card, above a yellow pill 'message' button.

· Home page only (1 route). · appears on 1 routes · implemented by `src/components/home/ShapesConnect.jsx`
