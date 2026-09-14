import Link from 'next/link';
import { Compass } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export const metadata = { title: 'صفحه پیدا نشد' };

export default function NotFound() {
  return (
    <main id="main" className="grid min-h-screen place-items-center px-4 py-10">
      <Card className="w-full max-w-md text-center">
        <CardHeader className="items-center gap-3">
          <span
            className="mx-auto grid size-12 place-items-center rounded-full bg-muted text-muted-foreground"
            aria-hidden="true"
          >
            <Compass size={22} />
          </span>
          <CardTitle className="text-lg">این صفحه پیدا نشد</CardTitle>
          <CardDescription>
            نشانی وارد‌شده وجود ندارد یا این بخش هنوز در دسترس نیست.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button asChild size="lg" className="min-h-11 w-full">
            <Link href="/dashboard">بازگشت به داشبورد</Link>
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}
