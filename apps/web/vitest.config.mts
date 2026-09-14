import { defineConfig } from 'vitest/config';
import { resolve } from 'node:path';

export default defineConfig({
  resolve: {
    // Mirrors tsconfig `paths`. Array form (not an object) because order decides
    // the match: `@/generated/*` lives outside `src/` and must win over `@/*`.
    alias: [
      { find: /^@\/generated\//, replacement: `${resolve(import.meta.dirname, 'generated')}/` },
      { find: /^@\//, replacement: `${resolve(import.meta.dirname, 'src')}/` },
    ],
  },
  test: {
    // Two projects, split by extension: pure logic (`.test.ts`) stays in node so
    // the fast majority of the suite pays nothing for jsdom, while component
    // tests (`.test.tsx`) get a DOM and Testing Library's cleanup hook.
    projects: [
      {
        extends: true,
        test: {
          name: 'node',
          environment: 'node',
          include: ['src/**/*.test.ts'],
        },
      },
      {
        extends: true,
        test: {
          name: 'dom',
          environment: 'jsdom',
          include: ['src/**/*.test.tsx'],
          setupFiles: ['./vitest.setup.dom.ts'],
        },
      },
    ],
  },
});
