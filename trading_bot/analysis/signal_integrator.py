"""
신호 통합 모듈 (4가지 신호 통합)
"""

import logging
from typing import Dict, Any, List

class SignalIntegrator:
    """신호 통합 클래스"""
    
    def __init__(self):
        """신호 통합기 초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 4가지 신호 가중치 (핵심 지표 + 전략 + 감정 + ML)
        self.weights = {
            'technical': 0.3,    # 5개 핵심 지표
            'strategy': 0.3,     # 4개 핵심 전략
            'sentiment': 0.2,    # 감정분석
            'ml': 0.2            # ML 예측
        }
        
        self.logger.info("SignalIntegrator 초기화 완료")
    
    def integrate_signals(self, signals: Dict[str, float]) -> Dict[str, Any]:
        """4가지 신호 통합"""
        try:
            # 1. 기술적 지표 신호 (5개 지표 평균)
            technical_signals = signals.get('technical_signals', {})
            technical_avg = sum(technical_signals.values()) / len(technical_signals) if technical_signals else 0.0
            
            # 2. 전략 신호 (4개 전략 평균)
            strategy_signals = signals.get('strategy_signals', {})
            strategy_avg = sum(strategy_signals.values()) / len(strategy_signals) if strategy_signals else 0.0
            
            # 3. 감정분석 신호
            sentiment_signal = signals.get('sentiment_signal', 0.0)
            
            # 4. ML 예측 신호
            ml_signal = signals.get('ml_signal', 0.0)
            
            # 4가지 신호 가중 평균
            final_signal = (
                technical_avg * self.weights['technical'] +
                strategy_avg * self.weights['strategy'] +
                sentiment_signal * self.weights['sentiment'] +
                ml_signal * self.weights['ml']
            )
            
            # 신호 정규화 (-1 ~ 1)
            final_signal = max(-1.0, min(1.0, final_signal))
            
            # 거래 결정
            trade_decision = self.make_trade_decision(final_signal)
            
            result = {
                'final_signal': final_signal,
                'trade_decision': trade_decision,
                'signal_breakdown': {
                    'technical': technical_avg,
                    'strategy': strategy_avg,
                    'sentiment': sentiment_signal,
                    'ml': ml_signal,
                    'weights': self.weights
                },
                'detailed_signals': {
                    'technical_indicators': technical_signals,
                    'strategies': strategy_signals
                }
            }
            
            self.logger.info(f"신호 통합 완료: 최종신호={final_signal:.3f}, 결정={trade_decision}")
            return result
            
        except Exception as e:
            self.logger.error(f"신호 통합 실패: {e}")
            return {
                'final_signal': 0.0,
                'trade_decision': 'HOLD',
                'signal_breakdown': {},
                'detailed_signals': {}
            }
    
    def make_trade_decision(self, signal: float) -> str:
        """거래 결정"""
        if signal > 0.3:
            return 'BUY'
        elif signal < -0.3:
            return 'SELL'
        else:
            return 'HOLD'
    
    def update_weights(self, new_weights: Dict[str, float]):
        """가중치 업데이트"""
        self.weights.update(new_weights)
        self.logger.info(f"신호 가중치 업데이트: {self.weights}") 