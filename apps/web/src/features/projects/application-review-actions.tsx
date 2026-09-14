"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useQueryClient } from "@tanstack/react-query";
import { Check, X } from "lucide-react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import {
  useAcceptFreelancer,
  useRejectFreelancerApplication,
} from "@/generated/api/project/project";
import { ActionDialog } from "@/components/ui/action-dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ApiError, getApiError } from "@/lib/api/errors";

const rejectSchema = z.object({ note: z.string().trim() });
type RejectValues = z.infer<typeof rejectSchema>;

export function ApplicationReviewActions({
  projectId,
  applicationId,
}: {
  projectId: string;
  applicationId: string;
}) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const rejectForm = useForm<RejectValues>({
    resolver: zodResolver(rejectSchema),
    defaultValues: { note: "" },
    mode: "onBlur",
  });
  const accept = useAcceptFreelancer<ApiError>();
  const reject = useRejectFreelancerApplication<ApiError>();
  const pending = accept.isPending || reject.isPending;

  async function finish(message: string): Promise<void> {
    toast.success(message);
    await queryClient.invalidateQueries({ queryKey: ["project", projectId] });
    await queryClient.invalidateQueries({
      queryKey: [`/api/v1/projects/${projectId}/applications`],
    });
    router.refresh();
  }

  function rethrow(error: unknown): never {
    const normalized = getApiError(error);
    throw new ApiError(
      normalized.status,
      normalized.code,
      normalized.message,
      normalized.fields,
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      <ActionDialog
        trigger={
          <button
            type="button"
            className="inline-flex min-h-10 items-center gap-1.5 rounded-lg border border-success bg-success px-3 py-2 text-xs font-semibold text-success-foreground"
            disabled={pending}
          >
            <Check size={15} aria-hidden="true" />
            پذیرش
          </button>
        }
        title="پذیرش درخواست"
        description="با پذیرش این درخواست، فریلنسر انتخاب‌شده و وضعیت پروژه توسط سرور به‌روزرسانی می‌شود."
        confirmLabel="پذیرش درخواست"
        pendingLabel="در حال پذیرش…"
        onConfirm={async () => {
          try {
            const result = await accept.mutateAsync({
              projectId,
              applicationId,
            });
            if (result.status !== 200)
              throw new Error("پاسخ نامعتبر از سرور دریافت شد.");
          } catch (error) {
            rethrow(error);
          }
        }}
        onDone={() => void finish("درخواست پذیرفته شد.")}
      />
      <ActionDialog
        trigger={
          <button
            type="button"
            className="inline-flex min-h-10 items-center gap-1.5 rounded-lg border border-destructive bg-destructive px-3 py-2 text-xs font-semibold text-destructive-foreground"
            disabled={pending}
          >
            <X size={15} aria-hidden="true" />
            رد درخواست
          </button>
        }
        title="رد درخواست"
        description="در صورت نیاز، دلیل رد درخواست را ثبت کنید."
        confirmLabel="رد درخواست"
        pendingLabel="در حال رد درخواست…"
        destructive
        onConfirm={async () => {
          const valid = await rejectForm.trigger();
          if (!valid) return;
          try {
            const result = await reject.mutateAsync({
              projectId,
              applicationId,
              data: { note: rejectForm.getValues("note") || null },
            });
            if (result.status !== 200)
              throw new Error("پاسخ نامعتبر از سرور دریافت شد.");
          } catch (error) {
            rethrow(error);
          }
        }}
        onDone={() => {
          rejectForm.reset();
          void finish("درخواست رد شد.");
        }}
      >
        <div className="grid gap-2">
          <Label htmlFor={`reject-note-${applicationId}`}>
            دلیل رد درخواست (اختیاری)
          </Label>
          <Input
            id={`reject-note-${applicationId}`}
            {...rejectForm.register("note")}
          />
        </div>
      </ActionDialog>
    </div>
  );
}
