import { describe, expect, it } from 'vitest';
import { revealClass, snapDelay, staggerDelay } from './motion';

describe('revealClass', () => {
  it('starts hidden with a transform offset', () => {
    const hidden = revealClass(false);
    expect(hidden).toContain('opacity-0');
    expect(hidden).toContain('translate-y-3');
  });

  it('settles to no offset once revealed', () => {
    const shown = revealClass(true);
    expect(shown).toContain('opacity-100');
    expect(shown).toContain('translate-y-0');
    expect(shown).not.toContain('opacity-0');
  });

  it('only animates opacity and transform', () => {
    expect(revealClass(true)).toContain('transition-[opacity,transform]');
  });

  it('opts out of the transition under reduced motion', () => {
    expect(revealClass(true)).toContain('motion-reduce:transition-none');
  });

  it('uses logical offsets for start/end so RTL drifts inward', () => {
    expect(revealClass(false, { direction: 'start' })).toContain('rtl:translate-x-3');
    expect(revealClass(false, { direction: 'start' })).toContain('ltr:-translate-x-3');
    expect(revealClass(false, { direction: 'end' })).toContain('rtl:-translate-x-3');
  });

  it('applies a delay only on the way in', () => {
    expect(revealClass(true, { delayMs: 150 })).toContain('delay-150');
    expect(revealClass(false, { delayMs: 150 })).not.toContain('delay-150');
  });

  it('emits no offset class for direction none', () => {
    expect(revealClass(false, { direction: 'none' })).not.toMatch(/translate-[xy]-3/);
  });
});

describe('snapDelay / staggerDelay', () => {
  it('snaps arbitrary delays onto emitted steps', () => {
    expect(snapDelay(0)).toBe(0);
    expect(snapDelay(80)).toBe(75);
    expect(snapDelay(160)).toBe(150);
    expect(snapDelay(1000)).toBe(300);
  });

  it('staggers a list and caps the tail', () => {
    expect(staggerDelay(0)).toBe(0);
    expect(staggerDelay(1)).toBe(75);
    expect(staggerDelay(2)).toBe(150);
    // Beyond the cap every remaining item shares the last step, so a long list
    // does not end with items still waiting seconds to appear.
    expect(staggerDelay(20)).toBe(300);
  });

  it('never produces a delay Tailwind cannot emit', () => {
    const emitted = new Set([0, 75, 150, 200, 300]);
    for (let index = 0; index < 50; index += 1) {
      expect(emitted.has(staggerDelay(index))).toBe(true);
    }
  });
});
