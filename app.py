import os
import base64
from typing import Optional, List, Dict
from dotenv import load_dotenv

# .env faylidan API kalitni yuklash
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Bilim Qadam — Raqamli Ta'lim Platformasi")

# CORS barcha domenlar va local fayllar uchun ruxsat etiladi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SOCRATIC_PROMPT = """
Sen "Bilim Qadam" — O'zbekiston maktab o'quvchilari uchun samimiy, har tomonlama bilimdon va tabiiy Sokratik repetitorsan.
Sening ixtisosliging: Barcha maktab fanlari bo'yicha (Matematika, Fizika, Kimyo, Biologiya, Ona tili va adabiyot, Tarix, Ingliz tili, Informatika, Mantiqiy savollar) o'quvchiga yo'l-yo'riq ko'rsatish va ularni mustaqil fikrlashga o'rgatishdir.

MULOQOT TAMOYILLARI:
1. TABIIY VA MULOYIM BO'L:
   - Agar foydalanuvchi oddiy salom bersa (masalan: "salom", "assalomu alaykum", "salom bolalar"), do'stona va qisqa alik ol: "Assalomu alaykum! Qaysi mavzu yoki misol ustida ishlaymiz?" deb so'ra.
   - Hech qachon "salomlashish taqiqlangan", "men sun'iy intellektman", "qoidalarga ko'ra..." deb ichki yo'riqnomalarni gapirma! O'zingni erkin va do'stona tut.
2. FANLAR CHЕGARASISIZ ANIQ JAVOB:
   - O'quvchi istalgan fandan (algebra, geometriya, fizika, biologiya, tarix, ingliz tili, informatika) savol bersa, ortiqcha cho'zmasdan va qayta-qayta o'zingni tanishtirmasdan, darhol uning savoliga bevosita javob va tushuntirish ber.
3. SOKRATIK METOD:
   - Tayyor javobni birdan to'kib solma. O'quvchiga yo'naltiruvchi tushuncha ber, asosiy qonuniyatni ko'rsat va fikrlashga undovchi 1 ta aniq savol ber.
4. FORMULALAR (KATEX):
   - Barcha matematik va fizik formulalarni faqat to'g'ri KaTeX formatida, bitta dollar $...$ (inline) yoki $$...$$ (display) formatida yoz (masalan: $F_A = \\rho \\cdot g \\cdot V$, $D = b^2 - 4ac$, $x = \\frac{-b \\pm \\sqrt{D}}{2a}$).
5. TIL:
   - Sof, chiroyli va tushunarli o'zbek adabiy tilida yoz.
"""

TEACHER_PROMPT = """
Sen "Bilim Qadam — Aqlli Muallim" — O'zbekiston maktab o'qituvchilari uchun maxsus AI metodistsan.
Vazifang: Berilgan fan, sinf va mavzu bo'yicha O'zbekiston Respublikasi Davlat Ta'lim Standartlari (DTS)ga mos:
- 4 xil variantdagi (A, B, C, D) sifatli nazorat ishlari va javoblar kaliti
- yoki 45 daqiqalik dars ishlanmasi (konspekt)
- yoki interaktiv krossvord va qiziqarli topshiriqlar yaratish.
Javobni o'zbek tilida, imlo xatolarisiz, chiroyli va chop etishga tayyor rasmiy formatda taqdim et.
"""

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    image_base64: Optional[str] = None
    image_mime_type: Optional[str] = "image/jpeg"
    history: Optional[List[ChatMessage]] = []
    subject: Optional[str] = "Umumiy Ta'lim"
    model_name: Optional[str] = "gemini-3.5-flash-lite"
    api_key: Optional[str] = None

class TeacherToolRequest(BaseModel):
    tool_type: str # 'quiz', 'lesson_plan', 'crossword'
    subject: str
    grade: str
    topic: str
    model_name: Optional[str] = "gemini-3.5-flash-lite"
    api_key: Optional[str] = None

class RegisterRequest(BaseModel):
    name: str
    age_group: str = "16-20"
    institution: str = "1-sonli ixtisoslashtirilgan maktab"
    region: str = "Toshkent shahri"
    phone: str
    password: str

class LoginRequest(BaseModel):
    login: str
    password: str

class GoogleAuthRequest(BaseModel):
    credential: Optional[str] = None
    email: Optional[str] = "sabina.sharifova@gmail.com"
    name: Optional[str] = "Sharifova Sabina"
    avatar: Optional[str] = None

class PaymentOrderRequest(BaseModel):
    plan_name: str
    amount: int
    provider: str # 'payme', 'click', 'uzum'
    card_number: str
    phone: str

class PaymentVerifyRequest(BaseModel):
    order_id: str
    otp_code: str

def get_client(user_api_key: Optional[str] = None) -> genai.Client:
    key = user_api_key or os.environ.get("GEMINI_API_KEY")
    if not key or key.strip() == "":
        raise HTTPException(
            status_code=400, 
            detail="Gemini API kaliti topilmadi! Iltimos, sozlamalar bo'limida o'z Gemini API kalitingizni kiriting."
        )
    return genai.Client(api_key=key.strip())

@app.get("/api/health")
def health_check():
    has_env_key = bool(os.environ.get("GEMINI_API_KEY"))
    return {
        "status": "online",
        "has_server_api_key": has_env_key,
        "default_model": "gemini-3.5-flash-lite",
        "supported_models": ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.8-flash"]
    }

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        client = get_client(req.api_key)
        contents = []

        # Suhbat tarixi (avvalgi muloqot)
        if req.history:
            for h in req.history[-10:]:
                role = "user" if h.role in ["user", "human"] else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=h.content)]
                ))

        # Joriy xabar (hech qanday sun'iy prefixlarsiz, toza xabar uzatiladi)
        current_parts = []
        if req.image_base64:
            raw_base64 = req.image_base64
            if "," in raw_base64:
                raw_base64 = raw_base64.split(",")[1]
            image_bytes = base64.b64decode(raw_base64)
            part_image = types.Part.from_bytes(data=image_bytes, mime_type=req.image_mime_type)
            current_parts.append(part_image)
            user_text = req.message if req.message else "Ushbu rasm/misolni tushuntirib bering."
            current_parts.append(types.Part.from_text(text=user_text))
        else:
            current_parts.append(types.Part.from_text(text=req.message))

        contents.append(types.Content(role="user", parts=current_parts))

        model = req.model_name or "gemini-3.5-flash-lite"
        
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SOCRATIC_PROMPT,
                temperature=0.5,
            )
        )
        
        return {
            "reply": response.text,
            "model_used": model
        }
    except Exception as e:
        error_msg = str(e)
        raise HTTPException(status_code=500, detail=f"Xatolik: {error_msg}")

@app.post("/api/teacher-tools")
async def teacher_tools_endpoint(req: TeacherToolRequest):
    try:
        client = get_client(req.api_key)
        
        if req.tool_type == "quiz":
            prompt = f"Fan: {req.subject}\nSinf: {req.grade}\nMavzu: {req.topic}\nIltimos, 4 ta variantli (A, B, C, D) nazorat ishi va uning javoblar kalitini tuzib bering."
        elif req.tool_type == "lesson_plan":
            prompt = f"Fan: {req.subject}\nSinf: {req.grade}\nMavzu: {req.topic}\nIltimos, 45 daqiqalik namunaviy dars ishlanmasi (konspekt)ni quyidagi bo'limlar bilan tayyorlab bering: Darsning maqsadi, Kerakli jihozlar, Darsning borishi (Tashkiliy qism, Yangi mavzu bayoni, Mustahkamlash, Baholash, Uyga vazifa)."
        else:
            prompt = f"Fan: {req.subject}\nSinf: {req.grade}\nMavzu: {req.topic}\nIltimos, ushbu mavzu bo'yicha o'quvchilar uchun qiziqarli krossvord savollari (Gorizontal va Vertikal) hamda interaktiv topshiriqlar tuzib bering."

        model = req.model_name or "gemini-3.5-flash-lite"
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=TEACHER_PROMPT,
                temperature=0.5,
            )
        )
        return {
            "content": response.text,
            "model_used": model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xatolik: {str(e)}")

# ========================================================
# 🔐 AUTHENTICATION & LIVE SERVER ENDPOINTS
# ========================================================
import time
import uuid

# Foydalanuvchilar va to'lov buyurtmalari (In-memory & session store)
USERS_DB = {
    "sabina": {
        "id": "usr_001",
        "name": "Sharifova Sabina",
        "age_group": "16-20",
        "institution": "1-sonli ixtisoslashtirilgan maktab",
        "region": "Toshkent shahri",
        "phone": "+998 90 123 45 67",
        "email": "sabina.sharifova@gmail.com",
        "plan": "Pro",
        "xp": 850,
        "solved": 42,
        "streak": 7
    }
}
ORDERS_DB = {}

@app.post("/api/auth/register")
def register_user(req: RegisterRequest):
    user_id = "usr_" + str(uuid.uuid4())[:8]
    USERS_DB[req.phone] = {
        "id": user_id,
        "name": req.name,
        "age_group": req.age_group,
        "institution": req.institution,
        "region": req.region,
        "phone": req.phone,
        "email": f"{req.phone}@bilimqadam.uz",
        "plan": "Pro", # Tanlov ishtirokchilariga 1 oylik PRO sovg'a
        "xp": 100,
        "solved": 1,
        "streak": 1
    }
    return {
        "success": True,
        "message": f"Xush kelibsiz, {req.name}! Ro'yxatdan muvaffaqiyatli o'tdingiz.",
        "user": USERS_DB[req.phone]
    }

@app.post("/api/auth/login")
def login_user(req: LoginRequest):
    # Agar foydalanuvchi mavjud bo'lsa yoki yangi bo'lsa kirgiziladi
    user = USERS_DB.get(req.login)
    if not user:
        user = {
            "id": "usr_" + str(uuid.uuid4())[:8],
            "name": req.login.split("@")[0].capitalize() if "@" in req.login else f"Foydalanuvchi {req.login[-4:]}",
            "age_group": "16-20",
            "institution": "1-sonli ixtisoslashtirilgan maktab",
            "region": "Toshkent shahri",
            "phone": req.login,
            "email": req.login if "@" in req.login else f"{req.login}@bilimqadam.uz",
            "plan": "Pro",
            "xp": 100,
            "solved": 1,
            "streak": 1,
            "isGuest": False,
            "is_authenticated": True
        }
        USERS_DB[req.login] = user
    return {
        "success": True,
        "message": f"Xush kelibsiz, {user['name']}!",
        "user": user
    }


class ClerkAuthRequest(BaseModel):
    clerk_id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    avatar: Optional[str] = None
    age_group: Optional[str] = "16-20"
    institution: Optional[str] = "Ta'lim muassasasi"
    region: Optional[str] = "Toshkent shahri"
    auth_provider: Optional[str] = "google"

@app.post("/api/auth/clerk")
def clerk_auth_login(req: ClerkAuthRequest):
    email = req.email.strip() if req.email else "foydalanuvchi@gmail.com"
    name = req.name.strip() if req.name else (email.split("@")[0].capitalize() if "@" in email else "Foydalanuvchi")
    
    # Mavjud foydalanuvchini olish yoki yangisini yaratish
    user = USERS_DB.get(email)
    if not user:
        user = {
            "id": "clerk_" + str(uuid.uuid4())[:8],
            "name": name,
            "age_group": req.age_group or "16-20",
            "institution": req.institution or "Ta'lim muassasasi",
            "region": req.region or "Toshkent shahri",
            "phone": "+998 90 000 00 00",
            "email": email,
            "avatar": req.avatar,
            "plan": "Pro",
            "xp": 100,
            "solved": 1,
            "streak": 1,
            "auth_provider": "clerk_google",
            "is_authenticated": True,
            "isGuest": False
        }
        USERS_DB[email] = user
    else:
        user["is_authenticated"] = True
        user["isGuest"] = False
        if req.name:
            user["name"] = req.name

    return {
        "success": True,
        "message": f"Google (Clerk) orqali muvaffaqiyatli kirdingiz: {user['name']} ({email})",
        "session_token": "clerk_sess_" + str(uuid.uuid4()),
        "user": user
    }

@app.post("/api/auth/google")
def google_auth(req: GoogleAuthRequest):
    email = req.email.strip() if req.email else "foydalanuvchi@gmail.com"
    name = req.name.strip() if req.name else (email.split("@")[0].capitalize() if "@" in email else "Foydalanuvchi")
    user = USERS_DB.get(email)
    if not user:
        user = {
            "id": "usr_google_" + str(uuid.uuid4())[:8],
            "name": name,
            "age_group": "16-20",
            "institution": "1-sonli ixtisoslashtirilgan maktab",
            "region": "Toshkent shahri",
            "phone": "+998 90 000 00 00",
            "email": email,
            "avatar": req.avatar,
            "plan": "Pro",
            "xp": 150,
            "solved": 2,
            "streak": 1,
            "is_google": True,
            "is_authenticated": True,
            "isGuest": False
        }
        USERS_DB[email] = user
    else:
        user["is_authenticated"] = True
        user["isGuest"] = False
        if req.name:
            user["name"] = req.name
    return {
        "success": True,
        "message": f"Google orqali muvaffaqiyatli kirdingiz: {name}",
        "user": user
    }

# ========================================================
# 💳 PAYMENT GATEWAY (PAYME, CLICK, UZUM BANK)
# ========================================================
@app.post("/api/payment/create-order")
def create_payment_order(req: PaymentOrderRequest):
    order_id = "ORD-" + str(uuid.uuid4())[:8].upper()
    ORDERS_DB[order_id] = {
        "order_id": order_id,
        "plan_name": req.plan_name,
        "amount": req.amount,
        "provider": req.provider,
        "card_number": req.card_number,
        "phone": req.phone,
        "status": "pending_otp",
        "created_at": time.time(),
        "otp": "1234" # Test rejimi kodi
    }
    return {
        "success": True,
        "order_id": order_id,
        "provider": req.provider.upper(),
        "amount": req.amount,
        "message": f"{req.phone} raqamiga SMS tasdiqlash kodi yuborildi.",
        "test_otp": "1234" # Test uchun
    }

@app.post("/api/payment/verify-otp")
def verify_payment_otp(req: PaymentVerifyRequest):
    order = ORDERS_DB.get(req.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    
    if req.otp_code != "1234" and req.otp_code != order.get("otp"):
        raise HTTPException(status_code=400, detail="SMS kod noto'g'ri kiritildi")
    
    order["status"] = "paid"
    order["paid_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    order["receipt_url"] = f"/api/payment/receipt/{req.order_id}"
    
    return {
        "success": True,
        "message": f"To'lov muvaffaqiyatli amalga oshirildi! {order['plan_name']} tarifi faollashtirildi.",
        "order": order
    }

# Frontend faylini berish
@app.get("/")
def get_index():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_path):
        return FileResponse(
            index_path,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return {"message": "Bilim Qadam AI backend ishlamoqda."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print("\n" + "="*50)
    print(f"🚀 «Bilim Qadam» (Gemini 2.5 / 3.5 Flash) ishga tushdi (Port: {port})!")
    print(f"🌐 Server manzili: http://0.0.0.0:{port}")
    print("="*50 + "\n")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=(port == 8000))