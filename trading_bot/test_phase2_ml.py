#!/usr/bin/env python3
"""
Phase 2 ML 예측 모듈 테스트
"""

import pandas as pd
import numpy as np
from analysis.ml import MLPredictor

def test_ml_prediction():
    """ML 예측 테스트"""
    print("=== Phase 2 ML 예측 테스트 ===")
    
    # 테스트 데이터 생성
    dates = pd.date_range('2024-01-01', periods=200, freq='H')
    df = pd.DataFrame({
        'open': [50000 + i * 10 for i in range(200)],
        'high': [50000 + i * 10 + 100 for i in range(200)],
        'low': [50000 + i * 10 - 100 for i in range(200)],
        'close': [50000 + i * 10 + 50 for i in range(200)],
        'volume': [1000 + i * 10 for i in range(200)]
    }, index=dates)
    
    # ML 예측기 초기화
    predictor = MLPredictor()
    
    # 모델 학습
    print("모델 학습 중...")
    predictor.train(df)
    
    # 예측 테스트
    if predictor.is_trained:
        prediction = predictor.predict(df)
        print(f"ML 예측 신호: {prediction:.3f}")
    else:
        print("모델이 학습되지 않았습니다")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_ml_prediction() 