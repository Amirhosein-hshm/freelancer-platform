import { z } from 'zod';

export const adminUserSchema = z.object({ email: z.string().email(), password: z.string().min(8), first_name: z.string().min(1), last_name: z.string().min(1) });
export const categorySchema = z.object({ name: z.string().min(1), slug: z.string().min(1), category_key: z.string().min(1), sort_order: z.number().int().optional() });
export const supervisorAssignmentSchema = z.object({ supervisor_user_id: z.string().min(1) });
