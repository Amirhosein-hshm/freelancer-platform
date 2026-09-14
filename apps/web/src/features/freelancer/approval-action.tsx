'use client';

import { Send } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { useSubmitFreelancerApproval } from '@/generated/api/freelancer/freelancer';
import { ActionDialog } from '@/components/ui/action-dialog';
import { Button } from '@/components/ui/button';
import { ApiError, getApiError } from '@/lib/api/errors';

export function ApprovalAction({ profileId, status }: { profileId: string; status: string }) {
  const router = useRouter();
  const mutation = useSubmitFreelancerApproval<ApiError>();
  if (status === 'approved' || status === 'suspended') return null;
  return <ActionDialog trigger={<Button><Send size={16} />ارسال برای تأیید</Button>} title="ارسال پروفایل برای تأیید" description="پیش‌نیازهای تأیید را سرور بررسی می‌کند. پس از ارسال، وضعیت نهایی توسط مدیر سامانه تعیین می‌شود." confirmLabel="ارسال درخواست" pendingLabel="در حال ارسال…" onConfirm={async () => {
    try { await mutation.mutateAsync({ profileId }); }
    catch (error) { const normalized = getApiError(error); if (normalized.status === 401) router.replace('/login?expired=1'); throw error; }
  }} onDone={() => { toast.success('درخواست تأیید ارسال شد.'); router.refresh(); }} />;
}
