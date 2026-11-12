import { useEffect, useRef } from 'react';
import gsap, { ScrollTrigger } from '../lib/gsap';
import { Matter, PhysicsLoop, bounds } from '../lib/physics';
import { bus, app } from '../lib/bus';

// Hero physics: three SVG paths (triangle, semicircle, bar) become Matter bodies that
// drop into the hero. The semicircle drives a masked <img> "proxy" in the DOM; the
// other two are drawn on the Matter canvas in the case colour. Ported from module 457.
export default function ShapesHeroCase({ color = '#000', image }) {
  const el = useRef(null);
  const proxy = useRef(null);

  useEffect(() => {
    const root = el.current;
    const { Engine, Runner, Render, World, Bodies, Body, Svg } = Matter;
    const b = bounds(root);
    const paths = [...root.querySelectorAll('path')];
    const { width: w, height: h } = b;
    const pixelRatio = Math.min(1.25, window.devicePixelRatio);

    const engine = Engine.create();
    const runner = Runner.create();
    const render = Render.create({
      element: root,
      engine,
      options: { width: w, height: h, wireframes: false, background: 'transparent', pixelRatio },
    });
    render.canvas.classList.add('absolute', 'top-0', 'left-0');

    const { ww, small } = app.bounds;
    const scale = ww / (small ? 800 : 1680);

    const shape = (i = 0, x = 1, yMul = 1, s = 1, av = 0) => {
      const path = paths[i];
      const { height: ph, width: pw } = bounds(path);
      const d = scale * s;
      const body = Bodies.fromVertices(
        w * x,
        -(ph > pw ? ph : pw) * d * yMul,
        Svg.pathToVertices(path),
        { render: { fillStyle: color, strokeStyle: '#fff', lineWidth: 1 } },
        true,
      );
      body.theScale = d;
      Body.scale(body, d, d);
      Body.setAngularVelocity(body, av);
      path.remove();
      return body;
    };

    const shapes = small
      ? [
          shape(0, 0.8, 3, 1, gsap.utils.random(0.3, 0.1)),
          shape(1, 0.5, 1, 1, -gsap.utils.random(0.13, 0.05)),
          shape(2, 0.6, 3, 0.925, gsap.utils.random(0.5, 0.1)),
        ]
      : [
          shape(0, 0.8, 2, 1, gsap.utils.random(0.3, 0.1)),
          shape(1, 0.5, 0.5, 1, -gsap.utils.random(0.13, 0.05)),
          shape(2, 0.6, 2, 1, gsap.utils.random(0.5, 0.1)),
        ];

    World.add(engine.world, [
      Bodies.rectangle(0, h, 4 * w, 1, { isStatic: true, render: { visible: false } }),
      Bodies.rectangle(small ? 0 : 0.25 * w, 0, 1, 4 * h, { isStatic: true, render: { visible: false } }),
      Bodies.rectangle(w, 0, 1, 4 * h, { isStatic: true, render: { visible: false } }),
    ]);

    const tick = () => {
      const s = shapes[1];
      if (!s || !proxy.current) return;
      const { position: p, angle, theScale } = s;
      proxy.current.style.transform = `translate3d(${p.x.toFixed(3)}px, ${p.y.toFixed(3)}px, 0) translateX(-50%) translateY(50%) rotate(${angle.toFixed(3)}rad) scale(${theScale})`;
    };

    const loop = new PhysicsLoop({ engine, runner, render, onPaint: tick });
    let active = true;
    const calls = [];
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
    const add = (i, delay) => calls.push(gsap.delayedCall(delay, () => World.add(engine.world, shapes[i])));
    const run = () => {
      start();
      add(0, 0.6);
      add(1, 0.1);
      add(2, 1.2);
    };

    let off;
    if (app.loaded) run();
    else off = bus.on('start-shapes', run);

    const st = ScrollTrigger.create({
      trigger: root,
      start: 'top bottom',
      end: 'bottom top',
      onToggle: (self) => (self.isActive ? start() : stop()),
    });
    loop.start();

    return () => {
      off?.();
      st.kill();
      calls.forEach((c) => c.kill());
      loop.destroy();
      World.clear(engine.world);
      Engine.clear(engine);
      render.canvas.remove();
    };
  }, [color]);

  return (
    <div ref={el} className="absolute inset-0 z-1">
      <svg viewBox="0 0 1440 800" fill="none" xmlns="http://www.w3.org/2000/svg" className="absolute top-0 left-0 w-full h-full invisible">
        <path d="M0,0l0,473.3h299.8L0,0z" />
        <path d="M0 350h700C700 156.7 543.3 0 350 0S0 156.7 0 350z" />
        <path d="M1075.86 123.593L872.713 0.450867L454.544 690.297L657.689 813.439L1075.86 123.593Z" />
      </svg>
      <div ref={proxy} className="semi-circle-prox absolute left-0 bottom-full h-[350px] w-[700px] will-change-transform z-5">
        <div className="semi-circle-prox__content inset-x-0 absolute media-cover">
          <img src={image.jpg} sizes="700px" alt="" />
        </div>
      </div>
    </div>
  );
}
