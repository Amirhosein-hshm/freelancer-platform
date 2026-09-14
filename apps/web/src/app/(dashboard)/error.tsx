'use client'; // Error boundaries must be Client Components

import { RotateCcw, ServerCrash } from 'lucide-react';
import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

/**
 * Catches failures thrown while rendering the authenticated area — most often
 * an unreachable backend from `getServerSessionUser`. 401s never reach here:
 * `server.ts` redirects those to /login.
 */
export default function DashboardError({
  error,
  retry,
}: {
  error: Error & { digest?: string };
  retry: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main id="main" className="grid min-h-screen place-items-center px-4 py-10">
      <Card className="w-full max-w-md text-center">
        <CardHeader className="items-center gap-3">
          <span
            className="mx-auto grid size-12 place-items-center rounded-full bg-destructive/10 text-destructive"
            aria-hidden="true"
          >
            <ServerCrash size={22} />
          </span>
          <CardTitle className="text-lg">ارتباط با سرور برقرار نشد</CardTitle>
          <CardDescription>
            در بارگذاری این صفحه مشکلی پیش آمد. اتصال اینترنت خود را بررسی کنید و دوباره تلاش کنید.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3">
          <Button onClick={() => retry()} size="lg" className="min-h-11 w-full">
            <RotateCcw size={16} />
            تلاش دوباره
          </Button>
          {error.digest ? (
            <p className="text-xs text-muted-foreground">
              کد پیگیری: <span className="ltr-embedded font-mono">{error.digest}</span>
            </p>
          ) : null}
        </CardContent>
      </Card>
    </main>
  );
}
