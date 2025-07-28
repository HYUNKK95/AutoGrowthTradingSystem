"""
성능 평가 시스템
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class PerformanceEvaluator:
    """성능 평가 클래스"""
    
    def __init__(self):
        """성능 평가 초기화"""
        self.logger = logging.getLogger(__name__)
        
    def calculate_performance_metrics(self, trades: List[Dict], 
                                   portfolio_history: List[Dict],
                                   initial_capital: float) -> Dict[str, Any]:
        """성능 지표 계산"""
        try:
            # 기본 수익률 계산
            total_return = self._calculate_total_return(portfolio_history, initial_capital)
            
            # 거래별 성능 계산
            trade_metrics = self._calculate_trade_metrics(trades)
            
            # 위험 지표 계산
            risk_metrics = self._calculate_risk_metrics(portfolio_history, initial_capital)
            
            # 시간별 성능 계산
            time_metrics = self._calculate_time_metrics(portfolio_history, initial_capital)
            
            return {
                'total_return': total_return,
                'trade_metrics': trade_metrics,
                'risk_metrics': risk_metrics,
                'time_metrics': time_metrics
            }
            
        except Exception as e:
            self.logger.error(f"성능 지표 계산 실패: {e}")
            return {}
    
    def _calculate_total_return(self, portfolio_history: List[Dict], 
                              initial_capital: float) -> Dict[str, float]:
        """총 수익률 계산"""
        if not portfolio_history:
            return {'total_return': 0.0, 'final_capital': initial_capital}
        
        final_capital = portfolio_history[-1]['capital']
        total_return = (final_capital - initial_capital) / initial_capital
        
        return {
            'total_return': total_return,
            'final_capital': final_capital,
            'initial_capital': initial_capital,
            'absolute_return': final_capital - initial_capital
        }
    
    def _calculate_trade_metrics(self, trades: List[Dict]) -> Dict[str, Any]:
        """거래별 성능 지표 계산"""
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0,
                'largest_win': 0.0,
                'largest_loss': 0.0
            }
        
        # 수익 거래만 필터링
        profitable_trades = [t for t in trades if 'profit' in t and t['profit'] > 0]
        losing_trades = [t for t in trades if 'profit' in t and t['profit'] < 0]
        
        total_trades = len([t for t in trades if 'profit' in t])
        winning_trades = len(profitable_trades)
        losing_trades_count = len(losing_trades)
        
        # 승률
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
        
        # 평균 수익/손실
        avg_win = np.mean([t['profit'] for t in profitable_trades]) if profitable_trades else 0.0
        avg_loss = abs(np.mean([t['profit'] for t in losing_trades])) if losing_trades else 0.0
        
        # 손익비
        profit_factor = avg_win / avg_loss if avg_loss > 0 else 0.0
        
        # 최대 수익/손실
        largest_win = max([t['profit'] for t in profitable_trades]) if profitable_trades else 0.0
        largest_loss = min([t['profit'] for t in losing_trades]) if losing_trades else 0.0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades_count,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'largest_win': largest_win,
            'largest_loss': largest_loss
        }
    
    def _calculate_risk_metrics(self, portfolio_history: List[Dict], 
                               initial_capital: float) -> Dict[str, float]:
        """위험 지표 계산"""
        if not portfolio_history:
            return {
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'volatility': 0.0,
                'var_95': 0.0,
                'calmar_ratio': 0.0
            }
        
        # 포트폴리오 데이터프레임 생성
        df = pd.DataFrame(portfolio_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # 수익률 계산
        df['return'] = df['capital'].pct_change()
        df['cumulative_return'] = df['capital'] / initial_capital
        
        # 샤프비율 (연간화)
        returns = df['return'].dropna()
        if len(returns) > 0:
            # 연간화 (1분봉 기준, 1년 = 525,600분)
            annual_return = returns.mean() * 525600
            annual_volatility = returns.std() * np.sqrt(525600)
            sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0.0
        else:
            sharpe_ratio = 0.0
        
        # 최대 드로다운
        df['peak'] = df['cumulative_return'].expanding().max()
        df['drawdown'] = (df['cumulative_return'] - df['peak']) / df['peak']
        max_drawdown = df['drawdown'].min()
        
        # 변동성
        volatility = returns.std() if len(returns) > 0 else 0.0
        
        # VaR (95%)
        var_95 = np.percentile(returns, 5) if len(returns) > 0 else 0.0
        
        # Calmar 비율
        total_return = (df['capital'].iloc[-1] - initial_capital) / initial_capital
        calmar_ratio = total_return / abs(max_drawdown) if max_drawdown != 0 else 0.0
        
        return {
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'volatility': volatility,
            'var_95': var_95,
            'calmar_ratio': calmar_ratio
        }
    
    def _calculate_time_metrics(self, portfolio_history: List[Dict], 
                               initial_capital: float) -> Dict[str, Any]:
        """시간별 성능 지표 계산"""
        if not portfolio_history:
            return {
                'monthly_returns': {},
                'daily_returns': {},
                'best_month': None,
                'worst_month': None
            }
        
        # 포트폴리오 데이터프레임 생성
        df = pd.DataFrame(portfolio_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # 월별 수익률
        df['month'] = df['timestamp'].dt.to_period('M')
        monthly_returns = df.groupby('month')['capital'].last().pct_change()
        
        # 일별 수익률
        df['date'] = df['timestamp'].dt.date
        daily_returns = df.groupby('date')['capital'].last().pct_change()
        
        # 최고/최저 월
        best_month = monthly_returns.idxmax() if len(monthly_returns) > 0 else None
        worst_month = monthly_returns.idxmin() if len(monthly_returns) > 0 else None
        
        return {
            'monthly_returns': monthly_returns.to_dict(),
            'daily_returns': daily_returns.to_dict(),
            'best_month': best_month,
            'worst_month': worst_month,
            'avg_monthly_return': monthly_returns.mean() if len(monthly_returns) > 0 else 0.0,
            'avg_daily_return': daily_returns.mean() if len(daily_returns) > 0 else 0.0
        }
    
    def generate_performance_report(self, backtest_results: Dict[str, Any]) -> str:
        """성능 리포트 생성"""
        try:
            report = []
            report.append("=" * 60)
            report.append("📊 백테스팅 성능 리포트")
            report.append("=" * 60)
            
            # 기본 정보
            symbol = backtest_results.get('symbol', 'Unknown')
            initial_capital = backtest_results.get('initial_capital', 0)
            final_capital = backtest_results.get('final_capital', 0)
            total_return = backtest_results.get('total_return', 0)
            
            report.append(f"📈 기본 성과")
            report.append(f"  - 심볼: {symbol}")
            report.append(f"  - 초기 자본: {initial_capital:,.0f}원")
            report.append(f"  - 최종 자본: {final_capital:,.0f}원")
            report.append(f"  - 총 수익률: {total_return*100:.2f}%")
            report.append("")
            
            # 거래 성과
            if 'performance' in backtest_results:
                perf = backtest_results['performance']
                trade_metrics = perf.get('trade_metrics', {})
                
                report.append(f"💰 거래 성과")
                report.append(f"  - 총 거래 수: {trade_metrics.get('total_trades', 0)}회")
                report.append(f"  - 승률: {trade_metrics.get('win_rate', 0)*100:.1f}%")
                report.append(f"  - 평균 수익: {trade_metrics.get('avg_win', 0)*100:.2f}%")
                report.append(f"  - 평균 손실: {trade_metrics.get('avg_loss', 0)*100:.2f}%")
                report.append(f"  - 손익비: {trade_metrics.get('profit_factor', 0):.2f}")
                report.append("")
                
                # 위험 지표
                risk_metrics = perf.get('risk_metrics', {})
                report.append(f"⚠️ 위험 지표")
                report.append(f"  - 샤프비율: {risk_metrics.get('sharpe_ratio', 0):.3f}")
                report.append(f"  - 최대 드로다운: {risk_metrics.get('max_drawdown', 0)*100:.2f}%")
                report.append(f"  - 변동성: {risk_metrics.get('volatility', 0)*100:.2f}%")
                report.append(f"  - VaR (95%): {risk_metrics.get('var_95', 0)*100:.2f}%")
                report.append(f"  - Calmar 비율: {risk_metrics.get('calmar_ratio', 0):.3f}")
                report.append("")
            
            report.append("=" * 60)
            
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"성능 리포트 생성 실패: {e}")
            return f"성능 리포트 생성 실패: {e}"
    
    def compare_strategies(self, strategy_results: Dict[str, Dict]) -> str:
        """전략 비교 리포트 생성"""
        try:
            report = []
            report.append("=" * 60)
            report.append("🔄 전략 비교 리포트")
            report.append("=" * 60)
            
            # 헤더
            report.append(f"{'전략':<15} {'수익률':<10} {'샤프비율':<10} {'최대DD':<10} {'승률':<8} {'거래수':<6}")
            report.append("-" * 60)
            
            # 각 전략 결과
            for strategy, result in strategy_results.items():
                if 'error' in result:
                    report.append(f"{strategy:<15} {'실패':<10} {'-':<10} {'-':<10} {'-':<8} {'-':<6}")
                    continue
                
                perf = result.get('performance', {})
                total_return = result.get('total_return', 0) * 100
                sharpe = perf.get('risk_metrics', {}).get('sharpe_ratio', 0)
                max_dd = perf.get('risk_metrics', {}).get('max_drawdown', 0) * 100
                win_rate = perf.get('trade_metrics', {}).get('win_rate', 0) * 100
                trades = perf.get('trade_metrics', {}).get('total_trades', 0)
                
                report.append(f"{strategy:<15} {total_return:>8.2f}% {sharpe:>9.3f} {max_dd:>9.2f}% {win_rate:>6.1f}% {trades:>5d}")
            
            report.append("=" * 60)
            
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"전략 비교 리포트 생성 실패: {e}")
            return f"전략 비교 리포트 생성 실패: {e}" 