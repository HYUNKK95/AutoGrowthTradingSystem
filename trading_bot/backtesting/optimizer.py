"""
파라미터 최적화 시스템
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from itertools import product
import json
import os

from .engine import BacktestEngine
from .performance import PerformanceEvaluator

class ParameterOptimizer:
    """파라미터 최적화 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        """파라미터 최적화 초기화"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.performance_evaluator = PerformanceEvaluator()
        
        # 최적화 설정
        self.optimization_metric = config.get('optimization_metric', 'sharpe_ratio')
        self.max_combinations = config.get('max_combinations', 1000)
        
        # 최적화 결과 저장
        self.results = []
        self.best_params = {}
        self.best_score = float('-inf')
        
    def optimize_parameters(self, symbol: str, start_date: str, end_date: str,
                          param_ranges: Dict[str, List]) -> Dict[str, Any]:
        """파라미터 최적화 실행"""
        try:
            self.logger.info(f"{symbol} 파라미터 최적화 시작")
            
            # 파라미터 조합 생성
            param_combinations = self._generate_param_combinations(param_ranges)
            
            if len(param_combinations) > self.max_combinations:
                self.logger.warning(f"조합 수가 너무 많음: {len(param_combinations)} > {self.max_combinations}")
                param_combinations = param_combinations[:self.max_combinations]
            
            self.logger.info(f"총 {len(param_combinations)}개 조합 테스트")
            
            # 각 조합 테스트
            for i, params in enumerate(param_combinations):
                self.logger.info(f"테스트 진행: {i+1}/{len(param_combinations)}")
                
                # 백테스팅 실행
                result = self._run_backtest_with_params(symbol, start_date, end_date, params)
                
                if result and 'error' not in result:
                    # 성능 지표 계산
                    performance = self._calculate_performance_score(result)
                    
                    # 결과 저장
                    self.results.append({
                        'params': params,
                        'performance': performance,
                        'backtest_result': result
                    })
                    
                    # 최고 성능 업데이트
                    if performance > self.best_score:
                        self.best_score = performance
                        self.best_params = params
                        self.logger.info(f"새로운 최고 성능: {performance:.4f}")
            
            # 최적화 결과 정리
            optimization_result = self._summarize_optimization_results()
            
            # 결과 저장
            self._save_optimization_results(symbol, optimization_result)
            
            self.logger.info(f"{symbol} 파라미터 최적화 완료")
            return optimization_result
            
        except Exception as e:
            self.logger.error(f"파라미터 최적화 실패: {e}")
            return {'error': str(e)}
    
    def _generate_param_combinations(self, param_ranges: Dict[str, List]) -> List[Dict]:
        """파라미터 조합 생성"""
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        
        combinations = []
        for combination in product(*param_values):
            param_dict = dict(zip(param_names, combination))
            combinations.append(param_dict)
        
        return combinations
    
    def _run_backtest_with_params(self, symbol: str, start_date: str, end_date: str,
                                 params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """특정 파라미터로 백테스팅 실행"""
        try:
            # 백테스팅 엔진 초기화 (파라미터 포함)
            engine_config = self.config.copy()
            engine_config.update(params)
            
            engine = BacktestEngine(engine_config)
            
            # 백테스팅 실행
            result = engine.run_backtest(symbol, start_date, end_date, 'integrated')
            
            return result
            
        except Exception as e:
            self.logger.error(f"백테스팅 실패 (파라미터: {params}): {e}")
            return None
    
    def _calculate_performance_score(self, backtest_result: Dict[str, Any]) -> float:
        """성능 점수 계산"""
        try:
            if 'performance' not in backtest_result:
                return float('-inf')
            
            perf = backtest_result['performance']
            
            if self.optimization_metric == 'sharpe_ratio':
                return perf.get('risk_metrics', {}).get('sharpe_ratio', 0.0)
            elif self.optimization_metric == 'total_return':
                return backtest_result.get('total_return', 0.0)
            elif self.optimization_metric == 'calmar_ratio':
                return perf.get('risk_metrics', {}).get('calmar_ratio', 0.0)
            elif self.optimization_metric == 'profit_factor':
                return perf.get('trade_metrics', {}).get('profit_factor', 0.0)
            elif self.optimization_metric == 'win_rate':
                return perf.get('trade_metrics', {}).get('win_rate', 0.0)
            else:
                # 복합 점수 (샤프비율 + 수익률 - 최대드로다운)
                sharpe = perf.get('risk_metrics', {}).get('sharpe_ratio', 0.0)
                total_return = backtest_result.get('total_return', 0.0)
                max_dd = abs(perf.get('risk_metrics', {}).get('max_drawdown', 0.0))
                
                return sharpe + total_return - max_dd
                
        except Exception as e:
            self.logger.error(f"성능 점수 계산 실패: {e}")
            return float('-inf')
    
    def _summarize_optimization_results(self) -> Dict[str, Any]:
        """최적화 결과 요약"""
        if not self.results:
            return {'error': '최적화 결과 없음'}
        
        # 결과 정렬 (성능 기준)
        sorted_results = sorted(self.results, key=lambda x: x['performance'], reverse=True)
        
        # 상위 10개 결과
        top_results = sorted_results[:10]
        
        # 통계 계산
        performances = [r['performance'] for r in self.results]
        
        summary = {
            'best_params': self.best_params,
            'best_score': self.best_score,
            'total_tests': len(self.results),
            'top_results': top_results,
            'performance_stats': {
                'mean': np.mean(performances),
                'std': np.std(performances),
                'min': np.min(performances),
                'max': np.max(performances)
            }
        }
        
        return summary
    
    def _save_optimization_results(self, symbol: str, results: Dict[str, Any]):
        """최적화 결과 저장"""
        try:
            # 결과 디렉토리 생성
            results_dir = 'optimization_results'
            os.makedirs(results_dir, exist_ok=True)
            
            # 파일명 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{results_dir}/{symbol}_optimization_{timestamp}.json"
            
            # JSON으로 저장
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"최적화 결과 저장: {filename}")
            
        except Exception as e:
            self.logger.error(f"최적화 결과 저장 실패: {e}")
    
    def generate_optimization_report(self, symbol: str, results: Dict[str, Any]) -> str:
        """최적화 리포트 생성"""
        try:
            report = []
            report.append("=" * 60)
            report.append(f"🔧 {symbol} 파라미터 최적화 리포트")
            report.append("=" * 60)
            
            if 'error' in results:
                report.append(f"❌ 최적화 실패: {results['error']}")
                return "\n".join(report)
            
            # 최적 파라미터
            best_params = results.get('best_params', {})
            best_score = results.get('best_score', 0)
            
            report.append(f"🏆 최적 파라미터")
            for param, value in best_params.items():
                report.append(f"  - {param}: {value}")
            report.append(f"  - 최적 성능 점수: {best_score:.4f}")
            report.append("")
            
            # 통계 정보
            stats = results.get('performance_stats', {})
            report.append(f"📊 성능 통계")
            report.append(f"  - 총 테스트 수: {results.get('total_tests', 0)}")
            report.append(f"  - 평균 성능: {stats.get('mean', 0):.4f}")
            report.append(f"  - 표준편차: {stats.get('std', 0):.4f}")
            report.append(f"  - 최소 성능: {stats.get('min', 0):.4f}")
            report.append(f"  - 최대 성능: {stats.get('max', 0):.4f}")
            report.append("")
            
            # 상위 결과
            top_results = results.get('top_results', [])
            if top_results:
                report.append(f"🥇 상위 5개 결과")
                for i, result in enumerate(top_results[:5], 1):
                    params = result['params']
                    performance = result['performance']
                    report.append(f"  {i}. 성능: {performance:.4f}")
                    for param, value in params.items():
                        report.append(f"     - {param}: {value}")
                    report.append("")
            
            report.append("=" * 60)
            
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"최적화 리포트 생성 실패: {e}")
            return f"최적화 리포트 생성 실패: {e}"
    
    def optimize_multiple_symbols(self, symbols: List[str], start_date: str, end_date: str,
                                 param_ranges: Dict[str, List]) -> Dict[str, Any]:
        """다중 심볼 파라미터 최적화"""
        try:
            self.logger.info(f"다중 심볼 파라미터 최적화 시작: {len(symbols)}개 심볼")
            
            all_results = {}
            
            for symbol in symbols:
                self.logger.info(f"최적화 진행: {symbol}")
                
                # 개별 심볼 최적화
                result = self.optimize_parameters(symbol, start_date, end_date, param_ranges)
                all_results[symbol] = result
            
            # 전체 요약
            summary = self._summarize_multi_symbol_results(all_results)
            
            return {
                'individual_results': all_results,
                'summary': summary
            }
            
        except Exception as e:
            self.logger.error(f"다중 심볼 최적화 실패: {e}")
            return {'error': str(e)}
    
    def _summarize_multi_symbol_results(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """다중 심볼 결과 요약"""
        successful_results = {k: v for k, v in all_results.items() if 'error' not in v}
        
        if not successful_results:
            return {'error': '성공한 최적화 결과 없음'}
        
        # 전체 통계
        all_scores = []
        best_symbol = None
        best_score = float('-inf')
        
        for symbol, result in successful_results.items():
            score = result.get('best_score', 0)
            all_scores.append(score)
            
            if score > best_score:
                best_score = score
                best_symbol = symbol
        
        summary = {
            'total_symbols': len(all_results),
            'successful_symbols': len(successful_results),
            'best_symbol': best_symbol,
            'best_overall_score': best_score,
            'average_score': np.mean(all_scores),
            'score_std': np.std(all_scores)
        }
        
        return summary 