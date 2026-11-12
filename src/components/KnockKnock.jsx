import { useEffect, useRef, useState } from 'react';
import gsap from '../lib/gsap';
import { createArrow, replay } from '../lib/rive';

// Password gate for protected cases (module 371). Same client-side check as the original.
export default function KnockKnock({ secret, onUnlock }) {
  const [pass, setPass] = useState('');
  const [message, setMessage] = useState(null);
  const input = useRef(null);
  const canvas = useRef(null);
  const inst = useRef(null);

  useEffect(() => {
    inst.current = createArrow(canvas.current);
    const tl = gsap
      .timeline()
      .fromTo(
        input.current,
        { clipPath: 'inset(0 0 0 100% round 5.5rem)' },
        { clipPath: 'inset(0 0 0 0% round 5.5rem)', duration: 1.5, ease: 'expo.inOut' },
      )
      .fromTo(
        canvas.current,
        { clipPath: 'circle(0% at 50%)' },
        { clipPath: 'circle(50% at 50%)', duration: 1.5, ease: 'expo.inOut' },
        0,
      );
    return () => {
      inst.current?.cleanup();
      tl.kill();
    };
  }, []);

  const submit = (e) => {
    e.preventDefault();
    if (pass === secret) onUnlock();
    else setMessage('Incorrect Password');
  };

  return (
    <form id="login" className="login flex" onSubmit={submit}>
      <div className="relative w-full max-w-[45rem]">
        <input
          ref={input}
          type="password"
          placeholder="Enter Password"
          className="block h-55 bg-gray-light rounded-full w-full pl-25 pr-75"
          value={pass}
          onChange={(e) => setPass(e.target.value)}
        />
        <button type="submit" className="login-btn absolute top-0 right-0 h-full w-55" onMouseEnter={() => replay(inst.current)}>
          <canvas ref={canvas} width="500" height="500" className="absolute top-0 right-0 h-full w-full bg-yellow rounded-full flex" />
        </button>
        {message && (
          <p className="absolute top-full left-0 w-full whitespace-nowrap text-center text-red text-14 pt-15">{message}</p>
        )}
      </div>
    </form>
  );
}

