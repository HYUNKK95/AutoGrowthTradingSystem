@echo off
chcp 65001 > nul
setlocal

set ZIP_NAME=AutoGrowthTradingSystem.zip
set TEMP_DIR=_temp_zip_source

REM 기존 zip 삭제
if exist "%ZIP_NAME%" (
    del "%ZIP_NAME%"
)

REM 임시 폴더 삭제 후 생성
if exist "%TEMP_DIR%" (
    rmdir /S /Q "%TEMP_DIR%"
)
mkdir "%TEMP_DIR%"

REM 제외 폴더 및 파일 복사 (robocopy)
robocopy . "%TEMP_DIR%" /E /XD .venv .idea .pytest_cache"%TEMP_DIR%" /XF "%ZIP_NAME%" "압축하기.bat" > nul

REM 압축 실행
powershell -nologo -command "Compress-Archive -Path '%TEMP_DIR%\*' -DestinationPath '%ZIP_NAME%' -Force"

REM 잠시 대기 후 임시 폴더 삭제
timeout /T 2 > nul
rmdir /S /Q "%TEMP_DIR%"

echo ✅ 압축 완료: %ZIP_NAME%
pause
