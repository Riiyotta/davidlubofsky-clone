import { useEffect, useRef } from 'react';
import gsap, { ScrollTrigger } from '../lib/gsap';
import { createArrow, replay } from '../lib/rive';

// Fixed "Back to cases" button (module 379): pops in, label slides away after the
// first pixel of scroll, circle scales out while the footer is in view.
export default function ButtonBack() {
  const root = useRef(null);
  const canvas = useRef(null);
  const back = useRef(null);
  const inst = useRef(null);

  useEffect(() => {
    inst.current = createArrow(canvas.current);
    const tl = gsap
      .timeline({ defaults: { duration: 1.5, ease: 'expo' } })
      .from(canvas.current, { scale: 0, duration: 1.25 }, 0.8)
      .from(back.current, { yPercent: 100 }, 0.85);

    const ctx = gsap.context(() => {
      ScrollTrigger.create({
        trigger: '.js-site-foot',
        start: 'top-=50% bottom',
        end: 'bottom top',
        onToggle: (self) => {
          self.isActive
            ? tl.clear().to(canvas.current, { scale: 0, duration: 0.5, ease: 'power2.inOut' }, 0).restart()
            : tl.clear().to(canvas.current, { scale: 1, duration: 1 }, 0).restart();
        },
      });
    });

    const mm = gsap.matchMedia();
    mm.add('(min-width: 650px)', () => {
      ScrollTrigger.create({
        trigger: root.current,
        start: 'top+=1 top',
        end: 'top+=2 top',
        onEnter: () => tl.clear().to(back.current, { yPercent: 100, duration: 0.5, ease: 'power2.inOut' }, 0).restart(),
        onEnterBack: () => tl.clear().to(back.current, { yPercent: 0 }, 0).restart(),
      });
    });

    return () => {
      inst.current?.cleanup();
      ctx.kill();
      mm.kill();
      tl.kill();
    };
  }, []);

  return (
    <a
      ref={root}
      href="/"
      data-back=""
      className="back inline-flex items-center ls-2 pointer-events-auto nuxt-link-active"
      onMouseEnter={() => replay(inst.current)}
    >
      <div className="back__circle">
        <canvas
          ref={canvas}
          width="256"
          height="256"
          className="h-[5.5rem] w-[5.5rem] relative bg-yellow rounded-full inline-flex scale-x-[-1]"
        />
      </div>
      <div className="overflow-hidden hidden s:inline-flex ml-13">
        <div ref={back}>Back to cases</div>
      </div>
    </a>
  );
}
