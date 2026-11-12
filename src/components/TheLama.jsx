import { useEffect, useRef } from 'react';
import gsap, { ScrollTrigger } from '../lib/gsap';
import { bus, app, lerp } from '../lib/bus';

const EPS = 1e-4;

// Footer 3D llama (module 263). Lazily loads three.js + /lama.glb once the footer is
// within one viewport. Mouse tilts the model; scrolling down drives a position /
// rotation timeline, scrolling up eases it back.
export default function TheLama() {
  const el = useRef(null);

  useEffect(() => {
    const s = { x: 0, y: 0, cx: 0, cy: 0, ease: 0.075, active: false, reverse: false, st: 0, sc: 0, dirty: true };
    const hasMouse = app.hasMouse;
    let destroyed = false;
    let three = null;
    let scene, camera, gl, group, model, tl, status, rtl, last = null;
    let b = { width: 0, height: 0, top: 0 };
    let max = 0;
    let xMap, yMap, yScroll;

    const draw = () => gl?.render(scene, camera);

    const createTimeline = (small = false) => {
      tl?.revert();
      tl = gsap
        .timeline({ paused: true, defaults: { ease: hasMouse ? 'power1' : 'power1.inOut' } })
        .fromTo(group.position, { z: -1.5, y: 0.5 }, { z: small ? 0.6 : 1.04, y: small ? -1.75 : -1.68 }, 0)
        .fromTo(group.rotation, { z: -0.6, x: -0.7, y: -0.9 }, { z: -0, x: 0.14, y: 0 }, 0);
      status?.revert();
      status = ScrollTrigger.create({
        trigger: el.current,
        start: 'top bottom',
        end: 'bottom bottom',
        onEnter: () => (s.active = true),
        onLeaveBack: () => (s.active = false),
        onUpdate: (self) => {
          if (!hasMouse) {
            tl?.progress(self.progress);
            draw();
          }
        },
      });
    };

    const resize = () => {
      const { ww, wh, maxScroll, small } = app.bounds;
      const r = el.current.getBoundingClientRect();
      b = { width: r.width, height: r.height, top: r.top + window.scrollY };
      s.dirty = true;
      if (hasMouse) {
        max = maxScroll + 2 * wh;
        xMap = gsap.utils.mapRange(0, b.width, -0.28, 0.28);
        yMap = gsap.utils.mapRange(0, b.height, -0.2, 0.1);
        yScroll = gsap.utils.mapRange(b.top, max, 0, 1);
      }
      if (camera && gl) {
        if (last !== ww) {
          camera.aspect = b.width / b.height;
          camera.updateProjectionMatrix();
          gl.setSize(b.width, b.height);
        }
        if (group) {
          createTimeline(small);
          last = ww;
        }
      }
    };

    const init = async () => {
      const [THREE, { GLTFLoader }, { MeshoptDecoder }] = await Promise.all([
        import('three'),
        import('three/examples/jsm/loaders/GLTFLoader.js'),
        import('three/examples/jsm/libs/meshopt_decoder.module.js'),
      ]);
      if (destroyed) return;
      three = THREE;
      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(75, b.width / b.height, 0.1, 1000);
      camera.position.z = 4;
      gl = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      gl.setSize(b.width, b.height);
      gl.setPixelRatio(Math.min(1.25, window.devicePixelRatio));
      gl.outputColorSpace = THREE.SRGBColorSpace;
      gl.useLegacyLights = true; // match the r1xx-era lighting the original was authored with
      gl.domElement.classList.add('absolute', 'top-0', 'left-0', 'w-full', 'h-full');
      el.current.appendChild(gl.domElement);
      const pl = new THREE.PointLight(0xffffff, 0.25);
      pl.position.set(1, 0, 5);
      scene.add(pl);
      scene.add(new THREE.AmbientLight(0xffda18));
      scene.fog = new THREE.Fog(0xffffff, 0.015, 100);
      group = new THREE.Group();
      scene.add(group);
      const loader = new GLTFLoader();
      loader.setMeshoptDecoder(MeshoptDecoder);
      loader.load('/lama.glb', (gltf) => {
        if (destroyed) return;
        model = gltf.scene;
        group.rotation.y = -1;
        group.add(model);
        draw();
      });
      last = null;
      resize();
    };

    const onScroll = ({ dY }) => {
      if (!s.active) return;
      const direction = Math.sign(-dY);
      if (direction === 1) {
        if (s.reverse) {
          rtl?.kill();
          s.reverse = false;
        }
        s.st -= dY;
        s.st = gsap.utils.clamp(b.top, max, s.st);
      } else if (direction === -1 && !s.reverse) {
        s.reverse = true;
        rtl = gsap.to(s, { st: b.top, duration: 1 });
      }
    };
    const onTick = ({ ratio }) => {
      if (!s.active || !model) return;
      if (Math.abs(s.x - s.cx) < EPS && Math.abs(s.y - s.cy) < EPS && Math.abs(s.st - s.sc) < EPS && !s.dirty) return;
      s.dirty = false;
      s.cx = lerp(s.cx, s.x, s.ease * ratio);
      s.cy = lerp(s.cy, s.y, s.ease * ratio);
      s.sc = lerp(s.sc, s.st, s.ease * ratio);
      tl?.progress(yScroll(s.sc));
      model.rotation.y = s.cx;
      model.rotation.x = s.cy;
      draw();
    };
    const onMove = (e) => {
      if (s.active && xMap) {
        s.x = xMap(e.clientX);
        s.y = yMap(e.clientY);
      }
    };

    resize();
    const offs = [bus.on('resize', resize)];
    if (hasMouse) {
      offs.push(bus.on('tick', onTick), bus.on('scroll', onScroll));
      window.addEventListener('mousemove', onMove);
    }
    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          io.disconnect();
          init();
        }
      },
      { rootMargin: '100% 0px' },
    );
    io.observe(el.current);

    return () => {
      destroyed = true;
      io.disconnect();
      offs.forEach((f) => f());
      window.removeEventListener('mousemove', onMove);
      tl?.kill();
      status?.kill();
      rtl?.kill();
      gl?.dispose();
      gl?.domElement.remove();
      void three;
    };
  }, []);

  return <div ref={el} className="absolute inset-0 -z-1 z-1" />;
}
