#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoGrowthTradingSystem - 타임스탬프 자동 업데이트 스크립트

이 스크립트는 CURRENT_TIMESTAMP.txt 파일을 현재 시간으로 업데이트합니다.
매일 자동으로 실행되도록 설정할 수 있습니다.
"""

import os
from datetime import datetime
from pathlib import Path

def update_timestamp():
    """타임스탬프 파일을 현재 시간으로 업데이트"""
    
    # 현재 시간 가져오기
    now = datetime.now()
    timestamp = now.strftime("%Y.%m.%d.%H.%M.%S")
    date_formatted = now.strftime("%Y년 %m월 %d일 %H시 %M분 %S초")
    
    # 파일 내용 생성
    content = f"""# AutoGrowthTradingSystem - 현재 타임스탬프

## 📅 **현재 시간**
**마지막 업데이트**: {timestamp}
**한국 시간**: {date_formatted}

## 📋 **용도**
- AI 어시스턴트가 현재 날짜/시간을 참고하기 위한 파일
- 프로젝트 진행 상황 추적
- 문서 업데이트 날짜 기록

## 🔄 **업데이트 방법**
이 파일은 매일 자동으로 업데이트되어야 합니다.

### Windows 배치 파일 사용:
```batch
@echo off
echo # AutoGrowthTradingSystem - 현재 타임스탬프 > CURRENT_TIMESTAMP.txt
echo. >> CURRENT_TIMESTAMP.txt
echo ## 📅 **현재 시간** >> CURRENT_TIMESTAMP.txt
echo **마지막 업데이트**: %date:~0,4%.%date:~5,2%.%date:~8,2%.%time:~0,2%.%time:~3,2%.%time:~6,2% >> CURRENT_TIMESTAMP.txt
echo. >> CURRENT_TIMESTAMP.txt
echo ## 📋 **용도** >> CURRENT_TIMESTAMP.txt
echo - AI 어시스턴트가 현재 날짜/시간을 참고하기 위한 파일 >> CURRENT_TIMESTAMP.txt
echo - 프로젝트 진행 상황 추적 >> CURRENT_TIMESTAMP.txt
echo - 문서 업데이트 날짜 기록 >> CURRENT_TIMESTAMP.txt
```

### Python 스크립트 사용:
```python
from datetime import datetime

timestamp = datetime.now().strftime("%Y.%m.%d.%H.%M.%S")

content = f\"\"\"# AutoGrowthTradingSystem - 현재 타임스탬프

## 📅 **현재 시간**
**마지막 업데이트**: {{timestamp}}

## 📋 **용도**
- AI 어시스턴트가 현재 날짜/시간을 참고하기 위한 파일
- 프로젝트 진행 상황 추적
- 문서 업데이트 날짜 기록

## 🔄 **업데이트 방법**
이 파일은 매일 자동으로 업데이트되어야 합니다.
\"\"\"

with open('CURRENT_TIMESTAMP.txt', 'w', encoding='utf-8') as f:
    f.write(content)
```

## ⏰ **자동 업데이트 설정**

### Windows 작업 스케줄러:
1. 작업 스케줄러 열기
2. "기본 작업 만들기" 선택
3. 트리거: 매일
4. 동작: 프로그램 시작
5. 프로그램: `python update_timestamp.py`

### Linux/Mac Cron:
```bash
# 매일 자정에 업데이트
0 0 * * * /usr/bin/python3 /path/to/project/update_timestamp.py
```

### 매일 자동 실행 배치 파일 (Windows):
```batch
@echo off
cd /d "%~dp0"
python update_timestamp.py
echo 타임스탬프 업데이트 완료: {timestamp}
pause
```

---
**파일 생성일**: 2024.01.31.15.30.00
**마지막 업데이트**: {timestamp}
**다음 업데이트**: 매일 자동 업데이트
**스크립트 버전**: 1.0
"""
    
    # 파일 쓰기
    try:
        with open('CURRENT_TIMESTAMP.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 타임스탬프 업데이트 완료: {timestamp}")
        print(f"📁 파일 위치: {os.path.abspath('CURRENT_TIMESTAMP.txt')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 타임스탬프 업데이트 실패: {e}")
        return False

def create_batch_file():
    """Windows용 배치 파일 생성"""
    
    batch_content = """@echo off
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
"""
    
    try:
        with open('update_timestamp.bat', 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        print("✅ 배치 파일 생성 완료: update_timestamp.bat")
        return True
        
    except Exception as e:
        print(f"❌ 배치 파일 생성 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("🕐 AutoGrowthTradingSystem - 타임스탬프 업데이트")
    print("=" * 50)
    
    # 타임스탬프 업데이트
    success = update_timestamp()
    
    if success:
        # 배치 파일 생성 (Windows용)
        create_batch_file()
        
        print("\n📋 사용 방법:")
        print("1. 수동 실행: python update_timestamp.py")
        print("2. 배치 파일 실행: update_timestamp.bat")
        print("3. 자동 실행: Windows 작업 스케줄러 설정")
        print("4. 매일 자동 실행: 매일 자정에 스케줄러 설정")
        
        print("\n🎯 설정 완료!")
        print("이제 AI 어시스턴트가 CURRENT_TIMESTAMP.txt 파일을 참고하여")
        print("현재 날짜와 시간을 알 수 있습니다.")
    
    else:
        print("\n❌ 설정 실패!")
        print("오류를 확인하고 다시 시도해주세요.")

if __name__ == "__main__":
    main() 