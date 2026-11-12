import { useEffect, useRef } from 'react';
import gsap, { ScrollTrigger } from '../../lib/gsap';
import { Matter, PhysicsLoop, bounds } from '../../lib/physics';
import { bus, app } from '../../lib/bus';
import { ButtonPlay } from './Buttons';

const onVideoReady = (v, cb) => {
  if (v.readyState >= 2) cb();
  else {
    v.addEventListener('canplay', cb, { once: true });
    v.addEventListener('error', cb, { once: true });
  }
};

// Home hero physics (module 458): dark triangle, bar and wedge drop in alongside a
// 300×500 video card (shape 3) that you can click to open the intro video modal.
export default function ShapesHeroHome({ modalOpen }) {
  const el = useRef(null);
  const pathsRef = useRef(null);
  const proxy = useRef(null);
  const flip = useRef(null);
  const vid = useRef(null);
  const circle = useRef(null);
  const path1 = useRef(null);
  const path2 = useRef(null);
  const api = useRef({});

  useEffect(() => {
    const { Engine, Runner, Render, World, Bodies, Body, Svg } = Matter;
    const theme = ['#303133', '#161617'];
    const paths = [...pathsRef.current.querySelectorAll('path')];
    const b = bounds(el.current);
    const { width: w, height: h } = b;
    const pixelRatio = Math.min(1.25, window.devicePixelRatio);
    const engine = Engine.create();
    const runner = Runner.create();
    const render = Render.create({
      element: el.current,
      engine,
      options: { width: w, height: h, wireframes: false, background: 'transparent', pixelRatio },
    });
    render.canvas.classList.add('absolute', 'top-0', 'left-0');
    const { ww, small: d } = app.bounds;
    const scale = ww / (d ? 800 : 1680);

    const shape = (i = 0, x = 1, yMul = 1, s = 1, av = 0, visible = true) => {
      const path = paths[i];
      const { height: ph, width: pw } = bounds(path);
      const c = scale * s;
      const body = Bodies.fromVertices(
        w * x,
        -(ph > pw ? ph : pw) * c * yMul,
        Svg.pathToVertices(path),
        { render: { fillStyle: theme[0], strokeStyle: theme[1], lineWidth: 1, visible } },
        true,
      );
      body.theScale = c;
      Body.scale(body, c, c);
      Body.setAngularVelocity(body, av);
      path.remove();
      return body;
    };
    const shapes = [
      shape(0, d ? 0.24 : 0.2, 1, 1.25, -0.1),
      shape(1, d ? 0.2 : 0.4, 1, d ? 0.92 : 1.08, 0.065),
      shape(2, d ? 0.8 : 0.58, 1, 1.15, d ? 0.165 : 0.2),
      shape(3, d ? 0.72 : 0.82, 1, d ? 1.05 : 1, 0.005, false),
    ];
    World.add(engine.world, [
      Bodies.rectangle(0, h, 2 * w, 1, { isStatic: true, render: { visible: false } }),
      Bodies.rectangle(0, 0, 1, 5 * h, { isStatic: true, render: { visible: false } }),
      Bodies.rectangle(w, 0, 1, 5 * h, { isStatic: true, render: { visible: false } }),
    ]);

    const tick = () => {
      const { position: p, angle, theScale } = shapes[3];
      if (!proxy.current) return;
      proxy.current.style.transform = `translate3d(${(p.x - 150).toFixed(3)}px, ${(p.y - 250).toFixed(3)}px, 0) rotate(${angle.toFixed(3)}rad) scale(${theScale})`;
    };
    const loop = new PhysicsLoop({ engine, runner, render, onPaint: tick });
    let active = false;
    let ctl;
    const start = () => {
      if (!active) {
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
    const run = () => {
      start();
      ctl = gsap
        .timeline()
        .set(proxy.current, { alpha: 1 })
        .add(() => World.add(engine.world, shapes[0]), 1)
        .add(() => World.add(engine.world, shapes[1]), 3)
        .add(() => World.add(engine.world, shapes[2]), 2)
        .add(() => World.add(engine.world, shapes[3]), 0.1)
        .addLabel('start', 2.25)
        .from(path1.current, { drawSVG: 0, duration: 1.5, ease: 'power3.inOut' }, 'start')
        .from(path2.current, { duration: 0.5, scale: 0, ease: 'expo' }, '-=.25')
        .from(el.current.querySelectorAll('.js-line'), { yPercent: 100, duration: 1.5, ease: 'expo', stagger: 0.1 }, 'start+=.25');
    };
    const load = () => onVideoReady(vid.current, run);
    let off;
    if (app.loaded) load();
    else off = bus.on('start-shapes', load);

    const st = ScrollTrigger.create({
      trigger: el.current,
      start: 'top bottom',
      end: 'bottom top',
      onToggle: (self) => {
        if (self.isActive) {
          vid.current?.play().catch(() => {});
          start();
        } else {
          vid.current?.pause();
          stop();
        }
      },
    });

    const recolor = (fill, stroke, lineWidth) =>
      shapes.forEach((s) =>
        gsap.to(s.render, { fillStyle: fill, strokeStyle: stroke, lineWidth, duration: 0.35, ease: 'linear', onUpdate: () => loop.invalidate() }),
      );
    api.current = {
      stop,
      open: () => {
        stop();
        recolor(theme[1], theme[0], 2);
      },
      close: () => {
        start();
        recolor(theme[0], theme[1], 1);
      },
    };
    const offClose = bus.on('close-modal', () => api.current.close());
    loop.start();

    return () => {
      off?.();
      offClose();
      st.kill();
      ctl?.kill();
      loop.destroy();
      World.clear(engine.world);
      Engine.clear(engine);
      render.canvas.remove();
    };
  }, []);

  const click = (e) => {
    if (modalOpen) return;
    api.current.open?.();
    bus.emit('open-modal', {
      flip: flip.current,
      flipVid: vid.current,
      flipCircle: circle.current.el,
      flipFrom: e.currentTarget,
    });
  };

  return (
    <div ref={el} className="absolute inset-0 will-change-transform -z-1">
      <svg ref={pathsRef} viewBox="0 0 1440 1080" fill="none" xmlns="http://www.w3.org/2000/svg" className="absolue top-0 left-0 w-full h-full invisible">
        <path d="M255.493 441.706L255.493 810.317L22 810.317L255.493 441.706Z" />
        <path d="M1075.86 123.593L872.713 0.450867L454.544 690.297L657.689 813.439L1075.86 123.593Z" />
        <path d="M234.162 425.297C363.122 523.438 546.951 498.764 645.659 370.475L177.335 14.0717C79.9171 143.342 105.202 327.156 234.162 425.297Z" />
        <path d="M0 0h300v500H0Z" />
      </svg>
      <div
        ref={proxy}
        className="absolute top-0 lef-0 h-[500px] w-[300px] pointer-events-auto opacity-0 z-5"
        onClick={click}
        onMouseEnter={() => circle.current?.play()}
      >
        <div className="absolute right-[90%] top-[-6rem] origin-top-right rotate-[5deg] js-m-fade">
          <svg viewBox="0 0 186 116" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-[18.6rem] h-auto text-yellow">
            <path
              ref={path1}
              className="stroke-current"
              d="M22.0169 114.644C11.2276 102.467 10.1127 85.7701 20.7602 73.6102C25.7936 67.8602 32.215 63.0254 39.6558 61.2827C47.0966 59.5399 55.6277 61.3408 60.7416 67.0123C65.8555 72.6837 66.4337 82.3592 61.0553 87.7886C55.761 93.1365 46.3053 92.8145 40.4638 88.0735C34.6224 83.3324 32.2433 75.2194 33.0938 67.7472C33.9443 60.2751 37.6385 53.3904 42.1422 47.3682C56.2085 28.6286 78.9013 17.0218 102.259 15.0221C125.617 13.0224 149.395 20.2711 168.605 33.6821"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
            <path ref={path2} className="fill-current" d="M174.859 38.9141L169.803 29.7809L164.758 35.3327L174.859 38.9141Z" />
          </svg>
          <div aria-label="Get to know me a bit better" className="media-cta__text text-28 max-w-[15rem] mt-10">
            {['Get to', 'know me a', 'bit better'].map((t) => (
              <div key={t} aria-hidden="true" className="overflow-hidden">
                <div className="js-line">{t}</div>
              </div>
            ))}
          </div>
        </div>
        <div
          ref={flip}
          className={`play-hover absolute inset-0 media-cover rounded-[2.3rem] overflow-hidden origin-top-left radius-fix ${!modalOpen ? 'cursor-pointer' : ''}`}
        >
          <video ref={vid} src="/intro-short.mp4" poster="/intro-short.jpg" muted loop autoPlay playsInline />
          <ButtonPlay
            ref={circle}
            className="absolute bottom-[4rem] left-1/2 -translate-x-1/2 z-2 w-[11rem] h-[11rem] s:h-[7rem] s:w-[7rem]"
          />
        </div>
      </div>
    </div>
  );
}
