import {
  BudgetType,
  type CreateProjectRequest,
  type FormFieldResponse,
  type ProjectResponse,
  type UpdateProjectRequest,
} from '@/generated/api/models';
import { isoToTehranLocal, tehranLocalToIso } from '@/lib/format';
import type { ProjectFormValues } from './project-schemas';

// Keep request construction separate from the component so create and edit can
// share the exact encoding rules without duplicating contract-shaped logic.
export function toCreateProjectRequest(
  values: ProjectFormValues,
  fields: FormFieldResponse[],
): CreateProjectRequest {
  return toProjectRequest(values, fields);
}

export function toUpdateProjectRequest(
  values: ProjectFormValues,
  fields: FormFieldResponse[],
): UpdateProjectRequest {
  return toProjectRequest(values, fields);
}

export function toProjectFormValues(project: ProjectResponse): ProjectFormValues {
  return {
    category_id: project.category_id,
    form_template_id: project.form_template_id,
    title: project.title,
    description: project.description,
    visibility: project.visibility,
    budget_type: project.budget.budget_type,
    currency_code: project.budget.currency_code,
    priority: project.priority,
    required_level: project.required_level ?? '',
    fixed_budget: project.budget.fixed_amount ?? '',
    budget_min: project.budget.min_amount ?? '',
    budget_max: project.budget.max_amount ?? '',
    application_deadline: isoToTehranLocal(project.application_deadline),
    form_values: Object.fromEntries(
      (project.form_values ?? []).map(({ field_id, value }) => [field_id, value]),
    ),
  };
}

function toProjectRequest(
  values: ProjectFormValues,
  fields: FormFieldResponse[],
): CreateProjectRequest {
  const usesSingleAmount =
    values.budget_type === BudgetType.fixed || values.budget_type === BudgetType.hourly;
  const usesRange = values.budget_type === BudgetType.range;

  return {
    form_template_id: values.form_template_id,
    title: values.title.trim(),
    description: values.description.trim(),
    visibility: values.visibility,
    budget_type: values.budget_type,
    currency_code: values.currency_code.trim(),
    required_level: values.required_level === '' ? null : values.required_level,
    fixed_budget: usesSingleAmount && values.fixed_budget !== '' ? values.fixed_budget : null,
    budget_min: usesRange && values.budget_min !== '' ? values.budget_min : null,
    budget_max: usesRange && values.budget_max !== '' ? values.budget_max : null,
    priority: values.priority,
    application_deadline:
      values.application_deadline === '' ? null : tehranLocalToIso(values.application_deadline),
    form_values: fields.flatMap((field) => {
      const value = values.form_values[field.field_id] ?? '';
      return value === '' ? [] : [{ field_id: field.field_id, value }];
    }),
  };
}
