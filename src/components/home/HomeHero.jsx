import { useEffect, useRef, useState } from 'react';
import gsap from '../../lib/gsap';
import { bus, app } from '../../lib/bus';
import ShapesHeroHome from './ShapesHeroHome';
import { HomeScrollIcon } from './Buttons';

const TITLE =
  'UX, Strategy, Design, and Development&nbsp;<svg class="inline-flex align-baseline w-[.175em] h-auto -translate-x-3/4" viewBox="0 0 17 10" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8.20927 0.5C12.7304 0.500001 16.3946 4.33833 16.4185 9.08242L-3.75149e-07 9.08242C0.021288 4.33832 3.68818 0.5 8.20927 0.5Z" fill="#FFD600"/></svg>';

// Home hero (module 380).
export default function HomeHero({ modalOpen }) {
  const title = useRef(null);
  const [shapesKey, setShapesKey] = useState(0);

  useEffect(() => {
    const line = () => gsap.delayedCall(0.62, () => title.current?.classList.add('is-active'));
    if (app.loaded) {
      line();
      return undefined;
    }
    return bus.on('start-shapes', line);
  }, []);

  useEffect(() => {
    let ww = window.innerWidth;
    return bus.on('resize', () => {
      if (window.innerWidth !== ww) {
        ww = window.innerWidth;
        setShapesKey((k) => k + 1);
      }
    });
  }, []);

  return (
    <div className="home-hero relative flex flex-col justify-between h-screen h-full-screen max-h-[100rem] site-gutter pt-110 s:pt-150 pb-40 z-1">
      <ShapesHeroHome key={shapesKey} modalOpen={modalOpen} />
      <div className="flex flex-col items-start js-i-fade js-m-fade">
        <h1 ref={title} className="home-hero__title relative max-w-[70rem] ls-2 t-uline z-2" dangerouslySetInnerHTML={{ __html: TITLE }} />
      </div>
      <button
        type="button"
        className="home-hero__scroll relative inline-flex items-end font-medium fs-1 ls-1 z-2 js-i-fade js-m-fade"
        onClick={() => bus.emit('scroll-to', 'work')}
      >
        <div className="flex flex-col w-[3.7rem]">
          <HomeScrollIcon fill="#ffffff" />
          <HomeScrollIcon delay={0.2} />
        </div>
        <span className="hidden s:inline-flex leading-none">Scroll to view my work</span>
      </button>
    </div>
  );
}
