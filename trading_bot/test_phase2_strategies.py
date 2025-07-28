#!/usr/bin/env python3
"""
Phase 2 전략 모듈 테스트
"""

import pandas as pd
import numpy as np
from analysis.strategies import CoreStrategyManager

def test_strategies():
    """핵심 전략 테스트"""
    print("=== Phase 2 핵심 전략 테스트 ===")
    
    # 테스트 데이터 생성
    dates = pd.date_range('2024-01-01', periods=100, freq='H')
    df = pd.DataFrame({
        'open': [50000 + i * 10 for i in range(100)],
        'high': [50000 + i * 10 + 100 for i in range(100)],
        'low': [50000 + i * 10 - 100 for i in range(100)],
        'close': [50000 + i * 10 + 50 for i in range(100)],
        'volume': [1000 + i * 10 for i in range(100)]
    }, index=dates)
    
    # 핵심 전략 분석 실행
    strategy_manager = CoreStrategyManager()
    signals = strategy_manager.analyze({'price_data': df})
    
    print(f"4개 핵심 전략 신호:")
    for strategy, signal in signals.items():
        print(f"  {strategy}: {signal:.3f}")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_strategies() 