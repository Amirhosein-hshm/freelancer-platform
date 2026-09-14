'use client';

import { useEffect, useState } from 'react';

/**
 * Global ARIA live region.
 *
 * Toasts announce themselves, and `aria-live` on a value that changes in place
 * covers most cases. This is for the rest: outcomes with no visible text of
 * their own, like "۲۳ نتیجه یافت شد" after a filter, or a background action
 * finishing. Non-component code can call `announce()` too, which a hook-only
 * API would not allow.
 */

type Politeness = 'polite' | 'assertive';

interface Announcement {
  message: string;
  politeness: Politeness;
  /** Distinguishes repeats of the same text, which SRs would otherwise skip. */
  id: number;
}

let current: Announcement = { message: '', politeness: 'polite', id: 0 };
const listeners = new Set<() => void>();

export function announce(message: string, politeness: Politeness = 'polite'): void {
  if (message.trim() === '') return;
  current = { message, politeness, id: current.id + 1 };
  for (const listener of listeners) listener();
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/**
 * Mount once, near the root. Both politeness levels get their own node: moving
 * a message between levels on a single region is unreliable across
 * screen readers.
 */
export function LiveRegion() {
  // Not useSyncExternalStore: this must never render on the server, and an
  // effect-driven subscription keeps the initial HTML empty.
  const [announcement, setAnnouncement] = useState<Announcement | null>(null);

  useEffect(() => subscribe(() => setAnnouncement(current)), []);

  // The nodes stay mounted — a region added at the same time as its text is not
  // announced. Repeating the same message is made detectable with a
  // zero-width space that alternates, rather than by remounting.
  const text =
    announcement === null ? '' : announcement.message + '​'.repeat(announcement.id % 2);
  const isPolite = announcement?.politeness !== 'assertive';

  return (
    <>
      <div role="status" aria-live="polite" aria-atomic="true" className="sr-only">
        {isPolite ? text : ''}
      </div>
      <div role="alert" aria-live="assertive" aria-atomic="true" className="sr-only">
        {isPolite ? '' : text}
      </div>
    </>
  );
}
