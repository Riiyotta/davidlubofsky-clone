import { useEffect, useRef } from 'react';
import { bus } from '../lib/bus';
import ButtonMain from './ButtonMain';
import { MAILTO } from '../data/case';

function throttle(fn, wait) {
  let last = 0;
  let timer = null;
  let lastArgs;
  return (...args) => {
    lastArgs = args;
    const now = Date.now();
    const remaining = wait - (now - last);
    if (remaining <= 0) {
      clearTimeout(timer);
      timer = null;
      last = now;
      fn(...lastArgs);
    } else if (!timer) {
      timer = setTimeout(() => {
        last = Date.now();
        timer = null;
        fn(...lastArgs);
      }, remaining);
    }
  };
}

export function Logo() {
  return (
    <a href="/" aria-label="Go to homepage" className="logo flex shrink-0 nuxt-link-active">
      <figure className="relative">
        <svg viewBox="0 0 60 49" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-[4.4rem] s:w-[5.9rem] h-auto">
          <path d="M37.7676 48.2477H59.3014V35.6703L37.7676 48.2477Z" fill="#BBBBBB" />
          <path d="M37.3547 0.194336H22.0273V48.1867H37.3547V0.194336Z" fill="#FFD600" />
          <path
            d="M0.300781 31.6509C0.300781 40.7635 8.28727 48.149 18.1584 48.1972V15.1046C8.28727 15.1475 0.300781 22.5384 0.300781 31.6509Z"
            className="logo__path transition-fill duration-300 ease-out"
          />
        </svg>
      </figure>
    </a>
  );
}

export default function Header() {
  const links = useRef(null);

  useEffect(() => {
    let hidden = false;
    // Nav links fade out once scrolled past 50px (throttled 100ms, as on the original).
    const onScroll = throttle(({ y }) => {
      if (!hidden && y > 50) {
        hidden = true;
        links.current?.classList.add('opacity-0');
      } else if (hidden && y <= 50) {
        hidden = false;
        links.current?.classList.remove('opacity-0');
      }
    }, 100);
    return bus.on('scroll', onScroll);
  }, []);

  return (
    <header className="site-head fixed top-0 left-0 w-full pl-11 pr-12 s:px-20 pt-12 s:pt-30 z-9 will-change-transform js-t-fade js-sh js-m-fade">
      <div className="relative flex items-end w-full s:h-[4.5rem]">
        <Logo />
        <span className="site-head__name hidden s:inline-flex ml-20 -mb-3 transition-color duration-300 ease-out">
          David
          <br />
          Lubofsky
        </span>
        <nav className="site-head__links ml-28 s:ml-0 s:absolute s:top-1/2 s:left-1/2 s:-translate-x-1/2 s:-translate-y-1/2 z-2">
          <ul ref={links} className="flex items-end transition-opacity duration-500 ease-out">
            <li>
              <a href="/#work" className="uline --not-full">
                <span className="site-head__link-text transition-color duration-300 ease-out">My Work</span>
              </a>
            </li>
            <li className="ml-15 s:ml-23">
              <a href="https://findworkhappiness.com" target="_blank" rel="noreferrer" className="uline --not-full">
                <span className="site-head__link-text transition-color duration-300 ease-out">My Book</span>
              </a>
            </li>
            <li className="ml-15 s:ml-23">
              <a
                href="https://www.linkedin.com/in/davidalubofsky/"
                target="_blank"
                rel="noreferrer"
                className="linkedin uline --not-full"
              >
                <span className="site-head__link-text transition-color duration-300 ease-out">in</span>
              </a>
            </li>
          </ul>
        </nav>
        <div className="site-head__cta absolute top-0 s:top-1/2 right-0 s:-translate-y-1/2">
          <ButtonMain label="Let’s work together" url={MAILTO} ariaLabel="Let’s work together" />
        </div>
      </div>
    </header>
  );
}
