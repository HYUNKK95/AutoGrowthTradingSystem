"""
Phase 2 통합 봇 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from bot.integrated_bot import IntegratedTradingBot
from bot.config import Config
from data.database import Database

def test_integrated_bot():
    """통합 봇 테스트"""
    print("=== Phase 2 통합 봇 테스트 ===")
    
    try:
        # 설정 생성
        config = Config(
            binance_api_key='test_key',
            binance_secret_key='test_secret',
            binance_testnet=True,
            binance_api_url='https://testnet.binance.vision',
            database_path='./data/test_trading_bot.db',
            log_level='INFO',
            log_file='./logs/test_trading_bot.log',
            trading_symbol='BTCUSDT',
            initial_capital=3000000,
            max_position_size=0.1,
            stop_loss_percent=0.02,
            take_profit_percent=0.04
        )
        
        # 통합 봇 초기화
        bot = IntegratedTradingBot(config)
        
        # 테스트 데이터 생성
        dates = pd.date_range(start='2024-01-01', end='2024-01-10', freq='1H')
        test_data = pd.DataFrame({
            'timestamp': [int(d.timestamp() * 1000) for d in dates],
            'open': np.random.uniform(45000, 55000, len(dates)),
            'high': np.random.uniform(45000, 55000, len(dates)),
            'low': np.random.uniform(45000, 55000, len(dates)),
            'close': np.random.uniform(45000, 55000, len(dates)),
            'volume': np.random.uniform(1000, 5000, len(dates))
        })
        
        # 최신 데이터로 분석
        latest_data = test_data.iloc[-50:].copy()
        
        # 통합 분석 실행
        result = bot.process_market_data()
        
        print(f"통합 분석 결과:")
        print(f"- 기술적 신호: {result.get('technical_signal', 0):.3f}")
        print(f"- 전략 신호: {result.get('strategy_signal', 0):.3f}")
        print(f"- 감정 신호: {result.get('sentiment_signal', 0):.3f}")
        print(f"- ML 신호: {result.get('ml_signal', 0):.3f}")
        print(f"- 최종 신호: {result.get('final_signal', 0):.3f}")
        
        # 거래 결정
        decision = bot.execute_trading_decision(result)
        print(f"거래 결정: {decision}")
        
        print("=== 테스트 완료 ===")
        
    except Exception as e:
        print(f"통합 봇 테스트 실패: {e}")
        print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_integrated_bot() 