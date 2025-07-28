#!/usr/bin/env python3
"""
Phase 2 기술적 분석 모듈 테스트
"""

import pandas as pd
import numpy as np
from analysis.technical import CoreTechnicalAnalyzer

def test_technical_analysis():
    """핵심 기술적 분석 테스트"""
    print("=== Phase 2 핵심 기술적 분석 테스트 ===")
    
    # 테스트 데이터 생성
    dates = pd.date_range('2024-01-01', periods=100, freq='H')
    df = pd.DataFrame({
        'open': [50000 + i * 10 for i in range(100)],
        'high': [50000 + i * 10 + 100 for i in range(100)],
        'low': [50000 + i * 10 - 100 for i in range(100)],
        'close': [50000 + i * 10 + 50 for i in range(100)],
        'volume': [1000 + i * 10 for i in range(100)]
    }, index=dates)
    
    # 핵심 기술적 분석 실행
    analyzer = CoreTechnicalAnalyzer()
    result = analyzer.analyze(df)
    
    print(f"5개 핵심 지표 신호:")
    for indicator, signal in result['signals'].items():
        print(f"  {indicator}: {signal}")
    
    print(f"기술적 분석 신호: {result['technical_signal']:.3f}")
    print(f"지표 값들:")
    for indicator, value in result['indicators'].items():
        if pd.notna(value):
            print(f"  {indicator}: {value:.2f}")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_technical_analysis() 