import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ScrollToPlugin } from 'gsap/ScrollToPlugin';
import { CustomEase } from 'gsap/CustomEase';
import { DrawSVGPlugin } from 'gsap/DrawSVGPlugin';
import { SplitText } from 'gsap/SplitText';
import { Flip } from 'gsap/Flip';

gsap.registerPlugin(ScrollTrigger, ScrollToPlugin, CustomEase, DrawSVGPlugin, SplitText, Flip);
gsap.config({ defaults: { ease: 'none' } });

// Custom eases copied verbatim from the original site bundle.
CustomEase.create(
  'snappy',
  'M0,0 C0.094,0.026 0.124,0.127 0.157,0.29 0.197,0.486 0.254,0.8 0.348,0.884 0.42,0.949 0.374,1 1,1',
);
CustomEase.create(
  'tranquil',
  'M0,0,C0,0,0.026,0,0.052,0,0.254,0,0.282,0.142,0.386,0.538,0.478,0.889,0.619,0.998,0.94,0.998,0.976,0.998,1,0.998,1,0.998',
);
CustomEase.create(
  'quickstart',
  'M0,0 C0,0 0.124,0 0.208,0.054 0.391,0.173 0.467,0.581 0.526,0.751 0.539,0.79 0.554,0.814 0.576,0.85 0.593,0.878 0.608,0.897 0.631,0.921 0.648,0.939 0.664,0.95 0.686,0.963 0.706,0.975 0.722,0.981 0.746,0.987 0.771,0.993 0.788,0.995 0.816,0.997 0.865,1 1,1 1,1',
);

export { gsap, ScrollTrigger, SplitText, Flip };
export default gsap;
