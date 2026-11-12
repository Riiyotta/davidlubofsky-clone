// Minimal client-side router + the original Nuxt page transition (mixin 338), ported 1:1.
//  - home → case:            the hovered case image falls, page fades, white mask wipes down
//  - case → next case:       the "next" semicircle image falls, page + footer fade
//  - anything else:          black mask wipes up, then the new page fades the mask out
import gsap from './gsap';
import { bus, app } from './bus';

export function parse(pathname) {
  const m = pathname.match(/^\/case\/([^/]+)\/?$/);
  if (m) return { name: 'case-slug', slug: m[1], path: `/case/${m[1]}/` };
  return { name: 'index', path: '/' };
}

const $ = (s, root = document) => root.querySelector(s);
const $$ = (s, root = document) => [...root.querySelectorAll(s)];
const rand = (a, b) => Math.floor(Math.random() * (b - a + 1) + a);

const h = gsap.timeline({ paused: true, defaults: { duration: 0.35, ease: 'power1' } });
let flags = { i: false, l: false, r: false };

let busy = false;
let state = { route: parse(window.location.pathname), params: {} };
let setRoute = () => {};
let pageEl = () => null;

export function bindRouter({ onChange, getPageEl }) {
  setRoute = onChange;
  pageEl = getPageEl;
}
export const currentRoute = () => state.route;

function leave(from, to, params, done) {
  const e = pageEl();
  const { hasMouse } = app;
  const r = from.name === 'index' && to.name === 'case-slug';
  const i = from.name === 'case-slug' && to.name === 'index';
  const n = from.name === 'case-slug' && to.name === 'case-slug';
  flags = { r, i, n, toNext: !!params.next };
  const head = $('.js-sh');
  const foot = $('.js-site-foot');
  const pe = $('.js-pe');
  h.clear().set(pe, { pointerEvents: 'auto' });

  if (e && (r || (n && params.next))) {
    const v = n ? $('.js-next-image', e) : $(`[data-image-fall="${to.slug}"]`, e);
    const b = $('.js-t-mask', e);
    let fades = [];
    if (hasMouse || n) fades = $$('.js-t-fade', e);
    else if (v) {
      const w = v.closest('.js-t-fade-device');
      fades = $$('.js-t-fade-device', e).filter((x) => x !== w);
      if (w) fades.push($('.js-t-fade', w));
    }
    if (b) h.set(b, { autoAlpha: 1 });
    if (fades.length) h.to(fades, { alpha: 0, duration: 0.27, ease: 'power1' });
    if (n && foot) h.to(foot, { alpha: 0, duration: 0.27, ease: 'power1' }, 0);
    h.addLabel('out');
    if (v) {
      const { top: g, height: x } = v.getBoundingClientRect();
      h.to(
        v,
        { y: () => window.innerHeight - g + x, duration: 0.7, rotation: `+=${rand(-92, -40)}`, ease: 'power3.in' },
        'out-=.2',
      );
    }
    if (b) {
      h.set(b, { autoAlpha: 1 }, 0)
        .fromTo(b, { yPercent: -100 }, { yPercent: 0, duration: 0.95, ease: 'snappy' }, 'out+=.4')
        .add(() => head?.classList.add('text-black'), 'out+=.5');
    }
  } else {
    const a = $('.js-mask');
    h.set(a, { autoAlpha: 1 }).fromTo(a, { yPercent: 100 }, { yPercent: 0, duration: 1, ease: 'snappy' });
  }
  h.add(() => done(), '+=.1').restart();
}

// Called by the App once the new page has mounted.
export function enter() {
  bus.emit('scroll-reset');
  bus.emit('enter');
  document.documentElement.classList.toggle('is-dark', state.route.name === 'index');
  const pe = $('.js-pe');
  const a = $('.js-mask');
  const head = $('.js-sh');
  h.clear().set(pe, { clearProps: 'pointerEvents' });
  if (flags.i || (flags.n && !flags.toNext)) {
    head?.classList.remove('text-black');
    h.to(a, { autoAlpha: 0, duration: 0.5, ease: 'power1' }, 0.1);
  }
  h.restart();
  busy = false;
}

export function navigate(path, params = {}, { push = true } = {}) {
  const to = parse(path);
  const from = state.route;
  if (busy) return;
  if (to.path === from.path) {
    if (params.scrollTo) bus.emit('scroll-to', params.scrollTo);
    return;
  }
  busy = true;
  leave(from, to, params, () => {
    if (push) history.pushState({}, '', to.path);
    state = { route: to, params };
    setRoute({ ...state });
  });
}

// Intercept same-origin links site-wide.
export function installLinkInterceptor() {
  const onClick = (ev) => {
    if (ev.defaultPrevented || ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
    const a = ev.target.closest?.('a[href]');
    if (!a || a.target === '_blank') return;
    const href = a.getAttribute('href');
    if (!href || !href.startsWith('/')) return;
    ev.preventDefault();
    if (href === '/#work') {
      // Header "My Work" (toWork): scroll on home, otherwise go home then scroll.
      if (state.route.name === 'index') bus.emit('scroll-to', 'work');
      else {
        const off = bus.on('enter', () => {
          off();
          gsap.delayedCall(0.1, () => bus.emit('scroll-to', 'work'));
        });
        navigate('/');
      }
      return;
    }
    navigate(href, { next: a.hasAttribute('data-next'), back: a.hasAttribute('data-back') });
  };
  const onPop = () => navigate(window.location.pathname, {}, { push: false });
  document.addEventListener('click', onClick);
  window.addEventListener('popstate', onPop);
  return () => {
    document.removeEventListener('click', onClick);
    window.removeEventListener('popstate', onPop);
  };
}
