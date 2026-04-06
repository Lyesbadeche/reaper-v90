# OmniReaperPro

## الفكرة
مشروع ماسح أمني للعقود الذكية باستخدام أدوات مثل:
- Slither
- Mythril
- Echidna
- Halmos

مع قاعدة بيانات PostgreSQL وواجهة API مبنية بـ Flask، بالإضافة إلى إمكانية ربط التنبيهات عبر Telegram.

---

## طريقة التشغيل
1. تأكد أن لديك **Docker** و **Docker Compose** مثبتين.
2. داخل مجلد المشروع شغّل:
   ```bash
   docker-compose up --build
