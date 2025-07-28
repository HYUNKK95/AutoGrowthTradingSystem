#!/usr/bin/env python3
"""
백테스팅 시스템 테스트
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtesting.engine import BacktestEngine
from config.coins_config import CoinsConfig

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backtesting_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_backtesting():
    """백테스팅 시스템 테스트"""
    print("=== Phase 3 백테스팅 시스템 테스트 ===")
    
    try:
        # 백테스팅 설정
        config = {
            'initial_capital': 3000000,  # 300만원
            'commission': 0.001,         # 0.1% 수수료
            'slippage': 0.0005          # 0.05% 슬리피지
        }
        
        # 백테스팅 엔진 초기화
        engine = BacktestEngine(config)
        
        # 테스트 기간 설정 (최근 3개월)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        # 50개 코인 목록
        coins_config = CoinsConfig()
        symbols = coins_config.coins
        
        print(f"백테스팅 설정:")
        print(f"- 초기 자본: {config['initial_capital']:,}원")
        print(f"- 수수료: {config['commission']*100}%")
        print(f"- 슬리피지: {config['slippage']*100}%")
        print(f"- 테스트 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        print(f"- 테스트 코인: {len(symbols)}개")
        print()
        
        # 단일 코인 테스트 (BTCUSDT)
        print("=== 단일 코인 백테스팅 테스트 (BTCUSDT) ===")
        btc_result = engine.run_backtest(
            symbol='BTCUSDT',
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            strategy='integrated'
        )
        
        if 'error' not in btc_result:
            print(f"BTCUSDT 백테스팅 결과:")
            print(f"- 초기 자본: {btc_result['initial_capital']:,}원")
            print(f"- 최종 자본: {btc_result['final_capital']:,.0f}원")
            print(f"- 총 수익률: {btc_result['total_return']*100:.2f}%")
            
            perf = btc_result['performance']
            print(f"- 샤프비율: {perf['sharpe_ratio']:.3f}")
            print(f"- 최대 드로다운: {perf['max_drawdown']*100:.2f}%")
            print(f"- 승률: {perf['win_rate']*100:.1f}%")
            print(f"- 총 거래 수: {perf['total_trades']}회")
            print(f"- 평균 수익: {perf['avg_win']*100:.2f}%")
            print(f"- 평균 손실: {perf['avg_loss']*100:.2f}%")
            print(f"- 손익비: {perf['profit_factor']:.2f}")
        else:
            print(f"BTCUSDT 백테스팅 실패: {btc_result['error']}")
        
        print()
        
        # 다중 코인 테스트 (상위 10개)
        print("=== 다중 코인 백테스팅 테스트 (상위 10개) ===")
        top_symbols = symbols[:10]  # 상위 10개만 테스트
        
        multi_result = engine.run_multi_backtest(
            symbols=top_symbols,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            strategy='integrated'
        )
        
        if 'portfolio_results' in multi_result:
            portfolio = multi_result['portfolio_results']
            print(f"포트폴리오 백테스팅 결과:")
            print(f"- 테스트 코인 수: {portfolio['num_coins']}개")
            print(f"- 총 초기 자본: {portfolio['total_initial_capital']:,}원")
            print(f"- 총 최종 자본: {portfolio['total_capital']:,.0f}원")
            print(f"- 포트폴리오 수익률: {portfolio['portfolio_return']*100:.2f}%")
            
            print("\n개별 코인 성능:")
            for symbol, perf in portfolio['performance_summary'].items():
                print(f"- {symbol}: {perf['total_return']*100:6.2f}% "
                      f"(승률: {perf['win_rate']*100:4.1f}%, "
                      f"거래: {perf['total_trades']:3d}회)")
        else:
            print("다중 코인 백테스팅 실패")
        
        print()
        print("=== 백테스팅 테스트 완료 ===")
        
    except Exception as e:
        logger.error(f"백테스팅 테스트 실패: {e}")
        print(f"테스트 실패: {e}")

def test_strategy_comparison():
    """전략 비교 테스트"""
    print("=== 전략 비교 테스트 ===")
    
    try:
        # 백테스팅 설정
        config = {
            'initial_capital': 3000000,
            'commission': 0.001,
            'slippage': 0.0005
        }
        
        engine = BacktestEngine(config)
        
        # 테스트 기간
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # 1개월
        
        # 테스트할 전략들
        strategies = ['integrated', 'technical', 'sentiment', 'ml']
        
        print(f"전략 비교 테스트 (BTCUSDT, 1개월):")
        print()
        
        for strategy in strategies:
            result = engine.run_backtest(
                symbol='BTCUSDT',
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                strategy=strategy
            )
            
            if 'error' not in result:
                perf = result['performance']
                print(f"{strategy.upper():12} 전략:")
                print(f"  - 수익률: {result['total_return']*100:6.2f}%")
                print(f"  - 샤프비율: {perf['sharpe_ratio']:6.3f}")
                print(f"  - 최대 드로다운: {perf['max_drawdown']*100:6.2f}%")
                print(f"  - 승률: {perf['win_rate']*100:6.1f}%")
                print(f"  - 거래 수: {perf['total_trades']:6d}회")
                print()
            else:
                print(f"{strategy.upper():12} 전략: 실패 - {result['error']}")
                print()
        
    except Exception as e:
        logger.error(f"전략 비교 테스트 실패: {e}")
        print(f"전략 비교 테스트 실패: {e}")

if __name__ == "__main__":
    # 로그 디렉토리 생성
    os.makedirs('logs', exist_ok=True)
    
    # 백테스팅 테스트 실행
    test_backtesting()
    
    print("\n" + "="*50 + "\n")
    
    # 전략 비교 테스트 실행
    test_strategy_comparison() 