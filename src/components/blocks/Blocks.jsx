import { useEffect, useRef } from 'react';
import gsap from '../../lib/gsap';
import { bus, app, lerp } from '../../lib/bus';
import LazyPicture from '../LazyPicture';
import { PERIOD_SVG, SMALL_SHAPES } from '../../data/case';
import { ScrollTrigger } from '../../lib/gsap';

const withPeriod = (t) => (t ? `${t}&#8288;${PERIOD_SVG}` : '');


export function MediaText({ block }) {
  if (!block) return null;
  return (
    <section className="media-text relative flex flex-col s:flex-row pb-75 s:pb-150 s:pr-44 site-max">
      {block.image && (
        <LazyPicture image={block.image} className="w-full relative s:max-w-1/2 l:max-w-[60rem] bg-gray-fill" />
      )}
      <div className="flex flex-col items-start w-full s:max-w-1/2 l:max-w-[51.3rem] mt-30 s:mt-0 s:ml-99 l:ml-180 px-24 s:px-0">
        <h2 className="title-2 ml-[-0.035em] js-has-underline" dangerouslySetInnerHTML={{ __html: withPeriod(block.title) }} />
        <div className="media-text__text txt mt-30 s:mt-40 js-has-underline" dangerouslySetInnerHTML={{ __html: block.text }} />
        {block.ctaLabel && (
          <a className="media-text__cta uline leading-none ls-1 mt-30" href={block.ctaLink} target="_blank" rel="noreferrer">
            {block.ctaLabel}
          </a>
        )}
      </div>
    </section>
  );
}

export function TitleText({ block }) {
  return (
    <div className="content px-24 s:px-44 l:pl-[17.3rem] l:pr-0 flex flex-col s:flex-row pb-75 s:pb-150 site-max">
      {block.title && (
        <h3
          className="title-2 w-full s:max-w-1/2 l:max-w-[50.9rem] js-has-underline"
          dangerouslySetInnerHTML={{ __html: withPeriod(block.title) }}
        />
      )}
      {block.text && (
        <div
          className="content__text m:ml-97 w-full s:max-w-1/2 l:max-w-[50.9rem] s:pt-5 mt-30 s:mt-0 js-has-underline"
          dangerouslySetInnerHTML={{ __html: block.text }}
        />
      )}
    </div>
  );
}

export function TextBlock({ block }) {
  if (!block.text) return null;
  const title = withPeriod(block.text.replace(/<\/?(p|strong)>/g, ''));
  return (
    <div className="title-text px-24 s:pl-[17.3rem] s:pr-0 flex flex-col pb-40 s:pb-60 last:pb-0 site-max">
      <div className="w-full flex flex-col items-start s:max-w-[50.9rem]">
        {block.index && (
          <div className="relative mb-30">
            {block.index}
            <div
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
              dangerouslySetInnerHTML={{ __html: SMALL_SHAPES[0] }}
            />
          </div>
        )}
        {block.bigText ? (
          <h3 className="title-2 w-full s:max-w-[50.9rem] js-has-underline" dangerouslySetInnerHTML={{ __html: title }} />
        ) : (
          <div className="title-text__text js-has-underline" dangerouslySetInnerHTML={{ __html: block.text }} />
        )}
      </div>
    </div>
  );
}

// Muted looping video, plays only while on screen (module 373).
export function BlockVideo({ block }) {
  const media = useRef(null);
  useEffect(() => {
    const st = ScrollTrigger.create({
      trigger: media.current.parentElement.parentElement,
      onToggle: (self) => {
        const v = media.current;
        if (!v) return;
        if (self.isActive) v.play().catch(() => {});
        else {
          v.currentTime = 0;
          v.pause();
        }
      },
    });
    return () => st.kill();
  }, []);
  if (!block.videoUrl) return null;
  return (
    <div className="block-media relative pb-75 s:pb-150 last:pb-0 media-cover px-24 s:px-44 m:pl-[17.3rem] l:pl-[31.4rem] l:pr-150 site-max">
      <div className="pt-[56.25%] relative media-cover">
        <video ref={media} src={block.videoUrl} loop muted playsInline />
      </div>
    </div>
  );
}

export function BlockImage({ block }) {
  return (
    <div className="block-media relative pb-75 s:pb-150 last:pb-0 site-max">
      <div className={block.fullWidth ? 'site-gutter' : 'px-24 s:px-44 m:pl-[17.3rem] l:pl-[31.4rem] l:pr-150'}>
        <LazyPicture image={block.image} />
      </div>
    </div>
  );
}

// Light-gray band that starts mid-way through the next block and runs to the
// "next case" section (module 378).
export function GrayStart() {
  const el = useRef(null);
  useEffect(() => {
    const resize = () => {
      const node = el.current;
      const next = node?.nextElementSibling;
      const end = document.querySelector('.js-bg-end');
      if (!next || !end) return;
      const top = next.offsetTop + next.getBoundingClientRect().height / 2;
      gsap.set(node, { top, height: end.offsetTop - top });
    };
    resize();
    // Images are lazy: recompute once they settle, and on resize.
    const ro = new ResizeObserver(resize);
    ro.observe(document.body);
    const off = bus.on('resize-reset', resize);
    return () => {
      ro.disconnect();
      off();
    };
  }, []);
  return (
    <div
      ref={el}
      className="absolute left-0 w-full pointer-events-none !max-w-[100%] bg-gray-case/20 -z-1 site-max"
    />
  );
}

// Drag-to-scroll carousel with lerped motion (module 376). Touch devices get native
// snap scrolling instead.
export function Carousel({ block }) {
  if (!block?.images) return null;
  return <CarouselInner block={block} />;
}

function CarouselInner({ block }) {
  const carousel = useRef(null);
  const draggable = useRef(null);
  const hasMouse = app.hasMouse;

  useEffect(() => {
    if (!hasMouse) return;
    const s = { active: false, cancelX: 0, cancelY: 0, on: 0, target: 0, current: 0, speed: 2.5, max: 0 };
    const transform = () => {
      draggable.current.style.transform = `translate3d(${-s.current}px, 0, 0)`;
    };
    const clamp = () => {
      s.target = Math.max(0, Math.min(s.target, s.max));
    };
    const resize = () => {
      const t = s.target;
      s.current = s.target = 0;
      transform();
      const slides = draggable.current.children;
      const lastRect = slides[slides.length - 1].getBoundingClientRect();
      s.max = Math.max(0, lastRect.right - (window.innerWidth - draggable.current.getBoundingClientRect().left));
      s.current = s.target = t;
      clamp();
      transform();
    };
    const down = (e) => {
      s.active = true;
      s.cancelX = e.clientX;
      s.cancelY = e.clientY;
      s.on = s.target + e.clientX * s.speed;
    };
    const move = (e) => {
      if (!s.active) return;
      if (Math.abs(e.clientX - s.cancelX) > Math.abs(e.clientY - s.cancelY) && e.cancelable) {
        e.preventDefault();
        e.stopPropagation();
      }
      s.target = s.on - e.clientX * s.speed;
      clamp();
    };
    const up = () => {
      s.active = false;
    };
    const tick = ({ ratio }) => {
      if (Math.abs(s.target - s.current) < 0.01) return;
      s.current = lerp(s.current, s.target, 0.1 * ratio);
      transform();
    };
    resize();
    const c = carousel.current;
    c.addEventListener('mousemove', move);
    c.addEventListener('mousedown', down);
    window.addEventListener('mouseup', up);
    const offs = [bus.on('resize-reset', resize), bus.on('tick', tick)];
    return () => {
      c.removeEventListener('mousemove', move);
      c.removeEventListener('mousedown', down);
      window.removeEventListener('mouseup', up);
      offs.forEach((f) => f());
    };
  }, [hasMouse]);

  return (
    <div className="carousel extend relative overflow-hidden site-max">
      <div ref={carousel} className={`carousel__content relative site-max pb-75 s:pb-150 select-none ${hasMouse ? 'site-gutter' : ''}`}>
        <div
          ref={draggable}
          className={`flex items-start ${!hasMouse ? 'touch-scroll px-24 s:pl-[4.14rem] s:pr-44' : ''}`}
          style={{ transform: 'translate3d(0px, 0px, 0px)' }}
        >
          {block.images.map((image, i) => (
            <LazyPicture key={i} image={image} className="carousel-slide mr-24 s:mr-30" />
          ))}
        </div>
      </div>
    </div>
  );
}

const MAP = {
  case_media_text: MediaText,
  case_title_text: TitleText,
  case_text: TextBlock,
  case_image: BlockImage,
  case_video: BlockVideo,
  case_gray_start: GrayStart,
  case_carousel: Carousel,
};

export default function CaseBlock({ data }) {
  const C = MAP[data.type];
  return C ? <C block={data} /> : null;
}
