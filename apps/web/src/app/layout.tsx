import type { Metadata, Viewport } from "next";
import Script from "next/script";
import { Providers } from "@/components/providers";
import "./globals.css";

const estedad = { variable: "font-estedad" };

export const metadata: Metadata = {
  title: {
    default: "دیدار | مدیریت پروژه‌های خلاق",
    template: "%s | دیدار",
  },
  description:
    "پلتفرم مدیریت پروژه و همکاری حرفه‌ای میان مشتریان، فریلنسرها و ناظران",
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f5f3ff" },
    { media: "(prefers-color-scheme: dark)", color: "#100e1c" },
  ],
};

const themeInitScript = `try{var s=localStorage.getItem('didar-theme');var d=s?s==='dark':window.matchMedia('(prefers-color-scheme: dark)').matches;if(d){document.documentElement.classList.add('dark')}}catch(e){}`;

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    // `data-scroll-behavior` is required in Next 16: it no longer overrides
    // `scroll-behavior` during route transitions, so smooth scrolling has to be
    // opted back into explicitly.
    <html
      lang="fa"
      dir="rtl"
      className={estedad.variable}
      data-scroll-behavior="smooth"
      suppressHydrationWarning
    >
      <head>
        <Script id="theme-init" strategy="beforeInteractive">
          {themeInitScript}
        </Script>
      </head>
      <body>
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:start-3 focus:z-50 focus:rounded-md focus:bg-primary focus:px-4 focus:py-2 focus:text-sm focus:text-primary-foreground"
        >
          پرش به محتوای اصلی
        </a>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
