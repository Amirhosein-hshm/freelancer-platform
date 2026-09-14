'use client';

import { Loader2 } from 'lucide-react';
import { useState, type ReactNode } from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { getApiError } from '@/lib/api/errors';

interface ActionDialogProps {
  /** The control that opens the dialog. Rendered as the dialog trigger. */
  trigger: ReactNode;
  title: string;
  description?: ReactNode;
  confirmLabel: string;
  pendingLabel?: string;
  cancelLabel?: string;
  destructive?: boolean;
  /** Blocks confirmation — e.g. a required reason that has not been filled in. */
  disabled?: boolean;
  /** Extra fields (a reason, a note) rendered above the footer. */
  children?: ReactNode;
  /**
   * Runs the action. Resolving closes the dialog; throwing keeps it open and
   * shows the backend's own message, so a 403/409/422 is never swallowed.
   */
  onConfirm: () => Promise<unknown>;
  /** Called after a successful confirm, once the dialog has closed. */
  onDone?: () => void;
}

/**
 * Confirmation dialog for a single backend action.
 *
 * Every project lifecycle call (publish, start, cancel, delete, accept, reject)
 * is irreversible or state-changing, so each goes through here: one place that
 * owns the pending state, keeps the dialog open on failure, and renders the
 * backend error inline instead of a toast the user may miss.
 */
export function ActionDialog({
  trigger,
  title,
  description,
  confirmLabel,
  pendingLabel = 'در حال انجام…',
  cancelLabel = 'انصراف',
  destructive = false,
  disabled = false,
  children,
  onConfirm,
  onDone,
}: ActionDialogProps) {
  const [open, setOpen] = useState(false);
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleOpenChange(next: boolean): void {
    // An in-flight request must not be abandoned mid-way by an outside click.
    if (isPending) return;
    setOpen(next);
    if (!next) setError(null);
  }

  async function handleConfirm(): Promise<void> {
    setIsPending(true);
    setError(null);
    try {
      await onConfirm();
      setOpen(false);
      onDone?.();
    } catch (thrown) {
      setError(getApiError(thrown).message);
    } finally {
      setIsPending(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent showCloseButton={!isPending}>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          {description ? <DialogDescription>{description}</DialogDescription> : null}
        </DialogHeader>

        {children}

        {error ? (
          <Alert variant="destructive" role="alert">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : null}

        <DialogFooter>
          <DialogClose asChild>
            <Button type="button" variant="outline" disabled={isPending}>
              {cancelLabel}
            </Button>
          </DialogClose>
          <Button
            type="button"
            variant={destructive ? 'destructive' : 'default'}
            onClick={handleConfirm}
            disabled={isPending || disabled}
          >
            {isPending ? <Loader2 size={16} className="animate-spin" aria-hidden="true" /> : null}
            {isPending ? pendingLabel : confirmLabel}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
