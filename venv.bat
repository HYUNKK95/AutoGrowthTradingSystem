@echo off
chcp 65001 > nul
setlocal

REM 🐍 가상환경 진입
call C:\Users\realf\Projects\AutoGrowthTradingSystem\.venv\Scripts\activate.bat

REM 📁 루트 폴더(Moneyday)로 이동
cd /d C:\Users\realf\Projects\AutoGrowthTradingSystem

echo ✅ .venv 진입 후 root 위치로 이동 완료
cmd /k
