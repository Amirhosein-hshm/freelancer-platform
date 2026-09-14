'use client';

import { useId, useState } from 'react';
import { useController, useFormContext } from 'react-hook-form';
import { FormFieldType, type FileAssetResponse, type FormFieldResponse } from '@/generated/api/models';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { FileUploader } from '@/features/files/file-uploader';
import { cn } from '@/lib/utils';
import { isoToTehranLocal, tehranLocalToIso } from '@/lib/format';

/**
 * Renders a form template's fields as the dynamic part of the project form.
 *
 * Every answer is transported as a single string (`FormValueInputRequest.value`),
 * so each type has one documented encoding here:
 *
 * - boolean → `'true'` / `'false'`
 * - multi_select → selected option values joined by `,`
 * - datetime → ISO-8601 UTC, read from the input as Tehran wall time
 * - file → uploaded asset ids joined by `,`
 *
 * The spec does not pin these encodings down — `value` is just a string — so a
 * backend that expects something else will 422, and that message is shown as-is
 * rather than being guessed at a second time.
 *
 * `validation_rules` is an open record the backend interprets; it is deliberately
 * not reimplemented. Only `is_required` is enforced before submitting.
 */
export function TemplateFields({
  fields,
  disabled = false,
}: {
  fields: FormFieldResponse[];
  disabled?: boolean;
}) {
  if (fields.length === 0) return null;

  return (
    <div className="grid gap-5">
      {fields.map((field) => (
        <TemplateField key={field.field_id} field={field} disabled={disabled} />
      ))}
    </div>
  );
}

function TemplateField({ field, disabled }: { field: FormFieldResponse; disabled: boolean }) {
  const form = useFormContext();
  const id = useId();
  const errorId = `${id}-error`;
  const descriptionId = `${id}-description`;

  const { field: controlled, fieldState } = useController({
    control: form.control,
    name: `form_values.${field.field_id}`,
    defaultValue: '',
  });

  const value = typeof controlled.value === 'string' ? controlled.value : '';
  const error = fieldState.error?.message;
  const describedBy = error ? errorId : field.description ? descriptionId : undefined;
  const invalid = error !== undefined;

  return (
    <div className="grid gap-2">
      {/* A checkbox labels itself inline; every other control gets a label above. */}
      {field.field_type === FormFieldType.boolean ? null : (
        <Label htmlFor={id}>
          {field.label}
          {field.is_required ? (
            <span className="text-destructive" aria-hidden="true">
              *
            </span>
          ) : null}
        </Label>
      )}

      <Control
        field={field}
        id={id}
        name={`form_values.${field.field_id}`}
        value={value}
        onChange={controlled.onChange}
        onBlur={controlled.onBlur}
        disabled={disabled}
        invalid={invalid}
        describedBy={describedBy}
      />

      {field.description && !error ? (
        <p id={descriptionId} className="text-xs leading-6 text-muted-foreground">
          {field.description}
        </p>
      ) : null}
      {error ? (
        <p id={errorId} role="alert" className="text-xs leading-6 font-medium text-destructive">
          {error}
        </p>
      ) : null}
    </div>
  );
}

interface ControlProps {
  field: FormFieldResponse;
  id: string;
  name: string;
  value: string;
  onChange: (value: string) => void;
  onBlur: () => void;
  disabled: boolean;
  invalid: boolean;
  describedBy: string | undefined;
}

function Control(props: ControlProps) {
  switch (props.field.field_type) {
    case FormFieldType.textarea:
    case FormFieldType.json:
      return <TextareaControl {...props} />;
    case FormFieldType.boolean:
      return <BooleanControl {...props} />;
    case FormFieldType.select:
      return <SelectControl {...props} />;
    case FormFieldType.multi_select:
      return <MultiSelectControl {...props} />;
    case FormFieldType.file:
      return <FileControl {...props} />;
    case FormFieldType.datetime:
      return <DateTimeControl {...props} />;
    default:
      return <InputControl {...props} />;
  }
}

const HTML_INPUT_TYPES: Partial<Record<FormFieldType, string>> = {
  number: 'number',
  decimal: 'number',
  date: 'date',
  email: 'email',
  phone: 'tel',
  url: 'url',
};

/** Latin-only content sits left-to-right even inside the RTL layout. */
const LTR_FIELD_TYPES: readonly FormFieldType[] = [
  FormFieldType.email,
  FormFieldType.url,
  FormFieldType.phone,
  FormFieldType.number,
  FormFieldType.decimal,
];

function InputControl({ field, id, name, value, onChange, onBlur, disabled, invalid, describedBy }: ControlProps) {
  return (
    <Input
      id={id}
      name={name}
      type={HTML_INPUT_TYPES[field.field_type] ?? 'text'}
      // `decimal` accepts fractions; `number` is whole by default.
      step={field.field_type === FormFieldType.decimal ? 'any' : undefined}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      onBlur={onBlur}
      disabled={disabled}
      dir={LTR_FIELD_TYPES.includes(field.field_type) ? 'ltr' : undefined}
      className={cn('min-h-11', invalid && 'border-destructive')}
      aria-invalid={invalid || undefined}
      aria-describedby={describedBy}
    />
  );
}

function TextareaControl({ id, name, value, onChange, onBlur, disabled, invalid, describedBy }: ControlProps) {
  return (
    <Textarea
      id={id}
      name={name}
      rows={4}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      onBlur={onBlur}
      disabled={disabled}
      className={cn('min-h-24', invalid && 'border-destructive')}
      aria-invalid={invalid || undefined}
      aria-describedby={describedBy}
    />
  );
}

function DateTimeControl({ id, name, value, onChange, onBlur, disabled, invalid, describedBy }: ControlProps) {
  return (
    <Input
      id={id}
      name={name}
      type="datetime-local"
      // Stored as ISO, shown as Tehran wall time.
      value={isoToTehranLocal(value)}
      onChange={(event) => onChange(tehranLocalToIso(event.target.value) ?? '')}
      onBlur={onBlur}
      disabled={disabled}
      dir="ltr"
      className={cn('min-h-11', invalid && 'border-destructive')}
      aria-invalid={invalid || undefined}
      aria-describedby={describedBy}
    />
  );
}

function BooleanControl({ field, id, name, value, onChange, disabled, invalid, describedBy }: ControlProps) {
  return (
    <div className="flex items-center gap-2.5">
      <Checkbox
        id={id}
        name={name}
        checked={value === 'true'}
        onCheckedChange={(checked) => onChange(checked === true ? 'true' : 'false')}
        disabled={disabled}
        aria-invalid={invalid || undefined}
        aria-describedby={describedBy}
      />
      <Label htmlFor={id} className="font-normal">
        {field.label}
        {field.is_required ? (
          <span className="text-destructive" aria-hidden="true">
            *
          </span>
        ) : null}
      </Label>
    </div>
  );
}

function SelectControl({ field, id, name, value, onChange, disabled, invalid, describedBy }: ControlProps) {
  const options = activeOptions(field);
  return (
    <Select value={value} onValueChange={onChange} disabled={disabled}>
      <SelectTrigger
        id={id}
        name={name}
        className={cn('min-h-11 w-full', invalid && 'border-destructive')}
        aria-invalid={invalid || undefined}
        aria-describedby={describedBy}
      >
        <SelectValue placeholder="انتخاب کنید" />
      </SelectTrigger>
      <SelectContent>
        {options.map((option) => (
          <SelectItem key={option.option_id} value={option.value}>
            {option.label}
          </SelectItem>
        ))}
      </SelectContent>
      <input type="hidden" name={name} value={value} />
    </Select>
  );
}

function MultiSelectControl({ field, name, value, onChange, disabled, invalid, describedBy }: ControlProps) {
  const options = activeOptions(field);
  const selected = splitList(value);

  function toggle(optionValue: string, checked: boolean): void {
    const next = checked
      ? [...selected, optionValue]
      : selected.filter((entry) => entry !== optionValue);
    // Keep template order rather than click order, so the value is stable.
    const ordered = options.map((option) => option.value).filter((entry) => next.includes(entry));
    onChange(ordered.join(','));
  }

  return (
    <div
      role="group"
      tabIndex={-1}
      data-form-name={name}
      aria-label={field.label}
      aria-describedby={describedBy}
      className={cn(
        'grid gap-2.5 rounded-lg border border-border p-3',
        invalid && 'border-destructive',
      )}
    >
      {options.map((option) => (
        <div key={option.option_id} className="flex items-center gap-2.5">
          <Checkbox
            id={`${field.field_id}-${option.option_id}`}
            checked={selected.includes(option.value)}
            onCheckedChange={(checked) => toggle(option.value, checked === true)}
            disabled={disabled}
          />
          <Label htmlFor={`${field.field_id}-${option.option_id}`} className="font-normal">
            {option.label}
          </Label>
        </div>
      ))}
      <input type="hidden" name={name} value={value} />
    </div>
  );
}

function FileControl({ field, name, value, onChange, disabled }: ControlProps) {
  // The uploader needs full asset objects to render chips, but only the ids are
  // part of the answer; on an edit the ids arrive without their metadata, so the
  // chips repopulate as files are re-uploaded rather than being reconstructed.
  const [assets, setAssets] = useState<FileAssetResponse[]>([]);
  const ids = splitList(value);

  return (
    <div className="grid gap-2" tabIndex={-1} data-form-name={name}>
      <FileUploader
        context="generic"
        value={assets}
        onChange={(next) => {
          setAssets(next);
          onChange(next.map((asset) => asset.file_asset_id).join(','));
        }}
        multiple={field.is_repeatable}
        disabled={disabled}
        label={field.label}
      />
      {assets.length === 0 && ids.length > 0 ? (
        <p className="text-xs text-muted-foreground">
          {`${ids.length} فایل از قبل ثبت شده است. برای جایگزینی، فایل جدید بارگذاری کنید.`}
        </p>
      ) : null}
      <input type="hidden" name={name} value={value} />
    </div>
  );
}

function activeOptions(field: FormFieldResponse) {
  return field.options
    .filter((option) => option.is_active)
    .sort((a, b) => a.sort_order - b.sort_order);
}

function splitList(value: string): string[] {
  return value
    .split(',')
    .map((entry) => entry.trim())
    .filter((entry) => entry !== '');
}
