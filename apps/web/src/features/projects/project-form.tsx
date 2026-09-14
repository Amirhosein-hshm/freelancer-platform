"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useQuery } from "@tanstack/react-query";
import { FolderPlus, Loader2, Save } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useId, useState } from "react";
import { FormProvider, useForm, useWatch } from "react-hook-form";
import { toast } from "sonner";
import { getCategories } from "@/generated/api/category/category";
import { listFormTemplates } from "@/generated/api/form/form";
import {
  BudgetType,
  FormTemplateStatus,
  FreelancerLevelEnum,
  ProjectPriority,
  ProjectVisibility,
  type CategoryResponse,
  type FormTemplateResponse,
  type ProjectResponse,
} from "@/generated/api/models";
import {
  useCreateProject,
  useUpdateProject,
} from "@/generated/api/project/project";
import {
  AmountField,
  SelectField,
  TextareaField,
  TextField,
} from "@/components/form/fields";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { FormErrorSummary } from "@/components/ui/form-error-summary";
import { Separator } from "@/components/ui/separator";
import {
  ApiError,
  getApiError,
  type NormalizedApiError,
} from "@/lib/api/errors";
import {
  BUDGET_TYPE_LABELS,
  FREELANCER_LEVEL_LABELS,
  PROJECT_PRIORITY_LABELS,
  PROJECT_VISIBILITY_LABELS,
} from "./project-domain";
import {
  toCreateProjectRequest,
  toProjectFormValues,
  toUpdateProjectRequest,
} from "./project-form-data";
import {
  activeTemplateFields,
  buildProjectFormSchema,
  type ProjectFormValues,
} from "./project-schemas";
import { TemplateFields } from "./template-fields";

const PAGE_SIZE = 100;

const DEFAULT_VALUES: ProjectFormValues = {
  category_id: "",
  form_template_id: "",
  title: "",
  description: "",
  visibility: ProjectVisibility.public,
  budget_type: BudgetType.fixed,
  currency_code: "IRR",
  priority: ProjectPriority.normal,
  required_level: "",
  fixed_budget: "",
  budget_min: "",
  budget_max: "",
  application_deadline: "",
  form_values: {},
};

export function ProjectForm({
  project,
  initialCategory,
  initialTemplate,
}: {
  project?: ProjectResponse;
  initialCategory?: CategoryResponse;
  initialTemplate?: FormTemplateResponse;
}) {
  const router = useRouter();
  const [submitError, setSubmitError] = useState<NormalizedApiError | null>(
    null,
  );
  const isEdit = project !== undefined;

  const categoriesQuery = useQuery({
    queryKey: ["project-create", "categories"],
    queryFn: getAllCategories,
    staleTime: 5 * 60_000,
  });

  const form = useForm<ProjectFormValues>({
    resolver: zodResolver(buildProjectFormSchema([])),
    defaultValues: project ? toProjectFormValues(project) : DEFAULT_VALUES,
    mode: "onBlur",
  });
  const categoryId = useWatch({ control: form.control, name: "category_id" });
  const templateId = useWatch({
    control: form.control,
    name: "form_template_id",
  });
  const budgetType = useWatch({ control: form.control, name: "budget_type" });
  const currencyCode = useWatch({
    control: form.control,
    name: "currency_code",
  });

  const templatesQuery = useQuery({
    queryKey: ["project-form", "templates", categoryId],
    queryFn: () => getAllPublishedTemplates(categoryId),
    enabled: categoryId !== "",
    staleTime: 60_000,
  });

  useEffect(() => {
    const error = categoriesQuery.error ?? templatesQuery.error;
    if (error && getApiError(error).status === 401) {
      router.replace("/login?expired=1");
    }
  }, [categoriesQuery.error, router, templatesQuery.error]);

  const categories = mergeCurrentItem(
    categoriesQuery.data,
    initialCategory,
    "category_id",
  );
  const templates = mergeCurrentItem(
    templatesQuery.data,
    initialTemplate?.category_id === categoryId ? initialTemplate : undefined,
    "template_id",
  );
  const selectedTemplate = templates.find(
    (template) => template.template_id === templateId,
  );
  const templateFields = activeTemplateFields(selectedTemplate?.fields);

  const createProject = useCreateProject<ApiError>({
    mutation: {
      onSuccess: (result) => {
        if (result.status !== 201) return;
        toast.success(
          `پروژه ${result.data.data.project_code} به‌صورت پیش‌نویس ساخته شد.`,
        );
        router.replace("/projects");
        router.refresh();
      },
      onError: (error) => {
        const normalized = getApiError(error);
        if (normalized.status === 401) {
          router.replace("/login?expired=1");
          return;
        }
        setSubmitError(normalized);
        applyBackendFieldErrors(form.setError, normalized.fields);
      },
    },
  });

  const updateProject = useUpdateProject<ApiError>({
    mutation: {
      onSuccess: (result) => {
        if (result.status !== 200 || !project) return;
        toast.success(`تغییرات پروژه ${project.project_code} ذخیره شد.`);
        router.replace(`/projects/${project.project_id}`);
        router.refresh();
      },
      onError: handleMutationError,
    },
  });

  function handleMutationError(error: ApiError): void {
    const normalized = getApiError(error);
    if (normalized.status === 401) {
      router.replace("/login?expired=1");
      return;
    }
    setSubmitError(normalized);
    applyBackendFieldErrors(form.setError, normalized.fields);
  }

  const onSubmit = form.handleSubmit((values) => {
    setSubmitError(null);
    const validated = buildProjectFormSchema(templateFields).safeParse(values);
    if (!validated.success) {
      for (const issue of validated.error.issues) {
        form.setError(issue.path.join(".") as keyof ProjectFormValues, {
          type: "client",
          message: issue.message,
        });
      }
      return;
    }
    if (project) {
      updateProject.mutate({
        projectId: project.project_id,
        data: toUpdateProjectRequest(values, templateFields),
      });
      return;
    }
    createProject.mutate({
      data: toCreateProjectRequest(values, templateFields),
    });
  });

  if (categoriesQuery.isPending) {
    return <FormLoading />;
  }
  if (categoriesQuery.isError) {
    return (
      <ErrorState
        error={getApiError(categoriesQuery.error)}
        onRetry={() => void categoriesQuery.refetch()}
      />
    );
  }
  if (categoriesQuery.data.length === 0) {
    return (
      <ErrorState
        error={{
          status: 404,
          code: "no_active_categories",
          message: "دسته‌بندی فعالی برای ساخت پروژه وجود ندارد.",
          fields: {},
        }}
      />
    );
  }

  const labels = buildFieldLabels(templateFields);
  const isPending = createProject.isPending || updateProject.isPending;
  const cancelHref = project ? `/projects/${project.project_id}` : "/projects";

  return (
    <FormProvider {...form}>
      <form onSubmit={onSubmit} noValidate className="grid gap-8">
        <FormErrorSummary errors={form.formState.errors} labels={labels} />

        {submitError ? (
          <Alert variant="destructive" role="alert">
            <AlertTitle>
              {submitError.status === 403
                ? "دسترسی کافی ندارید"
                : isEdit
                  ? "تغییرات ذخیره نشد"
                  : "پروژه ساخته نشد"}
            </AlertTitle>
            <AlertDescription>{submitError.message}</AlertDescription>
          </Alert>
        ) : null}

        <FormSection
          title="دسته‌بندی و قالب"
          description="قالب، اطلاعات تخصصی مورد نیاز پروژه را تعیین می‌کند."
        >
          <div className="grid gap-5 sm:grid-cols-2">
            <SelectField
              label="دسته‌بندی"
              name="category_id"
              required
              disabled={isPending}
              options={categories.map((category) => ({
                value: category.category_id,
                label: category.name,
              }))}
              onValueChange={() => {
                form.setValue("form_template_id", "");
                form.setValue("form_values", {});
                form.clearErrors(["form_template_id", "form_values"]);
              }}
            />
            <SelectField
              label="قالب پروژه"
              name="form_template_id"
              required
              disabled={
                isPending || categoryId === "" || templatesQuery.isPending
              }
              placeholder={
                templatesQuery.isPending
                  ? "در حال دریافت قالب‌ها…"
                  : "قالب را انتخاب کنید"
              }
              options={templates.map((template) => ({
                value: template.template_id,
                label: `${template.name} - نسخه ${template.version_no}`,
              }))}
              onValueChange={() => {
                form.setValue("form_values", {});
                form.clearErrors("form_values");
              }}
            />
          </div>
          {templatesQuery.isError ? (
            <ErrorState
              error={getApiError(templatesQuery.error)}
              onRetry={() => void templatesQuery.refetch()}
              className="py-8"
            />
          ) : null}
          {categoryId !== "" &&
          templatesQuery.isSuccess &&
          templatesQuery.data.length === 0 ? (
            <Alert>
              <AlertTitle>قالب منتشرشده‌ای وجود ندارد</AlertTitle>
              <AlertDescription>
                برای این دسته‌بندی هنوز قالب فعال و منتشرشده‌ای تعریف نشده است.
              </AlertDescription>
            </Alert>
          ) : null}
        </FormSection>

        <Separator />

        <FormSection
          title="مشخصات اصلی"
          description="عنوان و توضیحات روشن، انتخاب فریلنسر مناسب را آسان‌تر می‌کند."
        >
          <TextField
            label="عنوان پروژه"
            name="title"
            required
            maxLength={200}
            disabled={isPending}
          />
          <TextareaField
            label="شرح پروژه"
            name="description"
            required
            rows={6}
            disabled={isPending}
          />
          <div className="grid gap-5 sm:grid-cols-2">
            <SelectField
              label="سطح دسترسی"
              name="visibility"
              required
              disabled={isPending}
              options={enumOptions(
                ProjectVisibility,
                PROJECT_VISIBILITY_LABELS,
              )}
            />
            <SelectField
              label="اولویت"
              name="priority"
              required
              disabled={isPending}
              options={enumOptions(ProjectPriority, PROJECT_PRIORITY_LABELS)}
            />
            <SelectField
              label="حداقل سطح فریلنسر"
              name="required_level"
              emptyLabel="بدون محدودیت سطح"
              disabled={isPending}
              options={enumOptions(
                FreelancerLevelEnum,
                FREELANCER_LEVEL_LABELS,
              )}
            />
            <TextField
              label="مهلت ارسال درخواست"
              name="application_deadline"
              type="datetime-local"
              ltr
              disabled={isPending}
              description="اختیاری؛ زمان بر اساس تهران ثبت می‌شود."
            />
          </div>
        </FormSection>

        <Separator />

        <FormSection
          title="بودجه"
          description="نوع بودجه را انتخاب کنید؛ فقط مبلغ‌های مرتبط ارسال می‌شوند."
        >
          <div className="grid gap-5 sm:grid-cols-2">
            <SelectField
              label="نوع بودجه"
              name="budget_type"
              required
              disabled={isPending}
              options={enumOptions(BudgetType, BUDGET_TYPE_LABELS)}
              onValueChange={(value) => {
                if (value !== BudgetType.fixed && value !== BudgetType.hourly) {
                  form.setValue("fixed_budget", "");
                  form.clearErrors("fixed_budget");
                }
                if (value !== BudgetType.range) {
                  form.setValue("budget_min", "");
                  form.setValue("budget_max", "");
                  form.clearErrors(["budget_min", "budget_max"]);
                }
              }}
            />
            <TextField
              label="کد واحد پول"
              name="currency_code"
              required
              ltr
              maxLength={8}
              disabled={isPending}
              description="برای نمونه IRR، IRT یا USD؛ مقدار نهایی را سرور اعتبارسنجی می‌کند."
            />
          </div>
          {budgetType === BudgetType.fixed ||
          budgetType === BudgetType.hourly ? (
            <AmountField
              label={
                budgetType === BudgetType.hourly ? "نرخ هر ساعت" : "مبلغ بودجه"
              }
              name="fixed_budget"
              required
              currency={currencyCode}
              disabled={isPending}
            />
          ) : null}
          {budgetType === BudgetType.range ? (
            <div className="grid gap-5 sm:grid-cols-2">
              <AmountField
                label="کمینه بودجه"
                name="budget_min"
                required
                currency={currencyCode}
                disabled={isPending}
              />
              <AmountField
                label="بیشینه بودجه"
                name="budget_max"
                required
                currency={currencyCode}
                disabled={isPending}
              />
            </div>
          ) : null}
        </FormSection>

        {selectedTemplate ? (
          <>
            <Separator />
            <FormSection
              title="اطلاعات تخصصی پروژه"
              description={`فیلدهای قالب «${selectedTemplate.name}» را تکمیل کنید.`}
            >
              {templateFields.length > 0 ? (
                <TemplateFields fields={templateFields} disabled={isPending} />
              ) : (
                <p className="text-sm text-muted-foreground">
                  این قالب فیلد تکمیلی ندارد.
                </p>
              )}
            </FormSection>
          </>
        ) : null}

        <div className="flex flex-col-reverse gap-3 border-t border-border pt-6 sm:flex-row sm:justify-end">
          <Button
            type="button"
            variant="outline"
            disabled={isPending}
            onClick={() => router.push(cancelHref)}
          >
            انصراف
          </Button>
          <Button
            type="submit"
            disabled={isPending || !selectedTemplate}
            className="min-h-11 sm:min-w-44"
          >
            {isPending ? (
              <Loader2 size={16} className="animate-spin" aria-hidden="true" />
            ) : isEdit ? (
              <Save size={16} aria-hidden="true" />
            ) : (
              <FolderPlus size={16} aria-hidden="true" />
            )}
            {isPending
              ? isEdit
                ? "در حال ذخیره تغییرات…"
                : "در حال ساخت پروژه…"
              : isEdit
                ? "ذخیره تغییرات"
                : "ساخت پیش‌نویس پروژه"}
          </Button>
        </div>
      </form>
    </FormProvider>
  );
}

function FormSection({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  const titleId = useId();
  return (
    <section aria-labelledby={titleId} className="grid gap-5">
      <div className="grid gap-1">
        <h2 id={titleId} className="text-base font-semibold">
          {title}
        </h2>
        <p className="text-sm leading-6 text-muted-foreground">{description}</p>
      </div>
      {children}
    </section>
  );
}

function FormLoading() {
  return (
    <div
      role="status"
      className="grid min-h-48 place-items-center gap-3 rounded-lg border border-border"
    >
      <Loader2
        size={22}
        className="animate-spin text-primary"
        aria-hidden="true"
      />
      <p className="text-sm text-muted-foreground">
        در حال آماده‌سازی فرم پروژه…
      </p>
    </div>
  );
}

async function getAllCategories(): Promise<CategoryResponse[]> {
  const first = await getCategories({ page: 1, page_size: PAGE_SIZE });
  if (first.status !== 200) return [];
  const pages = await remainingPages(
    first.data.meta?.total_pages ?? 1,
    (page) => getCategories({ page, page_size: PAGE_SIZE }),
  );
  return [first, ...pages]
    .flatMap((response) => (response.status === 200 ? response.data.data : []))
    .filter((category) => category.is_active)
    .sort(
      (a, b) =>
        a.sort_order - b.sort_order || a.name.localeCompare(b.name, "fa"),
    );
}

async function getAllPublishedTemplates(
  categoryId: string,
): Promise<FormTemplateResponse[]> {
  const params = {
    category_id: categoryId,
    status: FormTemplateStatus.published,
    page: 1,
    page_size: PAGE_SIZE,
  };
  const first = await listFormTemplates(params);
  if (first.status !== 200) return [];
  const pages = await remainingPages(
    first.data.meta?.total_pages ?? 1,
    (page) => listFormTemplates({ ...params, page }),
  );
  return [first, ...pages]
    .flatMap((response) =>
      response.status === 200 ? response.data.data.templates : [],
    )
    .filter(
      (template) =>
        template.is_active && template.status === FormTemplateStatus.published,
    )
    .sort(
      (a, b) =>
        a.name.localeCompare(b.name, "fa") || b.version_no - a.version_no,
    );
}

async function remainingPages<T>(
  totalPages: number,
  load: (page: number) => Promise<T>,
): Promise<T[]> {
  if (totalPages <= 1) return [];
  return Promise.all(
    Array.from({ length: totalPages - 1 }, (_, index) => load(index + 2)),
  );
}

function enumOptions<T extends Record<string, string>>(
  values: T,
  labels: Record<T[keyof T], string>,
) {
  return Object.values(values).map((value) => ({
    value,
    label: labels[value as T[keyof T]],
  }));
}

function buildFieldLabels(
  fields: FormTemplateResponse["fields"],
): Record<string, string> {
  return {
    category_id: "دسته‌بندی",
    form_template_id: "قالب پروژه",
    title: "عنوان پروژه",
    description: "شرح پروژه",
    visibility: "سطح دسترسی",
    budget_type: "نوع بودجه",
    currency_code: "واحد پول",
    priority: "اولویت",
    required_level: "حداقل سطح فریلنسر",
    fixed_budget: "مبلغ بودجه",
    budget_min: "کمینه بودجه",
    budget_max: "بیشینه بودجه",
    application_deadline: "مهلت ارسال درخواست",
    ...Object.fromEntries(
      fields.map((field) => [`form_values.${field.field_id}`, field.label]),
    ),
  };
}

function applyBackendFieldErrors(
  setError: ReturnType<typeof useForm<ProjectFormValues>>["setError"],
  fields: Record<string, string>,
): void {
  const known = new Set(Object.keys(DEFAULT_VALUES));
  for (const [field, message] of Object.entries(fields)) {
    if (known.has(field)) {
      setError(field as keyof ProjectFormValues, { type: "server", message });
    }
  }
}

function mergeCurrentItem<T, K extends keyof T>(
  items: T[] | undefined,
  current: T | undefined,
  key: K,
): T[] {
  const available = items ?? [];
  if (!current || available.some((item) => item[key] === current[key]))
    return available;
  return [current, ...available];
}
