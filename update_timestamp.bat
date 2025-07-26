@echo off
echo AutoGrowthTradingSystem - 타임스탬프 업데이트
echo ============================================

cd /d "%~dp0"
python update_timestamp.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ 타임스탬프 업데이트가 성공적으로 완료되었습니다.
) else (
    echo.
    echo ❌ 타임스탬프 업데이트 중 오류가 발생했습니다.
)

echo.
echo 아무 키나 누르면 종료됩니다...
pause > nul
