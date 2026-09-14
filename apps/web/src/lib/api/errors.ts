import type { ErrorEnvelope } from '@/generated/api/models';

export interface NormalizedApiError {
  status: number;
  code: string;
  message: string;
  /** Field-level messages when the backend provides them (ErrorDetail.details). */
  fields: Record<string, string>;
}

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly fields: Record<string, string>;

  constructor(status: number, code: string, message: string, fields?: Record<string, string>) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.fields = fields ?? {};
  }

  get isUnauthorized(): boolean {
    return this.status === 401;
  }

  get isForbidden(): boolean {
    return this.status === 403;
  }

  get isValidation(): boolean {
    return this.status === 422;
  }

  toNormalized(): NormalizedApiError {
    return { status: this.status, code: this.code, message: this.message, fields: this.fields };
  }
}

export const NETWORK_ERROR_MESSAGE = 'ارتباط با سرور برقرار نشد. اتصال اینترنت را بررسی کنید و دوباره تلاش کنید.';

export function parseErrorBody(body: unknown): { code: string; message: string; fields: Record<string, string> } {
  const envelope = body as Partial<ErrorEnvelope> | undefined;
  const error = envelope?.error;
  if (error && typeof error.code === 'string' && typeof error.message === 'string') {
    return { code: error.code, message: error.message, fields: parseFieldErrors(error.details) };
  }
  return { code: 'unknown_error', message: NETWORK_ERROR_MESSAGE, fields: {} };
}

function parseFieldErrors(details: unknown): Record<string, string> {
  if (!details || typeof details !== 'object') return {};
  const fields: Record<string, string> = {};
  if (Array.isArray(details)) {
    for (const entry of details) {
      const item = entry as { loc?: unknown[]; msg?: unknown } | null;
      const field = item?.loc?.filter((part) => typeof part === 'string' && part !== 'body').pop();
      if (typeof field === 'string' && typeof item?.msg === 'string') {
        fields[field] = item.msg;
      }
    }
    return fields;
  }
  for (const [key, value] of Object.entries(details as Record<string, unknown>)) {
    if (typeof value === 'string') {
      fields[key] = value;
    } else if (Array.isArray(value) && typeof value[0] === 'string') {
      fields[key] = value[0];
    }
  }
  return fields;
}

/** Normalizes any thrown value into a user-presentable API error. */
export function getApiError(error: unknown): NormalizedApiError {
  if (error instanceof ApiError) return error.toNormalized();
  if (typeof error === 'object' && error !== null && 'status' in error) {
    const status = (error as { status?: unknown }).status;
    if (typeof status === 'number') {
      const parsed = parseErrorBody((error as { body?: unknown }).body);
      return { status, ...parsed };
    }
  }
  return { status: 0, code: 'network_error', message: NETWORK_ERROR_MESSAGE, fields: {} };
}
