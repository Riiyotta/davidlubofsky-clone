// Tiny event bus mirroring the original Nuxt `$nuxt.$emit/$on` events
// ("tick", "scroll", "start-shapes", "resize", "resize-reset").
const handlers = new Map();

export const bus = {
  on(name, fn) {
    if (!handlers.has(name)) handlers.set(name, new Set());
    handlers.get(name).add(fn);
    return () => bus.off(name, fn);
  },
  off(name, fn) {
    handlers.get(name)?.delete(fn);
  },
  emit(name, payload) {
    handlers.get(name)?.forEach((fn) => fn(payload));
  },
};

// Global app state (the original Vuex `app` store, reduced to what this page needs).
export const app = {
  loaded: false,
  hasMouse:
    typeof window !== 'undefined' &&
    window.matchMedia('(hover: hover) and (pointer: fine)').matches,
  isWindows: typeof navigator !== 'undefined' && /Win/i.test(navigator.platform),
  isFirefox: typeof navigator !== 'undefined' && /firefox/i.test(navigator.userAgent),
  get bounds() {
    const ww = window.innerWidth;
    const wh = window.innerHeight;
    return {
      ww,
      wh,
      small: ww < 650,
      maxScroll: document.documentElement.scrollHeight - wh,
    };
  },
};

export const lerp = (a, b, n) => a * (1 - n) + b * n;
