# استخدام Python 3.11 slim image كقاعدة
FROM python:3.11-slim

# تعيين متغير البيئة لمنع Python من إنشاء ملفات .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# تعيين مجلد العمل
WORKDIR /app

# نسخ ملف المتطلبات أولاً للاستفادة من Docker layer caching
COPY requirements.txt .

# تثبيت المتطلبات
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# نسخ كود التطبيق
COPY . .

# إنشاء مستخدم غير مميز لتشغيل التطبيق
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# فتح البورت 5000
EXPOSE 5000

# تعيين متغيرات البيئة الافتراضية
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# فحص صحة الحاوية
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# تشغيل التطبيق باستخدام Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]