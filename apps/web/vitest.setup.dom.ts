import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';

// Testing Library's automatic cleanup only registers itself when the test
// framework exposes `afterEach` globally; this project runs vitest without
// globals, so unmounting is wired up explicitly here.
afterEach(() => {
  cleanup();
});
