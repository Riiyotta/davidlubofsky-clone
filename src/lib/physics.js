// Port of the original Matter.js render loop (module 287): steps the engine on the
// GSAP ticker and only repaints when a body actually moved.
import 'pathseg';
import Matter from 'matter-js';
import gsap from './gsap';

export { Matter };

export class PhysicsLoop {
  constructor({ engine, runner, render = null, onPaint = null }) {
    this.engine = engine;
    this.runner = runner;
    this.render = render;
    this.onPaint = onPaint;
    this.running = false;
    this.dirty = true;
    this.frame = this.frame.bind(this);
    gsap.ticker.add(this.frame);
  }
  start() {
    if (!this.running) {
      this.runner.timePrev = undefined;
      this.running = true;
    }
  }
  stop() {
    this.running = false;
  }
  invalidate() {
    this.dirty = true;
  }
  frame(t) {
    if (this.running) Matter.Runner.tick(this.runner, this.engine, 1000 * t);
    if ((this.running && this.moved()) || this.dirty) {
      this.dirty = false;
      if (this.render) Matter.Render.world(this.render);
      if (this.onPaint) this.onPaint();
    }
  }
  moved() {
    let moved = false;
    this.engine.world.bodies.forEach((b) => {
      if (b.isStatic) return;
      const { x, y } = b.position;
      const l = b.lastPainted;
      if (!l || Math.abs(x - l.x) > 0.01 || Math.abs(y - l.y) > 0.01 || Math.abs(b.angle - l.angle) > 1e-4) {
        moved = true;
        b.lastPainted = { x, y, angle: b.angle };
      }
    });
    return moved;
  }
  destroy() {
    gsap.ticker.remove(this.frame);
  }
}

export const bounds = (el) => el.getBoundingClientRect();
