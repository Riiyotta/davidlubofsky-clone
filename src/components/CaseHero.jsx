import { useEffect, useRef, useState } from 'react';
import gsap, { SplitText } from '../lib/gsap';
import ShapesHeroCase from './ShapesHeroCase';

const PERIOD =
  '<svg class="w-[.175em] h-auto" viewBox="0 0 17 10" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8.20927 0.5C12.7304 0.500001 16.3946 4.33833 16.4185 9.08242L-3.75149e-07 9.08242C0.021288 4.33832 3.68818 0.5 8.20927 0.5Z" fill="#FFD600"/></svg>';

// Case hero (module 450): double line-split reveal of title, roles & description
// with the "snappy" ease, then the title underline animates in.
export default function CaseHero({ info }) {
  const title = useRef(null);
  const label = useRef(null);
  const roles = useRef(null);
  const desc = useRef(null);
  // Re-mount physics when the viewport width changes (original "Refresh" wrapper).
  const [shapesKey, setShapesKey] = useState(0);

  useEffect(() => {
    let ww = window.innerWidth;
    const onResize = () => {
      if (window.innerWidth !== ww) {
        ww = window.innerWidth;
        setShapesKey((k) => k + 1);
      }
    };
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  useEffect(() => {
    let linesCache;
    let titleSplits;
    let period;
    let tl;
    let cancelled = false;
    document.fonts.ready.then(() => {
      if (!cancelled) setup();
    });
    function setup() {
    tl = gsap.timeline({
      paused: true,
      defaults: { duration: 1.5, immediateRender: true, ease: 'snappy' },
      onComplete: () => unsplit(),
    });

    const span = document.createElement('span');
    span.classList.add('inline-flex', 'align-baseline', 'ml-[.025em]');
    span.innerHTML = PERIOD;
    period = span;

    titleSplits = [new SplitText(title.current, { type: 'lines', linesClass: 'overflow-hidden' })];
    titleSplits.push(new SplitText(titleSplits[0].lines, { type: 'lines' }));
    const lines = titleSplits[1].lines;
    const last = lines[lines.length - 1];
    last.classList.add('whitespace-nowrap');
    last.appendChild(span);

    linesCache = [roles.current, desc.current].map((node, i) => {
      const l1 = new SplitText(node, { type: 'lines', linesClass: 'overflow-hidden' });
      const l2 = new SplitText(l1.lines, { type: 'lines' });
      return { l1, l2, lines: i === 0 ? [...l2.lines, label.current] : l2.lines };
    });
    const sub = linesCache.flatMap((c) => c.lines);

    tl.from(lines, { yPercent: 100, stagger: 0.15 }, 0)
      .from(sub, { yPercent: 100, stagger: 0.1 }, 1)
      .add(() => title.current.classList.add('is-active'), 1)
      .restart();
    }

    function unsplit() {
      tl?.kill();
      linesCache?.forEach(({ l1, l2 }) => {
        l2.revert();
        l1.revert();
      });
      linesCache = null;
      titleSplits?.reverse().forEach((s) => s.revert());
      titleSplits = null;
      title.current?.append('⁠', period);
    }

    return () => {
      cancelled = true;
      tl?.kill();
    };
  }, []);

  return (
    <div className="case-hero relative flex flex-col justify-between h-screen h-full-screen max-h-[100rem] site-max site-gutter pt-110 s:pt-150 pb-35 z-2">
      <ShapesHeroCase key={shapesKey} color={info.color?.hex} image={info.featuredImage} />
      <div className="relative z-2">
        <h1
          ref={title}
          className="case-hero__title relative max-w-[67.5rem] t-uline ls-2"
          dangerouslySetInnerHTML={{ __html: info.titleFormated }}
        />
        <div className="case-hero__roles flex items-start w-full max-w-[33.9rem] mt-30">
          <div className="case-hero__label w-[7.5rem] s:w-[12.9rem] ls-3 shrink-0 overflow-hidden">
            <div ref={label}>Roles</div>
          </div>
          <p ref={roles} className="flex-1" dangerouslySetInnerHTML={{ __html: info.roles }} />
        </div>
      </div>
      <div className="relative z-2 flex items-end justify-start">
        <div className="w-full hidden s:block max-w-[73.6rem]" />
        <p ref={desc} className="case-hero__desc pr-75 s:pl-0 s:max-w-[55.5rem]">
          {info.shortDesc}
        </p>
      </div>
    </div>
  );
}
