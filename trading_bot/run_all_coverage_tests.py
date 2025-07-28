#!/usr/bin/env python3
"""
전체 프로젝트 커버리지 테스트 실행
"""

import subprocess
import sys
import os

def run_coverage_test():
    """전체 프로젝트 커버리지 테스트 실행"""
    print("🚀 전체 프로젝트 커버리지 테스트 시작")
    print("=" * 60)
    
    # 1. Config 클래스 커버리지
    print("📊 Config 클래스 커버리지 테스트...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", "test_config_80_coverage.py", 
        "--cov=bot.config", "--cov-report=term", "--tb=no"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Config 클래스 테스트 통과")
        # 커버리지 추출
        for line in result.stdout.split('\n'):
            if 'bot\\config.py' in line:
                print(f"   📈 {line.strip()}")
    else:
        print("❌ Config 클래스 테스트 실패")
    
    print()
    
    # 2. Database 클래스 커버리지
    print("📊 Database 클래스 커버리지 테스트...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", "test_database_80_coverage.py", 
        "--cov=data.database", "--cov-report=term", "--tb=no"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Database 클래스 테스트 통과")
        # 커버리지 추출
        for line in result.stdout.split('\n'):
            if 'data\\database.py' in line:
                print(f"   📈 {line.strip()}")
    else:
        print("❌ Database 클래스 테스트 실패")
    
    print()
    
    # 3. 전체 프로젝트 커버리지
    print("📊 전체 프로젝트 커버리지 테스트...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "test_config_80_coverage.py", "test_database_80_coverage.py",
        "--cov=bot", "--cov=config", "--cov=data", 
        "--cov-report=term", "--cov-report=html", "--tb=no"
    ], capture_output=True, text=True)
    
    print("✅ 전체 프로젝트 테스트 완료")
    
    # 커버리지 요약 추출
    print("\n📈 커버리지 요약:")
    for line in result.stdout.split('\n'):
        if 'TOTAL' in line and '%' in line:
            print(f"   {line.strip()}")
        elif 'Name' in line and 'Stmts' in line and 'Miss' in line and 'Cover' in line:
            print(f"   {line.strip()}")
        elif '---' in line and len(line.strip()) > 10:
            print(f"   {line.strip()}")
        elif any(x in line for x in ['bot\\', 'config\\', 'data\\']) and '%' in line:
            print(f"   {line.strip()}")
    
    print("\n📁 HTML 리포트 생성됨: htmlcov/index.html")
    print("🎉 커버리지 테스트 완료!")

if __name__ == "__main__":
    run_coverage_test() 