'use client';
import { ArrowLeft, Check, FileText, MessageCircle, ShieldCheck } from 'lucide-react';
import { useState } from 'react';
const stages = [{ label: 'تعریف پروژه', icon: FileText, state: 'تکمیل شد' }, { label: 'بازخورد مشتری', icon: MessageCircle, state: 'در جریان' }, { label: 'بازبینی نهایی', icon: ShieldCheck, state: 'مرحله بعد' }];
export function HeroWorkflow() {
  const [active, setActive] = useState(1);
  return <div className="workflow-visual" onMouseMove={(event) => { const box = event.currentTarget.getBoundingClientRect(); event.currentTarget.style.setProperty('--mx', `${((event.clientX - box.left) / box.width - .5) * 10}px`); event.currentTarget.style.setProperty('--my', `${((event.clientY - box.top) / box.height - .5) * 10}px`); }} onMouseLeave={(event) => { event.currentTarget.style.setProperty('--mx', '0px'); event.currentTarget.style.setProperty('--my', '0px'); }}>
    <div className="workflow-visual__top"><span>پروژه / هویت بصری</span><span>در حال اجرا</span></div><div className="workflow-visual__title"><span>برنامه امروز</span><strong>یک قدم<br />جلوتر.</strong></div>
    <div className="workflow-visual__timeline">{stages.map((stage, index) => { const Icon = stage.icon; return <button key={stage.label} className={index === active ? 'is-active' : ''} onClick={() => setActive(index)}><span className="timeline-icon"><Icon size={16} aria-hidden="true" /></span><span><b>{stage.label}</b><small>{index === active ? 'در حال بررسی' : stage.state}</small></span>{index < stages.length - 1 && <i aria-hidden="true" />}</button>; })}</div>
    <div className="workflow-visual__comment"><span className="comment-avatar">م</span><div><strong>بازخورد جدید</strong><p>«جهت درستی است؛ نسخه بعدی را ببینیم.»</p></div><Check size={17} aria-hidden="true" /></div><div className="workflow-visual__bottom"><span>به‌روزرسانی ۲ دقیقه پیش</span><ArrowLeft size={15} aria-hidden="true" /></div>
  </div>;
}
