import { describe, expect, it } from 'vitest';
import { createTicketSchema, ticketMessageSchema } from './ticket-domain';

describe('ticket schemas', () => {
  it('requires a recipient, subject, and initial message', () => {
    expect(createTicketSchema.safeParse({ target_user_id: '', subject: '', priority: 'normal', body: '', attachment_file_asset_ids: [] }).success).toBe(false);
  });

  it('accepts a message containing attachments and text', () => {
    expect(ticketMessageSchema.safeParse({ body: 'پیام', attachment_file_asset_ids: ['file-1'] }).success).toBe(true);
  });
});
