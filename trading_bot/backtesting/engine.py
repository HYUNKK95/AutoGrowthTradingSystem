"""
백테스팅 엔진
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from data.database import Database
from analysis.technical import CoreTechnicalAnalyzer
from analysis.sentiment import SentimentAnalyzer
from analysis.ml import MLPredictor
from analysis.signal_integrator import SignalIntegrator

class BacktestEngine:
    """백테스팅 엔진 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        """백테스팅 엔진 초기화"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 백테스팅 설정
        self.initial_capital = config.get('initial_capital', 3000000)
        self.commission = config.get('commission', 0.001)  # 0.1%
        self.slippage = config.get('slippage', 0.0005)    # 0.05%
        
        # 분석 모듈들
        self.technical_analyzer = CoreTechnicalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.ml_predictor = MLPredictor()
        self.signal_integrator = SignalIntegrator()
        
        # 데이터베이스
        self.database = Database()
        
        # 백테스팅 결과
        self.results = {}
        self.trades = []
        self.portfolio_history = []
        
        self.logger.info("백테스팅 엔진 초기화 완료")
    
    def run_backtest(self, symbol: str, start_date: str, end_date: str, 
                    strategy: str = 'integrated') -> Dict[str, Any]:
        """단일 코인 백테스팅 실행"""
        try:
            self.logger.info(f"{symbol} 백테스팅 시작: {start_date} ~ {end_date}")
            
            # 데이터 로드
            df = self._load_data(symbol, start_date, end_date)
            if df.empty:
                return {'error': '데이터 없음'}
            
            # 백테스팅 실행
            results = self._execute_backtest(df, symbol, strategy)
            
            self.logger.info(f"{symbol} 백테스팅 완료")
            return results
            
        except Exception as e:
            self.logger.error(f"{symbol} 백테스팅 실패: {e}")
            return {'error': str(e)}
    
    def run_multi_backtest(self, symbols: List[str], start_date: str, 
                          end_date: str, strategy: str = 'integrated') -> Dict[str, Any]:
        """다중 코인 백테스팅 실행"""
        all_results = {}
        
        for symbol in symbols:
            self.logger.info(f"백테스팅 진행: {symbol} ({symbols.index(symbol)+1}/{len(symbols)})")
            result = self.run_backtest(symbol, start_date, end_date, strategy)
            all_results[symbol] = result
        
        # 전체 성능 계산
        portfolio_results = self._calculate_portfolio_performance(all_results)
        
        return {
            'individual_results': all_results,
            'portfolio_results': portfolio_results
        }
    
    def _load_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """데이터 로드"""
        try:
            # 날짜를 timestamp로 변환
            start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
            end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
            
            # 가격 데이터 로드 (기본 테이블에서)
            df = self.database.get_price_data(
                symbol=symbol,
                start_time=start_timestamp,
                end_time=end_timestamp
            )
            
            if df.empty:
                self.logger.warning(f"{symbol} 데이터 없음")
                return pd.DataFrame()
            
            # 시간순 정렬
            df = df.sort_values('timestamp')
            
            self.logger.info(f"{symbol} 데이터 로드 완료: {len(df)}개 캔들")
            return df
            
        except Exception as e:
            self.logger.error(f"{symbol} 데이터 로드 실패: {e}")
            return pd.DataFrame()
    
    def _execute_backtest(self, df: pd.DataFrame, symbol: str, strategy: str) -> Dict[str, Any]:
        """백테스팅 실행"""
        # 초기 설정
        capital = self.initial_capital
        position = 0  # 0: 없음, 1: 롱, -1: 숏
        entry_price = 0
        trades = []
        portfolio_values = []
        
        # 각 캔들에 대해 백테스팅
        for i, row in df.iterrows():
            current_price = row['close']
            timestamp = row['timestamp']
            
            # 신호 생성
            signal = self._generate_signal(df.iloc[:i+1], strategy)
            
            # 거래 실행
            if signal != 0 and position == 0:  # 포지션 진입
                if signal > 0:  # 롱 진입
                    position = 1
                    entry_price = current_price * (1 + self.slippage)
                    capital -= capital * self.commission
                    trades.append({
                        'timestamp': timestamp,
                        'type': 'buy',
                        'price': entry_price,
                        'capital': capital
                    })
                elif signal < 0:  # 숏 진입
                    position = -1
                    entry_price = current_price * (1 - self.slippage)
                    capital -= capital * self.commission
                    trades.append({
                        'timestamp': timestamp,
                        'type': 'sell_short',
                        'price': entry_price,
                        'capital': capital
                    })
            
            elif position != 0 and signal == 0:  # 포지션 청산
                if position == 1:  # 롱 청산
                    exit_price = current_price * (1 - self.slippage)
                    profit = (exit_price - entry_price) / entry_price
                    capital *= (1 + profit - self.commission)
                    trades.append({
                        'timestamp': timestamp,
                        'type': 'sell',
                        'price': exit_price,
                        'capital': capital,
                        'profit': profit
                    })
                elif position == -1:  # 숏 청산
                    exit_price = current_price * (1 + self.slippage)
                    profit = (entry_price - exit_price) / entry_price
                    capital *= (1 + profit - self.commission)
                    trades.append({
                        'timestamp': timestamp,
                        'type': 'buy_cover',
                        'price': exit_price,
                        'capital': capital,
                        'profit': profit
                    })
                position = 0
                entry_price = 0
            
            # 포트폴리오 가치 기록
            portfolio_values.append({
                'timestamp': timestamp,
                'capital': capital,
                'position': position
            })
        
        # 최종 포지션 청산
        if position != 0:
            current_price = df.iloc[-1]['close']
            if position == 1:
                exit_price = current_price * (1 - self.slippage)
                profit = (exit_price - entry_price) / entry_price
                capital *= (1 + profit - self.commission)
            elif position == -1:
                exit_price = current_price * (1 + self.slippage)
                profit = (entry_price - exit_price) / entry_price
                capital *= (1 + profit - self.commission)
        
        # 성능 계산
        performance = self._calculate_performance(capital, trades, portfolio_values)
        
        return {
            'symbol': symbol,
            'initial_capital': self.initial_capital,
            'final_capital': capital,
            'total_return': (capital - self.initial_capital) / self.initial_capital,
            'trades': trades,
            'portfolio_history': portfolio_values,
            'performance': performance
        }
    
    def _generate_signal(self, df: pd.DataFrame, strategy: str) -> int:
        """거래 신호 생성"""
        if len(df) < 50:  # 최소 데이터 필요
            return 0
        
        try:
            if strategy == 'integrated':
                # 통합 신호 (기술적 + 감정 + ML)
                technical_signal = self.technical_analyzer.analyze(df)
                sentiment_signal = self.sentiment_analyzer.analyze(df)
                ml_signal = self.ml_predictor.predict(df)
                
                # 신호 통합
                final_signal = self.signal_integrator.integrate_signals(
                    technical_signal, sentiment_signal, ml_signal
                )
                
                return final_signal
            
            elif strategy == 'technical':
                # 기술적 분석만
                return self.technical_analyzer.analyze(df)
            
            elif strategy == 'sentiment':
                # 감정 분석만
                return self.sentiment_analyzer.analyze(df)
            
            elif strategy == 'ml':
                # ML 예측만
                return self.ml_predictor.predict(df)
            
            else:
                return 0
                
        except Exception as e:
            self.logger.error(f"신호 생성 실패: {e}")
            return 0
    
    def _calculate_performance(self, final_capital: float, trades: List[Dict], 
                             portfolio_values: List[Dict]) -> Dict[str, float]:
        """성능 지표 계산"""
        if not trades:
            return {
                'total_return': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'total_trades': 0
            }
        
        # 총 수익률
        total_return = (final_capital - self.initial_capital) / self.initial_capital
        
        # 수익률 계산
        profits = [t['profit'] for t in trades if 'profit' in t]
        
        if not profits:
            return {
                'total_return': total_return,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'total_trades': len(trades)
            }
        
        # 승률
        winning_trades = [p for p in profits if p > 0]
        win_rate = len(winning_trades) / len(profits) if profits else 0
        
        # 손익비
        avg_win = np.mean(winning_trades) if winning_trades else 0
        losing_trades = [p for p in profits if p < 0]
        avg_loss = abs(np.mean(losing_trades)) if losing_trades else 0
        profit_factor = avg_win / avg_loss if avg_loss > 0 else 0
        
        # 최대 드로다운
        portfolio_df = pd.DataFrame(portfolio_values)
        portfolio_df['cumulative_return'] = portfolio_df['capital'] / self.initial_capital
        portfolio_df['peak'] = portfolio_df['cumulative_return'].expanding().max()
        portfolio_df['drawdown'] = (portfolio_df['cumulative_return'] - portfolio_df['peak']) / portfolio_df['peak']
        max_drawdown = portfolio_df['drawdown'].min()
        
        # 샤프비율 (간단한 계산)
        returns = portfolio_df['cumulative_return'].pct_change().dropna()
        sharpe_ratio = returns.mean() / returns.std() if returns.std() > 0 else 0
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_trades': len(trades),
            'avg_win': avg_win,
            'avg_loss': avg_loss
        }
    
    def _calculate_portfolio_performance(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """포트폴리오 전체 성능 계산"""
        valid_results = {k: v for k, v in all_results.items() if 'error' not in v}
        
        if not valid_results:
            return {'error': '유효한 백테스팅 결과 없음'}
        
        # 전체 수익률
        total_capital = sum(r['final_capital'] for r in valid_results.values())
        total_initial = sum(r['initial_capital'] for r in valid_results.values())
        portfolio_return = (total_capital - total_initial) / total_initial
        
        # 개별 성능 요약
        performance_summary = {}
        for symbol, result in valid_results.items():
            perf = result['performance']
            performance_summary[symbol] = {
                'total_return': perf['total_return'],
                'sharpe_ratio': perf['sharpe_ratio'],
                'max_drawdown': perf['max_drawdown'],
                'win_rate': perf['win_rate'],
                'total_trades': perf['total_trades']
            }
        
        return {
            'portfolio_return': portfolio_return,
            'total_capital': total_capital,
            'total_initial_capital': total_initial,
            'performance_summary': performance_summary,
            'num_coins': len(valid_results)
        } 