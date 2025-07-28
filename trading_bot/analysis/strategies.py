"""
핵심 전략 모듈 (4개 전략) - 고급 버전
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Tuple, List
from dataclasses import dataclass
from enum import Enum

class StrategyType(Enum):
    """전략 타입"""
    SCALPING = "scalping"
    SWING = "swing"
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"

@dataclass
class StrategySignal:
    """전략 신호 데이터 클래스"""
    strategy_type: StrategyType
    signal: float
    strength: float
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    timestamp: int

class CoreStrategyManager:
    """핵심 전략 관리 클래스 - 고급 버전"""
    
    def __init__(self):
        """핵심 전략 관리자 초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 전략 파라미터
        self.scalping_period = 5  # 5분
        self.swing_period = 240   # 4시간
        self.trend_period = 50    # 50일
        self.reversion_period = 20 # 20일
        
        # 고급 파라미터
        self.volatility_threshold = 0.02
        self.trend_strength_threshold = 0.01
        self.reversion_threshold = 1.5
        self.min_volume_ratio = 1.2
        
        # 리스크 관리 파라미터
        self.max_position_size = 0.1  # 10%
        self.stop_loss_percent = 0.02  # 2%
        self.take_profit_percent = 0.04  # 4%
        self.max_drawdown = 0.05  # 5%
        
        # 신호 필터링
        self.min_signal_strength = 0.1
        self.confidence_threshold = 0.6
        
        self.logger.info("CoreStrategyManager 고급 버전 초기화 완료")
    
    def scalping_strategy(self, df: pd.DataFrame) -> Dict[str, Any]:
        """스캘핑 전략 (단기 변동성 활용) - 고급 버전"""
        try:
            # 단기 변동성 계산
            df['price_change'] = df['close'].pct_change()
            df['volatility'] = df['price_change'].rolling(window=self.scalping_period).std()
            df['volatility_ma'] = df['volatility'].rolling(window=20).mean()
            
            # 현재 변동성과 평균 변동성 비교
            current_volatility = df['volatility'].iloc[-1]
            avg_volatility = df['volatility_ma'].iloc[-1]
            
            # 모멘텀 계산
            momentum = df['close'].pct_change(periods=3).iloc[-1]
            momentum_ma = df['close'].pct_change(periods=3).rolling(window=10).mean().iloc[-1]
            
            # 거래량 확인
            volume_ratio = df['volume'].iloc[-1] / df['volume'].rolling(window=20).mean().iloc[-1]
            
            # 스캘핑 신호 생성 (더 정교한 로직)
            signal = 0.0
            strength = 0.0
            confidence = 0.0
            
            # 변동성 급증 + 모멘텀 확인
            if (current_volatility > avg_volatility * 1.2 and 
                volume_ratio > self.min_volume_ratio):
                
                if momentum > momentum_ma * 1.1:
                    signal = 1.0  # 매수
                    strength = min(1.0, (current_volatility / avg_volatility - 1) * 2)
                elif momentum < momentum_ma * 0.9:
                    signal = -1.0  # 매도
                    strength = min(1.0, (current_volatility / avg_volatility - 1) * 2)
            
            # 신뢰도 계산
            confidence = self._calculate_strategy_confidence(df, 'scalping')
            
            # 진입가, 손절가, 익절가 계산
            current_price = df['close'].iloc[-1]
            entry_price = current_price
            stop_loss = entry_price * (1 - self.stop_loss_percent) if signal > 0 else entry_price * (1 + self.stop_loss_percent)
            take_profit = entry_price * (1 + self.take_profit_percent) if signal > 0 else entry_price * (1 - self.take_profit_percent)
            
            return {
                'signal': signal,
                'strength': strength,
                'confidence': confidence,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'volatility': current_volatility,
                'momentum': momentum,
                'volume_ratio': volume_ratio
            }
                
        except Exception as e:
            self.logger.error(f"스캘핑 전략 실패: {e}")
            return self._get_default_strategy_result()
    
    def swing_strategy(self, df: pd.DataFrame) -> Dict[str, Any]:
        """스윙 트레이딩 전략 (중기 추세 활용) - 고급 버전"""
        try:
            # 중기 이동평균
            df['ma_swing'] = df['close'].rolling(window=self.swing_period).mean()
            df['ma_swing_short'] = df['close'].rolling(window=self.swing_period // 2).mean()
            
            # 추세 강도 계산
            df['trend_strength'] = (df['close'] - df['ma_swing']) / df['ma_swing']
            df['trend_ma'] = df['trend_strength'].rolling(window=10).mean()
            
            # 현재 추세 강도
            current_trend = df['trend_strength'].iloc[-1]
            trend_ma = df['trend_ma'].iloc[-1]
            
            # 추세 지속성 확인
            trend_consistency = self._calculate_trend_consistency(df)
            
            # 스윙 신호 생성 (더 정교한 로직)
            signal = 0.0
            strength = 0.0
            confidence = 0.0
            
            # 강한 상승 추세
            if (current_trend > trend_ma * 1.1 and 
                current_trend > self.trend_strength_threshold and
                trend_consistency > 0.7):
                signal = 1.0
                strength = min(1.0, current_trend / self.trend_strength_threshold)
            
            # 강한 하락 추세
            elif (current_trend < trend_ma * 0.9 and 
                  current_trend < -self.trend_strength_threshold and
                  trend_consistency > 0.7):
                signal = -1.0
                strength = min(1.0, abs(current_trend) / self.trend_strength_threshold)
            
            # 신뢰도 계산
            confidence = self._calculate_strategy_confidence(df, 'swing')
            
            # 진입가, 손절가, 익절가 계산
            current_price = df['close'].iloc[-1]
            entry_price = current_price
            stop_loss = entry_price * (1 - self.stop_loss_percent) if signal > 0 else entry_price * (1 + self.stop_loss_percent)
            take_profit = entry_price * (1 + self.take_profit_percent) if signal > 0 else entry_price * (1 - self.take_profit_percent)
            
            return {
                'signal': signal,
                'strength': strength,
                'confidence': confidence,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'trend_strength': current_trend,
                'trend_consistency': trend_consistency
            }
                
        except Exception as e:
            self.logger.error(f"스윙 전략 실패: {e}")
            return self._get_default_strategy_result()
    
    def trend_following_strategy(self, df: pd.DataFrame) -> Dict[str, Any]:
        """추세 추종 전략 (추세 방향 거래) - 고급 버전"""
        try:
            # 장기 이동평균
            df['ma_trend'] = df['close'].rolling(window=self.trend_period).mean()
            df['ma_short_trend'] = df['close'].rolling(window=10).mean()
            df['ma_medium_trend'] = df['close'].rolling(window=20).mean()
            
            # 추세 방향 확인
            trend_direction = 1 if df['ma_short_trend'].iloc[-1] > df['ma_trend'].iloc[-1] else -1
            
            # 추세 강도
            price_vs_ma = (df['close'].iloc[-1] - df['ma_trend'].iloc[-1]) / df['ma_trend'].iloc[-1]
            
            # 추세 지속성
            trend_consistency = self._calculate_trend_consistency(df)
            
            # 추세 추종 신호 생성 (더 정교한 로직)
            signal = 0.0
            strength = 0.0
            confidence = 0.0
            
            # 강한 상승 추세
            if (trend_direction > 0 and 
                price_vs_ma > self.trend_strength_threshold and
                trend_consistency > 0.6):
                signal = 1.0
                strength = min(1.0, price_vs_ma / self.trend_strength_threshold)
            
            # 강한 하락 추세
            elif (trend_direction < 0 and 
                  price_vs_ma < -self.trend_strength_threshold and
                  trend_consistency > 0.6):
                signal = -1.0
                strength = min(1.0, abs(price_vs_ma) / self.trend_strength_threshold)
            
            # 신뢰도 계산
            confidence = self._calculate_strategy_confidence(df, 'trend_following')
            
            # 진입가, 손절가, 익절가 계산
            current_price = df['close'].iloc[-1]
            entry_price = current_price
            stop_loss = entry_price * (1 - self.stop_loss_percent) if signal > 0 else entry_price * (1 + self.stop_loss_percent)
            take_profit = entry_price * (1 + self.take_profit_percent) if signal > 0 else entry_price * (1 - self.take_profit_percent)
            
            return {
                'signal': signal,
                'strength': strength,
                'confidence': confidence,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'trend_direction': trend_direction,
                'price_vs_ma': price_vs_ma,
                'trend_consistency': trend_consistency
            }
                
        except Exception as e:
            self.logger.error(f"추세 추종 전략 실패: {e}")
            return self._get_default_strategy_result()
    
    def mean_reversion_strategy(self, df: pd.DataFrame) -> Dict[str, Any]:
        """평균 회귀 전략 (평균값으로 회귀) - 고급 버전"""
        try:
            # 이동평균 계산
            df['ma_reversion'] = df['close'].rolling(window=self.reversion_period).mean()
            df['std_reversion'] = df['close'].rolling(window=self.reversion_period).std()
            
            # 현재 가격과 평균의 차이
            current_price = df['close'].iloc[-1]
            current_ma = df['ma_reversion'].iloc[-1]
            current_std = df['std_reversion'].iloc[-1]
            
            # 표준편차 대비 편차
            deviation = (current_price - current_ma) / current_std
            
            # 평균 회귀 히스토리 확인
            reversion_history = self._calculate_reversion_history(df)
            
            # 평균 회귀 신호 생성 (더 정교한 로직)
            signal = 0.0
            strength = 0.0
            confidence = 0.0
            
            # 강한 과매도 (매수 신호)
            if (deviation < -self.reversion_threshold and 
                reversion_history > 0.6):
                signal = 1.0
                strength = min(1.0, abs(deviation) / self.reversion_threshold)
            
            # 강한 과매수 (매도 신호)
            elif (deviation > self.reversion_threshold and 
                  reversion_history > 0.6):
                signal = -1.0
                strength = min(1.0, abs(deviation) / self.reversion_threshold)
            
            # 신뢰도 계산
            confidence = self._calculate_strategy_confidence(df, 'mean_reversion')
            
            # 진입가, 손절가, 익절가 계산
            entry_price = current_price
            stop_loss = entry_price * (1 - self.stop_loss_percent) if signal > 0 else entry_price * (1 + self.stop_loss_percent)
            take_profit = entry_price * (1 + self.take_profit_percent) if signal > 0 else entry_price * (1 - self.take_profit_percent)
            
            return {
                'signal': signal,
                'strength': strength,
                'confidence': confidence,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'deviation': deviation,
                'reversion_history': reversion_history
            }
                
        except Exception as e:
            self.logger.error(f"평균 회귀 전략 실패: {e}")
            return self._get_default_strategy_result()
    
    def _calculate_trend_consistency(self, df: pd.DataFrame) -> float:
        """추세 일관성 계산"""
        try:
            # 최근 20개 데이터에서 추세 일관성 확인
            recent_data = df.tail(20)
            price_changes = recent_data['close'].pct_change()
            
            # 상승/하락 일관성
            positive_changes = sum(1 for change in price_changes if change > 0)
            negative_changes = sum(1 for change in price_changes if change < 0)
            
            consistency = max(positive_changes, negative_changes) / len(price_changes)
            return consistency
            
        except Exception as e:
            self.logger.error(f"추세 일관성 계산 실패: {e}")
            return 0.5
    
    def _calculate_reversion_history(self, df: pd.DataFrame) -> float:
        """평균 회귀 히스토리 계산"""
        try:
            # 최근 50개 데이터에서 평균 회귀 성공률 계산
            recent_data = df.tail(50)
            success_count = 0
            
            for i in range(10, len(recent_data)):
                current_price = recent_data['close'].iloc[i]
                current_ma = recent_data['close'].rolling(window=self.reversion_period).mean().iloc[i]
                
                # 과매수/과매도 구간에서 회귀 확인
                if abs(current_price - current_ma) > current_ma * 0.02:  # 2% 이상 편차
                    # 다음 5개 데이터에서 회귀 확인
                    for j in range(i+1, min(i+6, len(recent_data))):
                        future_price = recent_data['close'].iloc[j]
                        if abs(future_price - current_ma) < abs(current_price - current_ma):
                            success_count += 1
                            break
            
            return success_count / max(1, len(recent_data) - 10)
            
        except Exception as e:
            self.logger.error(f"평균 회귀 히스토리 계산 실패: {e}")
            return 0.5
    
    def _calculate_strategy_confidence(self, df: pd.DataFrame, strategy_name: str) -> float:
        """전략 신뢰도 계산"""
        try:
            # 거래량 확인
            volume_ratio = df['volume'].iloc[-1] / df['volume'].rolling(window=20).mean().iloc[-1]
            
            # 변동성 확인
            volatility = df['close'].pct_change().rolling(window=20).std().iloc[-1]
            avg_volatility = df['close'].pct_change().rolling(window=50).std().iloc[-1]
            
            # 기본 신뢰도
            confidence = 0.5
            
            # 거래량 가중치
            if volume_ratio > 1.2:
                confidence += 0.2
            elif volume_ratio < 0.8:
                confidence -= 0.1
            
            # 변동성 가중치
            if volatility > avg_volatility * 1.1:
                confidence += 0.1
            elif volatility < avg_volatility * 0.9:
                confidence -= 0.1
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            self.logger.error(f"전략 신뢰도 계산 실패: {e}")
            return 0.5
    
    def _get_default_strategy_result(self) -> Dict[str, Any]:
        """기본 전략 결과"""
        return {
            'signal': 0.0,
            'strength': 0.0,
            'confidence': 0.0,
            'entry_price': 0.0,
            'stop_loss': 0.0,
            'take_profit': 0.0
        }
    
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """모든 핵심 전략 분석 - 고급 버전"""
        try:
            df = pd.DataFrame(market_data['price_data'])
            
            # 각 전략별 신호 생성
            strategies = {
                'scalping': self.scalping_strategy(df),
                'swing': self.swing_strategy(df),
                'trend_following': self.trend_following_strategy(df),
                'mean_reversion': self.mean_reversion_strategy(df)
            }
            
            # 전략별 신뢰도 기반 필터링
            filtered_strategies = {}
            for name, result in strategies.items():
                if result['confidence'] >= self.confidence_threshold:
                    filtered_strategies[name] = result
            
            self.logger.info(f"전략 분석 완료: {len(filtered_strategies)}개 전략 신뢰도 통과")
            return filtered_strategies
            
        except Exception as e:
            self.logger.error(f"전략 분석 실패: {e}")
            return {
                'scalping': self._get_default_strategy_result(),
                'swing': self._get_default_strategy_result(),
                'trend_following': self._get_default_strategy_result(),
                'mean_reversion': self._get_default_strategy_result()
            }
    
    def get_strategy_signals(self, df: pd.DataFrame) -> List[StrategySignal]:
        """전략 신호 히스토리 반환"""
        signals = []
        
        for i in range(50, len(df)):
            window_df = df.iloc[i-50:i+1]
            strategies = self.analyze({'price_data': window_df})
            
            for strategy_name, result in strategies.items():
                if result['signal'] != 0:
                    signal = StrategySignal(
                        strategy_type=StrategyType(strategy_name),
                        signal=result['signal'],
                        strength=result['strength'],
                        confidence=result['confidence'],
                        entry_price=result['entry_price'],
                        stop_loss=result['stop_loss'],
                        take_profit=result['take_profit'],
                        timestamp=int(pd.Timestamp.now().timestamp() * 1000)
                    )
                    signals.append(signal)
        
        return signals 