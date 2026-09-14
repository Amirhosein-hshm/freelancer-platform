'use client';

import {
  CircleCheckIcon,
  InfoIcon,
  Loader2Icon,
  OctagonXIcon,
  TriangleAlertIcon,
} from 'lucide-react';
import { Toaster as Sonner, type ToasterProps } from 'sonner';
import { useThemeMode } from '@/lib/theme';

/**
 * Toast surface. Uses the project's own theme signal rather than next-themes,
 * and maps sonner's CSS variables onto the Didar tokens.
 */
const Toaster = ({ ...props }: ToasterProps) => {
  const theme = useThemeMode();

  return (
    <Sonner
      theme={theme}
      dir="rtl"
      position="bottom-left"
      className="toaster group"
      icons={{
        success: <CircleCheckIcon className="size-4" />,
        info: <InfoIcon className="size-4" />,
        warning: <TriangleAlertIcon className="size-4" />,
        error: <OctagonXIcon className="size-4" />,
        loading: <Loader2Icon className="size-4 animate-spin" />,
      }}
      style={
        {
          '--normal-bg': 'var(--popover)',
          '--normal-text': 'var(--popover-foreground)',
          '--normal-border': 'var(--border)',
          '--success-bg': 'var(--popover)',
          '--success-text': 'var(--accent)',
          '--error-bg': 'var(--popover)',
          '--error-text': 'var(--destructive)',
          '--warning-bg': 'var(--popover)',
          '--warning-text': 'var(--warning)',
          '--border-radius': 'var(--radius-md)',
        } as React.CSSProperties
      }
      {...props}
    />
  );
};

export { Toaster };
