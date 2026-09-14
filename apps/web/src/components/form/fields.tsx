'use client';

import { useId, useState, type ReactNode } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { type FieldErrors, useController, useFormContext, useFormState } from 'react-hook-form';
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
import { cn } from '@/lib/utils';

/**
 * Form controls wired to the surrounding react-hook-form.
 *
 * Every field registers itself and reads its own error, rather than taking
 * values and errors as props. A `name` prop alone would render an input the form
 * never sees — which is exactly how the login form once failed: every submit
 * validated the untouched `defaultValues` and reported required fields as empty.
 * Registration is now impossible to forget.
 *
 * All of these require a `<FormProvider>` (react-hook-form) ancestor.
 */

interface BaseFieldProps {
  label: string;
  name: string;
  disabled?: boolean;
  /** Extra description, announced only while the field has no error. */
  description?: string;
  required?: boolean;
  className?: string;
}

interface TextFieldProps extends BaseFieldProps {
  type?: 'text' | 'email' | 'password' | 'tel' | 'url' | 'date' | 'datetime-local';
  placeholder?: string;
  /** Latin content (email, password, amounts) renders LTR inside the RTL layout. */
  ltr?: boolean;
  autoComplete?: string;
  inputMode?: 'text' | 'numeric' | 'decimal' | 'email' | 'tel' | 'url';
  maxLength?: number;
  /** Rendered after the input, e.g. a currency suffix. */
  suffix?: ReactNode;
}

export function TextField({
  label,
  name,
  type = 'text',
  placeholder,
  ltr = false,
  autoComplete,
  inputMode,
  maxLength,
  disabled,
  description,
  required,
  suffix,
  className,
}: TextFieldProps) {
  const form = useRequiredFormContext();
  const error = useFieldError(name);
  const ids = useFieldIds();
  const [visible, setVisible] = useState(false);

  const isPassword = type === 'password';
  const inputType = isPassword && visible ? 'text' : type;

  return (
    <FieldShell
      label={label}
      htmlFor={ids.id}
      error={error}
      description={description}
      required={required}
      ids={ids}
      className={className}
    >
      <div className="relative">
        <Input
          // Spread first: `register` supplies name, onChange, onBlur and the ref
          // that connects this input to the form. Everything below overrides
          // presentation only.
          {...form.register(name)}
          id={ids.id}
          type={inputType}
          placeholder={placeholder}
          autoComplete={autoComplete}
          inputMode={inputMode}
          maxLength={maxLength}
          disabled={disabled}
          dir={ltr ? 'ltr' : undefined}
          className={cn(
            'min-h-11',
            isPassword && 'pe-12 text-start',
            suffix && 'pe-16',
            error && 'border-destructive',
          )}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy(error, description, ids)}
        />
        {isPassword ? (
          <button
            type="button"
            onClick={() => setVisible((value) => !value)}
            aria-label={visible ? 'پنهان کردن رمز' : 'نمایش رمز'}
            className="absolute inset-y-0 end-2 z-10 my-auto grid size-9 place-items-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
          >
            {visible ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        ) : null}
        {suffix ? (
          <span
            className="pointer-events-none absolute inset-y-0 end-3 my-auto h-fit text-xs text-muted-foreground"
            aria-hidden="true"
          >
            {suffix}
          </span>
        ) : null}
      </div>
    </FieldShell>
  );
}

interface TextareaFieldProps extends BaseFieldProps {
  placeholder?: string;
  rows?: number;
}

export function TextareaField({
  label,
  name,
  placeholder,
  rows = 5,
  disabled,
  description,
  required,
  className,
}: TextareaFieldProps) {
  const form = useRequiredFormContext();
  const error = useFieldError(name);
  const ids = useFieldIds();

  return (
    <FieldShell
      label={label}
      htmlFor={ids.id}
      error={error}
      description={description}
      required={required}
      ids={ids}
      className={className}
    >
      <Textarea
        {...form.register(name)}
        id={ids.id}
        rows={rows}
        placeholder={placeholder}
        disabled={disabled}
        className={cn('min-h-24', error && 'border-destructive')}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy(error, description, ids)}
      />
    </FieldShell>
  );
}

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

interface SelectFieldProps extends BaseFieldProps {
  options: SelectOption[];
  placeholder?: string;
  /** Label for the option that clears the field; omit to make it unclearable. */
  emptyLabel?: string;
  onValueChange?: (value: string) => void;
}

/**
 * A `Select` is a controlled Radix widget rather than a native `<select>`, so it
 * goes through `useController` instead of `register`. A hidden native input
 * carries the field `name` so `FormErrorSummary` can still focus it.
 */
export function SelectField({
  label,
  name,
  options,
  placeholder = 'انتخاب کنید',
  emptyLabel,
  onValueChange,
  disabled,
  description,
  required,
  className,
}: SelectFieldProps) {
  const form = useRequiredFormContext();
  const error = useFieldError(name);
  const ids = useFieldIds();

  const { field } = useController({ control: form.control, name, defaultValue: '' });
  const value = typeof field.value === 'string' ? field.value : '';

  // Radix treats '' as "no value", so a clear option needs a real sentinel.
  const EMPTY = '__empty__';

  return (
    <FieldShell
      label={label}
      htmlFor={ids.id}
      error={error}
      description={description}
      required={required}
      ids={ids}
      className={className}
    >
      <Select
        value={value === '' ? undefined : value}
        onValueChange={(next) => {
          const resolved = next === EMPTY ? '' : next;
          field.onChange(resolved);
          onValueChange?.(resolved);
        }}
        disabled={disabled}
      >
        <SelectTrigger
          id={ids.id}
          className={cn('min-h-11 w-full', error && 'border-destructive')}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy(error, description, ids)}
        >
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent>
          {emptyLabel ? <SelectItem value={EMPTY}>{emptyLabel}</SelectItem> : null}
          {options.map((option) => (
            <SelectItem key={option.value} value={option.value} disabled={option.disabled}>
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <input type="hidden" name={name} value={value} />
    </FieldShell>
  );
}

/** Money input: Latin digits, no grouping, so the backend's decimal pattern matches. */
export function AmountField({
  currency,
  ...props
}: Omit<TextFieldProps, 'type' | 'ltr' | 'inputMode' | 'suffix'> & { currency?: string }) {
  return (
    <TextField
      {...props}
      type="text"
      ltr
      inputMode="decimal"
      placeholder={props.placeholder ?? '0'}
      suffix={currency}
    />
  );
}

function FieldShell({
  label,
  htmlFor,
  error,
  description,
  required,
  ids,
  className,
  children,
}: {
  label: string;
  htmlFor: string;
  error: string | undefined;
  description: string | undefined;
  required: boolean | undefined;
  ids: FieldIds;
  className?: string;
  children: ReactNode;
}) {
  return (
    <div className={cn('grid gap-2', className)}>
      <Label htmlFor={htmlFor}>
        {label}
        {required ? (
          <span className="text-destructive" aria-hidden="true">
            *
          </span>
        ) : null}
      </Label>
      {children}
      {description && !error ? (
        <p id={ids.descriptionId} className="text-xs leading-6 text-muted-foreground">
          {description}
        </p>
      ) : null}
      {error ? (
        <p id={ids.errorId} role="alert" className="text-xs leading-6 font-medium text-destructive">
          {error}
        </p>
      ) : null}
    </div>
  );
}

interface FieldIds {
  id: string;
  errorId: string;
  descriptionId: string;
}

function useFieldIds(): FieldIds {
  const id = useId();
  return { id, errorId: `${id}-error`, descriptionId: `${id}-description` };
}

function useRequiredFormContext() {
  const form = useFormContext();
  if (form === null) {
    throw new Error('Form fields must be rendered inside a react-hook-form <FormProvider>.');
  }
  return form;
}

/** Scoped subscription: a field re-renders on its own state changes only. */
function useFieldError(name: string): string | undefined {
  const form = useRequiredFormContext();
  const { errors } = useFormState({ control: form.control, name });
  return getFieldMessage(errors, name);
}

function describedBy(
  error: string | undefined,
  description: string | undefined,
  ids: FieldIds,
): string | undefined {
  if (error) return ids.errorId;
  if (description) return ids.descriptionId;
  return undefined;
}

/** Reads `errors` at a dotted path, so nested field names keep working. */
export function getFieldMessage(errors: FieldErrors, name: string): string | undefined {
  let node: unknown = errors;
  for (const segment of name.split('.')) {
    if (typeof node !== 'object' || node === null) return undefined;
    node = (node as Record<string, unknown>)[segment];
  }
  const message = (node as { message?: unknown } | undefined)?.message;
  return typeof message === 'string' && message !== '' ? message : undefined;
}
