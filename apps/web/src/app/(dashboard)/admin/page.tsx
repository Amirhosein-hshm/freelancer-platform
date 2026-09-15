import { redirect } from 'next/navigation';
import { getServerSessionUser } from '@/lib/api/server';
import { hasRole, ROLES } from '@/lib/auth/navigation';

export default async function AdminPage() {
  const user = await getServerSessionUser();
  if (!hasRole(user, ROLES.admin)) {
    redirect('/dashboard');
  }
  redirect('/admin/reports');
}
