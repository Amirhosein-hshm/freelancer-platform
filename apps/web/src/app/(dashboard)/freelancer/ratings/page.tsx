import type { Metadata } from 'next';
import { MessageSquareQuote, Star } from 'lucide-react';
import type { FreelancerRatingsResponse } from '@/generated/api/models';
import { AppShell } from '@/components/shell/app-shell';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/empty-state';
import { ErrorState } from '@/components/ui/error-state';
import { PageHeader } from '@/components/ui/page-header';
import { getServerSessionUser, serverGet } from '@/lib/api/server';
import { hasRole, ROLES } from '@/lib/auth/navigation';
import { formatNumber } from '@/lib/format';

export const metadata: Metadata = { title: 'امتیازهای من' };

export default async function FreelancerRatingsPage() {
  const user = await getServerSessionUser();
  if (!hasRole(user, ROLES.freelancer)) {
    return <AppShell user={user}><ErrorState error={{ status: 403, code: 'permission_denied', message: 'این بخش فقط برای نقش فریلنسر در دسترس است.', fields: {} }} /></AppShell>;
  }

  const profileId = user.freelancer_profile_id;
  if (!profileId) {
    return <AppShell user={user}><div className="mx-auto max-w-3xl"><EmptyState icon={Star} title="هنوز پروفایل فریلنسری ندارید" description="پس از تکمیل پروفایل، امتیازهای دریافتی در اینجا نمایش داده می‌شوند." /></div></AppShell>;
  }

  const result = await serverGet<FreelancerRatingsResponse>(`feedback/freelancers/${profileId}/ratings`);
  return (
    <AppShell user={user}>
      <div className="mx-auto grid max-w-5xl gap-6">
        <PageHeader title="امتیازهای من" description="بازخورد مشتریان درباره همکاری‌های تکمیل‌شده." />
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2 text-base"><Star size={18} aria-hidden="true" />میانگین امتیاز</CardTitle></CardHeader>
          <CardContent><p className="text-3xl font-semibold">{result.average_score ?? '—'} <span className="text-sm font-normal text-muted-foreground">از ۵</span></p></CardContent>
        </Card>
        {result.ratings.length === 0 ? <EmptyState icon={MessageSquareQuote} title="هنوز امتیازی ثبت نشده است" description="پس از ثبت امتیاز توسط مشتری، بازخوردها در این صفحه نمایش داده می‌شوند." /> : (
          <Card>
            <CardHeader><CardTitle className="text-base">بازخوردها</CardTitle></CardHeader>
            <CardContent><ul className="divide-y">{result.ratings.map((rating) => <li key={rating.rating_id} className="grid gap-3 py-4 first:pt-0 last:pb-0"><div className="flex flex-wrap items-center justify-between gap-3"><div className="flex items-center gap-2"><span className="font-semibold">{formatNumber(rating.score)} از ۵</span><span aria-label={`${rating.score} از ۵ ستاره`} className="text-amber-600">{'★'.repeat(rating.score)}{'☆'.repeat(5 - rating.score)}</span>{rating.is_public ? <Badge variant="outline">عمومی</Badge> : null}</div><span className="ltr-embedded font-mono text-xs text-muted-foreground">{rating.project_id}</span></div><p className="whitespace-pre-wrap text-sm leading-7">{rating.comment || 'متنی برای این امتیاز ثبت نشده است.'}</p></li>)}</ul></CardContent>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
