import { describe, expect, it } from 'vitest';
import type { FileAssetResponse } from '@/generated/api/models';
import {
  FILE_CONTEXT_LABELS,
  describeFileAsset,
  getFileExtension,
  getFileKind,
  truncateFileName,
} from './file-asset';

describe('getFileKind', () => {
  it('classifies by media type prefix', () => {
    expect(getFileKind('image/png')).toBe('image');
    expect(getFileKind('video/mp4')).toBe('video');
    expect(getFileKind('audio/mpeg')).toBe('audio');
  });

  it('recognises documents and archives by exact type', () => {
    expect(getFileKind('application/pdf')).toBe('pdf');
    expect(getFileKind('application/zip')).toBe('archive');
    expect(
      getFileKind('application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
    ).toBe('document');
  });

  it('tolerates casing and stray whitespace from the backend', () => {
    expect(getFileKind(' IMAGE/JPEG ')).toBe('image');
  });

  it('falls back rather than guessing', () => {
    expect(getFileKind('application/x-unknown')).toBe('other');
    expect(getFileKind('')).toBe('other');
  });
});

describe('getFileExtension', () => {
  it('reads the last extension', () => {
    expect(getFileExtension('طرح.final.PDF')).toBe('pdf');
  });

  it('returns empty when there is nothing usable', () => {
    expect(getFileExtension('README')).toBe('');
    // A dotfile is all name, no extension.
    expect(getFileExtension('.gitignore')).toBe('');
    // A trailing dot names no type.
    expect(getFileExtension('report.')).toBe('');
  });
});

describe('truncateFileName', () => {
  it('leaves short names alone', () => {
    expect(truncateFileName('طرح.pdf')).toBe('طرح.pdf');
  });

  it('truncates in the middle so the extension survives', () => {
    const long = `${'a'.repeat(60)}.pdf`;
    const result = truncateFileName(long, 20);

    expect(result.endsWith('.pdf')).toBe(true);
    expect(result).toContain('…');
    expect(result.length).toBeLessThanOrEqual(20);
  });

  it('still truncates when there is no extension', () => {
    const result = truncateFileName('b'.repeat(40), 10);
    expect(result.length).toBeLessThanOrEqual(10);
    expect(result).toContain('…');
  });
});

describe('describeFileAsset', () => {
  it('renders size and upload time in Persian', () => {
    const asset: FileAssetResponse = {
      file_asset_id: '018f6f2e-0000-7000-8000-000000000000',
      file_name: 'resume.pdf',
      size_bytes: 1536,
      mime_type: 'application/pdf',
      uploaded_at: '2026-08-29T11:34:31Z',
      context: 'resume',
    };

    const described = describeFileAsset(asset);
    expect(described).toContain('۱٫۵ کیلوبایت');
    expect(described).toContain('۱۴۰۵');
  });
});

describe('FILE_CONTEXT_LABELS', () => {
  it('covers every context the backend accepts', () => {
    // Guards against a regenerated FileAssetContext gaining a member with no
    // Persian label — TS catches it here rather than rendering a raw enum value.
    expect(Object.keys(FILE_CONTEXT_LABELS).sort()).toEqual([
      'delivery',
      'generic',
      'portfolio',
      'resume',
      'ticket_attachment',
    ]);
  });
});
