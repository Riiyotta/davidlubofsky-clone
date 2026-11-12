// Port of the original site's scroll mixin: wheel events are hijacked and the
// window scroll position is lerped toward a target every GSAP tick
// (ease 0.12, wheel multiplier 0.3 on macOS / 0.7 on Windows).
// Touch devices use native scroll and only emit the tick event.
import gsap, { ScrollTrigger } from './gsap';
import { bus, app, lerp } from './bus';

export function initSmoothScroll() {
  const scroll = {
    mouseMulti: app.isWindows ? 0.7 : 0.3,
    firefoxMulti: 20,
    ease: 0.12,
    target: window.scrollY,
    current: window.scrollY,
    still: true,
  };
  gsap.ticker.fps(-1);

  const isMobile = !app.hasMouse;
  const cleanups = [];

  if (isMobile) {
    const tickMobile = (time) =>
      bus.emit('tick', { y: window.scrollY, time, diff: 0, ratio: gsap.ticker.deltaRatio(60) });
    const onScroll = (e) => {
      scroll.target = window.scrollY;
      bus.emit('scroll', { y: scroll.target, dY: 0, oE: e });
    };
    gsap.ticker.add(tickMobile);
    window.addEventListener('scroll', onScroll, false);
    cleanups.push(() => gsap.ticker.remove(tickMobile), () => window.removeEventListener('scroll', onScroll));
  } else {
    const tick = (time) => {
      const ratio = gsap.ticker.deltaRatio(60);
      const diff = scroll.target - scroll.current;
      scroll.still = Math.abs(diff) < 0.05;
      if (!scroll.still) {
        scroll.current = +lerp(scroll.current, scroll.target, scroll.ease * ratio).toFixed(3);
        window.scrollTo(0, scroll.current);
      }
      bus.emit('tick', { y: scroll.current, time, diff, ratio });
    };
    const onWheel = (e) => {
      if (app.locked) return;
      e.preventDefault();
      let dY = e.wheelDeltaY || e.deltaY;
      if (app.isFirefox && e.deltaMode === 1) dY *= scroll.firefoxMulti;
      dY *= scroll.mouseMulti;
      scroll.target -= dY;
      scroll.target = gsap.utils.clamp(0, app.bounds.maxScroll, scroll.target);
      bus.emit('scroll', { y: scroll.target, dY, oE: e });
    };
    // Keyboard / scrollbar scrolling: sync when idle (same as the original).
    const onScroll = () => {
      if (scroll.still) scroll.current = scroll.target = window.scrollY;
    };
    gsap.ticker.add(tick);
    window.addEventListener('wheel', onWheel, { passive: false });
    window.addEventListener('scroll', onScroll, false);
    cleanups.push(
      () => gsap.ticker.remove(tick),
      () => window.removeEventListener('wheel', onWheel),
      () => window.removeEventListener('scroll', onScroll),
    );
  }

  const onResize = () => {
    if (!isMobile) {
      const max = app.bounds.maxScroll;
      scroll.target = gsap.utils.clamp(0, max, scroll.target);
      scroll.current = gsap.utils.clamp(0, max, scroll.current);
      window.scrollTo(0, scroll.current);
    }
    ScrollTrigger.refresh();
    bus.emit('resize-reset');
  };

  const onReset = () => {
    window.scrollTo(0, 0);
    scroll.current = scroll.target = 0;
    ScrollTrigger.refresh();
    bus.emit('resize-reset');
  };

  const onScrollTo = (id = null) => {
    let y = 0;
    if (id) {
      const el = document.getElementById(id);
      if (el) {
        y = el.getBoundingClientRect().top + window.scrollY;
        y -= parseFloat(getComputedStyle(el).scrollMarginTop) || 0;
      }
    }
    if (isMobile) {
      gsap.to(window, { scrollTo: { y }, duration: 1, ease: 'power3.inOut' });
    } else {
      gsap.to(scroll, {
        target: gsap.utils.clamp(0, document.documentElement.scrollHeight - window.innerHeight, y),
        duration: 0.5,
        ease: 'power1.in',
        onUpdate: () => bus.emit('scroll', { y: scroll.target, dY: 0 }),
      });
    }
  };

  cleanups.push(bus.on('resize', onResize), bus.on('scroll-reset', onReset), bus.on('scroll-to', onScrollTo));
  return () => cleanups.forEach((fn) => fn());
}
