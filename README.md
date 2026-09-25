# Do'kon Qarzdorlik

Do'konlar uchun mijozlarning qarzdorligini boshqarish platformasi (Django asosida).

## Imkoniyatlar
- Ro'yxatdan o'tish / kirish (har bir foydalanuvchi faqat o'z ma'lumotlarini ko'radi)
- Bosh sahifa: umumiy statistikalar, 7 kunlik qarz dinamikasi grafigi, eng ko'p qarzdor mijozlar
- Mijozlar: qo'shish, tahrirlash, o'chirish, qidirish, holat bo'yicha filtrlash
- Qarzlar: yangi qarz qo'shish, ro'yxat, qidirish va holat (faol/muddati o'tgan/to'langan) bo'yicha filtrlash
- To'lovlar: to'lov qabul qilish va tarixini ko'rish
- Do'konlar: qarzlarni yo'nalishlar (masalan TEXNO, Kiyim dunyosi) bo'yicha guruhlash

## Ishga tushirish

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Brauzerda: http://127.0.0.1:8000/

Admin panel: http://127.0.0.1:8000/admin/

## Texnologiyalar
- Backend: Django 6, Python
- Ma'lumotlar bazasi: SQLite (kerak bo'lsa PostgreSQL'ga oson o'tkaziladi)
- Frontend: Tailwind CSS (CDN), Chart.js
