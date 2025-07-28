"""
통합 트레이딩 봇 클래스 (Phase 2 완성 버전) - 고급 버전
"""

import logging
import time
import threading
from typing import Dict, Any, Optional, List
from bot.config import Config
from utils.logger import get_logger
import pandas as pd
from datetime import datetime, timedelta

# 분석 모듈들
from analysis.technical import CoreTechnicalAnalyzer
from analysis.strategies import CoreStrategyManager
from analysis.sentiment import SentimentAnalyzer
from analysis.ml import MLPredictor
from analysis.signal_integrator import SignalIntegrator

# 거래 모듈들
from trading.executor import OrderExecutor
from trading.risk_manager import RiskManager

# 데이터 모듈들
from data.database import Database

class IntegratedTradingBot:
    """통합 트레이딩 봇 클래스 - 고급 버전"""
    
    def __init__(self, config: Config):
        """봇 초기화"""
        self.config = config
        self.logger = get_logger('IntegratedTradingBot')
        
        # 상태 변수
        self.is_running = False
        self.current_position = 0.0
        self.total_pnl = 0.0
        self.start_time = None
        self.last_analysis_time = None
        
        # 성능 추적
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'win_rate': 0.0
        }
        
        # 실시간 모니터링
        self.monitoring_data = {
            'current_price': 0.0,
            'signal_strength': 0.0,
            'confidence': 0.0,
            'last_trade_time': None,
            'active_orders': []
        }
        
        # 컴포넌트 초기화
        self.initialize_components()
        
        # 모니터링 스레드
        self.monitoring_thread = None
        
        self.logger.info("IntegratedTradingBot 고급 버전 초기화 완료")
    
    def initialize_components(self):
        """컴포넌트 초기화"""
        self.logger.info("컴포넌트 초기화 시작")
        
        # 데이터 모듈들
        self.database = Database(self.config.database_path)
        
        # 분석 모듈들
        self.technical_analyzer = CoreTechnicalAnalyzer()  # 5개 핵심 지표
        self.strategy_manager = CoreStrategyManager()      # 4개 핵심 전략
        self.sentiment_analyzer = SentimentAnalyzer()
        self.ml_predictor = MLPredictor()
        self.signal_integrator = SignalIntegrator()
        
        # 거래 모듈들
        self.order_executor = OrderExecutor(self.config)
        self.risk_manager = RiskManager(self.config)
        
        self.logger.info("컴포넌트 초기화 완료")
    
    def process_market_data(self) -> Dict[str, Any]:
        """시장 데이터 처리 - 고급 버전"""
        try:
            # 1. 최신 가격 데이터 조회
            df = self.database.get_price_data(
                self.config.trading_symbol,
                limit=200  # 더 많은 데이터로 분석
            )
            
            if df.empty:
                return {'error': '과거 데이터 없음'}
            
            # 2. 데이터 품질 검증
            if not self._validate_data_quality(df):
                return {'error': '데이터 품질 문제'}
            
            # 3. 핵심 기술적 분석 (5개 지표)
            technical_signals = self.technical_analyzer.analyze(df)
            
            # 4. 핵심 전략 분석 (4개 전략)
            strategy_signals = self.strategy_manager.analyze({'price_data': df})
            
            # 5. 감정분석
            sentiment_result = self.sentiment_analyzer.analyze()
            
            # 6. ML 예측
            ml_signal = self.ml_predictor.predict(df)
            
            # 7. 4가지 신호 통합
            signals = {
                'technical_signals': technical_signals.get('signals', {}),
                'strategy_signals': strategy_signals,
                'sentiment_signal': sentiment_result.get('sentiment_signal', 0.0),
                'ml_signal': ml_signal
            }
            
            final_result = self.signal_integrator.integrate_signals(signals)
            
            # 8. 성능 메트릭 업데이트
            self._update_performance_metrics(final_result)
            
            # 9. 모니터링 데이터 업데이트
            self._update_monitoring_data(final_result)
            
            return {
                'technical_signals': technical_signals,
                'strategy_signals': strategy_signals,
                'sentiment_analysis': sentiment_result,
                'ml_prediction': ml_signal,
                'final_signal': final_result,
                'data_quality': self._get_data_quality_score(df)
            }
            
        except Exception as e:
            self.logger.error(f"시장 데이터 처리 실패: {e}")
            return {'error': str(e)}
    
    def _validate_data_quality(self, df: pd.DataFrame) -> bool:
        """데이터 품질 검증"""
        try:
            # 결측치 확인
            missing_data = df.isnull().sum().sum()
            if missing_data > len(df) * 0.1:  # 10% 이상 결측치
                self.logger.warning(f"결측치가 많습니다: {missing_data}")
                return False
            
            # 이상치 확인
            price_changes = df['close'].pct_change()
            outliers = price_changes[abs(price_changes) > 0.1]  # 10% 이상 변동
            if len(outliers) > len(df) * 0.05:  # 5% 이상 이상치
                self.logger.warning(f"이상치가 많습니다: {len(outliers)}")
                return False
            
            # 최신 데이터 확인
            last_timestamp = df.index[-1]
            current_time = pd.Timestamp.now()
            if (current_time - last_timestamp).total_seconds() > 3600:  # 1시간 이상 지연
                self.logger.warning("데이터가 오래되었습니다")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"데이터 품질 검증 실패: {e}")
            return False
    
    def _get_data_quality_score(self, df: pd.DataFrame) -> float:
        """데이터 품질 점수 계산"""
        try:
            score = 1.0
            
            # 결측치 점수
            missing_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
            score -= missing_ratio
            
            # 이상치 점수
            price_changes = df['close'].pct_change()
            outlier_ratio = len(price_changes[abs(price_changes) > 0.1]) / len(price_changes)
            score -= outlier_ratio
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.error(f"데이터 품질 점수 계산 실패: {e}")
            return 0.5
    
    def execute_trading_decision(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """거래 결정 실행 - 고급 버전"""
        try:
            if 'error' in market_data:
                return None
            
            final_signal = market_data.get('final_signal', {})
            trade_decision = final_signal.get('trade_decision', 'HOLD')
            
            if trade_decision == 'HOLD':
                self.logger.info("거래 결정: HOLD")
                return None
            
            # 리스크 체크
            risk_check = self.risk_manager.check_risk(final_signal)
            
            if not risk_check['can_trade']:
                self.logger.warning(f"거래 차단: {risk_check['reasons']}")
                return None
            
            # 성능 기반 거래 제한
            if not self._should_trade_based_on_performance():
                self.logger.info("성능 기반 거래 제한")
                return None
            
            # 거래 실행
            trade_result = self.order_executor.execute_trade(final_signal)
            
            if trade_result:
                # 거래 결과 업데이트
                self._update_trade_result(trade_result)
                
                self.logger.info(f"거래 실행 성공: {trade_decision}")
                return trade_result
            else:
                self.logger.warning("거래 실행 실패")
                return None
            
        except Exception as e:
            self.logger.error(f"거래 결정 실행 실패: {e}")
            return None
    
    def _should_trade_based_on_performance(self) -> bool:
        """성능 기반 거래 여부 결정"""
        try:
            # 최대 손실 한도 확인
            if self.performance_metrics['total_pnl'] < -self.config.initial_capital * 0.1:  # 10% 손실
                self.logger.warning("최대 손실 한도 도달")
                return False
            
            # 연속 손실 확인
            if self.performance_metrics['losing_trades'] >= 5:  # 연속 5회 손실
                self.logger.warning("연속 손실로 인한 거래 중단")
                return False
            
            # 승률 확인
            if (self.performance_metrics['total_trades'] > 10 and 
                self.performance_metrics['win_rate'] < 0.4):  # 40% 미만 승률
                self.logger.warning("낮은 승률로 인한 거래 중단")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"성능 기반 거래 결정 실패: {e}")
            return True
    
    def _update_performance_metrics(self, signal: Dict[str, Any]):
        """성능 메트릭 업데이트"""
        try:
            # 신호 강도 추적
            signal_strength = abs(signal.get('final_signal', 0.0))
            self.performance_metrics['signal_strength_avg'] = (
                (self.performance_metrics.get('signal_strength_avg', 0.0) * 
                 self.performance_metrics['total_trades'] + signal_strength) /
                (self.performance_metrics['total_trades'] + 1)
            )
            
        except Exception as e:
            self.logger.error(f"성능 메트릭 업데이트 실패: {e}")
    
    def _update_trade_result(self, trade_result: Dict[str, Any]):
        """거래 결과 업데이트"""
        try:
            self.performance_metrics['total_trades'] += 1
            
            # PnL 계산
            order = trade_result['order']
            if hasattr(order, 'price') and order.price > 0:
                # 간단한 PnL 계산 (실제로는 더 복잡한 로직 필요)
                pnl = 0.0  # 실제 PnL 계산 로직 구현 필요
                self.performance_metrics['total_pnl'] += pnl
                
                if pnl > 0:
                    self.performance_metrics['winning_trades'] += 1
                else:
                    self.performance_metrics['losing_trades'] += 1
            
            # 승률 계산
            if self.performance_metrics['total_trades'] > 0:
                self.performance_metrics['win_rate'] = (
                    self.performance_metrics['winning_trades'] / 
                    self.performance_metrics['total_trades']
                )
            
            # 최대 손실 업데이트
            if self.performance_metrics['total_pnl'] < self.performance_metrics['max_drawdown']:
                self.performance_metrics['max_drawdown'] = self.performance_metrics['total_pnl']
            
        except Exception as e:
            self.logger.error(f"거래 결과 업데이트 실패: {e}")
    
    def _update_monitoring_data(self, signal: Dict[str, Any]):
        """모니터링 데이터 업데이트"""
        try:
            self.monitoring_data['signal_strength'] = signal.get('final_signal', 0.0)
            self.monitoring_data['confidence'] = signal.get('confidence', 0.0)
            self.monitoring_data['last_analysis_time'] = datetime.now()
            
            # 활성 주문 업데이트
            trading_summary = self.order_executor.get_trading_summary()
            self.monitoring_data['active_orders'] = trading_summary.get('active_orders', 0)
            
        except Exception as e:
            self.logger.error(f"모니터링 데이터 업데이트 실패: {e}")
    
    def start_monitoring(self):
        """실시간 모니터링 시작"""
        if self.monitoring_thread is None or not self.monitoring_thread.is_alive():
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            self.logger.info("실시간 모니터링 시작")
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.is_running:
            try:
                # 현재 가격 업데이트
                current_price = self.order_executor.get_current_price(self.config.trading_symbol)
                if current_price:
                    self.monitoring_data['current_price'] = current_price
                
                # 성능 메트릭 업데이트
                self._update_performance_metrics_realtime()
                
                # 30초 대기
                time.sleep(30)
                
            except Exception as e:
                self.logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(60)
    
    def _update_performance_metrics_realtime(self):
        """실시간 성능 메트릭 업데이트"""
        try:
            # 샤프 비율 계산 (간단한 버전)
            if self.performance_metrics['total_trades'] > 10:
                returns = [0.01] * self.performance_metrics['total_trades']  # 실제 수익률 계산 필요
                if len(returns) > 1:
                    mean_return = sum(returns) / len(returns)
                    std_return = (sum((r - mean_return) ** 2 for r in returns) / len(returns)) ** 0.5
                    if std_return > 0:
                        self.performance_metrics['sharpe_ratio'] = mean_return / std_return
            
        except Exception as e:
            self.logger.error(f"실시간 성능 메트릭 업데이트 실패: {e}")
    
    def run(self):
        """봇 실행 - 고급 버전"""
        self.logger.info("봇 실행 시작")
        self.is_running = True
        self.start_time = datetime.now()
        
        # 모니터링 시작
        self.start_monitoring()
        
        try:
            while self.is_running:
                # 1. 시장 데이터 처리
                market_data = self.process_market_data()
                
                # 2. 거래 결정 실행
                trade_result = self.execute_trading_decision(market_data)
                
                # 3. 상태 로깅
                self.log_status()
                
                # 4. 성능 체크
                self._check_performance_alerts()
                
                # 5. 대기 (1분)
                time.sleep(60)
                
        except KeyboardInterrupt:
            self.logger.info("사용자에 의해 중단됨")
        except Exception as e:
            self.logger.error(f"봇 실행 중 오류: {e}")
        finally:
            self.is_running = False
            self.logger.info("봇 실행 종료")
    
    def _check_performance_alerts(self):
        """성능 알림 체크"""
        try:
            # 손실 한도 알림
            if self.performance_metrics['total_pnl'] < -self.config.initial_capital * 0.05:  # 5% 손실
                self.logger.warning("손실 한도 경고: 5% 손실 도달")
            
            # 연속 손실 알림
            if self.performance_metrics['losing_trades'] >= 3:
                self.logger.warning("연속 손실 경고: 3회 연속 손실")
            
            # 낮은 승률 알림
            if (self.performance_metrics['total_trades'] > 10 and 
                self.performance_metrics['win_rate'] < 0.5):
                self.logger.warning("낮은 승률 경고: 50% 미만 승률")
                
        except Exception as e:
            self.logger.error(f"성능 알림 체크 실패: {e}")
    
    def log_status(self):
        """상태 로깅 - 고급 버전"""
        try:
            risk_status = self.risk_manager.get_risk_status()
            trading_summary = self.order_executor.get_trading_summary()
            
            self.logger.info(
                f"봇 상태 - "
                f"총거래: {self.performance_metrics['total_trades']}, "
                f"승률: {self.performance_metrics['win_rate']:.2%}, "
                f"총PnL: {self.performance_metrics['total_pnl']:.2f}, "
                f"신호강도: {self.monitoring_data['signal_strength']:.3f}, "
                f"활성주문: {self.monitoring_data['active_orders']}"
            )
            
        except Exception as e:
            self.logger.error(f"상태 로깅 실패: {e}")
    
    def stop(self):
        """봇 중지"""
        self.logger.info("봇 중지 요청")
        self.is_running = False
    
    def get_status(self) -> Dict[str, Any]:
        """봇 상태 반환 - 고급 버전"""
        try:
            risk_status = self.risk_manager.get_risk_status()
            trading_summary = self.order_executor.get_trading_summary()
            
            return {
                'is_running': self.is_running,
                'current_position': self.current_position,
                'total_pnl': self.total_pnl,
                'trading_symbol': self.config.trading_symbol,
                'risk_status': risk_status,
                'performance_metrics': self.performance_metrics,
                'monitoring_data': self.monitoring_data,
                'trading_summary': trading_summary,
                'uptime': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
            }
            
        except Exception as e:
            self.logger.error(f"상태 조회 실패: {e}")
            return {}
    
    def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 생성"""
        try:
            return {
                'total_trades': self.performance_metrics['total_trades'],
                'winning_trades': self.performance_metrics['winning_trades'],
                'losing_trades': self.performance_metrics['losing_trades'],
                'win_rate': self.performance_metrics['win_rate'],
                'total_pnl': self.performance_metrics['total_pnl'],
                'max_drawdown': self.performance_metrics['max_drawdown'],
                'sharpe_ratio': self.performance_metrics['sharpe_ratio'],
                'avg_signal_strength': self.performance_metrics.get('signal_strength_avg', 0.0),
                'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600 if self.start_time else 0
            }
            
        except Exception as e:
            self.logger.error(f"성능 리포트 생성 실패: {e}")
            return {} 