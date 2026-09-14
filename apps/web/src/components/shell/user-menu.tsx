'use client';

import Link from 'next/link';
import { ChevronDown, KeyRound, UserRound } from 'lucide-react';
import { LogoutButton } from '@/features/auth/logout-button';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import type { UserMeResponse } from '@/generated/api/models';
import { ROLE_LABELS } from '@/lib/auth/navigation';

export function UserMenu({ user }: { user: UserMeResponse }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="min-h-11 gap-2 px-3">
          <span className="grid size-7 place-items-center rounded-full bg-primary/10 text-primary">
            <UserRound size={15} />
          </span>
          <span dir="ltr" className="max-w-[160px] truncate text-xs font-medium sm:text-sm">
            {user.email}
          </span>
          <ChevronDown size={14} className="text-muted-foreground" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-64">
        <DropdownMenuLabel className="grid gap-1">
          <span dir="ltr" className="truncate text-xs font-normal text-muted-foreground">
            {user.email}
          </span>
          <span className="flex flex-wrap gap-1 pt-1">
            {user.roles.map((role) => (
              <Badge key={role} variant="secondary" className="text-[11px]">
                {ROLE_LABELS[role] ?? role}
              </Badge>
            ))}
          </span>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link href="/change-password" className="min-h-9 cursor-pointer">
            <KeyRound size={15} />
            تغییر رمز عبور
          </Link>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild variant="destructive">
          <LogoutButton />
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
