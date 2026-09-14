import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { Slot } from "radix-ui"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex shrink-0 items-center justify-center gap-2 rounded-lg text-sm font-semibold whitespace-nowrap transition-[background-color,color,border-color,box-shadow,transform] outline-none active:translate-y-px focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/40 disabled:pointer-events-none disabled:opacity-50 disabled:transform-none aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        default: "border border-primary bg-primary text-primary-foreground shadow-sm hover:bg-primary/88 dark:text-white",
        destructive:
          "border border-destructive bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/88 focus-visible:ring-destructive/25",
        success:
          "border border-success bg-success text-success-foreground shadow-sm hover:bg-success/88 focus-visible:ring-success/25",
        warning:
          "border border-warning bg-warning text-warning-foreground shadow-sm hover:bg-warning/88 focus-visible:ring-warning/25",
        outline:
          "border border-border bg-background text-foreground shadow-xs hover:border-primary/45 hover:bg-muted",
        secondary:
          "border border-secondary bg-secondary text-secondary-foreground hover:bg-secondary/82 dark:text-white",
        ghost:
          "border border-transparent bg-transparent text-foreground hover:bg-muted",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "min-h-10 px-4 py-2 has-[>svg]:px-3",
        xs: "h-6 gap-1 rounded-md px-2 text-xs has-[>svg]:px-1.5 [&_svg:not([class*='size-'])]:size-3",
        sm: "min-h-9 gap-1.5 rounded-lg px-3 has-[>svg]:px-2.5",
        lg: "min-h-11 rounded-lg px-6 has-[>svg]:px-4",
        icon: "size-9",
        "icon-xs": "size-6 rounded-md [&_svg:not([class*='size-'])]:size-3",
        "icon-sm": "size-8",
        "icon-lg": "size-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant = "default",
  size = "default",
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot.Root : "button"

  return (
    <Comp
      data-slot="button"
      data-variant={variant}
      data-size={size}
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
