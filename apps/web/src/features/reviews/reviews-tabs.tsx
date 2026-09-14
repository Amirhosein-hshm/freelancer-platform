'use client';

import type { PaginationMeta, ProjectResponse, ReviewResponse } from '@/generated/api/models';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PendingReviewList, ScopedProjectList } from './review-queue';
import { useListQuery } from '@/lib/url/use-list-query';

export function ReviewsTabs(props: { pending: ReviewResponse[]; pendingMeta: PaginationMeta; projects: ProjectResponse[]; projectMeta: PaginationMeta }) {
  const query = useListQuery();
  return <Tabs defaultValue="pending" className="grid gap-4"><TabsList><TabsTrigger value="pending">در انتظار بررسی</TabsTrigger><TabsTrigger value="projects">همه پروژه‌ها</TabsTrigger></TabsList><TabsContent value="pending"><PendingReviewList items={props.pending} meta={props.pendingMeta} query={query} /></TabsContent><TabsContent value="projects"><ScopedProjectList items={props.projects} meta={props.projectMeta} query={query} /></TabsContent></Tabs>;
}
