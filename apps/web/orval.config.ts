import { defineConfig } from 'orval';

export default defineConfig({
  mediaPlatform: {
    input: {
      target: process.env.OPENAPI_URL ?? './openapi.json',
    },
    output: {
      mode: 'tags-split',
      target: 'generated/api/endpoints.ts',
      schemas: 'generated/api/models',
      client: 'react-query',
      httpClient: 'fetch',
      clean: true,
      override: {
        mutator: {
          path: 'src/lib/api/mutator.ts',
          name: 'customFetch',
        },
      },
    },
  },
});
