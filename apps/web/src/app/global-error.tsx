'use client'; // Error boundaries must be Client Components

import { useEffect } from 'react';
// global-error replaces the root layout, so it must import the stylesheet itself.
import './globals.css';

/**
 * Last-resort boundary for failures in the root layout. Must render its own
 * <html>/<body> because it replaces the root layout when active.
 */
export default function GlobalError({
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
    <html lang="fa" dir="rtl" data-scroll-behavior="smooth">
      <body>
        <main className="grid min-h-screen place-items-center px-4 py-10 text-center">
          <div className="grid max-w-md gap-4">
            <h1 className="text-xl font-bold">خطای غیرمنتظره</h1>
            <p className="text-sm text-muted-foreground">
              مشکلی در بارگذاری برنامه پیش آمد. لطفاً دوباره تلاش کنید.
            </p>
            <button
              type="button"
              onClick={() => retry()}
              className="mx-auto min-h-11 rounded-md bg-primary px-6 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 focus-visible:ring-[3px] focus-visible:ring-ring/50"
            >
              تلاش دوباره
            </button>
            {error.digest ? (
              <p className="text-xs text-muted-foreground">
                کد پیگیری: <span className="ltr-embedded font-mono">{error.digest}</span>
              </p>
            ) : null}
          </div>
        </main>
      </body>
    </html>
  );
}
