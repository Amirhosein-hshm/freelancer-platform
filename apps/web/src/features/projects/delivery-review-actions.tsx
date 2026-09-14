"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { useQueryClient } from "@tanstack/react-query";
import { Check, X } from "lucide-react";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { z } from "zod";
import { useReviewDelivery } from "@/generated/api/review/review";
import {
  ReviewStatus,
  type ReviewStatus as ReviewStatusType,
} from "@/generated/api/models";
import { ActionDialog } from "@/components/ui/action-dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ApiError, getApiError } from "@/lib/api/errors";

const schema = z.object({
  reason: z.string().trim().min(1, "دلیل درخواست اصلاح را وارد کنید."),
});
type Values = z.infer<typeof schema>;

export function DeliveryReviewActions({
  deliveryId,
  projectId,
}: {
  deliveryId: string;
  projectId: string;
}) {
  const queryClient = useQueryClient();
  const router = useRouter();
  const review = useReviewDelivery<ApiError>();
  const form = useForm<Values>({
    resolver: zodResolver(schema),
    defaultValues: { reason: "" },
    mode: "onBlur",
  });
  async function submit(decision: ReviewStatusType, reason?: string) {
    try {
      const result = await review.mutateAsync({
        deliveryId,
        data: {
          decision,
          reject_reason: reason ?? null,
          notes: reason ?? null,
        },
      });
      if (result.status !== 200)
        throw new Error("پاسخ نامعتبر از سرور دریافت شد.");
    } catch (error) {
      const e = getApiError(error);
      throw new ApiError(e.status, e.code, e.message, e.fields);
    }
  }
  async function done(message: string) {
    const { toast } = await import("sonner");
    toast.success(message);
    await queryClient.invalidateQueries({ queryKey: ["project", projectId] });
    router.refresh();
  }
  return (
    <div className="flex flex-wrap gap-2">
      <ActionDialog
        trigger={
          <Button type="button" variant="success" size="sm" disabled={review.isPending}>
            <Check size={15} aria-hidden="true" />
            تأیید تحویل
          </Button>
        }
        title="تأیید تحویل"
        description="با تأیید این تحویل، پروژه طبق وضعیت فعلی به مرحله تکمیل می‌رسد."
        confirmLabel="تأیید تحویل"
        pendingLabel="در حال تأیید…"
        onConfirm={() => submit(ReviewStatus.approved)}
        onDone={() => void done("تحویل تأیید شد.")}
      />
      <ActionDialog
        trigger={
          <Button type="button" variant="destructive" size="sm" disabled={review.isPending}>
            <X size={15} aria-hidden="true" />
            درخواست اصلاح
          </Button>
        }
        title="درخواست اصلاح"
        description="دلیل اصلاح برای فریلنسر ارسال می‌شود. حداکثر سه دور اصلاح مجاز است."
        confirmLabel="ثبت درخواست اصلاح"
        pendingLabel="در حال ثبت…"
        destructive
        disabled={!form.formState.isValid}
        onConfirm={async () => {
          if (!(await form.trigger())) return;
          await submit(ReviewStatus.rejected, form.getValues("reason"));
        }}
        onDone={() => {
          form.reset();
          void done("درخواست اصلاح ثبت شد.");
        }}
      >
        <div className="grid gap-2">
          <Label htmlFor={`revision-reason-${deliveryId}`}>
            دلیل درخواست اصلاح
          </Label>
          <Input
            id={`revision-reason-${deliveryId}`}
            {...form.register("reason")}
          />
          {form.formState.errors.reason ? (
            <p className="text-sm text-destructive">
              {form.formState.errors.reason.message}
            </p>
          ) : null}
        </div>
      </ActionDialog>
    </div>
  );
}
