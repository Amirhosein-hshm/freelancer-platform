import { describe, expect, it } from 'vitest';
import {
  BudgetType,
  ProjectPriority,
  ProjectStatus,
  ProjectVisibility,
  type FormFieldResponse,
  type ProjectResponse,
} from '@/generated/api/models';
import {
  toCreateProjectRequest,
  toProjectFormValues,
  toUpdateProjectRequest,
} from './project-form-data';
import type { ProjectFormValues } from './project-schemas';

const base: ProjectFormValues = {
  category_id: 'category-ignored',
  form_template_id: 'template-1',
  title: '  پروژه نمونه  ',
  description: '  توضیحات کامل پروژه  ',
  visibility: ProjectVisibility.public,
  budget_type: BudgetType.fixed,
  currency_code: 'IRR',
  priority: ProjectPriority.normal,
  required_level: '',
  fixed_budget: '1200000',
  budget_min: '',
  budget_max: '',
  application_deadline: '',
  form_values: {},
};

describe('toCreateProjectRequest', () => {
  it('omits category and irrelevant budget values', () => {
    const request = toCreateProjectRequest(base, []);

    expect(request).toEqual({
      form_template_id: 'template-1',
      title: 'پروژه نمونه',
      description: 'توضیحات کامل پروژه',
      visibility: ProjectVisibility.public,
      budget_type: BudgetType.fixed,
      currency_code: 'IRR',
      required_level: null,
      fixed_budget: '1200000',
      budget_min: null,
      budget_max: null,
      priority: ProjectPriority.normal,
      application_deadline: null,
      form_values: [],
    });
    expect(request).not.toHaveProperty('category_id');
  });

  it('sends only answered active template fields and converts Tehran deadline', () => {
    const fields = [field('one'), field('two')];
    const request = toCreateProjectRequest(
      {
        ...base,
        budget_type: BudgetType.range,
        fixed_budget: '999',
        budget_min: '100',
        budget_max: '200',
        application_deadline: '2026-09-01T12:00',
        form_values: { one: 'پاسخ', two: '' },
      },
      fields,
    );

    expect(request.fixed_budget).toBeNull();
    expect(request.budget_min).toBe('100');
    expect(request.budget_max).toBe('200');
    expect(request.application_deadline).toBe('2026-09-01T08:30:00.000Z');
    expect(request.form_values).toEqual([{ field_id: 'one', value: 'پاسخ' }]);
  });
});

describe('project editing data', () => {
  it('builds the same full replacement shape without category_id', () => {
    const request = toUpdateProjectRequest(base, []);

    expect(request).toEqual(toCreateProjectRequest(base, []));
    expect(request).not.toHaveProperty('category_id');
  });

  it('prefills every editable value, including template answers and Tehran time', () => {
    const project = {
      project_id: 'project-1',
      project_code: 'PRJ-1',
      customer_user_id: 'customer-1',
      category_id: 'category-1',
      form_template_id: 'template-1',
      form_values: [
        { field_id: 'field-1', value: 'پاسخ' },
        { field_id: 'field-2', value: 'false' },
      ],
      required_level: null,
      title: 'عنوان',
      description: 'توضیحات کامل پروژه',
      status: ProjectStatus.draft,
      visibility: ProjectVisibility.private,
      priority: ProjectPriority.high,
      budget: {
        budget_type: BudgetType.range,
        fixed_amount: null,
        min_amount: '100',
        max_amount: '200',
        currency_code: 'USD',
      },
      selected_application_id: null,
      application_deadline: '2026-09-01T08:30:00.000Z',
      created_by_user_id: 'customer-1',
      created_at: '2026-08-30T00:00:00.000Z',
    } as unknown as ProjectResponse;

    expect(toProjectFormValues(project)).toEqual({
      category_id: 'category-1',
      form_template_id: 'template-1',
      title: 'عنوان',
      description: 'توضیحات کامل پروژه',
      visibility: ProjectVisibility.private,
      budget_type: BudgetType.range,
      currency_code: 'USD',
      priority: ProjectPriority.high,
      required_level: '',
      fixed_budget: '',
      budget_min: '100',
      budget_max: '200',
      application_deadline: '2026-09-01T12:00',
      form_values: { 'field-1': 'پاسخ', 'field-2': 'false' },
    });
    expect(toProjectFormValues({ ...project, form_template_id: 'template-version-2' }).form_template_id)
      .toBe('template-version-2');
  });
});

function field(fieldId: string): FormFieldResponse {
  return {
    field_id: fieldId,
    field_key: fieldId,
    label: fieldId,
    description: null,
    field_type: 'text',
    is_required: false,
    is_repeatable: false,
    is_unique: false,
    sort_order: 0,
    validation_rules: {},
    is_active: true,
    options: [],
  };
}
