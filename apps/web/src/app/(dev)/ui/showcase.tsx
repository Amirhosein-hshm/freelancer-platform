'use client';

import { AlertCircle, FolderOpen } from 'lucide-react';
import { type ReactNode, useState } from 'react';
import { toast } from 'sonner';
import type { FileAssetResponse } from '@/generated/api/models';
import { Button } from '@/components/ui/button';
import { EmptyState } from '@/components/ui/empty-state';
import { ErrorState } from '@/components/ui/error-state';
import { FormErrorSummary } from '@/components/ui/form-error-summary';
import { announce } from '@/components/ui/live-region';
import { PaginationBar } from '@/components/ui/pagination-bar';
import { FileUploader } from '@/features/files/file-uploader';
import { normalizePaginationMeta } from '@/lib/api/pagination';
import { formatBytes, formatDateTime, formatNumber } from '@/lib/format';
import { revealClass, staggerDelay } from '@/lib/motion';
import { useListQuery } from '@/lib/url/use-list-query';
import { useReveal } from '@/lib/use-reveal';

const TOTAL_ITEMS = 137;

/**
 * Renders every Slice 2 primitive against real state, so they are exercised
 * rather than merely type-checked. Reachable only outside production — see the
 * gate in `page.tsx`.
 */
export function Showcase() {
  const query = useListQuery();
  const meta = normalizePaginationMeta(
    { page: query.page, page_size: query.pageSize, total_items: TOTAL_ITEMS },
    query.pageQuery,
  );

  const [assets, setAssets] = useState<FileAssetResponse[]>([]);

  return (
    <div className="mx-auto grid max-w-3xl gap-10 px-6 py-10">
      <header className="grid gap-1">
        <h1 className="text-2xl font-bold">اجزای مشترک</h1>
        <p className="text-sm text-muted-foreground">
          این صفحه فقط در محیط توسعه در دسترس است.
        </p>
      </header>

      <Section title="قالب‌بندی">
        <ul className="grid gap-1 text-sm">
          <li>عدد: {formatNumber(TOTAL_ITEMS)}</li>
          <li>تاریخ و ساعت: {formatDateTime('2026-08-29T11:34:31Z')}</li>
          <li>اندازه: {formatBytes(2_411_724)}</li>
        </ul>
      </Section>

      <Section title="صفحه‌بندی (وضعیت در نشانی صفحه)">
        <PaginationBar meta={meta} query={query} itemNoun="پروژه" />
      </Section>

      <Section title="حالت خالی">
        <EmptyState
          icon={FolderOpen}
          title="هنوز پروژه‌ای ندارید"
          description="اولین پروژه خود را بسازید تا اینجا نمایش داده شود."
          action={<Button>ساخت پروژه</Button>}
        />
      </Section>

      <Section title="حالت خطا">
        <div className="grid gap-4">
          <ErrorState
            error={{ status: 403, code: 'forbidden', message: '', fields: {} }}
            onRetry={() => undefined}
          />
          <ErrorState
            error={{ status: 503, code: 'unavailable', message: '', fields: {} }}
            onRetry={() => toast.success('تلاش دوباره انجام شد')}
          />
        </div>
      </Section>

      <Section title="خلاصه خطاهای فرم">
        <FormErrorSummary
          errors={{
            email: { type: 'required', message: 'ایمیل الزامی است' },
            password: { type: 'min', message: 'گذرواژه باید حداقل ۸ نویسه باشد' },
          }}
          labels={{ email: 'ایمیل', password: 'گذرواژه' }}
        />
      </Section>

      <Section title="بارگذاری فایل">
        <FileUploader
          context="generic"
          value={assets}
          onChange={setAssets}
          multiple
          hint="بارگذاری واقعی است و خطاهای سرور بدون تغییر نمایش داده می‌شود."
        />
      </Section>

      <Section title="اعلان و اعلام برای صفحه‌خوان">
        <div className="flex flex-wrap gap-2">
          <Button onClick={() => toast.success('ذخیره شد')}>اعلان موفق</Button>
          <Button variant="destructive" onClick={() => toast.error('ذخیره نشد')}>
            اعلان خطا
          </Button>
          <Button variant="outline" onClick={() => announce('۱۳۷ نتیجه یافت شد')}>
            <AlertCircle size={16} />
            اعلام بی‌صدا
          </Button>
        </div>
      </Section>

      <Section title="ظهور تدریجی هنگام اسکرول">
        <div className="grid gap-3">
          {[0, 1, 2, 3].map((index) => (
            <RevealCard key={index} index={index} />
          ))}
        </div>
        <p className="mt-3 text-xs text-muted-foreground">
          با فعال بودن «کاهش حرکت» در سیستم، همه کارت‌ها بدون انیمیشن نمایش داده می‌شوند.
        </p>
      </Section>
    </div>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="grid gap-3">
      <h2 className="text-sm font-semibold text-muted-foreground">{title}</h2>
      {children}
    </section>
  );
}

function RevealCard({ index }: { index: number }) {
  const { ref, isRevealed } = useReveal();

  return (
    <div
      ref={ref}
      className={`rounded-xl border border-border bg-card p-4 text-sm ${revealClass(isRevealed, {
        delayMs: staggerDelay(index),
      })}`}
    >
      کارت شماره {formatNumber(index + 1)}
    </div>
  );
}
