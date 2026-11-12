import { useEffect, useRef } from 'react';
import gsap, { ScrollTrigger } from '../lib/gsap';
import { app } from '../lib/bus';
import TheLama from './TheLama';
import { MAILTO, global } from '../data/case';

// Yellow footer: content parallaxes from -35% to 0 while scrolling in (mouse devices),
// and the header fades out once the footer reaches the viewport centre.
export default function Footer() {
  const el = useRef(null);
  const parallax = useRef(null);
  const year = new Date().getFullYear();

  useEffect(() => {
    const ctx = gsap.context(() => {
      const head = document.querySelector('.js-sh');
      gsap.set(el.current, { alpha: 1 });
      if (app.hasMouse) {
        gsap
          .timeline({ scrollTrigger: { trigger: el.current, start: 'top bottom', end: 'bottom bottom', scrub: true } })
          .fromTo(parallax.current, { yPercent: -35 }, { yPercent: 0, ease: 'none' });
      }
      ScrollTrigger.create({
        trigger: el.current,
        start: 'top center',
        onEnter: () => gsap.to(head, { autoAlpha: 0, duration: 0.35, ease: 'power1' }),
        onLeaveBack: () => gsap.to(head, { autoAlpha: 1, duration: 0.35, ease: 'power1' }),
      });
    });
    return () => ctx.revert();
  }, []);

  return (
    <footer ref={el} className="foot relative overflow-hidden text-black z-2 js-site-foot js-m-fade">
      <div ref={parallax} className="site-max flex relative h-[65rem] s:h-[71rem] has-hover:h-screen has-hover:max-h-[71rem]">
        <TheLama />
        <div className="py-24 s:pt-52 s:pb-30 flex flex-col justify-between w-full relative z-2">
          <div className="site-gutter flex w-full">
            <h2 className="foot__title w-full max-w-[73.6rem] ls-2 whitespace-pre-line">
              {'Putting the\n                    '}
              <span className="title-uline --light">human</span>
              {'\n                    back into\n                    humankind'}
              <span className="foot__heart text-[.62em]">🖤</span>
            </h2>
            <div className="hidden s:flex">
              <p className="foot__avail mr-20 w-[23rem]">
                Next availability:
                <br />
                <strong>{global.available}</strong>
              </p>
              <ul className="foot-social flex-1 pt-5">
                <li className="mb-14">
                  <a href={MAILTO} className="foot-social__link uline --light">Shoot me a message</a>
                </li>
                <li className="mb-14">
                  <a href="https://www.linkedin.com/in/davidalubofsky/" className="foot-social__link uline --light">Connect on LinkedIn</a>
                </li>
                <li>
                  <a href="https://findworkhappiness.com" className="foot-social__link uline --light">Check out my book</a>
                </li>
              </ul>
            </div>
          </div>
          <div className="site-gutter flex justify-between s:justify-start items-end w-full">
            <div aria-hidden="true" className="flex flex-col order-first s:hidden">
              <ul className="foot-social w-full flex-1 flex flex-wrap pt-5">
                <li className="w-1/2 mb-10">
                  <a href={MAILTO} className="foot-social__link uline --light">Email me</a>
                </li>
                <li className="w-1/2 mb-10">
                  <a href="https://www.linkedin.com/in/davidalubofsky/" className="foot-social__link uline --light">LinkedIn</a>
                </li>
                <li className="w-1/2 mb-10">
                  <a href="https://findworkhappiness.com" className="foot-social__link uline --light">My book</a>
                </li>
              </ul>
              <p className="foot__avail s:mr-20 s:w-[23rem] whitespace-nowrap s:whitespace-normal mt-10 mb-1 s:mb-0 s:mt-0">
                Next availability: <br className="hidden s:inline" />
                <strong>{global.available}</strong>
              </p>
            </div>
            <div className="flex-1 s:order-2 hidden s:inline-flex">
              <p className="text-14 mt-40">UX, Strategy, Design, and Dev. 🦙 ©{year} David Lubofsky</p>
            </div>
            <div className="w-full s:max-w-[73.6rem] pb-6 s:pb-0 order-last s:order-1">
              <svg viewBox="0 0 53 43" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-[5.3rem] s:w-[6rem] h-auto ml-auto s:-ml-22">
                <path d="M33.1562 42.0534H52.0014V31.0465L33.1562 42.0534Z" fill="#BBBBBB" />
                <path d="M32.7944 0H19.3809V42H32.7944V0Z" fill="#161617" />
                <path d="M0.367188 27.5289C0.367188 35.5037 7.35648 41.967 15.9951 42.0093V13.0486C7.35648 13.0861 0.367188 19.5542 0.367188 27.5289Z" fill="white" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
