#!/usr/bin/env python3
"""
Phase 3 백테스팅 시스템 테스트
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtesting.engine import BacktestEngine
from backtesting.performance import PerformanceEvaluator
from backtesting.optimizer import ParameterOptimizer
from config.coins_config import CoinsConfig

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/phase3_backtesting_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_backtesting_engine():
    """백테스팅 엔진 테스트"""
    print("=== Phase 3 백테스팅 엔진 테스트 ===")
    
    try:
        # 백테스팅 설정
        config = {
            'initial_capital': 3000000,  # 300만원
            'commission': 0.001,         # 0.1% 수수료
            'slippage': 0.0005          # 0.05% 슬리피지
        }
        
        # 백테스팅 엔진 초기화
        engine = BacktestEngine(config)
        
        # 테스트 기간 설정 (최근 1개월)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        print(f"백테스팅 설정:")
        print(f"- 초기 자본: {config['initial_capital']:,}원")
        print(f"- 수수료: {config['commission']*100}%")
        print(f"- 슬리피지: {config['slippage']*100}%")
        print(f"- 테스트 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        print()
        
        # BTCUSDT 백테스팅 테스트
        print("=== BTCUSDT 백테스팅 테스트 ===")
        btc_result = engine.run_backtest(
            symbol='BTCUSDT',
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            strategy='integrated'
        )
        
        if 'error' not in btc_result:
            print(f"✅ BTCUSDT 백테스팅 성공")
            print(f"- 초기 자본: {btc_result['initial_capital']:,}원")
            print(f"- 최종 자본: {btc_result['final_capital']:,.0f}원")
            print(f"- 총 수익률: {btc_result['total_return']*100:.2f}%")
            print(f"- 총 거래 수: {len(btc_result['trades'])}회")
        else:
            print(f"❌ BTCUSDT 백테스팅 실패: {btc_result['error']}")
        
        return btc_result
        
    except Exception as e:
        logger.error(f"백테스팅 엔진 테스트 실패: {e}")
        print(f"테스트 실패: {e}")
        return None

def test_performance_evaluator():
    """성능 평가 시스템 테스트"""
    print("\n=== Phase 3 성능 평가 시스템 테스트 ===")
    
    try:
        # 성능 평가기 초기화
        evaluator = PerformanceEvaluator()
        
        # 백테스팅 결과 생성 (테스트용)
        test_result = {
            'symbol': 'BTCUSDT',
            'initial_capital': 3000000,
            'final_capital': 3150000,
            'total_return': 0.05,
            'trades': [
                {'timestamp': '2025-07-01', 'type': 'buy', 'price': 50000, 'capital': 3000000},
                {'timestamp': '2025-07-15', 'type': 'sell', 'price': 52500, 'capital': 3150000, 'profit': 0.05}
            ],
            'portfolio_history': [
                {'timestamp': '2025-07-01', 'capital': 3000000, 'position': 1},
                {'timestamp': '2025-07-15', 'capital': 3150000, 'position': 0}
            ]
        }
        
        # 성능 지표 계산
        performance = evaluator.calculate_performance_metrics(
            test_result['trades'],
            test_result['portfolio_history'],
            test_result['initial_capital']
        )
        
        print(f"✅ 성능 평가 성공")
        print(f"- 총 수익률: {performance.get('total_return', {}).get('total_return', 0)*100:.2f}%")
        print(f"- 승률: {performance.get('trade_metrics', {}).get('win_rate', 0)*100:.1f}%")
        print(f"- 샤프비율: {performance.get('risk_metrics', {}).get('sharpe_ratio', 0):.3f}")
        print(f"- 최대 드로다운: {performance.get('risk_metrics', {}).get('max_drawdown', 0)*100:.2f}%")
        
        # 성능 리포트 생성
        report = evaluator.generate_performance_report(test_result)
        print("\n📊 성능 리포트:")
        print(report)
        
        return performance
        
    except Exception as e:
        logger.error(f"성능 평가 테스트 실패: {e}")
        print(f"테스트 실패: {e}")
        return None

def test_parameter_optimizer():
    """파라미터 최적화 시스템 테스트"""
    print("\n=== Phase 3 파라미터 최적화 시스템 테스트 ===")
    
    try:
        # 최적화 설정
        config = {
            'initial_capital': 3000000,
            'commission': 0.001,
            'slippage': 0.0005,
            'optimization_metric': 'sharpe_ratio',
            'max_combinations': 10  # 테스트용으로 적게 설정
        }
        
        # 파라미터 최적화기 초기화
        optimizer = ParameterOptimizer(config)
        
        # 테스트 기간
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)  # 1주일
        
        # 파라미터 범위 (테스트용으로 적게 설정)
        param_ranges = {
            'commission': [0.0005, 0.001, 0.002],
            'slippage': [0.0003, 0.0005, 0.001]
        }
        
        print(f"파라미터 최적화 설정:")
        print(f"- 최적화 지표: {config['optimization_metric']}")
        print(f"- 최대 조합 수: {config['max_combinations']}")
        print(f"- 테스트 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        print(f"- 파라미터 범위: {param_ranges}")
        print()
        
        # BTCUSDT 파라미터 최적화
        print("=== BTCUSDT 파라미터 최적화 ===")
        optimization_result = optimizer.optimize_parameters(
            symbol='BTCUSDT',
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            param_ranges=param_ranges
        )
        
        if 'error' not in optimization_result:
            print(f"✅ 파라미터 최적화 성공")
            print(f"- 최적 파라미터: {optimization_result.get('best_params', {})}")
            print(f"- 최적 성능 점수: {optimization_result.get('best_score', 0):.4f}")
            print(f"- 총 테스트 수: {optimization_result.get('total_tests', 0)}")
            
            # 최적화 리포트 생성
            report = optimizer.generate_optimization_report('BTCUSDT', optimization_result)
            print("\n🔧 최적화 리포트:")
            print(report)
        else:
            print(f"❌ 파라미터 최적화 실패: {optimization_result['error']}")
        
        return optimization_result
        
    except Exception as e:
        logger.error(f"파라미터 최적화 테스트 실패: {e}")
        print(f"테스트 실패: {e}")
        return None

def test_strategy_comparison():
    """전략 비교 테스트"""
    print("\n=== Phase 3 전략 비교 테스트 ===")
    
    try:
        # 백테스팅 설정
        config = {
            'initial_capital': 3000000,
            'commission': 0.001,
            'slippage': 0.0005
        }
        
        # 백테스팅 엔진 초기화
        engine = BacktestEngine(config)
        
        # 테스트 기간
        end_date = datetime.now()
        start_date = end_date - timedelta(days=14)  # 2주일
        
        # 테스트할 전략들
        strategies = ['integrated', 'technical', 'sentiment', 'ml']
        
        print(f"전략 비교 테스트 (BTCUSDT, 2주일):")
        print()
        
        strategy_results = {}
        
        for strategy in strategies:
            print(f"테스트 중: {strategy.upper()} 전략")
            
            result = engine.run_backtest(
                symbol='BTCUSDT',
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                strategy=strategy
            )
            
            strategy_results[strategy] = result
            
            if 'error' not in result:
                perf = result.get('performance', {})
                print(f"  ✅ 성공 - 수익률: {result.get('total_return', 0)*100:.2f}%")
            else:
                print(f"  ❌ 실패 - {result['error']}")
        
        # 전략 비교 리포트 생성
        evaluator = PerformanceEvaluator()
        comparison_report = evaluator.compare_strategies(strategy_results)
        
        print("\n🔄 전략 비교 리포트:")
        print(comparison_report)
        
        return strategy_results
        
    except Exception as e:
        logger.error(f"전략 비교 테스트 실패: {e}")
        print(f"테스트 실패: {e}")
        return None

def main():
    """메인 테스트 함수"""
    print("🚀 Phase 3 백테스팅 시스템 테스트 시작")
    print("=" * 60)
    
    # 로그 디렉토리 생성
    os.makedirs('logs', exist_ok=True)
    
    # 1. 백테스팅 엔진 테스트
    backtest_result = test_backtesting_engine()
    
    # 2. 성능 평가 시스템 테스트
    performance_result = test_performance_evaluator()
    
    # 3. 파라미터 최적화 테스트
    optimization_result = test_parameter_optimizer()
    
    # 4. 전략 비교 테스트
    strategy_results = test_strategy_comparison()
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 Phase 3 테스트 결과 요약")
    print("=" * 60)
    
    tests = [
        ("백테스팅 엔진", backtest_result),
        ("성능 평가 시스템", performance_result),
        ("파라미터 최적화", optimization_result),
        ("전략 비교", strategy_results)
    ]
    
    for test_name, result in tests:
        if result and 'error' not in result:
            print(f"✅ {test_name}: 성공")
        else:
            print(f"❌ {test_name}: 실패")
    
    print("\n🎉 Phase 3 백테스팅 시스템 테스트 완료!")

if __name__ == "__main__":
    main() 