// Site content (generated from the original DatoCMS payloads into site.json — all media paths are local).
import site from './site.json';

export const cases = site.cases;
export const homePage = site.home;
export const global = site.global;

// Order used for "next case": protected cases are skipped (same as the original).
export const caseOrder = site.order;
export function nextCaseFor(slug) {
  const filtered = caseOrder.filter((c) => !c.protected);
  const i = filtered.findIndex((c) => c.slug === slug);
  const next = filtered[i + 1] || filtered[0];
  return cases[next.slug];
}

export const MAILTO = `mailto:me@davidlubofsky.com?subject=${encodeURIComponent("I'd like to discuss partnering together")}`;

export const PERIOD_SVG =
  '<svg class="inline-flex align-baseline w-[.175em] h-auto" viewBox="0 0 17 10" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8.20927 0.5C12.7304 0.500001 16.3946 4.33833 16.4185 9.08242L-3.75149e-07 9.08242C0.021288 4.33832 3.68818 0.5 8.20927 0.5Z" fill="#FFD600"/></svg>';

export const SMALL_SHAPES = [
  '<svg class="h-[3.9rem] w-auto" viewBox="0 0 55 39" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M1.89005 1.50218L32.3421 37.9597L53.7411 20.0857L1.89005 1.50218Z" stroke="#FFDA18" stroke-linecap="round"/></svg>',
  '<svg class="h-[4.5rem] w-auto" viewBox="0 0 48 45" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M9.83269 6.30984C-1.09118 15.2921 -2.07238 32.1461 7.59981 44.0269L47.2704 11.4072C37.4889 -0.383719 20.7566 -2.67247 9.83269 6.30984Z" stroke="#FFDA18" stroke-linecap="round"/></svg>',
  '<svg class="h-[4.6rem] w-auto" viewBox="0 0 48 46" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M11.091 1.18242L0.779297 12.5225L36.2868 44.81L46.5985 33.4699L11.091 1.18242Z" stroke="#FFDA18" stroke-linecap="round"/></svg>',
];
