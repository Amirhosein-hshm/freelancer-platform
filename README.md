# Freelance Platform Monorepo

یک پلتفرم جامع مدیریت پروژه‌های فریلنسری و رسانه‌ای متشکل از فرانت‌اند **Next.js 16** و بک‌اند **FastAPI** که در قالب یک **Nx Monorepo** با ساختار یکپارچه مدیریت می‌شود.

---

## 🏗 ساختار مخزن (Monorepo Layout)

```text
freelancer-platform/
├── apps/
│   ├── web/                     # پروژه فرانت‌اند Next.js 16 (React 19, Tailwind CSS v4, Orval, TanStack Query)
│   │   ├── src/                 # کد منبع فرانت‌اند (کامپوننت‌ها، صفحات، هوک‌ها و فیلترها)
│   │   ├── generated/           # کلاینت‌های TypeScript تولید شده از OpenAPI
│   │   ├── openapi.json         # مشخصات کامل OpenAPI بک‌اند
│   │   ├── package.json
│   │   └── project.json         # کانفیگ پروژه‌ای Nx برای web
│   │
│   └── backend/                 # سرویس بک‌اند Python (FastAPI, SQLAlchemy 2 async, Alembic, PostgreSQL)
│       ├── src/app/             # لایه‌های Domain, Application, Infrastructure, Presentation, Bootstrap
│       ├── tests/               # تست‌های جامع Unit و Integration
│       ├── pyproject.toml
│       ├── alembic.ini
│       ├── Dockerfile
│       └── project.json         # کانفیگ پروژه‌ای Nx برای backend
│
├── package.json                 # وابستگی‌های سراسری و اسکریپت‌های مونو‌ریپو
├── pnpm-workspace.yaml          # ورک‌اسپیس pnpm
├── nx.json                      # پیکربندی مرکزی Nx
├── docker-compose.yml           # ارکستراسیون کامل کانتینرها (DB, Migrate, Backend, Web)
└── .env.example                 # نمونه متغیرهای محیطی سراسری
```

---

## ⚡️ اجرای سریع با دستورات Nx (Root Scripts)

وابستگی‌ها از طریق `pnpm` مدیریت می‌شوند:

```bash
# نصب تمام وابستگی‌های مونو‌ریپو
pnpm install

# اجرای محیط توسعه (فرانت‌اند روی پورت 3000)
pnpm dev
# یا با nx:
pnpm nx dev web

# اجرای همزمان فرانت‌اند و بک‌اند
pnpm dev:all

# اجرای تست‌ها
pnpm test          # اجرای همه تست‌ها با کشینگ Nx
pnpm test:web      # اجرای تست‌های ویست (Vitest) فرانت‌اند
pnpm test:backend  # اجرای تست‌های pytest بک‌اند

# بررسی Typecheck و Lint
pnpm typecheck
pnpm lint

# بیلد فرانت‌اند برای پروداکشن
pnpm build
```

---

## 🔌 نحوه اتصال فرانت‌اند به بک‌اند (API Proxy)

در فرانت‌اند (`apps/web`)، مرورگر هرگز آدرس‌های مستقیم یا پورت‌های داخلی بک‌اند را فراخوانی نمی‌کند.
تمام درخواست‌ها به روت پروکسی یکسان درون برنامه فرستاده می‌شوند:

- مرورگر: درخواست به `/api/v1/*`
- روت سروری Next.js (`apps/web/src/app/api/v1/[...path]/route.ts`):
  - توکن‌های احراز هویت را در کوکی‌های امن HTTP-Only مدیریت می‌کند.
  - درخواست را به آدرس بک‌اند (`API_BASE_URL`، پیش‌فرض `http://127.0.0.1:8000`) هدایت می‌کند.
  - پاسخ‌ها را به همراه هدرها و هندلینگ خطای استاندارد بازمی‌گرداند.

برای به‌روزرسانی کلاینت TypeScript از روی قرارداد API بک‌اند:
```bash
pnpm nx run web:generate:api
```

---

## 🐳 اجرای کامل با Docker Compose

سریع‌ترین راه برای بالا آوردن کل استک (PostgreSQL + Migrations + Seeding + FastAPI Backend + Next.js Web):

```bash
cp .env.example .env
# مقادیر JWT_SECRET و کلمات عبور را در صورت نیاز تغییر دهید

docker compose up --build
```

سرویس‌های راه‌اندازی شده:
- **db:** دیتابیس `postgres:16-alpine` روی پورت 5432
- **migrate:** اجرای Alembic migrations و دیتای اولیه ادمین و نقش‌ها
- **backend:** سرور FastAPI روی `http://localhost:8000` (مستندات در `/docs`)
- **web:** فرانت‌اند Next.js روی `http://localhost:3000`

---

## 📚 مستندات تکمیلی معماری و دامین بک‌اند

- `ARCHITECTURE.md` — اصول معماری تمیز و قوانین وابستگی لایه‌ها
- `DOMAIN.md` — موجودیت‌ها، Value Objectها و اینترفیس‌های مخازن
- `APPLICATION.md` — Use Caseها، DTOها و پورت‌های ارتباطی
- `AUTHORIZATION.md` — مدل کنترل دسترسی مبتنی بر نقش (RBAC)
- `API_DESIGN.md` — قرارداد خروجی استاندارد، فرمت خطاها و اندپوینت‌ها
- `PRESENTATION.md` — ساختار FastAPI، تزریق وابستگی و کانکشن‌های WebSocket
- `INFRASTRUCTURE.md` — پایگاه‌داده، مدل‌های SQLAlchemy، مایگریشن‌ها و هش رمزها
- `TESTING.md` — راهنمای جامع تست‌ها و استراتژی پوشش کد
