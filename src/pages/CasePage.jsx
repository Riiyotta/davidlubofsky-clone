import { useRef, useState } from 'react';
import CaseHero from '../components/CaseHero';
import CaseBlock from '../components/blocks/Blocks';
import ShapesNext from '../components/ShapesNext';
import ButtonBack from '../components/ButtonBack';
import KnockKnock from '../components/KnockKnock';
import usePageUnderlines from '../lib/usePageUnderlines';
import { nextCaseFor } from '../data/case';

export default function CasePage({ item, pageRef }) {
  const [locked, setLocked] = useState(!!item.protected);
  const local = useRef(null);
  const ref = pageRef || local;
  const next = nextCaseFor(item.slug);
  usePageUnderlines(ref, [locked]);

  return (
    <div ref={ref} className="text-black relative min-h-[100svh] z-2">
      {item.protected && locked ? (
        <div className="fixed inset-0 flex items-center justify-center">
          <KnockKnock secret={item.password} onUnlock={() => setLocked(false)} />
        </div>
      ) : (
        <>
          <CaseHero info={item} />
          <div className="relative py-75 s:py-150 z-2 js-t-fade">
            {item.blocks.map((b) => (
              <CaseBlock key={`block-${b.id}`} data={b} />
            ))}
          </div>
          <div className="relative z-3 js-bg-end">
            <a href={`/case/${next.slug}/`} data-next="" className="block relative">
              <ShapesNext image={next.featuredImage} title={next.title} />
            </a>
          </div>
          <div className="fixed bottom-0 left-0 pb-35 pointer-events-none w-full z-5 js-t-fade">
            <div className="site-max site-gutter flex justify-end s:block">
              <ButtonBack />
            </div>
          </div>
        </>
      )}
    </div>
  );
}
