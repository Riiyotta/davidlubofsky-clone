import { useEffect, useRef, useState } from 'react';
import gsap from '../lib/gsap';
import { bus, app } from '../lib/bus';

// Intro loader: ring draws, logo parts pop in, then fall away; emits "start-shapes".
// Timeline ported 1:1 from the original layout bundle.
export default function Loader() {
  const [gone, setGone] = useState(false);
  const content = useRef(null);
  const circle = useRef(null);
  const circle1 = useRef(null);
  const circle2 = useRef(null);
  const part1 = useRef(null);
  const part2 = useRef(null);
  const part3 = useRef(null);

  useEffect(() => {
    const t = window.innerHeight / 1.5;
    const fades = document.querySelectorAll('.js-i-fade');
    const tl = gsap
      .timeline({ paused: true, defaults: { duration: 1.5, ease: 'expo.inOut' } })
      .set(content.current, { alpha: 1 })
      .from(circle1.current, { drawSVG: 0, ease: 'power3.inOut' })
      .addLabel('p2')
      .from(part2.current, { scaleY: 0 }, 0)
      .from(part3.current, { scale: 0 }, 0.25)
      .from(part1.current, { scale: 0 }, 0.5)
      .from(circle2.current, { drawSVG: 0, ease: 'power1.inOut' }, 'p2')
      .set(circle.current, { scaleX: -1, rotation: 90 })
      .set(circle1.current, { alpha: 0 })
      .addLabel('p3')
      .to(circle2.current, { drawSVG: 0, duration: 0.75 }, 'p3')
      .to(part1.current, { y: t, rotation: -45, duration: 0.85, ease: 'power3.in' }, 'p3+=.15')
      .to(part3.current, { y: t, rotation: -45, duration: 0.85, ease: 'power3.in' }, 'p3+=.3')
      .to(part2.current, { y: t, rotation: 90, duration: 0.85, ease: 'power3.in' }, 'p3+=.45')
      .add(() => {
        app.loaded = true;
        bus.emit('start-shapes');
      }, '-=0.5')
      .add(() => setGone(true))
      .fromTo(fades, { alpha: 0 }, { alpha: 1, duration: 1, ease: 'power1' });
    tl.play();
    return () => tl.kill();
  }, []);

  if (gone) return null;
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black z-10">
      <div ref={content} className="w-[21rem] h-[21rem] relative flex items-center justify-center opacity-0">
        <svg ref={circle} className="absolute top-0 left-0 w-full h-full -rotate-90" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
          <circle ref={circle1} cx="50" cy="50" r="48" fill="none" stroke="#303133" strokeWidth="0.5" />
          <circle ref={circle2} cx="50" cy="50" r="48" fill="none" stroke="#FFD600" strokeWidth="0.8" />
        </svg>
        <figure className="inline-flex relative w-[8.1rem] h-[6.6rem]">
          <svg ref={part1} className="absolute bottom-0 left-0 w-[2.5rem] h-auto origin-right" viewBox="0 0 25 46" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M0 23.2269C0 35.7373 10.9645 45.8768 24.5164 45.943V0.510742C10.9645 0.56965 0 10.7164 0 23.2269Z" fill="white" />
          </svg>
          <svg ref={part2} className="absolute bottom-0 left-[2.98rem] w-[2.2rem] h-auto origin-bottom" viewBox="0 0 22 66" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21.8706 0.0410156H0.828003V65.9289H21.8706V0.0410156Z" fill="#FFD600" />
          </svg>
          <svg ref={part3} className="absolute bottom-[-0.1rem] right-0 w-[3rem] h-auto origin-bottom-left" viewBox="0 0 30 19" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M0.437439 18.0123H30.0009V0.745117L0.437439 18.0123Z" fill="#BBBBBB" />
          </svg>
        </figure>
      </div>
    </div>
  );
}
