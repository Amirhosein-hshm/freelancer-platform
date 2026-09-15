import { Check, FileText, MessageCircle, ShieldCheck } from 'lucide-react';

const workflowSteps = [
  {
    number: '۰۱',
    title: 'تعریف دقیق',
    description: 'نیاز، بودجه و خروجی‌های پروژه از همان ابتدا شفاف ثبت می‌شود.',
    Icon: FileText,
  },
  {
    number: '۰۲',
    title: 'همکاری مستقیم',
    description: 'گفتگوها، فایل‌ها و تصمیم‌ها در یک محیط یکپارچه پیگیری می‌شوند.',
    Icon: MessageCircle,
  },
  {
    number: '۰۳',
    title: 'بازبینی مستقل',
    description: 'تحویل‌ها پیش از تایید، توسط ناظر متخصص ارزیابی کیفی می‌شوند.',
    Icon: ShieldCheck,
  },
  {
    number: '۰۴',
    title: 'تحویل و تسویه',
    description: 'هر مرحله با اطمینان ثبت و تسویه حساب با رضایت دوطرف انجام می‌شود.',
    Icon: Check,
  },
] as const;

export function DashboardWorkflow() {
  return (
    <section aria-labelledby="workflow-heading" className="rounded-2xl border border-border bg-card p-6 shadow-xs sm:p-7">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border pb-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-[#e66042]">
            <span className="h-[2px] w-5 bg-[#e66042]" />
            روش کار دیدار
          </div>
          <h2 id="workflow-heading" className="mt-1 text-lg font-bold">
            مسیر استاندارد پروژه‌ها در دیدار
          </h2>
        </div>
        <span className="text-xs text-muted-foreground">فرآیند ۴ مرحله‌ای شفاف و قابل اطمینان</span>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {workflowSteps.map((step) => {
          const Icon = step.Icon;
          return (
            <div
              key={step.number}
              className="relative rounded-xl border border-border/80 bg-muted/30 p-4 transition-colors hover:border-[#e66042]/40 hover:bg-muted/50"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-extrabold text-[#e66042]">
                  {step.number}
                </span>
                <span className="grid size-7 place-items-center rounded-md bg-background text-muted-foreground shadow-xs">
                  <Icon size={15} />
                </span>
              </div>
              <h3 className="mt-3 text-sm font-bold text-foreground">{step.title}</h3>
              <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">
                {step.description}
              </p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
