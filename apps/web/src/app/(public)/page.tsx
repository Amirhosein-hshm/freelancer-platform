import Link from 'next/link';
import { ArrowLeft, ArrowUpLeft, Check, CircleDot, FileText, MessageCircle, ShieldCheck, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/theme-toggle';
import { HeroWorkflow } from '@/components/landing/hero-workflow';

const workflow = [
  ['۰۱', 'تعریف دقیق', 'نیاز، بودجه و مسیر پروژه از همان ابتدا روشن است.', FileText],
  ['۰۲', 'همکاری واقعی', 'گفتگوها، فایل‌ها و تصمیم‌ها در یک فضای مشترک می‌مانند.', MessageCircle],
  ['۰۳', 'بازبینی مستقل', 'تحویل‌ها پیش از تأیید نهایی، با نگاه حرفه‌ای بررسی می‌شوند.', ShieldCheck],
  ['۰۴', 'تحویل مطمئن', 'هر مرحله ثبت می‌شود تا پروژه با اطمینان به پایان برسد.', Check],
] as const;
const roles = [
  ['برای مشتری', 'تصمیم‌های مهم را گم نکنید.', 'از اولین بریف تا تأیید نهایی، تصویر کاملی از مسیر دارید.'],
  ['برای فریلنسر', 'تمرکزتان را روی کار بگذارید.', 'نیازمندی‌های شفاف و بازخورد ساختارمند، همکاری را جلو می‌برد.'],
  ['برای ناظر', 'کیفیت را قابل اعتماد کنید.', 'بازبینی مستقل کمک می‌کند استاندارد پروژه در هر تحویل حفظ شود.'],
] as const;

export default function HomePage() {
  return <main id="main" className="didar-page">
    <header className="didar-header"><div className="didar-header__inner"><Link href="/" className="didar-brand" aria-label="دیدار، صفحه اصلی"><span className="didar-brand__mark"><Sparkles size={17} aria-hidden="true" /></span><span>دیدار</span></Link><nav className="didar-nav" aria-label="ناوبری اصلی"><a href="#workflow">چطور کار می‌کند</a><a href="#roles">برای چه کسی</a></nav><div className="didar-header__actions"><ThemeToggle /><Link href="/login" className="didar-login">ورود</Link><Button asChild size="sm" className="didar-header__cta"><Link href="/register">شروع کنید <ArrowLeft size={15} aria-hidden="true" /></Link></Button></div></div></header>
    <section className="didar-hero" aria-labelledby="hero-title"><div className="didar-hero__grid" aria-hidden="true" /><div className="didar-hero__inner"><div className="didar-hero__copy"><p className="eyebrow"><span /> فضای کار حرفه‌ای برای پروژه‌های خلاق</p><h1 id="hero-title">پروژه‌های خلاق،<br /><em>در یک مسیر روشن.</em></h1><p className="didar-hero__intro">از تعریف نیاز تا تحویل نهایی، همه‌چیز در دیدار جای خودش را دارد؛ روشن، منظم و قابل اعتماد.</p><div className="didar-actions"><Button asChild size="lg" className="didar-primary"><Link href="/login">ورود به فضای کار <ArrowLeft size={17} aria-hidden="true" /></Link></Button><Link href="/register" className="didar-text-link">حساب جدید بسازید <ArrowUpLeft size={16} aria-hidden="true" /></Link></div><div className="didar-hero__note"><CircleDot size={13} aria-hidden="true" /> ساخته شده برای همکاری‌های جدی</div></div><HeroWorkflow /></div><div className="didar-hero__footer"><span>دیدار / ۱۴۰۳</span><span>اسکرول کنید <ArrowLeft size={14} aria-hidden="true" /></span></div></section>
    <section id="workflow" className="didar-section didar-workflow"><div className="didar-section__label"><span>۰۱ / مسیر پروژه</span><span>از ایده تا نتیجه</span></div><div className="didar-section__heading"><p>یک مسیر، بدون نقطه کور.</p><h2>همه‌چیز<br /><em>سر جای خودش.</em></h2></div><div className="didar-workflow__list">{workflow.map(([number, title, text, Icon]) => <article key={number} className="workflow-row"><span className="workflow-row__number">{number}</span><Icon size={21} strokeWidth={1.5} aria-hidden="true" /><div><h3>{title}</h3><p>{text}</p></div><ArrowUpLeft size={18} aria-hidden="true" /></article>)}</div></section>
    <section id="roles" className="didar-section didar-roles"><div className="didar-section__label"><span>۰۲ / برای هر نقش</span><span>همکاری بهتر، نتیجه بهتر</span></div><div className="didar-roles__intro"><h2>وقتی همه<br /><em>هم‌جهت‌اند.</em></h2><p>دیدار فاصله میان ایده، اجرا و تأیید را کم می‌کند. هر نقش، ابزار و تصویر روشنی از قدم بعدی دارد.</p></div><div className="didar-roles__grid">{roles.map(([label, title, text], index) => <article key={label}><span className="role-index">۰{index + 1}</span><p className="role-label">{label}</p><h3>{title}</h3><p>{text}</p></article>)}</div></section>
    <section className="didar-cta"><div><p className="eyebrow"><span /> مسیر بعدی همین‌جاست</p><h2>پروژه بعدی‌تان<br /><em>از کجا شروع می‌شود؟</em></h2></div><div className="didar-cta__action"><p>یک فضای روشن برای کارهای مهم.</p><Button asChild size="lg" className="didar-primary"><Link href="/register">ایجاد حساب کاربری <ArrowLeft size={17} aria-hidden="true" /></Link></Button></div></section>
    <footer className="didar-footer"><Link href="/" className="didar-brand"><span className="didar-brand__mark"><Sparkles size={15} aria-hidden="true" /></span><span>دیدار</span></Link><p>پلتفرم مدیریت پروژه‌های خلاق</p><div><Link href="/login">ورود</Link><Link href="/register">ثبت‌نام</Link></div><small>© ۱۴۰۳ دیدار. همه‌چیز برای یک همکاری بهتر.</small></footer>
  </main>;
}
