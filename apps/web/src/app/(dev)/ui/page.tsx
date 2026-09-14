import { notFound } from 'next/navigation';
import { Suspense } from 'react';
import { Showcase } from './showcase';

export const metadata = { title: 'اجزای مشترک' };

/**
 * Development-only gallery of the shared primitives. Gated at the route level so
 * it is never reachable in a production deployment, and so the client bundle for
 * it is not shipped to real users.
 *
 * The Suspense boundary is required: `Showcase` reads `useSearchParams` through
 * `useListQuery`, which opts the subtree out of static prerendering.
 */
export default function UiShowcasePage() {
  if (process.env.NODE_ENV === 'production') notFound();

  return (
    <Suspense fallback={null}>
      <Showcase />
    </Suspense>
  );
}
