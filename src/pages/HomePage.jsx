import { useCallback, useRef, useState } from 'react';
import HomeHero from '../components/home/HomeHero';
import HomeItems from '../components/home/HomeItems';
import ShapesConnect from '../components/home/ShapesConnect';
import IntroModal from '../components/home/IntroModal';
import usePageUnderlines from '../lib/usePageUnderlines';
import { homePage } from '../data/case';

export default function HomePage({ pageRef }) {
  const local = useRef(null);
  const ref = pageRef || local;
  const [modalOpen, setModalOpen] = useState(false);
  const onOpenChange = useCallback((v) => setModalOpen(v), []);
  usePageUnderlines(ref);

  return (
    <div ref={ref} className="text-white site-max z-2">
      <div className="fixed inset-0 bg-white invisible z-2 js-t-mask" />
      <HomeHero modalOpen={modalOpen} />
      <HomeItems className="z-3" cases={homePage.featuredCases} />
      <ShapesConnect className="z-1" modalOpen={modalOpen} />
      <IntroModal onOpenChange={onOpenChange} />
    </div>
  );
}
