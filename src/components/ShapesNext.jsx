import { useEffect, useRef } from 'react';
import gsap, { ScrollTrigger } from '../lib/gsap';
import { Matter, PhysicsLoop, bounds } from '../lib/physics';
import { app } from '../lib/bus';
import ButtonMain from './ButtonMain';

// "Next case" section (module 459): the words "View", "next", "brand" and a yellow arrow
// fall as physics bodies onto a static, rotated semicircle that holds the next case image.
export default function ShapesNext({ image, title }) {
  const el = useRef(null);
  const canvas = useRef(null);
  const box = useRef(null);
  const proxy = useRef(null);

  useEffect(() => {
    const { Engine, Runner, World, Bodies, Body, Svg } = Matter;
    const paths = [...canvas.current.querySelectorAll('.js-shape')];
    const texts = [...canvas.current.querySelectorAll('.js-text')];
    const b = bounds(el.current);
    const { width: w, height: h } = b;
    const engine = Engine.create();
    const runner = Runner.create();

    let shapes;
    const tick = () => {
      shapes?.forEach((s, i) => {
        const { position: p, angle, theScale } = s;
        texts[i].style.transform = `translate3d(${p.x}px, ${p.y}px, 0) translateX(-50%) translateY(50%) rotate(${angle}rad) scale(${theScale})`;
      });
    };
    const loop = new PhysicsLoop({ engine, runner, onPaint: tick });

    const { ww, small } = app.bounds;
    const scale = ww / 1680;

    const shape = (i = 0, x = 1, yMul = 1, av = 0) => {
      const path = paths[i];
      const { height: ph, width: pw } = bounds(path);
      const c = scale * (small ? 1.8 : 1.2);
      const body = Bodies.fromVertices(w * x, -ph * c * yMul, Svg.pathToVertices(path), { render: { visible: false } }, true);
      gsap.set(texts[i], { height: ph, width: pw });
      body.theScale = c;
      Body.scale(body, c, c);
      Body.setAngularVelocity(body, av);
      path.remove();
      return body;
    };

    const createBox = (isSmall = false) => {
      const bb = bounds(box.current);
      const r = isSmall ? 1.5 * scale : scale;
      const x = isSmall ? (w / 2) * 0.925 : w / 2;
      const y = isSmall ? (h / 2) * 1.225 : (h / 2) * 0.875;
      const body = Bodies.fromVertices(x, y, Svg.pathToVertices(box.current), { render: { opacity: 0 }, isStatic: true, angle: -0.75 }, true);
      Body.scale(body, r, r);
      gsap.set(proxy.current, {
        height: bb.height * r,
        width: bb.width * r,
        xPercent: -50,
        yPercent: -50,
        top: y,
        left: x,
        rotation: -33,
      });
      return body;
    };

    const lo = 0.035;
    const hi = 0.125;
    shapes = [
      shape(0, 0.1, 1, gsap.utils.random(lo, hi)),
      shape(1, 0.34, 1.5, -gsap.utils.random(lo, hi)),
      shape(2, 0.85, 2.5, gsap.utils.random(lo, hi)),
      shape(3, 0.85, 1, gsap.utils.random(lo, hi)),
    ];
    World.add(engine.world, [
      Bodies.rectangle(0, h, 2 * w, 1, { isStatic: true, render: { visible: false } }),
      Bodies.rectangle(0, 0, 1, 2 * h, { isStatic: true, render: { visible: false } }),
      Bodies.rectangle(w, 0, 1, 2 * h, { isStatic: true, render: { visible: false } }),
      createBox(small),
    ]);

    let initial = false;
    let active = false;
    let visible = false;
    const calls = [];
    const awaken = (i, d) => calls.push(gsap.delayedCall(d, () => World.add(engine.world, shapes[i])));
    const run = () => {
      loop.start();
      awaken(0, 0.5);
      awaken(1, 1);
      awaken(2, 1.5);
      awaken(3, 1);
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
        visible ? start() : stop();
      },
    });

    return () => {
      st.kill();
      calls.forEach((c) => c.kill());
      loop.destroy();
      World.clear(engine.world);
      Engine.clear(engine);
    };
  }, []);

  return (
    <section ref={el} className="next relative bg-white">
      <div className="relative h-[60rem] s:h-[77rem] overflow-hidden js-t-fade">
        <div className="absolute absolute top-0 left-[2.4rem] s:left-[17.3rem] flex flex-col items-start pt-75 s:pt-150 w-full max-w-[30rem] s:max-w-[25rem] z-5">
          <h2 className="next__title">{title}</h2>
          <ButtonMain label="Check it out" light className="mt-20 s:mt-30" />
        </div>
        <div ref={canvas} className="flex absolute inset-x-0 top-0 bottom-[.5rem] text pointer-events-none js-m-fade">
          <svg viewBox="0 0 341 118" fill="none" xmlns="http://www.w3.org/2000/svg" className="absolute bottom-full left-0 js-text z-2">
            <path d="M44.1235 115.728H62.9144L106.328 2.98198H89.6428C65.9922 65.9964 57.8927 84.4633 57.8927 102.606H49.3072C49.3072 84.4633 41.3696 66.1583 17.557 2.98198H0.709961L44.1235 115.728Z" fill="#161617" />
            <path d="M112.119 115.728H127.832V31.9783H112.119V115.728ZM111.471 16.5892H128.48V0.714111H111.471V16.5892Z" fill="#161617" />
            <path d="M179.376 117.833C194.279 117.833 207.238 110.868 215.014 101.148L207.238 91.7529C200.92 99.5284 191.849 105.036 180.024 105.036C165.282 105.036 153.619 95.3167 151.837 78.3077H217.281V73.4479C217.281 47.5294 201.73 30.0344 177.594 30.0344C153.781 30.0344 136.124 48.1774 136.124 73.9339C136.124 100.662 154.429 117.833 179.376 117.833ZM152.161 67.2923C154.267 51.2552 164.472 42.3457 177.918 42.3457C191.363 42.3457 201.406 51.2552 202.378 67.2923H152.161Z" fill="#161617" />
            <path d="M240.108 115.728H261.005C272.506 74.4199 275.422 57.7348 274.936 47.3674H282.874C282.55 58.0588 285.304 74.5819 296.805 115.728H317.702L340.218 31.9783H324.667C313.652 72.314 311.06 86.0832 312.518 100.338L305.066 101.958C305.066 90.295 301.989 76.3638 289.353 31.9783H268.456C255.821 76.3638 252.743 90.295 252.743 101.958L245.454 100.338C246.75 86.5692 244.32 72.8 233.305 31.9783H217.429L240.108 115.728Z" fill="#161617" />
          </svg>
          <svg viewBox="0 0 318 109" fill="none" xmlns="http://www.w3.org/2000/svg" className="absolute bottom-full left-0 js-text z-2">
            <path d="M0.0153809 106H15.7285L15.7285 60.4805C15.7285 42.8235 26.4199 33.4281 39.8651 33.4281C53.4723 33.4281 61.0859 41.2036 61.0859 57.2407L61.0859 106H76.799L76.799 52.219C76.799 32.2941 66.5936 20.3068 46.5067 20.3068C27.8778 20.3068 19.2923 31.8082 15.5665 46.5493L8.27691 42.1756C10.3828 36.8299 13.2986 31.3222 14.9185 22.2507L0.0153809 22.2507L0.0153809 106Z" fill="#161617" />
            <path d="M129.059 108.106C143.962 108.106 156.921 101.14 164.697 91.4207L156.921 82.0253C150.603 89.8008 141.532 95.3085 129.707 95.3085C114.965 95.3085 103.302 85.5891 101.52 68.58L166.964 68.58L166.964 63.7203C166.964 37.8018 151.413 20.3068 127.277 20.3068C103.464 20.3068 85.8072 38.4498 85.8072 64.2063C85.8072 90.9348 104.112 108.106 129.059 108.106ZM101.844 57.5647C103.95 41.5276 114.156 32.6181 127.601 32.6181C141.046 32.6181 151.089 41.5276 152.061 57.5647L101.844 57.5647Z" fill="#161617" />
            <path d="M169.885 106H187.38C203.741 84.2931 207.953 76.6796 207.953 70.2H215.729C215.729 77.6515 219.941 85.2651 236.464 106H253.959L222.694 63.3963L252.825 22.2507L235.33 22.2507C219.779 42.3376 215.729 50.1131 215.729 57.8887L207.953 57.8887C207.953 50.1131 204.065 42.3376 188.514 22.2507L170.857 22.2507L200.664 63.5583L169.885 106Z" fill="#161617" />
            <path d="M297.358 108.106C305.62 108.106 312.909 104.866 317.607 101.302L313.071 90.7728C309.831 93.2026 305.782 95.4705 300.436 95.4705C293.956 95.4705 290.069 92.2307 290.069 83.6452V34.076L315.825 34.076V22.2507L290.069 22.2507V0.219971L274.355 0.219971C274.355 8.4815 277.919 19.9828 283.265 23.3846L279.377 29.0543C273.222 25.6525 266.418 22.2507 258.156 22.2507V34.076L274.355 34.076V85.5891C274.355 100.978 282.779 108.106 297.358 108.106Z" fill="#161617" />
          </svg>
          <svg viewBox="0 0 411 119" fill="none" xmlns="http://www.w3.org/2000/svg" className="absolute bottom-full left-0 js-text z-2">
            <path d="M47.9646 118.106C71.4533 118.106 86.5184 98.343 86.5184 74.2064C86.5184 49.9078 71.4533 30.1449 47.9646 30.1449C30.9556 30.1449 18.6443 43.5901 15.7285 59.1412L8.4389 54.4435C13.4606 41.3223 15.7285 25.6092 15.7285 11.03V0.986572H0.0153809V116H15.0805L15.7285 96.8851C21.3982 109.358 32.7375 118.106 47.9646 118.106ZM15.8905 74.2064C15.8905 57.0353 27.0678 43.1042 43.2669 43.1042C60.4379 43.1042 70.3193 57.0353 70.3193 74.2064C70.3193 91.2154 60.4379 105.309 43.2669 105.309C27.0678 105.309 15.8905 91.2154 15.8905 74.2064Z" fill="#161617" />
            <path d="M94.0333 116H109.908V80.848C109.908 59.9512 121.41 45.534 144.088 45.534V30.3069C121.572 30.3069 112.176 46.6679 109.422 63.839L102.295 59.4652C105.859 51.6897 108.126 42.9422 108.936 32.2508H94.0333V116Z" fill="#161617" />
            <path d="M175.254 118.106C194.693 118.106 207.004 101.583 196.961 83.4398L202.63 80.2C209.92 88.1376 214.132 101.907 216.238 116H229.683V69.3466C229.683 43.9141 212.998 30.1449 189.185 30.1449C175.254 30.1449 160.999 36.3005 152.575 45.534L160.999 54.9295C167.316 47.8019 176.874 42.7802 187.889 42.7802C203.44 42.7802 214.294 52.4996 214.294 69.5086V87.0036C214.294 87.8136 214.294 88.7855 214.456 89.7575C204.574 69.6706 190.805 64.0009 177.684 64.0009C160.351 64.0009 147.553 76.1503 147.553 91.3774C147.553 105.795 158.083 118.106 175.254 118.106ZM162.781 91.2154C162.781 80.848 169.422 73.8824 179.142 73.8824C189.023 73.8824 194.369 81.01 194.369 91.5394C194.369 101.583 188.213 108.386 178.332 108.386C168.612 108.386 162.781 101.583 162.781 91.2154Z" fill="#161617" />
            <path d="M239.591 116H255.304V70.4806C255.304 52.8236 265.995 43.4281 279.44 43.4281C293.048 43.4281 300.661 51.2037 300.661 67.2408V116H316.374V62.2191C316.374 42.2942 306.169 30.3069 286.082 30.3069C267.453 30.3069 258.868 41.8082 255.142 56.5494L247.852 52.1756C249.958 46.8299 252.874 41.3223 254.494 32.2508H239.591V116Z" fill="#161617" />
            <path d="M362.316 118.106C377.544 118.106 388.883 109.358 394.553 97.0471C394.877 103.203 395.2 108.872 395.362 116H410.266V0.986572H394.553V11.03C394.553 25.7711 396.658 41.3223 402.004 54.4435L394.553 59.1412C391.637 43.5901 379.325 30.1449 362.316 30.1449C338.828 30.1449 323.763 49.9078 323.763 74.2064C323.763 98.343 338.828 118.106 362.316 118.106ZM339.962 74.2064C339.962 57.0353 349.843 43.1042 367.176 43.1042C383.213 43.1042 394.391 57.0353 394.391 74.2064C394.391 91.2154 383.213 105.309 367.176 105.309C349.843 105.309 339.962 91.2154 339.962 74.2064Z" fill="#161617" />
          </svg>
          <svg viewBox="0 0 182 93" fill="none" xmlns="http://www.w3.org/2000/svg" className="absolute bottom-full left-0 js-text z-2">
            <path fillRule="evenodd" clipRule="evenodd" d="M131.631 92.6802C159.275 92.545 181.641 71.8623 181.641 46.343C181.641 20.8238 159.275 0.126021 131.631 0.00585938V33.6121L-3.77642e-05 33.6121L-3.88659e-05 58.8161L131.631 58.8161V92.6802Z" fill="#FFD600" />
          </svg>
          <div className="absolute top-0 left-0 flex">
            <svg viewBox="0 0 345 115" fill="none" xmlns="http://www.w3.org/2000/svg" className="min-w-[345px] h-auto invisible">
              <path className="js-shape" d="M0 0H129L344.5 30.5L321.5 115H44.5L0 0Z" fill="none" />
            </svg>
            <svg viewBox="0 0 320 110" fill="none" xmlns="http://www.w3.org/2000/svg" className="min-w-[320px] h-auto invisible">
              <path className="js-shape" d="M0.5 23L291 0L319.5 22.5V110H0.5V23Z" fill="none" />
            </svg>
            <svg viewBox="0 0 415 119" fill="none" xmlns="http://www.w3.org/2000/svg" className="min-w-[415px] h-auto invisible">
              <path className="js-shape" d="M0.5 0L226.5 35.5L414.5 0V119H0.5V0Z" fill="none" />
              <path ref={box} className="js-box" d="M0 350h700C700 156.7 543.3 0 350 0S0 156.7 0 350z" />
            </svg>
            <svg viewBox="0 0 186 96" fill="none" xmlns="http://www.w3.org/2000/svg" className="min-w-[186px] h-auto invisible">
              <path className="js-shape" d="M0.5 33.5L132.5 0L173 17L186 45.5L173 75L132.5 95.5L0.5 60.5V33.5Z" fill="none" />
            </svg>
          </div>
        </div>
      </div>
      <div ref={proxy} className="semi-circle-prox absolute h-[350px] w-[700px] will-change-transform z-5 js-next-image">
        <div className="semi-circle-prox__content inset-0 absolute media-cover">
          <img src={image.jpg} sizes="700px" loading="lazy" decoding="async" alt="" />
        </div>
      </div>
    </section>
  );
}
