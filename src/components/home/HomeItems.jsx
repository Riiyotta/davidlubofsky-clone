import { useEffect, useRef } from 'react';
import gsap, { SplitText } from '../../lib/gsap';
import { bus, app } from '../../lib/bus';
import { SMALL_SHAPES } from '../../data/case';

const PERIOD =
  '<svg class="absolute bottom-[.175em] right-[-.2125em] w-[.1775em] h-auto" viewBox="0 0 17 10" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8.20927 0.5C12.7304 0.500001 16.3946 4.33833 16.4185 9.08242L-3.75149e-07 9.08242C0.021288 4.33832 3.68818 0.5 8.20927 0.5Z" fill="#FFD600"/></svg>';

function titleWithPeriod(t) {
  const words = t.split(' ');
  const last = words.pop();
  return `${words.join(' ')} <span class="relative">${last}${PERIOD}</span>`;
}

// One case in the home list (module 381). On hover devices the featured image is
// revealed through an elliptical mask that follows the cursor; on touch it scrubs
// with scroll.
function HomeItem({ homeCase, index, className }) {
  const el = useRef(null);
  const clip = useRef(null);
  const mask = useRef(null);
  const image = useRef(null);

  useEffect(() => {
    if (!app.hasMouse) {
      gsap.set([mask.current, image.current], { rotation: gsap.utils.wrap([-30, 30]) });
      gsap.set(mask.current, { clipPath: 'ellipse(50% 50% at 50% 100%)' });
      const st = gsap
        .timeline({ defaults: { ease: 'power1.inOut', duration: 0.5 }, scrollTrigger: { trigger: el.current, scrub: 0.1 } })
        .fromTo(clip.current, { yPercent: 12.5 }, { yPercent: -12.5, duration: 1 }, 0)
        .fromTo(clip.current, { scale: 0.5 }, { scale: 1, ease: 'power1' }, 0);
      return () => st.kill();
    }
    let ctx;
    let tl;
    const fns = {};
    const resize = () => {
      const r = el.current.getBoundingClientRect();
      const { left, width, height } = r;
      const top = r.top + window.scrollY;
      const a = { duration: 1, ease: 'expo' };
      ctx?.revert();
      ctx = gsap.context(() => {
        fns.x = gsap.utils.pipe(gsap.utils.mapRange(left, left + width, -50, 25), gsap.quickTo(clip.current, 'xPercent', a));
        fns.y = gsap.utils.pipe(gsap.utils.mapRange(top, top + height, -62.5, -25), gsap.quickTo(clip.current, 'yPercent', a));
        fns.x2 = gsap.utils.pipe(gsap.utils.mapRange(left, left + width, 5, -5), gsap.quickTo(image.current, 'xPercent', a));
        fns.y2 = gsap.utils.pipe(gsap.utils.mapRange(top, top + height, 5, -5), gsap.quickTo(image.current, 'yPercent', a));
        tl = gsap
          .timeline({ paused: true, defaults: { duration: 1, ease: 'snappy' } })
          .set(mask.current, { clipPath: 'ellipse(0% 0% at 50% 100%)', rotation: -22.5 })
          .set(image.current, { rotation: 22.5 })
          .progress(1)
          .progress(0);
      });
    };
    const move = (e) => {
      fns.x?.(e.clientX);
      fns.y?.(e.pageY);
      fns.x2?.(e.clientX);
      fns.y2?.(e.pageY);
    };
    const enter = () => tl?.clear().to(mask.current, { clipPath: 'ellipse(50% 50% at 50% 100%)' }).restart();
    const leave = () => tl?.clear().to(mask.current, { clipPath: 'ellipse(0% 0% at 50% 100%)' }).restart();
    resize();
    const node = el.current;
    node.addEventListener('mousemove', move);
    node.addEventListener('mouseenter', enter);
    node.addEventListener('mouseleave', leave);
    const off = bus.on('resize-reset', resize);
    return () => {
      node.removeEventListener('mousemove', move);
      node.removeEventListener('mouseenter', enter);
      node.removeEventListener('mouseleave', leave);
      off();
      ctx?.revert();
      tl?.kill();
    };
  }, []);

  const img = homeCase.featuredImage;
  const logo = homeCase.companyLogo;
  return (
    <article ref={el} className={`home-item relative max-w-[50rem] ${!app.hasMouse ? 'js-t-fade-device' : ''} ${className}`}>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[115%] pointer-events-none opacity-90 has-hover:opacity-100">
        <div ref={clip} className="home-item__clip pt-[100%] relative" data-image-fall={homeCase.slug}>
          <div
            ref={mask}
            className="home-item__clip-mask absolute inset-0 origin-center overflow-hidden -translate-y-1/2 translate-x-[15%] has-hover:translate-x-0 has-hover:translate-y-0"
          >
            <div ref={image} className="absolute top-[25%] bottom-[-25%] inset-x-[-25%] media-cover">
              <img src={img.jpg} sizes="(min-width: 650px) 60vw, 150vw" loading="lazy" decoding="async" alt="" />
            </div>
          </div>
        </div>
      </div>
      <a href={`/case/${homeCase.slug}/`} className="relative flex flex-col items-start z-2 js-t-fade js-t-fade-device-selected">
        <div className="relative flex min-h-[4.5rem] mb-20">
          <div className="absolute top-0 left-0 h-full flex items-center">
            {String(index + 1).padStart(2, '0')}
            <div
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
              dangerouslySetInnerHTML={{ __html: SMALL_SHAPES[gsap.utils.wrap(0, 3, index)] }}
            />
          </div>
          <figure className="flex ml-60 s:ml-[14.1rem]">
            {logo && (
              <img className="h-[3.8rem] s:h-[4.5rem] w-auto" src={logo.svg || logo.jpg} alt={`${homeCase.company || 'Client'} logo`} />
            )}
          </figure>
        </div>
        <h2
          className="home-item__title ml-[-0.035em] ls-2 max-w-[95%] js-has-underline"
          dangerouslySetInnerHTML={{ __html: titleWithPeriod(homeCase.titleFormated) }}
        />
        <p className="home-item__desc mt-30">{homeCase.shortDesc}</p>
        <span className="home-item__link flex items-center mt-25">
          <span className="uline">Check it out</span>
          <svg className="h-[1rem] w-aut ml-12" viewBox="0 0 18 10" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M13.3223 6.31806L13.3223 3.82019L0.00028801 3.82019L0.0002879 6.31806L13.3223 6.31806Z" fill="#FFD600" />
            <path d="M18 5.08203C18 7.61114 15.7834 9.66093 13.0438 9.67432V0.489746C15.7834 0.501655 18 2.55293 18 5.08203Z" fill="#FFD600" />
          </svg>
        </span>
      </a>
    </article>
  );
}

// The "Web experiences and products I've been lucky enough to help build" list (module 452).
export default function HomeItems({ cases, className = '' }) {
  const paths = useRef(null);
  const p1 = useRef(null);
  const p2 = useRef(null);
  const p3 = useRef(null);
  const lines = useRef(null);

  useEffect(() => {
    let tl;
    let D;
    let e;
    let cancelled = false;
    document.fonts.ready.then(() => {
      if (cancelled) return;
      D = new SplitText(lines.current, { type: 'lines', linesClass: 'overflow-hidden' });
      e = new SplitText(D.lines, { type: 'lines', linesClass: 'line origin-top-left' });
      tl = gsap
        .timeline({
          delay: 0.5,
          onComplete: () => {
            e.revert();
            D.revert();
          },
          scrollTrigger: { trigger: paths.current, start: 'top center' },
        })
        .from([p3.current, p1.current], {
          drawSVG: gsap.utils.wrap(['100% 100%', 0]),
          duration: 1.5,
          stagger: 1.25,
          ease: 'power3.inOut',
        })
        .from(p2.current, { duration: 0.5, scale: 0, ease: 'expo' }, '-=.25')
        .from(e.lines, { yPercent: 100, rotation: 10, duration: 1.5, ease: 'expo', stagger: 0.1 }, 0);
    });
    return () => {
      cancelled = true;
      tl?.scrollTrigger?.kill();
      tl?.kill();
    };
  }, []);

  return (
    <div
      id="work"
      className={`home-items relative w-full px-24 s:px-75 l:px-100 xl:px-0 xl:max-w-[110.6rem] xl:ml-[17.1rem] mt-160 pt-40 js-m-fade ${className}`}
    >
      <div className="absolute top-0 left-[62rem] js-t-fade">
        <svg ref={paths} className="w-[32.7rem] h-[29.4rem]" viewBox="0 0 327 294" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path
            ref={p1}
            d="M188.856 145.079C207.423 182.529 162.202 235.255 118.365 203.706C103.975 191.675 119.55 170.431 135.49 180.01C150 188.73 154.983 210.176 148.077 229.114C132.784 271.047 78.2158 280.385 18.0388 241.994"
            stroke="#FFDA18"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
          <path ref={p2} d="M11.1116 237.691L17.3988 246.024L21.6151 239.82L11.1116 237.691Z" fill="#FFD600" />
          <path
            ref={p3}
            d="M274.291 26.7462C231.497 11.9747 98.7659 -30.0518 79.237 41.4943C75.031 56.9032 77.6288 73.6075 84.0739 88.215C96.1364 115.549 120.68 135.639 147.193 149.417C181.05 167.008 219.395 175.876 257.537 174.932C270.333 174.614 283.302 173.164 295.12 168.253C306.938 163.342 317.579 154.616 322.651 142.866C327.704 131.159 326.771 117.43 321.973 105.605C317.175 93.7796 308.807 83.7173 299.368 75.1402C281.634 59.0716 260.078 47.8163 236.757 42.4487"
            stroke="#FFDA18"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
        </svg>
        <p ref={lines} className="home-items__title absolute top-[3rem] left-[6rem] min-w-[32.1rem] ls-2">
          Web experiences and products I’ve been lucky enough to help build.
        </p>
      </div>
      <div className="w-full">
        {cases.map((c, t) => (
          <HomeItem
            key={c.id}
            homeCase={c}
            index={t}
            className={[t % 2 === 0 ? '' : 's:ml-auto', t !== cases.length - 1 ? 'mb-225 s:mb-100 xl:mb-0' : ''].join(' ')}
          />
        ))}
      </div>
    </div>
  );
}
