'use client';

import { Loader2, Upload } from 'lucide-react';
import { type DragEvent, useId, useRef, useState } from 'react';
import type { FileAssetContext, FileAssetResponse } from '@/generated/api/models';
import { Button } from '@/components/ui/button';
import { announce } from '@/components/ui/live-region';
import { formatNumber } from '@/lib/format';
import { cn } from '@/lib/utils';
import { FILE_CONTEXT_LABELS } from './file-asset';
import { FileAssetChip } from './file-asset-chip';
import { useFileUpload } from './use-file-upload';

/**
 * Drop-zone uploader for one or more files in a single backend context.
 *
 * Files upload sequentially rather than in parallel: the backend rejects per
 * file, and a serial queue means the first rejection stops the run instead of
 * leaving the user with a scatter of partial successes and failures.
 *
 * `accept` is passed through to the input as a picker hint only. Nothing is
 * validated locally — see `use-file-upload.ts`.
 */
export function FileUploader({
  context,
  value,
  onChange,
  multiple = false,
  accept,
  disabled = false,
  label,
  hint,
  className,
}: {
  context: FileAssetContext;
  /** Assets uploaded so far; owned by the parent so forms can submit their ids. */
  value: FileAssetResponse[];
  onChange: (assets: FileAssetResponse[]) => void;
  multiple?: boolean;
  accept?: string;
  disabled?: boolean;
  label?: string;
  hint?: string;
  className?: string;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const inputId = useId();
  const [isDragging, setIsDragging] = useState(false);
  const [queued, setQueued] = useState(0);

  const { upload, isUploading, error, reset } = useFileUpload({ context });

  const contextLabel = label ?? FILE_CONTEXT_LABELS[context];
  const isBusy = isUploading || queued > 0;
  const isLocked = disabled || isBusy;

  async function uploadAll(files: File[]): Promise<void> {
    const selected = multiple ? files : files.slice(0, 1);
    if (selected.length === 0) return;

    reset();
    setQueued(selected.length);
    const uploaded: FileAssetResponse[] = [];

    try {
      for (const file of selected) {
        const asset = await upload(file);
        // A rejection is terminal: keep what succeeded, stop the queue.
        if (!asset) break;
        uploaded.push(asset);
        setQueued((remaining) => remaining - 1);
      }
    } finally {
      setQueued(0);
    }

    if (uploaded.length === 0) return;
    onChange(multiple ? [...value, ...uploaded] : uploaded);
    announce(`${formatNumber(uploaded.length)} فایل بارگذاری شد.`);
  }

  function handleDrop(event: DragEvent<HTMLLabelElement>): void {
    event.preventDefault();
    setIsDragging(false);
    if (isLocked) return;
    void uploadAll([...event.dataTransfer.files]);
  }

  return (
    <div className={cn('grid gap-3', className)}>
      {/* The zone is a label, so a click anywhere in it opens the picker and the
          input keeps its native keyboard and screen reader behaviour. */}
      <label
        htmlFor={inputId}
        onDragOver={(event) => {
          event.preventDefault();
          if (!isLocked) setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={cn(
          'grid cursor-pointer place-items-center gap-2 rounded-xl border border-dashed border-border px-6 py-8 text-center transition-colors duration-200',
          isDragging && 'border-primary bg-primary/5',
          isLocked && 'pointer-events-none opacity-60',
        )}
      >
        <span
          className="grid size-11 place-items-center rounded-full bg-muted text-muted-foreground"
          aria-hidden="true"
        >
          {isBusy ? <Loader2 size={20} className="animate-spin" /> : <Upload size={20} />}
        </span>
        <span className="text-sm font-medium">
          {isBusy
            ? `در حال بارگذاری${queued > 1 ? ` (${formatNumber(queued)} فایل باقی‌مانده)` : ''}…`
            : `${contextLabel} را اینجا رها کنید یا انتخاب کنید`}
        </span>
        {hint ? <span className="text-xs text-muted-foreground">{hint}</span> : null}

        <input
          ref={inputRef}
          id={inputId}
          type="file"
          className="sr-only"
          multiple={multiple}
          accept={accept}
          disabled={isLocked}
          onChange={(event) => {
            const files = [...(event.target.files ?? [])];
            // Clear first so re-picking the same file still fires a change.
            event.target.value = '';
            void uploadAll(files);
          }}
        />
      </label>

      {error ? (
        <div role="alert" className="grid gap-2 rounded-lg border border-destructive/40 bg-destructive/5 p-3">
          <p className="text-sm text-destructive">{error.message}</p>
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="w-fit"
            onClick={() => {
              reset();
              inputRef.current?.click();
            }}
          >
            انتخاب فایل دیگر
          </Button>
        </div>
      ) : null}

      {value.length > 0 ? (
        <ul className="grid gap-2">
          {value.map((asset) => (
            <li key={asset.file_asset_id}>
              <FileAssetChip
                asset={asset}
                onRemove={
                  isLocked
                    ? undefined
                    : () => onChange(value.filter((item) => item.file_asset_id !== asset.file_asset_id))
                }
              />
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
