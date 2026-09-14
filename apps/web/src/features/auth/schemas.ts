import { z } from 'zod';

const emailSchema = z
  .string()
  .trim()
  .min(1, 'ایمیل را وارد کنید.')
  .email('قالب ایمیل معتبر نیست.');

export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'رمز عبور را وارد کنید.'),
});

export type LoginValues = z.infer<typeof loginSchema>;

export const REGISTER_ROLES = [
  { value: 'customer', label: 'مشتری', hint: 'پروژه تعریف می‌کنم و متخصص انتخاب می‌کنم.' },
  { value: 'freelancer', label: 'فریلنسر', hint: 'به پروژه‌ها درخواست می‌دهم و تحویل می‌کنم.' },
] as const;

export const registerSchema = z
  .object({
    first_name: z.string().trim().min(1, 'نام را وارد کنید.').max(80, 'نام حداکثر ۸۰ نویسه است.'),
    last_name: z.string().trim().min(1, 'نام خانوادگی را وارد کنید.').max(80, 'نام خانوادگی حداکثر ۸۰ نویسه است.'),
    email: emailSchema,
    password: z.string().min(8, 'رمز عبور باید حداقل ۸ نویسه باشد.'),
    confirm_password: z.string().min(1, 'تکرار رمز عبور را وارد کنید.'),
    role: z.enum(['customer', 'freelancer'], { message: 'نوع حساب را انتخاب کنید.' }),
  })
  .refine((values) => values.password === values.confirm_password, {
    path: ['confirm_password'],
    message: 'تکرار رمز عبور با رمز عبور یکسان نیست.',
  });

export type RegisterValues = z.infer<typeof registerSchema>;

export const forgotPasswordSchema = z.object({
  email: emailSchema,
});

export type ForgotPasswordValues = z.infer<typeof forgotPasswordSchema>;

export const changePasswordSchema = z
  .object({
    old_password: z.string().min(1, 'رمز عبور فعلی را وارد کنید.'),
    new_password: z.string().min(8, 'رمز عبور جدید باید حداقل ۸ نویسه باشد.'),
    confirm_password: z.string().min(1, 'تکرار رمز عبور جدید را وارد کنید.'),
  })
  .refine((values) => values.new_password === values.confirm_password, {
    path: ['confirm_password'],
    message: 'تکرار رمز عبور با رمز عبور جدید یکسان نیست.',
  });

export type ChangePasswordValues = z.infer<typeof changePasswordSchema>;
