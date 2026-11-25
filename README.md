# «Bilim Qadam» — Sokratik Sun'iy Intellekt Ta’lim Ekotizimi

> **"Raqamli avlod qizlari"** respublika tanlovi uchun maxsus ishlab chiqilgan milliy innovatsion ta'lim platformasi.

---

## 🌟 Loyiha haqida
**«Bilim Qadam»** — O‘zbekiston umumta'lim maktablari o'quvchilari (5–11-sinflar, 10–15 va 16–20 yosh toifalari) uchun mo‘ljallangan, Google Gemini 2.5/3.5 Flash neyrotarmog‘i asosida ishlovchi birinchi milliy Sokratik ta'lim platformasi.

### Asosiy Imkoniyatlar:
1. **🧠 Sokratik AI Repetitor:** O‘quvchiga tayyor javobni bermasdan, bosqichma-bosqich yo'llovchi savollar bilan mustaqil yechishga o'rgatadi.
2. **🌐 Milliy Bosh Sahifa Portali:** O'quvchilar, o'qituvchilar, ota-onalar va hakamlar hay'ati uchun 4 ta interaktiv yo'nalish.
3. **🔐 Clerk & Google OAuth 2.0:** Shaxsiy Gmail orqali xavfsiz kirish va ro'yxatdan o'tish (Hakamlar uchun alohida ko'rgazmali demo hisob).
4. **📐 3D Stereometriya & Funksiyalar:** Three.js asosidagi interaktiv 3D geometrik figuralar va matematik grafiklar.
5. **📝 Aqlli Muallim (DTS Test Generator):** O'qituvchilar uchun 45 daqiqalik dars konspektlari va 4 variantli testlar.
6. **⚔️ Bilim Jangi (P2P Duel):** Tengdoshlar bilan 60 soniyalik jonli intellektual bellashuv.
7. **💳 Fintech To'lov Tizimi:** Payme, Click va Uzum Bank orqali rasmiy elektron chek va obuna faollashtirish.

---

## 🚀 Lokal muhitda ishga tushirish (Local Run)

```bash
# 1. Kerakli kutubxonalarni o'rnatish
pip install -r requirements.txt

# 2. Serverni ishga tushirish
python app.py
```
Brauzerda: `http://localhost:8000`

---

## 🌐 GitHub va Render.com orqali Deploy qilish (Jonli Internetga chiqarish)

### 1-qadam: GitHub-ga yuklash (Push to GitHub)
1. [github.com](https://github.com) ga kiring va yangi repository yarating (masalan: `bilim-qadam-ai`).
2. Terminalda quyidagi buyruqlarni ketma-ket bajaring:

```bash
git init
git add .
git commit -m "feat: Bilim Qadam release v1.0"
git branch -M main
git remote add origin https://github.com/SIZNING_GITHUB_USERNAME/bilim-qadam-ai.git
git push -u origin main
```

---

### 2-qadam: Render.com orqali Deploy qilish
1. [render.com](https://render.com) saytiga kiring va o'z GitHub hisobingiz orqali kiring (Sign In with GitHub).
2. Render bosh sahifasida **"New +"** tugmasini bosing va **"Web Service"** ni tanlang.
3. Yangi ochilgan ro'yxatdan o'zingizning **`bilim-qadam-ai`** repositoryingizni tanlab, **"Connect"** tugmasini bosing.
4. Quyidagi parametrlarni tekshiring yoki kiriting:
   - **Name:** `bilim-qadam` (yoki ixtiyoriy nom)
   - **Region:** `Frankfurt (EU Central)`
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`
5. **Environment Variables (Muhim!):**
   - **"Add Environment Variable"** tugmasini bosing:
     - **Key:** `GEMINI_API_KEY`
     - **Value:** `Sizning_Google_Gemini_API_Kalitingiz`
     *(API kalitni [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) dan bepul olishingiz mumkin).*
6. Pastdagi **"Deploy Web Service"** tugmasini bosing!

Render 1-2 daqiqada avtomatik build qilib, sizga dunyo bo'ylab ishlaydigan jonli havola beradi:
👉 `https://bilim-qadam.onrender.com`

---

## 📂 Loyiha arxitekturasi:
* `app.py` — FastAPI asosidagi backend server, Gemini API, Clerk/Google Auth va Fintech API.
* `index.html` — Yagona sahifali (SPA) zamonaviy frontend interfeys, KaTeX, Three.js, Canvas.
* `requirements.txt` — Python bog'liqliklari (FastAPI, Uvicorn, Google GenAI SDK).
* `render.yaml` — Render platformasi uchun avtomatlashtirilgan Blueprint konfiguratsiyasi.
* `Procfile` — Bulutli serverlar uchun Web jarayoni marshrutizatori.
