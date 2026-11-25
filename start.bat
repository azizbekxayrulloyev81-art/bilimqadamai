@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ========================================================
echo   Bilim Qadam AI - Gemini AI Serverini Ishga Tushirish
echo   "Raqamli avlod qizlari" tanlovi uchun
echo ========================================================
echo.
echo Server ishga tushmoqda...
start http://localhost:8000
python app.py
pause
