"""
ML 예측 모듈
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import logging
from typing import Dict, Any, Tuple
import joblib
import os

class MLPredictor:
    """ML 예측 클래스"""
    
    def __init__(self, model_path: str = "./models/price_predictor.pkl"):
        """ML 예측기 초기화"""
        self.logger = logging.getLogger(__name__)
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.model = None
        self.is_trained = False
        
        # 특성 정의
        self.features = [
            'open', 'high', 'low', 'close', 'volume',
            'ma_short', 'ma_long', 'rsi', 'bb_upper', 'bb_lower',
            'macd', 'volume_sma'
        ]
        
        # 모델 로드 시도
        self.load_model()
        
        self.logger.info("MLPredictor 초기화 완료")
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """특성 엔지니어링"""
        try:
            # 기술적 지표 계산
            df['ma_short'] = df['close'].rolling(window=20).mean()
            df['ma_long'] = df['close'].rolling(window=50).mean()
            df['rsi'] = self.calculate_rsi(df['close'])
            df['bb_upper'] = df['close'].rolling(window=20).mean() + 2 * df['close'].rolling(window=20).std()
            df['bb_lower'] = df['close'].rolling(window=20).mean() - 2 * df['close'].rolling(window=20).std()
            df['macd'] = self.calculate_macd(df['close'])
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            
            # 추가 특성
            df['price_change'] = df['close'].pct_change()
            df['volume_change'] = df['volume'].pct_change()
            df['high_low_ratio'] = df['high'] / df['low']
            
            # 결측치 처리
            df = df.dropna()
            
            return df
            
        except Exception as e:
            self.logger.error(f"특성 엔지니어링 실패: {e}")
            return df
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series) -> pd.Series:
        """MACD 계산"""
        exp1 = prices.ewm(span=12).mean()
        exp2 = prices.ewm(span=26).mean()
        macd = exp1 - exp2
        return macd
    
    def create_target(self, df: pd.DataFrame, horizon: int = 1) -> pd.Series:
        """타겟 변수 생성 (미래 수익률)"""
        future_returns = df['close'].shift(-horizon) / df['close'] - 1
        return future_returns
    
    def train(self, df: pd.DataFrame):
        """모델 학습"""
        try:
            self.logger.info("ML 모델 학습 시작")
            
            # 특성 엔지니어링
            df = self.prepare_features(df)
            
            # 타겟 변수 생성
            target = self.create_target(df)
            
            # 유효한 데이터만 선택
            valid_data = df[self.features + ['close']].join(target).dropna()
            
            if len(valid_data) < 100:
                self.logger.warning("학습 데이터가 부족합니다")
                return
            
            X = valid_data[self.features]
            y = valid_data.iloc[:, -1]  # 타겟 변수
            
            # 데이터 분할
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # 특성 스케일링
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # 모델 학습
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            self.model.fit(X_train_scaled, y_train)
            
            # 모델 평가
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            self.logger.info(f"모델 학습 완료 - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
            
            # 모델 저장
            self.save_model()
            
            self.is_trained = True
            
        except Exception as e:
            self.logger.error(f"모델 학습 실패: {e}")
    
    def predict(self, df: pd.DataFrame) -> float:
        """가격 예측"""
        try:
            if not self.is_trained or self.model is None:
                self.logger.warning("모델이 학습되지 않았습니다")
                return 0.0
            
            # 특성 엔지니어링
            df = self.prepare_features(df)
            
            # 최신 데이터 추출
            latest_features = df[self.features].iloc[-1:].values
            
            # 특성 스케일링
            latest_features_scaled = self.scaler.transform(latest_features)
            
            # 예측
            prediction = self.model.predict(latest_features_scaled)[0]
            
            # 예측 신호 생성 (-1 ~ 1)
            ml_signal = max(-1.0, min(1.0, prediction * 10))  # 스케일링
            
            self.logger.info(f"ML 예측 완료: 예측={prediction:.4f}, 신호={ml_signal:.3f}")
            
            return ml_signal
            
        except Exception as e:
            self.logger.error(f"ML 예측 실패: {e}")
            return 0.0
    
    def save_model(self):
        """모델 저장"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'features': self.features
            }, self.model_path)
            self.logger.info(f"모델 저장 완료: {self.model_path}")
        except Exception as e:
            self.logger.error(f"모델 저장 실패: {e}")
    
    def load_model(self):
        """모델 로드"""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.features = model_data['features']
                self.is_trained = True
                self.logger.info(f"모델 로드 완료: {self.model_path}")
        except Exception as e:
            self.logger.error(f"모델 로드 실패: {e}") 