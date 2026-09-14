import { z } from 'zod';
import type { SubmitDeliveryRequest } from '@/generated/api/models';

export const deliverySchema = z.object({
  delivery_note: z.string().trim(),
  file_asset_ids: z.array(z.string()),
});

export type DeliveryValues = z.infer<typeof deliverySchema>;

export function toDeliveryRequest(values: DeliveryValues): SubmitDeliveryRequest {
  return {
    delivery_note: values.delivery_note === '' ? null : values.delivery_note,
    file_asset_ids: values.file_asset_ids,
  };
}
