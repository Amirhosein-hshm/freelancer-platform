'use client';

import {
  FileArchive,
  FileAudio,
  FileImage,
  FileText,
  FileVideo,
  File as FileIcon,
  X,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { FileAssetResponse } from '@/generated/api/models';
import { Button } from '@/components/ui/button';
import { describeFileAsset, getFileKind, truncateFileName, type FileKind } from './file-asset';
import { cn } from '@/lib/utils';

const KIND_ICON: Record<FileKind, LucideIcon> = {
  image: FileImage,
  video: FileVideo,
  audio: FileAudio,
  pdf: FileText,
  archive: FileArchive,
  document: FileText,
  other: FileIcon,
};

/**
 * A single uploaded asset.
 *
 * There is no download affordance because the API exposes none: every documented
 * response is JSON and `FileAssetResponse` carries no URL. The chip therefore
 * shows what is knowable — name, size, upload time — and nothing that would
 * dead-end the user.
 */
export function FileAssetChip({
  asset,
  onRemove,
  className,
}: {
  asset: FileAssetResponse;
  /** Detaches the asset from the form it was uploaded for; no delete endpoint. */
  onRemove?: () => void;
  className?: string;
}) {
  const Icon = KIND_ICON[getFileKind(asset.mime_type)];

  return (
    <div
      className={cn(
        'flex items-center gap-3 rounded-lg border border-border bg-card px-3 py-2',
        className,
      )}
    >
      <span
        className="grid size-9 shrink-0 place-items-center rounded-md bg-muted text-muted-foreground"
        aria-hidden="true"
      >
        <Icon size={18} />
      </span>

      <div className="min-w-0 grow">
        <p className="truncate text-sm font-medium" title={asset.file_name}>
          {truncateFileName(asset.file_name)}
        </p>
        <p className="text-xs text-muted-foreground">{describeFileAsset(asset)}</p>
      </div>

      {onRemove ? (
        <Button
          type="button"
          variant="ghost"
          size="icon-sm"
          onClick={onRemove}
          aria-label={`حذف ${asset.file_name}`}
        >
          <X size={16} />
        </Button>
      ) : null}
    </div>
  );
}
