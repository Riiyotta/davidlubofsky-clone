import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react';
import gsap from '../../lib/gsap';
import { bus } from '../../lib/bus';
import { createRive, replay } from '../../lib/rive';

// Yellow play circle (module 309).
export const ButtonPlay = forwardRef(function ButtonPlay({ className = '' }, ref) {
  const el = useRef(null);
  const canvas = useRef(null);
  const inst = useRef(null);
  useEffect(() => {
    inst.current = createRive(canvas.current, '/riv/play.riv', 'play-btn');
    return () => inst.current?.cleanup();
  }, []);
  useImperativeHandle(ref, () => ({ el: el.current, play: () => replay(inst.current) }));
  return (
    <div ref={el} className={`z-2 rounded-full flex items-center justify-center ${className}`}>
      <canvas
        ref={canvas}
        aria-label="Open modal"
        width="256"
        height="256"
        className="flex absolute inset-0 w-full h-full bg-yellow rounded-full"
      />
    </div>
  );
});

// Play/pause toggle that follows the cursor inside the modal (module 307).
export const ButtonPlayPause = forwardRef(function ButtonPlayPause({ className = '' }, ref) {
  const canvas = useRef(null);
  const el = useRef(null);
  useEffect(() => {
    let input;
    const inst = createRive(canvas.current, '/riv/play-pause.riv', 'play-pause', {
      stateMachines: 'states',
      autoplay: true,
      onLoad: () => {
        input = inst.stateMachineInputs('states')?.find((i) => i.name === 'switch-play');
        if (input) input.value = false;
      },
    });
    const offs = [
      bus.on('modal-play', () => input && (input.value = false)),
      bus.on('modal-pause', () => input && (input.value = true)),
    ];
    return () => {
      offs.forEach((f) => f());
      inst.cleanup();
    };
  }, []);
  useImperativeHandle(ref, () => el.current);
  return (
    <button ref={el} type="button" className={className}>
      <canvas
        ref={canvas}
        aria-label="Play/Pause"
        width="256"
        height="256"
        className="flex relative h-[7rem] w-[7rem] rounded-full bg-yellow"
      />
    </button>
  );
});

// Modal close (module 308).
export function ButtonClose({ onClick }) {
  const canvas = useRef(null);
  const inst = useRef(null);
  useEffect(() => {
    inst.current = createRive(canvas.current, '/riv/close.riv', 'close');
    return () => inst.current?.cleanup();
  }, []);
  return (
    <button type="button" className="close-hover" onMouseEnter={() => replay(inst.current)} onClick={onClick}>
      <div className="close__circle">
        <canvas
          ref={canvas}
          aria-label="Close modal"
          width="256"
          height="256"
          className="flex relative h-[5.5rem] w-[5.5rem] rounded-full bg-yellow"
        />
      </div>
    </button>
  );
}

// Looping triangle in the "Scroll to view my work" button (module 306).
export function HomeScrollIcon({ fill = '#FFD600', delay = 0 }) {
  const root = useRef(null);
  useEffect(() => {
    const icons = root.current.querySelectorAll('svg');
    const tl = gsap
      .timeline({ repeat: -1, delay, defaults: { duration: 1, ease: 'expo.inOut' } })
      .to(icons, { yPercent: 100 }, 1);
    return () => tl.kill();
  }, [delay]);
  return (
    <div ref={root} className="home-scroll-icon relative overflow-hidden h-[1.4rem] w-[.8rem]">
      {[0, 1].map((k) => (
        <svg key={k} className="absolute left-0 w-full h-full" viewBox="0 0 8 14" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M-9.53674e-07 14L-3.41715e-07 -3.49691e-07L8 0L-9.53674e-07 14Z" fill={fill} />
        </svg>
      ))}
    </div>
  );
}
