import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import { bus } from './lib/bus';
import { initSmoothScroll } from './lib/smoothScroll';
import { bindRouter, currentRoute, enter, installLinkInterceptor } from './lib/router';
import Loader from './components/Loader';
import Header from './components/Header';
import Footer from './components/Footer';
import CasePage from './pages/CasePage';
import HomePage from './pages/HomePage';
import { cases } from './data/case';

function NotFound() {
  return (
    <div className="text-black relative min-h-[100svh] z-2 flex items-center justify-center site-gutter">
      <h1 className="title-2">Page not found</h1>
    </div>
  );
}

export default function App() {
  const [route, setRoute] = useState(() => currentRoute());
  const pageRef = useRef(null);
  const first = useRef(true);

  useLayoutEffect(() => {
    document.documentElement.classList.toggle('is-dark', currentRoute().name === 'index');
    bindRouter({ onChange: (s) => setRoute(s.route), getPageEl: () => pageRef.current });
  }, []);

  // Viewport height var (used by .h-full-screen) + global resize event.
  useEffect(() => {
    const setVh = () => document.documentElement.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);
    setVh();
    let t;
    const onResize = () => {
      setVh();
      clearTimeout(t);
      t = setTimeout(() => bus.emit('resize'), 150);
    };
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  useEffect(() => {
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    window.scrollTo(0, 0);
    const offScroll = initSmoothScroll();
    const offLinks = installLinkInterceptor();
    const onMouse = (e) => bus.emit('mousemove', { x: e.clientX, y: e.clientY });
    window.addEventListener('mousemove', onMouse);
    return () => {
      offScroll();
      offLinks();
      window.removeEventListener('mousemove', onMouse);
    };
  }, []);

  // Page enter (after the new route has mounted).
  useEffect(() => {
    if (first.current) {
      first.current = false;
      return;
    }
    enter();
  }, [route.path]);

  const item = route.name === 'case-slug' ? cases[route.slug] : null;
  let page;
  if (route.name === 'index') page = <HomePage key="/" pageRef={pageRef} />;
  else if (item) page = <CasePage key={route.path} item={item} pageRef={pageRef} />;
  else page = <NotFound key={route.path} />;

  return (
    <div className="relative w-full overflow-hidden">
      <Header />
      {page}
      <Footer key={`foot-${route.path}`} />
      <div className="fixed inset-0 bg-black invisible z-[99] js-mask" />
      <div className="fixed inset-0 pointer-events-none z-[100] js-pe" />
      <Loader />
    </div>
  );
}
