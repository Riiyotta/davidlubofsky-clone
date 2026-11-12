import { useEffect, useRef } from 'react';
import gsap, { ScrollTrigger } from '../../lib/gsap';
import { Matter, PhysicsLoop, bounds } from '../../lib/physics';
import { bus, app } from '../../lib/bus';
import ButtonMain from '../ButtonMain';
import { ButtonPlay } from './Buttons';
import { MAILTO } from '../../data/case';
import connectSvgs from '../../data/connectSvgs';

// "Want to partner together" (module 456): five words fall as physics bodies around
// the intro video card + "Shoot me a message" button.
export default function ShapesConnect({ modalOpen, className = '' }) {
  const el = useRef(null);
  const canvas = useRef(null);
  const box = useRef(null);
  const flip = useRef(null);
  const vid = useRef(null);
  const circle = useRef(null);
  const api = useRef({});

  useEffect(() => {
    const { Engine, Runner, World, Bodies, Body, Svg } = Matter;
    const paths = [...canvas.current.querySelectorAll('.js-shape')];
    const texts = [...canvas.current.querySelectorAll('.js-text')];
    const b = bounds(el.current);
    const { width: w, height: h, top } = b;
    const engine = Engine.create();
    const runner = Runner.create();
    let shapes;
    const { ww, small: o } = app.bounds;
    const scale = (ww / 1680) * (o ? 2 : 1.25);
    const tick = () =>
      shapes?.forEach((s, i) => {
        const { position: p, angle } = s;
        texts[i].style.transform = `translate3d(${p.x}px, ${p.y}px, 0) translateX(-50%) translateY(50%) rotate(${angle}rad) scale(${scale})`;
      });
    const loop = new PhysicsLoop({ engine, runner, onPaint: tick });

    const shape = (i = 0, x = 1, yMul = 1, av = 0) => {
      const path = paths[i];
      const { height: ph, width: pw } = bounds(path);
      const body = Bodies.fromVertices(w * x, (-ph / 2) * scale * yMul, Svg.pathToVertices(path), { render: { visible: false } }, true);
      gsap.set(texts[i], { height: ph, width: pw });
      Body.scale(body, scale, scale);
      Body.setAngularVelocity(body, av);
      path.remove();
      return body;
    };
    shapes = o
      ? [shape(0, 0.6, 1, -0.014), shape(1, 0.23, 1, 0.07), shape(2, 0.2, 1, -0.04), shape(3, 0.55, 1, 0.015), shape(4, 0.75, 1, -0.31)]
      : [shape(0, 0.235, 1, -0.015), shape(1, 0.2, 1, -0.018), shape(2, 0.38, 1, -0.04), shape(3, 0.75, 1, 0.02), shape(4, 0.615, 1, -0.28)];
    World.add(engine.world, [
      Bodies.rectangle(0, h, 2 * w, 1, { isStatic: true, render: { visible: false } }),
      Bodies.rectangle(0, 0, 1, 2 * h, { isStatic: true, render: { visible: false } }),
      Bodies.rectangle(w, 0, 1, 2 * h, { isStatic: true, render: { visible: false } }),
    ]);
    if (!o) {
      const bb = bounds(box.current);
      World.add(
        engine.world,
        Bodies.rectangle(bb.left + 0.5 * bb.width, bb.top - top + 0.5 * bb.height, bb.width, bb.height, {
          isStatic: true,
          render: { visible: false },
        }),
      );
    }

    let initial = false;
    let active = false;
    let visible = false;
    const tweens = [];
    const animate = (i, delay) =>
      tweens.push(
        gsap.to(texts[i], { alpha: 1, duration: 0.5, ease: 'power1', delay, onStart: () => World.add(engine.world, shapes[i]) }),
      );
    const run = () => {
      loop.start();
      animate(0, 2);
      animate(1, 0.2);
      animate(2, 1);
      animate(3, 1.5);
      animate(4, 3);
    };
    const start = () => {
      if (!initial && visible) {
        initial = active = true;
        run();
      } else if (!active && visible) {
        active = true;
        loop.start();
      }
    };
    const stop = () => {
      if (active) {
        active = false;
        loop.stop();
      }
    };
    const st = ScrollTrigger.create({
      trigger: el.current,
      onToggle: (self) => {
        visible = self.isActive;
        if (visible) {
          vid.current?.play().catch(() => {});
          start();
        } else {
          vid.current?.pause();
          stop();
        }
      },
    });
    api.current = { stop };
    const offClose = bus.on('close-modal', start);
    return () => {
      offClose();
      st.kill();
      tweens.forEach((t) => t.kill());
      loop.destroy();
      World.clear(engine.world);
      Engine.clear(engine);
    };
  }, []);

  const click = (e) => {
    if (modalOpen) return;
    api.current.stop?.();
    bus.emit('open-modal', { flip: flip.current, flipVid: vid.current, flipCircle: circle.current.el, flipFrom: e.currentTarget });
  };

  return (
    <section
      ref={el}
      className={`relative pb-175 mt-75 s:mt-150 pt-125 s:pt-180 mb-5 flex justify-center site-gutter will-change-transform ${className}`}
    >
      <div ref={canvas} className="flex absolue inset-0 text pointer-events-none js-m-fade" dangerouslySetInnerHTML={{ __html: connectSvgs }} />
      <div ref={box} className="flex flex-col items-center">
        <figure
          className={`relative media-fill w-[17.5rem] s:w-[29.5rem] z-2 ${!modalOpen ? 'cursor-pointer' : ''}`}
          style={{ aspectRatio: '300/500' }}
          onClick={click}
          onMouseEnter={() => circle.current?.play()}
        >
          <div ref={flip} className="play-hover absolute inset-0 media-cover rounded-[3rem] overflow-hidden radius-fix z-1">
            <video ref={vid} className="rounded-[3rem]" src="/intro-short.mp4" poster="/intro-short.jpg" preload="none" muted loop playsInline />
            <ButtonPlay ref={circle} className="absolute bottom-[2.5rem] left-1/2 -translate-x-1/2 h-[7rem] w-[7rem]" />
          </div>
        </figure>
        <ButtonMain url={MAILTO} className="mt-25 js-m-fade" />
      </div>
    </section>
  );
}
