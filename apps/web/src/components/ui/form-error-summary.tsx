'use client';

import { useEffect, useId, useRef } from 'react';
import type { FieldErrors } from 'react-hook-form';
import { prefersReducedMotion } from '@/lib/motion';
import { cn } from '@/lib/utils';

/**
 * Focusable summary of a form's validation errors.
 *
 * `FormItem` derives its ids from `useId()`, so a summary rendered outside the
 * field cannot compute `htmlFor`. Fields are instead located by their `name`
 * attribute — which React Hook Form always renders — and focused imperatively.
 *
 * The summary takes focus itself when it appears, so a keyboard or screen reader
 * user who submits an invalid form lands on the list of problems rather than
 * being left at the submit button with silent errors above the fold.
 */
export function FormErrorSummary({
  errors,
  labels,
  title = 'فرم را نمی‌توان ثبت کرد',
  className,
}: {
  errors: FieldErrors;
  /** Field name → Persian label, so the summary reads like the form does. */
  labels: Record<string, string>;
  title?: string;
  className?: string;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const titleId = useId();
  const entries = collectFieldErrors(errors, labels);
  const count = entries.length;

  useEffect(() => {
    // Re-focus on every transition into an errored state, not just the first:
    // a second failed submit is just as much a dead end as the first.
    if (count > 0) containerRef.current?.focus();
  }, [count]);

  if (count === 0) return null;

  return (
    <div
      ref={containerRef}
      // -1 keeps it out of the tab order once dismissed by fixing the fields.
      tabIndex={-1}
      role="alert"
      aria-labelledby={titleId}
      className={cn(
        'grid gap-2 rounded-lg border border-destructive/40 bg-destructive/5 p-4 outline-none focus-visible:ring-[3px] focus-visible:ring-destructive/30',
        className,
      )}
    >
      <p id={titleId} className="text-sm font-semibold text-destructive">
        {title}
      </p>
      <ul className="grid list-disc gap-1 ps-5 text-sm text-destructive">
        {entries.map((entry) => (
          <li key={entry.name}>
            <button
              type="button"
              onClick={() => focusField(entry.name)}
              className="cursor-pointer text-start underline decoration-dotted underline-offset-4 hover:decoration-solid"
            >
              {entry.label}: {entry.message}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

interface FieldErrorEntry {
  name: string;
  label: string;
  message: string;
}

/**
 * Flattens React Hook Form's nested error tree into one entry per errored leaf,
 * keyed by dotted path so the `name` attribute lookup still resolves.
 */
export function collectFieldErrors(
  errors: FieldErrors,
  labels: Record<string, string>,
  prefix = '',
): FieldErrorEntry[] {
  const entries: FieldErrorEntry[] = [];

  for (const [key, value] of Object.entries(errors)) {
    if (!value || typeof value !== 'object') continue;
    const path = prefix === '' ? key : `${prefix}.${key}`;

    const message = 'message' in value ? value.message : undefined;
    if (typeof message === 'string' && message !== '') {
      entries.push({ name: path, label: labels[path] ?? path, message });
      continue;
    }

    // No message here means this node is a group (object or array of fields).
    entries.push(...collectFieldErrors(value as FieldErrors, labels, path));
  }

  return entries;
}

function focusField(name: string): void {
  const escaped = CSS.escape(name);
  const field = document.querySelector<HTMLElement>(
    `[name="${escaped}"]:not([type="hidden"]), [data-form-name="${escaped}"]`,
  );
  if (!field) return;
  field.focus();
  field.scrollIntoView({
    block: 'center',
    behavior: prefersReducedMotion() ? 'auto' : 'smooth',
  });
}
