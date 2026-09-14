'use client';

import { useCallback, useState } from 'react';
import { useUploadFile } from '@/generated/api/file/file';
import type { FileAssetContext, FileAssetResponse } from '@/generated/api/models';
import { ApiError, type NormalizedApiError, getApiError } from '@/lib/api/errors';

const UNEXPECTED_UPLOAD_MESSAGE = 'پاسخ سرور برای بارگذاری فایل نامعتبر بود.';

/**
 * Uploads one file at a time to `POST /api/v1/files`.
 *
 * No local size or MIME gate: the spec documents no limits, so the request is
 * attempted and the backend's own 400/409/422 message is what the user sees.
 * That keeps the rule the backend actually enforces as the only rule.
 */
export interface FileUpload {
  upload: (file: File) => Promise<FileAssetResponse | null>;
  isUploading: boolean;
  /** Last failure, already normalized for `ErrorState` or inline display. */
  error: NormalizedApiError | null;
  reset: () => void;
}

export function useFileUpload({
  context,
  onUploaded,
  onError,
}: {
  context: FileAssetContext;
  onUploaded?: (asset: FileAssetResponse) => void;
  onError?: (error: NormalizedApiError) => void;
}): FileUpload {
  const { mutateAsync, isPending } = useUploadFile();
  const [error, setError] = useState<NormalizedApiError | null>(null);

  const upload = useCallback(
    async (file: File): Promise<FileAssetResponse | null> => {
      setError(null);
      try {
        const result = await mutateAsync({ data: { file, context } });
        // Unreachable in practice — `customFetch` throws on a non-2xx — but the
        // generated return type is a union over every documented status, and
        // narrowing it here is what makes `result.data.data` well-typed.
        if (result.status !== 201) throw new ApiError(result.status, 'unexpected_response', UNEXPECTED_UPLOAD_MESSAGE);

        const asset = result.data.data;
        onUploaded?.(asset);
        return asset;
      } catch (thrown) {
        const normalized = getApiError(thrown);
        setError(normalized);
        onError?.(normalized);
        return null;
      }
    },
    [context, mutateAsync, onError, onUploaded],
  );

  const reset = useCallback(() => setError(null), []);

  return { upload, isUploading: isPending, error, reset };
}
