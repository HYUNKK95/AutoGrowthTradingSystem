# Phase 3: 봇 테스트 및 개선 상세 구현 가이드

## 🎯 Phase 3 목표
- 50개 코인 백테스팅 엔진 구현
- 성능 평가 시스템 구축 (핵심 지표 + 전략)
- 파라미터 튜닝 자동화
- 봇 성능 개선 및 최적화
- 버그 수정 및 안정성 향상

## 📋 구현 체크리스트

### **백테스팅**
- [ ] 백테스팅 엔진 구현
- [ ] 과거 데이터 재현 시뮬레이션
- [ ] 거래 시뮬레이션 (매수/매도/홀드)
- [ ] 수익률 계산 및 추적

### **성능 평가**
- [ ] 수익률 계산 (총 수익률, 월 수익률)
- [ ] 샤프비율 계산
- [ ] 최대드로다운 계산
- [ ] 승률 및 손익비 계산
- [ ] 성능 지표 시각화

### **파라미터 튜닝**
- [ ] 그리드 서치 구현
- [ ] 최적 파라미터 탐색
- [ ] 교차 검증
- [ ] 파라미터 최적화 결과 저장

### **성능 개선**
- [ ] 백테스팅 결과 분석
- [ ] 전략 개선
- [ ] 파라미터 조정
- [ ] 안정성 향상

## 🏗️ 백테스팅 구조

### **백테스팅 모듈 구조**
```
backtesting/
├── __init__.py
├── engine.py          # 백테스팅 엔진
├── performance.py     # 성능 평가
├── optimizer.py       # 파라미터 최적화
└── visualizer.py      # 결과 시각화
```

### **성능 평가 구조**
```
evaluation/
├── __init__.py
├── metrics.py         # 성능 지표
├── analyzer.py        # 성능 분석
└── reporter.py        # 성능 리포트
```

## 💻 구현 예시 코드

### **1. backtesting/engine.py**
```python
"""
백테스팅 엔진
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from data.database import Database
from analysis.technical import TechnicalAnalyzer
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
        self.technical_analyzer = CoreTechnicalAnalyzer()  # 5개 핵심 지표
        self.strategy_manager = CoreStrategyManager()      # 4개 핵심 전략
        self.sentiment_analyzer = SentimentAnalyzer()
        self.ml_predictor = MLPredictor()
        self.signal_integrator = SignalIntegrator()
        
        # 데이터베이스
        self.database = Database()
        
        # 백테스팅 결과
        self.trades = []
        self.portfolio_values = []
        self.current_position = 0.0
        self.current_capital = self.initial_capital
        
        self.logger.info("BacktestEngine 초기화 완료")
    
    def load_historical_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """과거 데이터 로드"""
        try:
            # 데이터베이스에서 과거 데이터 조회
            start_timestamp = int(pd.Timestamp(start_date).timestamp() * 1000)
            end_timestamp = int(pd.Timestamp(end_date).timestamp() * 1000)
            
            df = self.database.get_price_data(
                symbol, 
                start_time=start_timestamp, 
                end_time=end_timestamp
            )
            
            if df.empty:
                self.logger.warning("과거 데이터가 없습니다")
                return pd.DataFrame()
            
            # 데이터 정렬
            df = df.sort_values('timestamp')
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.set_index('datetime')
            
            self.logger.info(f"과거 데이터 로드 완료: {len(df)}개 레코드")
            return df
            
        except Exception as e:
            self.logger.error(f"과거 데이터 로드 실패: {e}")
            return pd.DataFrame()
    
    def simulate_trade(self, signal: float, current_price: float, timestamp: datetime) -> Optional[Dict[str, Any]]:
        """거래 시뮬레이션"""
        try:
            # 거래 결정
            if signal > 0.3:
                action = 'BUY'
            elif signal < -0.3:
                action = 'SELL'
            else:
                action = 'HOLD'
            
            if action == 'HOLD':
                return None
            
            # 수량 계산 (신호 강도에 따라)
            position_size = abs(signal) * 0.1  # 최대 10%
            quantity = (self.current_capital * position_size) / current_price
            
            # 수수료 및 슬리피지 적용
            if action == 'BUY':
                actual_price = current_price * (1 + self.slippage)
                cost = quantity * actual_price * (1 + self.commission)
                
                if cost > self.current_capital:
                    return None  # 자본 부족
                
                self.current_capital -= cost
                self.current_position += quantity
                
            elif action == 'SELL':
                actual_price = current_price * (1 - self.slippage)
                revenue = quantity * actual_price * (1 - self.commission)
                
                if quantity > self.current_position:
                    return None  # 포지션 부족
                
                self.current_capital += revenue
                self.current_position -= quantity
            
            # 거래 기록
            trade = {
                'timestamp': timestamp,
                'action': action,
                'price': current_price,
                'quantity': quantity,
                'signal': signal,
                'capital': self.current_capital,
                'position': self.current_position
            }
            
            self.trades.append(trade)
            return trade
            
        except Exception as e:
            self.logger.error(f"거래 시뮬레이션 실패: {e}")
            return None
    
    def calculate_portfolio_value(self, current_price: float) -> float:
        """포트폴리오 가치 계산"""
        position_value = self.current_position * current_price
        return self.current_capital + position_value
    
    def run_backtest(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """백테스팅 실행"""
        try:
            self.logger.info(f"백테스팅 시작: {symbol} ({start_date} ~ {end_date})")
            
            # 과거 데이터 로드
            df = self.load_historical_data(symbol, start_date, end_date)
            if df.empty:
                return {'error': '데이터 없음'}
            
            # ML 모델 학습
            self.ml_predictor.train(df)
            
            # 백테스팅 실행
            for i in range(50, len(df)):  # 50개 데이터 이후부터 시작
                current_data = df.iloc[:i+1]
                current_row = df.iloc[i]
                
                # 기술적 분석
                technical_result = self.technical_analyzer.analyze(current_data)
                
                # 감정분석 (시뮬레이션)
                sentiment_result = self.sentiment_analyzer.analyze()
                
                # ML 예측
                ml_signal = self.ml_predictor.predict(current_data)
                
                # 신호 통합
                signals = {
                    'technical_signal': technical_result.get('technical_signal', 0.0),
                    'sentiment_signal': sentiment_result.get('sentiment_signal', 0.0),
                    'ml_signal': ml_signal
                }
                
                final_result = self.signal_integrator.integrate_signals(signals)
                final_signal = final_result.get('final_signal', 0.0)
                
                # 거래 시뮬레이션
                trade = self.simulate_trade(
                    final_signal, 
                    current_row['close'], 
                    current_row.name
                )
                
                # 포트폴리오 가치 기록
                portfolio_value = self.calculate_portfolio_value(current_row['close'])
                self.portfolio_values.append({
                    'timestamp': current_row.name,
                    'price': current_row['close'],
                    'portfolio_value': portfolio_value,
                    'capital': self.current_capital,
                    'position': self.current_position
                })
            
            # 결과 계산
            results = self.calculate_backtest_results()
            
            self.logger.info(f"백테스팅 완료: 총 수익률 {results['total_return']:.2%}")
            return results
            
        except Exception as e:
            self.logger.error(f"백테스팅 실패: {e}")
            return {'error': str(e)}
    
    def calculate_backtest_results(self) -> Dict[str, Any]:
        """백테스팅 결과 계산"""
        try:
            if not self.portfolio_values:
                return {'error': '포트폴리오 데이터 없음'}
            
            # 기본 지표
            initial_value = self.initial_capital
            final_value = self.portfolio_values[-1]['portfolio_value']
            total_return = (final_value - initial_value) / initial_value
            
            # 수익률 시계열
            returns = []
            for i in range(1, len(self.portfolio_values)):
                prev_value = self.portfolio_values[i-1]['portfolio_value']
                curr_value = self.portfolio_values[i]['portfolio_value']
                daily_return = (curr_value - prev_value) / prev_value
                returns.append(daily_return)
            
            # 성능 지표
            avg_return = np.mean(returns) if returns else 0
            volatility = np.std(returns) if returns else 0
            sharpe_ratio = avg_return / volatility if volatility > 0 else 0
            
            # 최대드로다운
            peak = initial_value
            max_drawdown = 0
            for pv in self.portfolio_values:
                if pv['portfolio_value'] > peak:
                    peak = pv['portfolio_value']
                drawdown = (peak - pv['portfolio_value']) / peak
                max_drawdown = max(max_drawdown, drawdown)
            
            # 거래 통계
            total_trades = len(self.trades)
            winning_trades = len([t for t in self.trades if t.get('pnl', 0) > 0])
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            return {
                'total_return': total_return,
                'annual_return': total_return * 365 / len(self.portfolio_values),
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'volatility': volatility,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': win_rate,
                'final_capital': final_value,
                'trades': self.trades,
                'portfolio_values': self.portfolio_values
            }
            
        except Exception as e:
            self.logger.error(f"백테스팅 결과 계산 실패: {e}")
            return {'error': str(e)}
```

### **2. evaluation/metrics.py**
```python
"""
성능 지표 계산
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List

class PerformanceMetrics:
    """성능 지표 계산 클래스"""
    
    def __init__(self):
        """성능 지표 계산기 초기화"""
        pass
    
    def calculate_returns(self, portfolio_values: List[Dict[str, Any]]) -> List[float]:
        """수익률 계산"""
        returns = []
        for i in range(1, len(portfolio_values)):
            prev_value = portfolio_values[i-1]['portfolio_value']
            curr_value = portfolio_values[i]['portfolio_value']
            daily_return = (curr_value - prev_value) / prev_value
            returns.append(daily_return)
        return returns
    
    def calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """샤프비율 계산"""
        if not returns:
            return 0.0
        
        avg_return = np.mean(returns)
        volatility = np.std(returns)
        
        if volatility == 0:
            return 0.0
        
        # 연율화
        sharpe_ratio = (avg_return - risk_free_rate/365) / volatility * np.sqrt(365)
        return sharpe_ratio
    
    def calculate_max_drawdown(self, portfolio_values: List[Dict[str, Any]]) -> float:
        """최대드로다운 계산"""
        if not portfolio_values:
            return 0.0
        
        values = [pv['portfolio_value'] for pv in portfolio_values]
        peak = values[0]
        max_drawdown = 0
        
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    def calculate_win_rate(self, trades: List[Dict[str, Any]]) -> float:
        """승률 계산"""
        if not trades:
            return 0.0
        
        winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
        return winning_trades / len(trades)
    
    def calculate_profit_factor(self, trades: List[Dict[str, Any]]) -> float:
        """손익비 계산"""
        if not trades:
            return 0.0
        
        total_profit = sum([t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0])
        total_loss = abs(sum([t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0]))
        
        return total_profit / total_loss if total_loss > 0 else 0.0
    
    def calculate_calmar_ratio(self, total_return: float, max_drawdown: float) -> float:
        """칼마 비율 계산"""
        if max_drawdown == 0:
            return 0.0
        return total_return / max_drawdown
    
    def calculate_all_metrics(self, backtest_results: Dict[str, Any]) -> Dict[str, Any]:
        """모든 성능 지표 계산"""
        try:
            portfolio_values = backtest_results.get('portfolio_values', [])
            trades = backtest_results.get('trades', [])
            
            # 기본 수익률
            total_return = backtest_results.get('total_return', 0)
            annual_return = backtest_results.get('annual_return', 0)
            
            # 수익률 시계열
            returns = self.calculate_returns(portfolio_values)
            
            # 성능 지표
            sharpe_ratio = self.calculate_sharpe_ratio(returns)
            max_drawdown = self.calculate_max_drawdown(portfolio_values)
            win_rate = self.calculate_win_rate(trades)
            profit_factor = self.calculate_profit_factor(trades)
            calmar_ratio = self.calculate_calmar_ratio(total_return, max_drawdown)
            
            # 추가 지표
            volatility = np.std(returns) if returns else 0
            avg_trade_return = np.mean([t.get('pnl', 0) for t in trades]) if trades else 0
            
            return {
                'total_return': total_return,
                'annual_return': annual_return,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'win_rate': win_rate,
                'profit_factor': profit_factor,
                'calmar_ratio': calmar_ratio,
                'volatility': volatility,
                'avg_trade_return': avg_trade_return,
                'total_trades': len(trades),
                'winning_trades': len([t for t in trades if t.get('pnl', 0) > 0])
            }
            
        except Exception as e:
            return {'error': f'성능 지표 계산 실패: {e}'}
```

### **3. backtesting/optimizer.py**
```python
"""
파라미터 최적화
"""

import itertools
import logging
from typing import Dict, Any, List, Tuple
from backtesting.engine import BacktestEngine
from evaluation.metrics import PerformanceMetrics

class ParameterOptimizer:
    """파라미터 최적화 클래스"""
    
    def __init__(self):
        """파라미터 최적화기 초기화"""
        self.logger = logging.getLogger(__name__)
        self.metrics = PerformanceMetrics()
        
        # 최적화할 파라미터 범위
        self.parameter_ranges = {
            'ma_short': [10, 15, 20, 25, 30],
            'ma_long': [40, 50, 60, 70, 80],
            'rsi_period': [10, 14, 20],
            'rsi_overbought': [65, 70, 75],
            'rsi_oversold': [25, 30, 35],
            'signal_threshold': [0.2, 0.3, 0.4, 0.5],
            'position_size': [0.05, 0.1, 0.15, 0.2]
        }
        
        self.logger.info("ParameterOptimizer 초기화 완료")
    
    def generate_parameter_combinations(self) -> List[Dict[str, Any]]:
        """파라미터 조합 생성"""
        param_names = list(self.parameter_ranges.keys())
        param_values = list(self.parameter_ranges.values())
        
        combinations = []
        for combination in itertools.product(*param_values):
            param_dict = dict(zip(param_names, combination))
            combinations.append(param_dict)
        
        self.logger.info(f"총 {len(combinations)}개의 파라미터 조합 생성")
        return combinations
    
    def optimize_parameters(self, symbol: str, start_date: str, end_date: str, 
                          optimization_metric: str = 'sharpe_ratio') -> Dict[str, Any]:
        """파라미터 최적화"""
        try:
            self.logger.info("파라미터 최적화 시작")
            
            # 파라미터 조합 생성
            parameter_combinations = self.generate_parameter_combinations()
            
            # 최적화 결과 저장
            optimization_results = []
            
            for i, params in enumerate(parameter_combinations):
                self.logger.info(f"파라미터 조합 {i+1}/{len(parameter_combinations)} 테스트")
                
                # 백테스팅 실행
                backtest_results = self.run_backtest_with_params(
                    symbol, start_date, end_date, params
                )
                
                if 'error' not in backtest_results:
                    # 성능 지표 계산
                    metrics = self.metrics.calculate_all_metrics(backtest_results)
                    
                    # 최적화 지표 추출
                    optimization_score = metrics.get(optimization_metric, 0)
                    
                    result = {
                        'parameters': params,
                        'optimization_score': optimization_score,
                        'metrics': metrics,
                        'backtest_results': backtest_results
                    }
                    
                    optimization_results.append(result)
                    
                    self.logger.info(f"파라미터 조합 {i+1} - {optimization_metric}: {optimization_score:.4f}")
            
            # 최적 파라미터 찾기
            if optimization_results:
                best_result = max(optimization_results, 
                                key=lambda x: x['optimization_score'])
                
                self.logger.info(f"최적 파라미터 발견: {best_result['parameters']}")
                
                return {
                    'best_parameters': best_result['parameters'],
                    'best_score': best_result['optimization_score'],
                    'best_metrics': best_result['metrics'],
                    'all_results': optimization_results
                }
            else:
                return {'error': '최적화 결과 없음'}
                
        except Exception as e:
            self.logger.error(f"파라미터 최적화 실패: {e}")
            return {'error': str(e)}
    
    def run_backtest_with_params(self, symbol: str, start_date: str, end_date: str, 
                                params: Dict[str, Any]) -> Dict[str, Any]:
        """특정 파라미터로 백테스팅 실행"""
        try:
            # 백테스팅 엔진 초기화
            config = {
                'initial_capital': 3000000,
                'commission': 0.001,
                'slippage': 0.0005
            }
            
            engine = BacktestEngine(config)
            
            # 파라미터 적용
            engine.technical_analyzer.ma_short = params.get('ma_short', 20)
            engine.technical_analyzer.ma_long = params.get('ma_long', 50)
            engine.technical_analyzer.rsi_period = params.get('rsi_period', 14)
            
            # 신호 임계값 적용
            engine.signal_integrator.weights = {
                'technical': params.get('technical_weight', 0.4),
                'sentiment': params.get('sentiment_weight', 0.3),
                'ml': params.get('ml_weight', 0.3)
            }
            
            # 백테스팅 실행
            results = engine.run_backtest(symbol, start_date, end_date)
            
            return results
            
        except Exception as e:
            self.logger.error(f"파라미터 백테스팅 실패: {e}")
            return {'error': str(e)}
    
    def save_optimization_results(self, results: Dict[str, Any], filename: str):
        """최적화 결과 저장"""
        try:
            import json
            from datetime import datetime
            
            # JSON으로 저장할 수 있도록 변환
            save_data = {
                'timestamp': datetime.now().isoformat(),
                'best_parameters': results.get('best_parameters', {}),
                'best_score': results.get('best_score', 0),
                'best_metrics': results.get('best_metrics', {}),
                'total_combinations': len(results.get('all_results', []))
            }
            
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            self.logger.info(f"최적화 결과 저장: {filename}")
            
        except Exception as e:
            self.logger.error(f"최적화 결과 저장 실패: {e}")
```

### **4. backtesting/visualizer.py**
```python
"""
백테스팅 결과 시각화
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import seaborn as sns

class BacktestVisualizer:
    """백테스팅 결과 시각화 클래스"""
    
    def __init__(self):
        """시각화기 초기화"""
        plt.style.use('seaborn-v0_8')
        self.logger = logging.getLogger(__name__)
    
    def plot_portfolio_value(self, portfolio_values: List[Dict[str, Any]], 
                           save_path: str = None):
        """포트폴리오 가치 변화 그래프"""
        try:
            df = pd.DataFrame(portfolio_values)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            plt.figure(figsize=(12, 6))
            plt.plot(df['timestamp'], df['portfolio_value'], label='포트폴리오 가치', linewidth=2)
            plt.plot(df['timestamp'], df['price'], label='가격', alpha=0.7)
            
            plt.title('포트폴리오 가치 변화', fontsize=14, fontweight='bold')
            plt.xlabel('날짜')
            plt.ylabel('가치 (KRW)')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            plt.show()
            
        except Exception as e:
            self.logger.error(f"포트폴리오 가치 그래프 생성 실패: {e}")
    
    def plot_drawdown(self, portfolio_values: List[Dict[str, Any]], 
                     save_path: str = None):
        """드로다운 그래프"""
        try:
            df = pd.DataFrame(portfolio_values)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # 드로다운 계산
            peak = df['portfolio_value'].expanding().max()
            drawdown = (peak - df['portfolio_value']) / peak * 100
            
            plt.figure(figsize=(12, 6))
            plt.fill_between(df['timestamp'], drawdown, 0, alpha=0.3, color='red')
            plt.plot(df['timestamp'], drawdown, color='red', linewidth=2)
            
            plt.title('드로다운 분석', fontsize=14, fontweight='bold')
            plt.xlabel('날짜')
            plt.ylabel('드로다운 (%)')
            plt.grid(True, alpha=0.3)
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            plt.show()
            
        except Exception as e:
            self.logger.error(f"드로다운 그래프 생성 실패: {e}")
    
    def plot_monthly_returns(self, portfolio_values: List[Dict[str, Any]], 
                           save_path: str = None):
        """월별 수익률 히트맵"""
        try:
            df = pd.DataFrame(portfolio_values)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            
            # 일별 수익률 계산
            df['daily_return'] = df['portfolio_value'].pct_change()
            
            # 월별 수익률 계산
            monthly_returns = df.groupby([df['timestamp'].dt.year, 
                                        df['timestamp'].dt.month])['daily_return'].sum()
            
            # 히트맵 데이터 준비
            returns_matrix = monthly_returns.unstack()
            
            plt.figure(figsize=(10, 6))
            sns.heatmap(returns_matrix, annot=True, fmt='.2%', cmap='RdYlGn', 
                       center=0, cbar_kws={'label': '월별 수익률'})
            
            plt.title('월별 수익률 히트맵', fontsize=14, fontweight='bold')
            plt.xlabel('월')
            plt.ylabel('년')
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            plt.show()
            
        except Exception as e:
            self.logger.error(f"월별 수익률 히트맵 생성 실패: {e}")
    
    def plot_trade_analysis(self, trades: List[Dict[str, Any]], 
                           save_path: str = None):
        """거래 분석 그래프"""
        try:
            if not trades:
                return
            
            df = pd.DataFrame(trades)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # 거래별 수익률 계산
            df['pnl'] = df.apply(lambda row: 
                (row['price'] - row.get('entry_price', row['price'])) * row['quantity']
                if row['action'] == 'SELL' else 0, axis=1)
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # 거래 시점 그래프
            ax1.scatter(df[df['action'] == 'BUY']['timestamp'], 
                       df[df['action'] == 'BUY']['price'], 
                       color='green', marker='^', s=100, label='매수')
            ax1.scatter(df[df['action'] == 'SELL']['timestamp'], 
                       df[df['action'] == 'SELL']['price'], 
                       color='red', marker='v', s=100, label='매도')
            ax1.set_title('거래 시점 분석', fontweight='bold')
            ax1.set_ylabel('가격')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 거래별 수익률
            ax2.bar(range(len(df)), df['pnl'], 
                   color=['green' if pnl > 0 else 'red' for pnl in df['pnl']])
            ax2.set_title('거래별 수익률', fontweight='bold')
            ax2.set_xlabel('거래 순서')
            ax2.set_ylabel('수익률 (KRW)')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            plt.show()
            
        except Exception as e:
            self.logger.error(f"거래 분석 그래프 생성 실패: {e}")
    
    def create_performance_report(self, backtest_results: Dict[str, Any], 
                                save_path: str = None):
        """성능 리포트 생성"""
        try:
            metrics = backtest_results.get('metrics', {})
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            
            # 1. 주요 지표
            key_metrics = ['total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate']
            metric_values = [metrics.get(m, 0) for m in key_metrics]
            metric_labels = ['총 수익률', '샤프비율', '최대드로다운', '승률']
            
            axes[0, 0].bar(metric_labels, metric_values, 
                           color=['green', 'blue', 'red', 'orange'])
            axes[0, 0].set_title('주요 성능 지표', fontweight='bold')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # 2. 수익률 분포
            if 'returns' in backtest_results:
                returns = backtest_results['returns']
                axes[0, 1].hist(returns, bins=30, alpha=0.7, color='skyblue')
                axes[0, 1].set_title('수익률 분포', fontweight='bold')
                axes[0, 1].set_xlabel('일별 수익률')
                axes[0, 1].set_ylabel('빈도')
            
            # 3. 누적 수익률
            if 'portfolio_values' in backtest_results:
                portfolio_values = backtest_results['portfolio_values']
                df = pd.DataFrame(portfolio_values)
                cumulative_return = (df['portfolio_value'] / df['portfolio_value'].iloc[0] - 1) * 100
                
                axes[1, 0].plot(cumulative_return.index, cumulative_return.values, linewidth=2)
                axes[1, 0].set_title('누적 수익률', fontweight='bold')
                axes[1, 0].set_xlabel('거래일')
                axes[1, 0].set_ylabel('누적 수익률 (%)')
                axes[1, 0].grid(True, alpha=0.3)
            
            # 4. 거래 통계
            trade_stats = [
                metrics.get('total_trades', 0),
                metrics.get('winning_trades', 0),
                len(backtest_results.get('trades', [])) - metrics.get('winning_trades', 0)
            ]
            trade_labels = ['총 거래', '승리 거래', '손실 거래']
            colors = ['gray', 'green', 'red']
            
            axes[1, 1].pie(trade_stats, labels=trade_labels, colors=colors, autopct='%1.1f%%')
            axes[1, 1].set_title('거래 통계', fontweight='bold')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            plt.show()
            
        except Exception as e:
            self.logger.error(f"성능 리포트 생성 실패: {e}")
```

## ✅ 테스트 방법

### **1. 백테스팅 테스트**
```python
# test_backtest.py
from backtesting.engine import BacktestEngine

def test_backtest():
    """백테스팅 테스트"""
    print("=== 백테스팅 테스트 ===")
    
    # 백테스팅 설정
    config = {
        'initial_capital': 3000000,
        'commission': 0.001,
        'slippage': 0.0005
    }
    
    # 백테스팅 엔진 초기화
    engine = BacktestEngine(config)
    
    # 백테스팅 실행
    results = engine.run_backtest(
        symbol='BTCUSDT',
        start_date='2024-01-01',
        end_date='2024-03-01'
    )
    
    if 'error' not in results:
        print(f"총 수익률: {results['total_return']:.2%}")
        print(f"샤프비율: {results['sharpe_ratio']:.3f}")
        print(f"최대드로다운: {results['max_drawdown']:.2%}")
        print(f"총 거래: {results['total_trades']}")
        print(f"승률: {results['win_rate']:.2%}")
    else:
        print(f"백테스팅 실패: {results['error']}")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_backtest()
```

### **2. 성능 지표 테스트**
```python
# test_metrics.py
from evaluation.metrics import PerformanceMetrics

def test_metrics():
    """성능 지표 테스트"""
    print("=== 성능 지표 테스트 ===")
    
    # 테스트 데이터
    backtest_results = {
        'total_return': 0.15,
        'portfolio_values': [
            {'portfolio_value': 3000000},
            {'portfolio_value': 3100000},
            {'portfolio_value': 3050000},
            {'portfolio_value': 3200000}
        ],
        'trades': [
            {'pnl': 100000},
            {'pnl': -50000},
            {'pnl': 150000}
        ]
    }
    
    # 성능 지표 계산
    metrics = PerformanceMetrics()
    results = metrics.calculate_all_metrics(backtest_results)
    
    print(f"총 수익률: {results['total_return']:.2%}")
    print(f"샤프비율: {results['sharpe_ratio']:.3f}")
    print(f"최대드로다운: {results['max_drawdown']:.2%}")
    print(f"승률: {results['win_rate']:.2%}")
    print(f"손익비: {results['profit_factor']:.2f}")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_metrics()
```

### **3. 파라미터 최적화 테스트**
```python
# test_optimizer.py
from backtesting.optimizer import ParameterOptimizer

def test_optimizer():
    """파라미터 최적화 테스트"""
    print("=== 파라미터 최적화 테스트 ===")
    
    # 최적화기 초기화
    optimizer = ParameterOptimizer()
    
    # 최적화 실행 (간단한 파라미터로 테스트)
    results = optimizer.optimize_parameters(
        symbol='BTCUSDT',
        start_date='2024-01-01',
        end_date='2024-02-01',
        optimization_metric='sharpe_ratio'
    )
    
    if 'error' not in results:
        print(f"최적 파라미터: {results['best_parameters']}")
        print(f"최적 점수: {results['best_score']:.4f}")
        print(f"총 조합 수: {len(results['all_results'])}")
    else:
        print(f"최적화 실패: {results['error']}")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_optimizer()
```

## 🚀 실행 방법

### **1. 백테스팅 실행**
```bash
# 백테스팅 실행
python -c "
from backtesting.engine import BacktestEngine

config = {'initial_capital': 3000000, 'commission': 0.001, 'slippage': 0.0005}
engine = BacktestEngine(config)
results = engine.run_backtest('BTCUSDT', '2024-01-01', '2024-03-01')
print(f'총 수익률: {results.get(\"total_return\", 0):.2%}')
"
```

### **2. 파라미터 최적화**
```bash
# 파라미터 최적화
python -c "
from backtesting.optimizer import ParameterOptimizer

optimizer = ParameterOptimizer()
results = optimizer.optimize_parameters('BTCUSDT', '2024-01-01', '2024-02-01')
print(f'최적 파라미터: {results.get(\"best_parameters\", {})}')
"
```

## 📊 Phase 3 완료 기준

### **✅ 완료 체크리스트**
- [ ] 백테스팅 엔진 구현 완료
- [ ] 성능 평가 시스템 구현 완료
- [ ] 파라미터 최적화 구현 완료
- [ ] 결과 시각화 구현 완료
- [ ] 모든 테스트 통과
- [ ] 성능 개선 완료

### **🎯 성공 지표**
- **백테스팅**: 과거 데이터 재현 성공
- **성능 평가**: 모든 지표 정상 계산
- **파라미터 최적화**: 최적 파라미터 발견
- **시각화**: 결과 그래프 정상 생성
- **성능 개선**: 백테스팅 결과 반영

## 🚀 다음 단계 (Phase 4)

Phase 3이 완료되면 다음 단계로 진행합니다:

1. **실시간 봇 실행**
2. **Telegram 알림 시스템**
3. **실시간 PnL 추적**
4. **자동 재시작 시스템**

Phase 4 상세 가이드는 `PHASE_4_DETAILED.md`에서 확인할 수 있습니다. 