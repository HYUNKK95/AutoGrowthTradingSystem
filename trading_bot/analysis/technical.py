"""
핵심 기술적 분석 모듈 (5개 지표) - 고급 버전
"""

import pandas as pd
import numpy as np
import ta
import logging
from typing import Dict, Any, Tuple, List
from dataclasses import dataclass

@dataclass
class TechnicalSignal:
    """기술적 신호 데이터 클래스"""
    signal: float
    strength: float
    confidence: float
    timestamp: int
    indicators: Dict[str, float]

class CoreTechnicalAnalyzer:
    """핵심 기술적 분석 클래스 - 고급 버전"""
    
    def __init__(self):
        """핵심 기술적 분석기 초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 핵심 지표 파라미터 (과도한 복잡성 방지)
        self.rsi_period = 14
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.bb_period = 20
        self.bb_std = 2
        self.ma_short = 20
        self.ma_long = 50
        self.volume_ma_period = 20
        
        # 추가 고급 파라미터
        self.stochastic_k = 14
        self.stochastic_d = 3
        self.atr_period = 14
        self.cci_period = 20
        self.williams_r_period = 14
        
        # 신호 필터링 파라미터
        self.min_signal_strength = 0.1
        self.confidence_threshold = 0.6
        
        self.logger.info("CoreTechnicalAnalyzer 고급 버전 초기화 완료")
    
    def calculate_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """RSI 지표 계산 - 고급 버전"""
        df['rsi'] = ta.momentum.rsi(df['close'], window=self.rsi_period)
        
        # RSI 신호 생성 (더 정교한 로직)
        df['rsi_signal'] = 0.0
        df['rsi_strength'] = 0.0
        
        # 과매수/과매도 구간
        df.loc[df['rsi'] > 70, 'rsi_signal'] = -1.0
        df.loc[df['rsi'] < 30, 'rsi_signal'] = 1.0
        
        # RSI 강도 계산
        df['rsi_strength'] = np.where(
            df['rsi'] > 70, (df['rsi'] - 70) / 30,
            np.where(df['rsi'] < 30, (30 - df['rsi']) / 30, 0.0)
        )
        
        # RSI 다이버전스 감지
        df['rsi_divergence'] = self._detect_rsi_divergence(df)
        
        return df
    
    def _detect_rsi_divergence(self, df: pd.DataFrame) -> pd.Series:
        """RSI 다이버전스 감지"""
        divergence = pd.Series(0.0, index=df.index)
        
        # 최근 20개 데이터에서 다이버전스 확인
        for i in range(20, len(df)):
            # 가격 고점/저점
            price_high = df['high'].iloc[i-20:i+1].max()
            price_low = df['low'].iloc[i-20:i+1].min()
            rsi_high = df['rsi'].iloc[i-20:i+1].max()
            rsi_low = df['rsi'].iloc[i-20:i+1].min()
            
            # 베어리시 다이버전스 (가격은 상승, RSI는 하락)
            if (df['close'].iloc[i] > price_high * 0.95 and 
                df['rsi'].iloc[i] < rsi_high * 0.8):
                divergence.iloc[i] = -1.0
            
            # 불리시 다이버전스 (가격은 하락, RSI는 상승)
            elif (df['close'].iloc[i] < price_low * 1.05 and 
                  df['rsi'].iloc[i] > rsi_low * 1.2):
                divergence.iloc[i] = 1.0
        
        return divergence
    
    def calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """MACD 지표 계산 - 고급 버전"""
        # MACD 계산
        macd = ta.trend.MACD(
            df['close'], 
            window_fast=self.macd_fast, 
            window_slow=self.macd_slow, 
            window_sign=self.macd_signal
        )
        
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_histogram'] = macd.macd_diff()
        
        # MACD 신호 생성 (더 정교한 로직)
        df['macd_trading_signal'] = 0.0
        df['macd_strength'] = 0.0
        
        # MACD 크로스오버
        df['macd_crossover'] = np.where(
            (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1)), 1.0,
            np.where((df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1)), -1.0, 0.0)
        )
        
        # MACD 히스토그램 기반 신호
        df['macd_histogram_signal'] = np.where(
            df['macd_histogram'] > 0, 1.0, -1.0
        )
        
        # 최종 MACD 신호
        df['macd_trading_signal'] = np.where(
            df['macd_crossover'] != 0, df['macd_crossover'],
            df['macd_histogram_signal']
        )
        
        # MACD 강도 계산
        df['macd_strength'] = abs(df['macd_histogram']) / df['close'] * 100
        
        return df
    
    def calculate_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """볼린저 밴드 계산 - 고급 버전"""
        bb = ta.volatility.BollingerBands(
            df['close'], 
            window=self.bb_period, 
            window_dev=self.bb_std
        )
        
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # 볼린저 밴드 신호 생성 (더 정교한 로직)
        df['bb_signal'] = 0.0
        df['bb_strength'] = 0.0
        
        # 밴드 위치에 따른 신호
        df.loc[df['bb_position'] < 0.1, 'bb_signal'] = 1.0  # 하단 밴드 근처
        df.loc[df['bb_position'] > 0.9, 'bb_signal'] = -1.0  # 상단 밴드 근처
        
        # 밴드 수축/확장 감지
        bb_width_ma = df['bb_width'].rolling(window=20).mean()
        df['bb_squeeze'] = np.where(
            df['bb_width'] < bb_width_ma * 0.8, 1.0,  # 수축
            np.where(df['bb_width'] > bb_width_ma * 1.2, -1.0, 0.0)  # 확장
        )
        
        # 볼린저 밴드 강도
        df['bb_strength'] = abs(df['bb_position'] - 0.5) * 2
        
        return df
    
    def calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """이동평균 계산 - 고급 버전"""
        # 다양한 이동평균
        df['ma_short'] = ta.trend.sma_indicator(df['close'], window=self.ma_short)
        df['ma_long'] = ta.trend.sma_indicator(df['close'], window=self.ma_long)
        df['ma_ema_short'] = ta.trend.ema_indicator(df['close'], window=self.ma_short)
        df['ma_ema_long'] = ta.trend.ema_indicator(df['close'], window=self.ma_long)
        
        # 이동평균 신호 생성
        df['ma_signal'] = 0.0
        df['ma_strength'] = 0.0
        
        # 골든 크로스 / 데드 크로스
        df['ma_crossover'] = np.where(
            (df['ma_short'] > df['ma_long']) & (df['ma_short'].shift(1) <= df['ma_long'].shift(1)), 1.0,
            np.where((df['ma_short'] < df['ma_long']) & (df['ma_short'].shift(1) >= df['ma_long'].shift(1)), -1.0, 0.0)
        )
        
        # 가격과 이동평균의 관계
        df['price_vs_ma'] = (df['close'] - df['ma_long']) / df['ma_long']
        
        # 최종 이동평균 신호
        df['ma_signal'] = np.where(
            df['ma_crossover'] != 0, df['ma_crossover'],
            np.where(df['price_vs_ma'] > 0.02, 1.0,
                    np.where(df['price_vs_ma'] < -0.02, -1.0, 0.0))
        )
        
        # 이동평균 강도
        df['ma_strength'] = abs(df['price_vs_ma'])
        
        return df
    
    def calculate_volume(self, df: pd.DataFrame) -> pd.DataFrame:
        """거래량 분석 - 고급 버전"""
        # 거래량 지표들
        df['volume_ma'] = ta.trend.sma_indicator(df['volume'], window=self.volume_ma_period)
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        df['volume_sma'] = ta.volume.volume_sma(df['close'], df['volume'], window=20)
        
        # 거래량 신호 생성
        df['volume_signal'] = 0.0
        df['volume_strength'] = 0.0
        
        # 거래량 급증/급감
        df.loc[df['volume_ratio'] > 1.5, 'volume_signal'] = 1.0
        df.loc[df['volume_ratio'] < 0.5, 'volume_signal'] = -1.0
        
        # 거래량과 가격 변화의 관계
        price_change = df['close'].pct_change()
        volume_price_correlation = df['volume'].rolling(window=10).corr(price_change)
        
        df['volume_price_signal'] = np.where(
            volume_price_correlation > 0.3, 1.0,
            np.where(volume_price_correlation < -0.3, -1.0, 0.0)
        )
        
        # 최종 거래량 신호
        df['volume_signal'] = np.where(
            df['volume_signal'] != 0, df['volume_signal'],
            df['volume_price_signal']
        )
        
        # 거래량 강도
        df['volume_strength'] = abs(df['volume_ratio'] - 1.0)
        
        return df
    
    def calculate_additional_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """추가 고급 지표 계산"""
        # 스토캐스틱
        stoch = ta.momentum.StochasticOscillator(
            df['high'], df['low'], df['close'],
            window=self.stochastic_k, smooth_window=self.stochastic_d
        )
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        
        # ATR (Average True Range)
        df['atr'] = ta.volatility.average_true_range(
            df['high'], df['low'], df['close'], window=self.atr_period
        )
        
        # CCI (Commodity Channel Index)
        df['cci'] = ta.trend.cci(
            df['high'], df['low'], df['close'], window=self.cci_period
        )
        
        # Williams %R
        df['williams_r'] = ta.momentum.williams_r(
            df['high'], df['low'], df['close'], window=self.williams_r_period
        )
        
        return df
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """기술적 분석 실행 - 고급 버전"""
        try:
            # 모든 지표 계산
            df = self.calculate_moving_averages(df)
            df = self.calculate_rsi(df)
            df = self.calculate_bollinger_bands(df)
            df = self.calculate_macd(df)
            df = self.calculate_volume(df)
            df = self.calculate_additional_indicators(df)
            
            # 최신 데이터 추출
            latest = df.iloc[-1]
            
            # 종합 신호 계산 (가중 평균)
            signals = {
                'ma_signal': latest['ma_signal'],
                'rsi_signal': latest['rsi_signal'],
                'bb_signal': latest['bb_signal'],
                'macd_signal': latest['macd_trading_signal'],
                'volume_signal': latest['volume_signal']
            }
            
            # 신호 강도
            strengths = {
                'ma_strength': latest['ma_strength'],
                'rsi_strength': latest['rsi_strength'],
                'bb_strength': latest['bb_strength'],
                'macd_strength': latest['macd_strength'],
                'volume_strength': latest['volume_strength']
            }
            
            # 가중 평균 신호 (강도 기반)
            total_weight = sum(strengths.values())
            if total_weight > 0:
                technical_signal = sum(
                    signals[key] * strengths[key] for key in signals.keys()
                ) / total_weight
            else:
                technical_signal = sum(signals.values()) / len(signals)
            
            # 신호 정규화 (-1 ~ 1)
            technical_signal = max(-1, min(1, technical_signal))
            
            # 신뢰도 계산
            confidence = self._calculate_confidence(signals, strengths)
            
            # 신호 필터링
            if abs(technical_signal) < self.min_signal_strength:
                technical_signal = 0.0
            
            result = {
                'technical_signal': technical_signal,
                'confidence': confidence,
                'signals': signals,
                'strengths': strengths,
                'indicators': {
                    'ma_short': latest['ma_short'],
                    'ma_long': latest['ma_long'],
                    'rsi': latest['rsi'],
                    'bb_upper': latest['bb_upper'],
                    'bb_lower': latest['bb_lower'],
                    'macd': latest['macd'],
                    'volume_ratio': latest['volume_ratio'],
                    'atr': latest['atr'],
                    'cci': latest['cci'],
                    'williams_r': latest['williams_r']
                },
                'timestamp': int(pd.Timestamp.now().timestamp() * 1000)
            }
            
            self.logger.info(f"기술적 분석 완료: 신호={technical_signal:.3f}, 신뢰도={confidence:.3f}")
            return result
            
        except Exception as e:
            self.logger.error(f"기술적 분석 실패: {e}")
            return {
                'technical_signal': 0.0,
                'confidence': 0.0,
                'signals': {},
                'strengths': {},
                'indicators': {},
                'timestamp': int(pd.Timestamp.now().timestamp() * 1000)
            }
    
    def _calculate_confidence(self, signals: Dict[str, float], strengths: Dict[str, float]) -> float:
        """신호 신뢰도 계산"""
        # 신호 일관성 확인
        positive_signals = sum(1 for s in signals.values() if s > 0)
        negative_signals = sum(1 for s in signals.values() if s < 0)
        
        # 신호 일관성 점수
        consistency = max(positive_signals, negative_signals) / len(signals)
        
        # 강도 평균
        avg_strength = sum(strengths.values()) / len(strengths)
        
        # 최종 신뢰도
        confidence = (consistency + avg_strength) / 2
        return min(1.0, confidence)
    
    def get_signal_history(self, df: pd.DataFrame, periods: int = 20) -> List[TechnicalSignal]:
        """신호 히스토리 반환"""
        signals = []
        
        for i in range(max(50, periods), len(df)):
            window_df = df.iloc[i-periods:i+1]
            result = self.analyze(window_df)
            
            signal = TechnicalSignal(
                signal=result['technical_signal'],
                strength=result['confidence'],
                confidence=result['confidence'],
                timestamp=int(pd.Timestamp.now().timestamp() * 1000),
                indicators=result['indicators']
            )
            signals.append(signal)
        
        return signals 