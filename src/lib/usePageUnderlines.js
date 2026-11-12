import { useEffect } from 'react';
import gsap, { ScrollTrigger } from './gsap';

// Page mixin: every <em>/.title-uline inside .js-has-underline gets a random tilt
// (is-p / is-n) and draws its yellow underline once 25% into the viewport.
export default function usePageUnderlines(ref, deps = []) {
  useEffect(() => {
    if (!ref.current) return undefined;
    const ctx = gsap.context(() => {
      const els = [
        ...ref.current.querySelectorAll('.js-has-underline .title-uline'),
        ...ref.current.querySelectorAll('.js-has-underline em'),
      ];
      const dirs = ['is-p', 'is-n'];
      els.forEach((el) => {
        el.classList.add(dirs[Math.floor(Math.random() * 2)]);
        ScrollTrigger.create({ trigger: el, start: 'top bottom-=25%', once: true, toggleClass: 'is-active' });
      });
    }, ref);
    // Lazy images change the layout height: keep trigger positions accurate.
    const refresh = () => ScrollTrigger.refresh();
    const imgs = [...ref.current.querySelectorAll('img')];
    imgs.forEach((img) => img.complete || img.addEventListener('load', refresh, { once: true }));
    return () => {
      imgs.forEach((img) => img.removeEventListener('load', refresh));
      ctx.revert();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
}
