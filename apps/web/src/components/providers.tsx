'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, type ReactNode } from 'react';
import { LiveRegion } from '@/components/ui/live-region';
import { Toaster } from '@/components/ui/sonner';
import { ApiError } from '@/lib/api/errors';

function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        refetchOnWindowFocus: false,
        retry: (failureCount, error) => {
          if (error instanceof ApiError && [0, 401, 403, 422].includes(error.status)) {
            return false;
          }
          return failureCount < 2;
        },
      },
    },
  });
}

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(createQueryClient);
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* One instance each, at the root: a live region must already exist when
          its text changes, and a second Toaster would duplicate every toast. */}
      <Toaster />
      <LiveRegion />
    </QueryClientProvider>
  );
}
