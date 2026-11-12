import { useEffect, useRef } from 'react';
import { createArrow, replay } from '../lib/rive';

// Yellow pill button: the clip-path mask collapses onto the circle on hover (pure CSS
// from the original stylesheet) while the Rive arrow animation replays.
export default function ButtonMain({ label = 'Shoot me a message', light = false, url, className = '', ariaLabel }) {
  const canvas = useRef(null);
  const inst = useRef(null);

  useEffect(() => {
    inst.current = createArrow(canvas.current);
    return () => inst.current?.cleanup();
  }, []);

  const Tag = url ? 'a' : 'div';
  const linkProps = url
    ? url.startsWith('mailto:')
      ? { href: url }
      : { href: url, target: '_blank', rel: 'noopener noreferrer' }
    : {};

  return (
    <Tag
      {...linkProps}
      aria-label={ariaLabel}
      className={`btn relative ${className}`}
      onMouseEnter={() => replay(inst.current)}
    >
      <div
        aria-hidden="true"
        className={`btn__text absolute inset-0 flex items-center pl-25 pt-[0.1em] ${light ? 'text-black' : 'text-white'}`}
      >
        {label}
      </div>
      <div className="btn-mask relative bg-yellow flex items-center pl-10 text-black z-2">
        <div className="btn-mask__text pl-15 pt-[0.1em]">{label}</div>
        <canvas ref={canvas} width="256" height="256" className="btn__circle relative inline-flex" />
      </div>
    </Tag>
  );
}
