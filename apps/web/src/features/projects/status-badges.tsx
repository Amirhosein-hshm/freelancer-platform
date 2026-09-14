import { Badge } from '@/components/ui/badge';
import type {
  DeliveryStatus,
  ProjectApplicationStatus,
  ProjectStatus,
} from '@/generated/api/models';
import {
  APPLICATION_STATUS_LABELS,
  APPLICATION_STATUS_TONES,
  DELIVERY_STATUS_LABELS,
  DELIVERY_STATUS_TONES,
  PROJECT_STATUS_LABELS,
  PROJECT_STATUS_TONES,
} from './project-domain';

/**
 * Status badges for the three lifecycle enums.
 *
 * Each falls back to the raw backend value rather than rendering nothing: if the
 * backend adds a status before the client is regenerated, the user sees the new
 * value instead of an empty badge.
 */

export function ProjectStatusBadge({ status }: { status: ProjectStatus }) {
  return (
    <Badge variant={PROJECT_STATUS_TONES[status] ?? 'outline'}>
      {PROJECT_STATUS_LABELS[status] ?? status}
    </Badge>
  );
}

export function ApplicationStatusBadge({ status }: { status: ProjectApplicationStatus }) {
  return (
    <Badge variant={APPLICATION_STATUS_TONES[status] ?? 'outline'}>
      {APPLICATION_STATUS_LABELS[status] ?? status}
    </Badge>
  );
}

export function DeliveryStatusBadge({ status }: { status: DeliveryStatus }) {
  return (
    <Badge variant={DELIVERY_STATUS_TONES[status] ?? 'outline'}>
      {DELIVERY_STATUS_LABELS[status] ?? status}
    </Badge>
  );
}
