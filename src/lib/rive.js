import { Rive, RuntimeLoader } from '@rive-app/canvas';

// Serve the Rive runtime locally instead of from unpkg.
RuntimeLoader.setWasmUrl('/rive.wasm');
Rive.suppressDeprecationWarnings = ['default-state-machine'];

export function createRive(canvas, src, artboard, opts = {}) {
  return new Rive({ src, canvas, artboard, autoplay: false, ...opts });
}

export const createArrow = (canvas) => createRive(canvas, '/riv/arrow.riv', 'arrow-btn');

export function replay(inst) {
  if (!inst) return;
  try {
    inst.reset();
    inst.play();
  } catch {
    /* rive not loaded yet */
  }
}
