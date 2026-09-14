import Link from 'next/link';
import { ArrowRight, Check, FileText, MessageCircle, ShieldCheck, Sparkles } from 'lucide-react';
import type { ReactNode } from 'react';
import { ThemeToggle } from '@/components/theme-toggle';

export function AuthLayout({ eyebrow, title, description, children }: { eyebrow: string; title: string; description?: string; children: ReactNode }) {
  return <main id="main" className="auth-page">
    <header className="auth-header"><Link href="/" className="auth-brand"><span className="auth-brand__mark"><Sparkles size={16} aria-hidden="true" /></span><span>دیدار</span></Link><div className="auth-header__actions"><Link href="/" className="auth-home-link"><ArrowRight size={15} aria-hidden="true" /> بازگشت به صفحه اصلی</Link><ThemeToggle /></div></header>
    <div className="auth-layout"><section className="auth-panel"><div className="auth-panel__inner"><p className="auth-eyebrow"><span /> {eyebrow}</p><h1>{title}</h1>{description ? <p className="auth-description">{description}</p> : null}{children}</div></section><aside className="auth-story" aria-hidden="true"><div className="auth-story__grid" /><div className="auth-story__inner"><p className="auth-story__kicker">دیدار / فضای کار حرفه‌ای</p><h2>هر پروژه،<br /><em>یک مسیر روشن.</em></h2><p className="auth-story__copy">از اولین گفتگو تا آخرین تحویل، همکاری‌های مهم را با وضوح و تمرکز جلو ببرید.</p><div className="auth-story__steps"><div><span><FileText size={15} /></span><p><b>تعریف</b><small>نیازها روشن می‌شوند</small></p></div><div><span><MessageCircle size={15} /></span><p><b>همکاری</b><small>بازخوردها کنار هم</small></p></div><div><span><ShieldCheck size={15} /></span><p><b>اعتماد</b><small>تحویل با اطمینان</small></p></div></div><div className="auth-story__stamp"><Check size={15} /> یک قدم جلوتر</div></div></aside></div>
  </main>;
}
