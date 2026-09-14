import { describe, expect, it } from 'vitest';
import { deliverySchema, toDeliveryRequest } from './delivery-domain';

describe('delivery data', () => {
  it('maps optional notes and uploaded asset ids without extra rules', () => {
    const values = { delivery_note: '', file_asset_ids: ['file-1', 'file-2'] };
    expect(deliverySchema.safeParse(values).success).toBe(true);
    expect(toDeliveryRequest(values)).toEqual({ delivery_note: null, file_asset_ids: ['file-1', 'file-2'] });
  });
});
