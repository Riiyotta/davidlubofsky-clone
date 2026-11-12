import { useEffect, useRef, useState } from 'react';
import gsap, { Flip } from '../../lib/gsap';
import { bus } from '../../lib/bus';
import { ButtonClose, ButtonPlayPause } from './Buttons';

// Full intro video modal (module 382). The clicked video card is Flip-animated from
// its spot on the page into the centre; a timeline scrubber + cursor-following
// play/pause button control the full-length video.
export default function IntroModal({ onOpenChange }) {
  const [active, setActive] = useState(false);
  const [time, setTime] = useState(0);
  const payload = useRef(null);
  const s = useRef({ paused: false, hovered: false });
  const targetMedia = useRef(null);
  const vid = useRef(null);
  const track = useRef(null);
  const handle = useRef(null);
  const close = useRef(null);
  const playPause = useRef(null);

  useEffect(
    () =>
      bus.on('open-modal', (p) => {
        payload.current = p;
        onOpenChange(true);
        setActive(true);
      }),
    [onOpenChange],
  );

  // open(): runs once the <aside> has rendered.
  useEffect(() => {
    if (!active) return undefined;
    const st = s.current;
    const { flip, flipVid, flipCircle, flipFrom } = payload.current;
    st.from = flipFrom;
    st.target = flip;
    st.targetVid = flipVid;
    st.targetCircle = flipCircle;
    st.fades = [...document.querySelectorAll('.js-m-fade')];
    st.paused = false;
    st.xSet = gsap.utils.pipe(
      gsap.utils.mapRange(0, 36, 0, track.current.getBoundingClientRect().width),
      gsap.quickSetter(handle.current, 'x', 'px'),
    );
    const state = Flip.getState(flip);
    flip.remove();
    targetMedia.current.appendChild(flip);
    flip.appendChild(vid.current);
    flipVid.pause();
    Flip.from(state, { duration: 1, ease: 'snappy', scale: true })
      .set(vid.current, { alpha: 1 })
      .to(st.fades, { alpha: 0, duration: 0.35, ease: 'power1' }, 0.1)
      .to(flipCircle, { scale: 0, duration: 0.75, ease: 'expo' }, 0.1)
      .from(track.current, { scaleX: 0, duration: 1.25, ease: 'snappy' }, 0.5)
      .add(() => resize(), 0.75)
      .add(() => vid.current?.play().catch(() => {}), 0.25)
      .fromTo([handle.current, close.current], { scale: 0 }, { scale: 1, duration: 1, ease: 'expo' }, 1);

    const tick = () => {
      const t = vid.current?.currentTime || 0;
      setTime(parseInt(t, 10));
      st.xSet(t);
    };
    const off = bus.on('tick', tick);
    st.offTick = off;

    function resize() {
      const e = { duration: 1, ease: 'expo' };
      gsap.set(playPause.current, { x: window.innerWidth / 2, y: window.innerHeight / 2 });
      st.x = gsap.quickTo(playPause.current, 'x', e);
      st.y = gsap.quickTo(playPause.current, 'y', e);
    }
    return () => off();
  }, [active]);

  const doClose = () => {
    const st = s.current;
    const state = Flip.getState(st.target);
    vid.current.remove();
    st.target.remove();
    st.from.appendChild(st.target);
    st.targetVid.play().catch(() => {});
    Flip.from(state, { duration: 1, ease: 'snappy', scale: true, force3D: true })
      .to([close.current, handle.current], {
        scale: 0,
        duration: 0.5,
        ease: 'expo',
        onComplete: () => {
          setActive(false);
          onOpenChange(false);
        },
      }, 0)
      .to(track.current, { scaleX: 0, duration: 0.5, ease: 'expo' }, 0)
      .to(st.fades, { alpha: 1, duration: 0.5, ease: 'power1' }, 0.5)
      .to(st.targetCircle, { scale: 1, duration: 0.75, ease: 'expo' }, 0.5);
    bus.emit('close-modal');
    st.offTick?.();
    st.x = null;
  };

  const toggle = () => {
    const st = s.current;
    if (st.paused) {
      st.paused = false;
      bus.emit('modal-play');
      vid.current.play().catch(() => {});
    } else {
      st.paused = true;
      bus.emit('modal-pause');
      vid.current.pause();
    }
  };

  const btl = useRef(null);
  const move = (e) => {
    const st = s.current;
    if (!st.x) return;
    const t = e.nativeEvent.composedPath().find((n) => n?.hasAttribute?.('data-clickable'));
    if (!btl.current) btl.current = gsap.timeline({ paused: true, defaults: { duration: 0.5, ease: 'expo' } });
    if (!st.hovered && t) {
      st.hovered = true;
      btl.current.clear().to(playPause.current, { scale: 1 }).restart();
    } else if (st.hovered && !t) {
      st.hovered = false;
      btl.current.clear().to(playPause.current, { scale: 0 }).restart();
    }
    st.x(e.clientX);
    st.y(e.clientY);
  };

  if (!active) return null;
  return (
    <aside className="fixed inset-0 z-[99] flex items-center flex-col justify-center items-center" onMouseMove={move}>
      <div
        className="flex items-center justify-center relative portrait:w-full portrait:max-w-[75%] landscape:h-full landscape:max-h-[75vh] cursor-none"
        style={{ aspectRatio: '300/500' }}
        data-clickable=""
        onClick={toggle}
      >
        <div ref={targetMedia} className="absolute inset-0">
          <video
            ref={vid}
            className="absolute top-0 left-0 w-full h-full object-cover opacity-0 oversize"
            src="/videos/intro-full.mp4"
            playsInline
          />
        </div>
      </div>
      <ButtonPlayPause ref={playPause} className="absolute top-[-3.5rem] left-[-3.5rem] z-5 pointer-events-none scale-0" />
      <div className="timeline relative h-[2px] rounded-full w-full max-w-[30rem] mt-30">
        <div ref={track} className="absolute inset-0 bg-gray-modal origin-left" />
        <div ref={handle} className="timeline-handle absolute top-0 left-0 w-0 h-full z-2">
          <div className="timeline-handle__content absolute top-1/2 -translate-y-1/2">
            <svg className="w-[1.3rem] h-auto" viewBox="0 0 13 14" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M9.62605 0.362286C12.7794 2.79554 13.3632 7.32441 10.93 10.4778C8.49672 13.6312 3.96785 14.215 0.814453 11.7817L9.62605 0.362286Z"
                fill="#FFD600"
              />
            </svg>
            <div className="timeline__time absolute top-full left-1/2 -translate-x-1/2 text-center whitespace-nowrap text-yellow will-change-transform pt-5">
              0:{String(time).padStart(2, '0')}
            </div>
          </div>
        </div>
      </div>
      <div ref={close} className="absolute top-0 right-0 p-12 s:p-25 z-5">
        <ButtonClose onClick={doClose} />
      </div>
    </aside>
  );
}
