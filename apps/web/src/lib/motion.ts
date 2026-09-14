/**
 * Motion primitives. Everything here animates opacity and transform only — no
 * layout-affecting properties — and treats reduced motion as the final state
 * rendered immediately rather than as a slower animation.
 *
 * Pure helpers live here so they can be called from either side of the
 * client boundary; the observer hooks live in `use-reveal.ts`.
 */

export const REDUCED_MOTION_QUERY = '(prefers-reduced-motion: reduce)';

export function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return false;
  return window.matchMedia(REDUCED_MOTION_QUERY).matches;
}

/** Offsets stay within 8–16px: enough to read as motion, not as a jump. */
export type RevealDirection = 'up' | 'down' | 'start' | 'end' | 'none';

const HIDDEN_TRANSFORM: Record<RevealDirection, string> = {
  up: 'translate-y-3',
  down: '-translate-y-3',
  // Logical: in RTL, `start` is the right edge, so the element drifts inward.
  start: 'rtl:translate-x-3 ltr:-translate-x-3',
  end: 'rtl:-translate-x-3 ltr:translate-x-3',
  none: '',
};

/**
 * Stagger delays come from a fixed set so Tailwind can see the class names —
 * an arbitrary `delay-[${n}ms]` built from a variable is never emitted.
 */
const DELAY_CLASS: Record<number, string> = {
  0: '',
  75: 'delay-75',
  150: 'delay-150',
  200: 'delay-200',
  300: 'delay-300',
};

const DELAY_STEPS = [0, 75, 150, 200, 300] as const;

/** Snaps an arbitrary delay onto the nearest emitted step. */
export function snapDelay(delayMs: number): number {
  let closest: number = DELAY_STEPS[0];
  for (const step of DELAY_STEPS) {
    if (Math.abs(step - delayMs) < Math.abs(closest - delayMs)) closest = step;
  }
  return closest;
}

/** Per-item delay for a staggered list, capped so long lists stay responsive. */
export function staggerDelay(index: number, stepMs = 75): number {
  return snapDelay(Math.min(index * stepMs, DELAY_STEPS[DELAY_STEPS.length - 1]));
}

/**
 * Class names for a revealable element. Pair with `useReveal`:
 *
 *   const { ref, isRevealed } = useReveal();
 *   <div ref={ref} className={revealClass(isRevealed)}>…</div>
 */
export function revealClass(
  isRevealed: boolean,
  { direction = 'up', delayMs = 0 }: { direction?: RevealDirection; delayMs?: number } = {},
): string {
  const base =
    'transition-[opacity,transform] duration-300 ease-out motion-reduce:transition-none';
  const state = isRevealed
    ? 'opacity-100 translate-x-0 translate-y-0'
    : `opacity-0 ${HIDDEN_TRANSFORM[direction]}`;
  // Delay only on the way in; the hidden state must apply immediately.
  const delay = isRevealed ? DELAY_CLASS[snapDelay(delayMs)] : '';

  return [base, state, delay].filter(Boolean).join(' ');
}
