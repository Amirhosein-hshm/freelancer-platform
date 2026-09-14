import type { FileAssetContext, FileAssetResponse } from '@/generated/api/models';
import { formatBytes, formatDateTime } from '@/lib/format';

/**
 * File-asset helpers shared by every uploader in the app.
 *
 * Deliberately absent: size and MIME validation. The OpenAPI spec documents no
 * limits, so any threshold here would be invented policy that silently diverges
 * from the backend's. Uploads are attempted and the backend's 400/409/422 is
 * surfaced verbatim. `accept` hints are the caller's to pass — they are an input
 * affordance, not validation.
 *
 * Also absent: downloads. Every endpoint in the spec returns
 * `application/json`, and `FileAssetResponse` carries no URL or storage key, so
 * there is nothing to link to. Uploaded assets are referenced by
 * `file_asset_id` and displayed as metadata until the backend exposes a
 * content route.
 */

/** Persian labels for the upload contexts the backend accepts. */
export const FILE_CONTEXT_LABELS: Record<FileAssetContext, string> = {
  resume: 'رزومه',
  portfolio: 'نمونه کار',
  delivery: 'تحویل پروژه',
  ticket_attachment: 'پیوست تیکت',
  generic: 'فایل',
};

export type FileKind = 'image' | 'video' | 'audio' | 'pdf' | 'archive' | 'document' | 'other';

const ARCHIVE_TYPES = new Set([
  'application/zip',
  'application/x-zip-compressed',
  'application/x-rar-compressed',
  'application/vnd.rar',
  'application/x-7z-compressed',
  'application/gzip',
  'application/x-tar',
]);

const DOCUMENT_TYPES = new Set([
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-powerpoint',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  'text/plain',
  'text/csv',
]);

/** Coarse classification, used only to pick an icon. */
export function getFileKind(mimeType: string): FileKind {
  const type = mimeType.toLowerCase().trim();
  if (type.startsWith('image/')) return 'image';
  if (type.startsWith('video/')) return 'video';
  if (type.startsWith('audio/')) return 'audio';
  if (type === 'application/pdf') return 'pdf';
  if (ARCHIVE_TYPES.has(type)) return 'archive';
  if (DOCUMENT_TYPES.has(type)) return 'document';
  return 'other';
}

/** `"طرح-اولیه.pdf"` → `"pdf"`; empty when there is no usable extension. */
export function getFileExtension(fileName: string): string {
  const lastDot = fileName.lastIndexOf('.');
  if (lastDot <= 0 || lastDot === fileName.length - 1) return '';
  return fileName.slice(lastDot + 1).toLowerCase();
}

/**
 * Middle-truncates a long name so both the beginning and the extension stay
 * readable — end-truncation would hide exactly the part that identifies the
 * file type.
 */
export function truncateFileName(fileName: string, maxLength = 32): string {
  if (fileName.length <= maxLength) return fileName;

  const extension = getFileExtension(fileName);
  const suffix = extension === '' ? '' : `.${extension}`;
  const head = Math.max(1, maxLength - suffix.length - 1);
  return `${fileName.slice(0, head)}…${suffix}`;
}

/** One-line summary for a chip or table cell: «۱٫۲ مگابایت • ۷ شهریور ۱۴۰۵، ۱۵:۰۴». */
export function describeFileAsset(asset: FileAssetResponse): string {
  return `${formatBytes(asset.size_bytes)} • ${formatDateTime(asset.uploaded_at)}`;
}
