import { z } from 'zod';

export const TICKET_STATUS_LABELS: Record<string, string> = {
  open: 'باز',
  closed: 'بسته',
  archived: 'بایگانی‌شده',
};

export const TICKET_PRIORITY_LABELS: Record<string, string> = {
  low: 'کم',
  normal: 'عادی',
  high: 'زیاد',
  urgent: 'فوری',
};

export const createTicketSchema = z.object({
  target_user_id: z.string().min(1, 'مخاطب را انتخاب کنید.'),
  subject: z.string().trim().min(1, 'موضوع را وارد کنید.'),
  priority: z.enum(['low', 'normal', 'high', 'urgent']),
  body: z.string().trim().min(1, 'پیام اولیه را وارد کنید.'),
  attachment_file_asset_ids: z.array(z.string()),
});

export const ticketMessageSchema = z.object({
  body: z.string().trim().min(1, 'متن پیام را وارد کنید.'),
  attachment_file_asset_ids: z.array(z.string()),
});

export type CreateTicketValues = z.infer<typeof createTicketSchema>;
export type TicketMessageValues = z.infer<typeof ticketMessageSchema>;
