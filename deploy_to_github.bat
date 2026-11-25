@echo off
chcp 65001 >nul
echo ========================================================
echo  🚀 «Bilim Qadam» GitHub-ga yuklash yordamchisi
echo ========================================================
echo.
set /p REPO_URL="GitHub repository havolasini kiriting (masalan: https://github.com/username/bilim-qadam.git): "

if "%REPO_URL%"=="" (
    echo [XATO] Havola kiritilmadi!
    pause
    exit /b
)

git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main
echo.
echo Kodlar GitHub-ga yuborilmoqda...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo  ✅ MUVAFFAQIYATLI YUKLANDI!
    echo  Endi Render.com ga kirib, ushbu repozitoriyni ulang.
    echo ========================================================
) else (
    echo.
    echo [OGOHLANTIRISH] GitHub autentifikatsiyasini tekshiring.
)
pause
