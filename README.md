# GitHub Actions - راهنمای Deploy خودکار

این پوشه شامل Workflow های خودکار برای پروژه است.

## فایل‌ها

- **`deploy.yml`** — Pipeline اصلی: Lint → Test → Deploy

---

## مراحل راه‌اندازی

### ۱. API Key کدرد کلود رو به Secret تبدیل کن

1. برو به `https://github.com/alipoorkaramali/wagtail-project/settings/secrets/actions`
2. **New repository secret** بزن
3. **Name**: `cr_token` (دقیقاً همین، حروف کوچک)
4. **Secret**: API Key کدرد کلودت رو پیست کن
5. **Add secret**

### ۲. Workflow رو آپلود کن

```
git add .github/
git commit -m "Add CI/CD workflow"
git push origin main
```

### ۳. تست کن

برو به تب **Actions** توی گیت‌هاب:
`https://github.com/alipoorkaramali/wagtail-project/actions`

---

## Pipeline چیکار می‌کنه؟

### Job 1: Lint (Ruff)

- کد رو با Ruff چک می‌کنه
- **Blocking نیست** — فقط هشدار می‌ده تا راحت‌تر بتونی push کنی

### Job 2: Test (Django)

- `manage.py check` رو اجرا می‌کنه
- چک می‌کنه migration ها کامل باشن
- تست‌ها رو با coverage اجرا می‌کنه
- **Blocking نیست** — ولی اگه تست‌ها fail بشن، توصیه می‌شه قبل از Deploy حلشون کنی

### Job 3: Deploy (فقط روی main)

- `cr list` رو صدا می‌زنه تا مطمئن شه token کار می‌کنه
- `cr deploy wagtail-sandbox` رو اجرا می‌کنه
- نتیجه رو توی **Summary** صفحه Actions نشون می‌ده

---

## شرط‌های اجرا

| رویداد ↕▾ | Lint ↕▾ | Test ↕▾ | Deploy ↕▾ |
|---|---|---|---|
| −Push روی `main` | ✅ | ✅ | ✅ |
| −Push روی `develop` | ✅ | ✅ | ❌ |
| −Pull Request | ✅ | ✅ | ❌ |
| −Manual Trigger | ✅ | ✅ | ✅ (اگه روی main باشه) |
⚙

---

## عیب‌یابی سریع

| علامت ↕▾ | معنی ↕▾ | راه‌حل ↕▾ |
|---|---|---|
| −❌ روی `Verify secret is set` | `cr_token` ست نشده | مرحله ۱ رو دوباره انجام بده |
| −❌ روی `Install CodeRed CLI` | wget نتونست دانلود کنه | دوباره اجرا کن، موقتیه |
| ❌ روی `Verify token works` | API Key غلطه | کلید جدید بساز و Secret رو آپدیت کن |
| ❌ روی `Deploy` | خطا توی دیپلوی | لاگ کامل رو ببین و بفرست |
| 🟡 روی Test (continue-on-error) | تست‌ها fail شدن | توی لاگ ببین کدوم تست، حلش کن |
⚙

---

## اجرای دستی

اگه نمی‌خوای push کنی ولی می‌خوای Deploy بشه:

1. برو به تب **Actions**
2. از سایدبار **Deploy to CodeRed Cloud** رو انتخاب کن
3. دکمه **Run workflow** رو بزن
4. برنچ `main` رو انتخاب کن و اجرا کن

---

## اجرای محلی قبل از push

قبل از اینکه push کنی، مطمئن شو همه‌چیز لوکال OK هست:

```
# لینت
pip install ruff
ruff check .
ruff format --check .

# تست
python manage.py check
python manage.py test

# دیپلوی دستی (برای تست)
cr deploy wagtail-sandbox
```

---

## نکات امنیتی

- **هرگز** API Key رو توی کد ننویس
- **هرگز** `.env` یا `~/.cr.ini` رو commit نکن
- اگه کلیدت لو رفت، از داشبورد CodeRed باطلش کن و Secret رو آپدیت کن