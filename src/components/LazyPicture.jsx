import { useEffect, useRef, useState } from 'react';

// Mirrors the original LazyPicture: aspect-ratio spacer + picture, image fades in on load.
export default function LazyPicture({ image, className = '', lazy = true, sizes = '100vw' }) {
  const ref = useRef(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (ref.current?.complete) setLoaded(true);
  }, []);

  if (!image) return null;
  return (
    <figure className={`relative w-full overflow-hidden ${className} media-cover ${lazy ? 'lazy' : ''}`}>
      <div style={{ paddingTop: `${(image.height / image.width) * 100}%` }} />
      <picture className="absolute inset-0">
        {image.webp && <source type="image/webp" srcSet={image.webp} sizes={sizes} />}
        <img
          ref={ref}
          className={loaded ? 'is-loaded' : ''}
          src={image.jpg}
          sizes={sizes}
          loading={lazy ? 'lazy' : 'eager'}
          decoding="async"
          draggable="false"
          width={image.width}
          height={image.height}
          alt={image.alt || ""}
          onLoad={() => setLoaded(true)}
        />
      </picture>
    </figure>
  );
}
