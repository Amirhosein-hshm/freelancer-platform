'use client';

import { type RefObject, useEffect, useRef, useState, useSyncExternalStore } from 'react';
import { REDUCED_MOTION_QUERY, prefersReducedMotion } from './motion';

/**
 * `useSyncExternalStore` rather than an effect: the media query is external
 * state, and reading it during render avoids a cascading re-render on mount.
 * The server snapshot is `true`, so server markup is the settled, unanimated
 * state and nothing moves during hydration.
 */
export function useReducedMotion(): boolean {
  return useSyncExternalStore(subscribeToReducedMotion, prefersReducedMotion, () => true);
}

function subscribeToReducedMotion(onChange: () => void): () => void {
  const media = window.matchMedia(REDUCED_MOTION_QUERY);
  media.addEventListener('change', onChange);
  return () => media.removeEventListener('change', onChange);
}

/**
 * Reveals an element as it enters the viewport and resets it as it leaves.
 *
 * Returns a ref and the current state; feed the state into `revealClass`. The
 * This replayable behavior supports subtle bidirectional choreography on
 * editorial pages while still settling immediately for reduced-motion users.
 *
 * Under reduced motion (or without IntersectionObserver) the element starts
 * revealed and no observer is created at all.
 */
export function useReveal<T extends HTMLElement = HTMLDivElement>({
  threshold = 0.15,
  rootMargin = '0px 0px -10% 0px',
}: { threshold?: number; rootMargin?: string } = {}): {
  ref: RefObject<T | null>;
  isRevealed: boolean;
} {
  const ref = useRef<T>(null);
  const [isRevealed, setIsRevealed] = useState(false);

  useEffect(() => {
    const element = ref.current;

    if (!element || prefersReducedMotion() || typeof IntersectionObserver === 'undefined') {
      setIsRevealed(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          setIsRevealed(entry.isIntersecting);
        }
      },
      { threshold, rootMargin },
    );

    observer.observe(element);
    return () => observer.disconnect();
  }, [threshold, rootMargin]);

  return { ref, isRevealed };
}
