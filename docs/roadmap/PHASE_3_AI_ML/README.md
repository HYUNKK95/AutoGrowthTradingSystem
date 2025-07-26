# 🤖 Phase 3: AI/ML 기반 거래 시스템

## 📋 **개요**

### 🎯 **목표**
- **AI 기반 예측**: LSTM, Transformer 기반 가격 예측 모델
- **강화학습 거래**: Q-Learning, DDPG 기반 거래 에이전트
- **감정 분석**: NLP 기반 뉴스/소셜 감정 분석
- **포트폴리오 최적화**: Modern Portfolio Theory + AI
- **자동화 거래**: 완전 자동화된 거래 시스템

### 📊 **성능 목표**
- **예측 정확도**: > 65% (시장 평균 대비)
- **수익률**: > 20% 연간 (리스크 조정)
- **샤프 비율**: > 2.0
- **최대 낙폭**: < 15%
- **모델 학습 시간**: < 2시간 (일일 재학습)

## 🏗️ **AI/ML 아키텍처**

### 📁 **AI/ML 시스템 구조**
```
ai-ml-system/
├── prediction-models/              # 예측 모델
│   ├── lstm/                      # LSTM 기반 예측
│   ├── transformer/               # Transformer 기반 예측
│   ├── ensemble/                  # 앙상블 모델
│   └── time-series/               # 시계열 분석
├── reinforcement-learning/         # 강화학습
│   ├── q-learning/                # Q-Learning 에이전트
│   ├── ddpg/                      # DDPG 에이전트
│   ├── ppo/                       # PPO 에이전트
│   └── multi-agent/               # 다중 에이전트
├── sentiment-analysis/            # 감정 분석
│   ├── news-analysis/             # 뉴스 분석
│   ├── social-media/              # 소셜 미디어 분석
│   ├── nlp-models/                # NLP 모델
│   └── real-time/                 # 실시간 분석
├── portfolio-optimization/        # 포트폴리오 최적화
│   ├── modern-portfolio/          # Modern Portfolio Theory
│   ├── risk-management/           # 리스크 관리
│   ├── rebalancing/               # 자동 리밸런싱
│   └── optimization/              # 최적화 알고리즘
├── data-pipeline/                 # 데이터 파이프라인
│   ├── data-collection/           # 데이터 수집
│   ├── data-preprocessing/        # 데이터 전처리
│   ├── feature-engineering/       # 특성 엔지니어링
│   └── data-validation/           # 데이터 검증
└── trading-execution/             # 거래 실행
    ├── signal-generation/         # 신호 생성
    ├── order-execution/           # 주문 실행
    ├── risk-control/              # 리스크 제어
    └── performance-tracking/      # 성과 추적
```

## 🔧 **예측 모델 시스템**

### 📦 **LSTM 기반 가격 예측**

```python
# ai-ml-system/prediction-models/lstm/price_predictor.py
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class LSTMPredictor:
    """LSTM 기반 가격 예측 모델"""
    
    def __init__(self, sequence_length: int = 60, prediction_horizon: int = 1):
        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.feature_columns = [
            'open', 'high', 'low', 'close', 'volume',
            'rsi', 'macd', 'bollinger_upper', 'bollinger_lower',
            'sma_20', 'sma_50', 'ema_12', 'ema_26'
        ]
        
        logger.info(f"Initialized LSTM predictor with sequence length: {sequence_length}")
    
    def build_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """LSTM 모델 구축"""
        model = Sequential([
            # 첫 번째 LSTM 레이어
            LSTM(units=50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            
            # 두 번째 LSTM 레이어
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),
            
            # 세 번째 LSTM 레이어
            LSTM(units=50, return_sequences=False),
            Dropout(0.2),
            
            # 출력 레이어
            Dense(units=25),
            Dense(units=self.prediction_horizon)
        ])
        
        # 모델 컴파일
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mean_squared_error',
            metrics=['mae']
        )
        
        logger.info("LSTM model built successfully")
        return model
    
    def prepare_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """데이터 준비"""
        try:
            # 특성 선택
            features = data[self.feature_columns].values
            
            # 정규화
            scaled_features = self.scaler.fit_transform(features)
            
            # 시퀀스 데이터 생성
            X, y = [], []
            
            for i in range(self.sequence_length, len(scaled_features) - self.prediction_horizon + 1):
                X.append(scaled_features[i-self.sequence_length:i])
                y.append(scaled_features[i:i+self.prediction_horizon, 3])  # close price
            
            X = np.array(X)
            y = np.array(y)
            
            logger.info(f"Prepared data: X shape {X.shape}, y shape {y.shape}")
            return X, y
            
        except Exception as e:
            logger.error(f"Data preparation failed: {e}")
            raise
    
    def train(self, data: pd.DataFrame, epochs: int = 100, batch_size: int = 32,
              validation_split: float = 0.2) -> Dict[str, List[float]]:
        """모델 학습"""
        try:
            # 데이터 준비
            X, y = self.prepare_data(data)
            
            # 모델 구축
            self.model = self.build_model((X.shape[1], X.shape[2]))
            
            # 조기 종료 콜백
            early_stopping = tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            )
            
            # 학습
            history = self.model.fit(
                X, y,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=validation_split,
                callbacks=[early_stopping],
                verbose=1
            )
            
            logger.info("LSTM model training completed")
            return history.history
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """가격 예측"""
        try:
            if self.model is None:
                raise ValueError("Model not trained. Call train() first.")
            
            # 데이터 준비
            features = data[self.feature_columns].values
            scaled_features = self.scaler.transform(features)
            
            # 예측을 위한 시퀀스 생성
            last_sequence = scaled_features[-self.sequence_length:]
            X_pred = last_sequence.reshape(1, self.sequence_length, len(self.feature_columns))
            
            # 예측
            scaled_prediction = self.model.predict(X_pred)
            
            # 역정규화
            prediction = self.scaler.inverse_transform(
                np.zeros((1, len(self.feature_columns)))
            )
            prediction[0, 3] = scaled_prediction[0, 0]  # close price
            
            logger.info(f"Prediction completed: {prediction[0, 3]}")
            return prediction[0, 3]
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    def evaluate(self, test_data: pd.DataFrame) -> Dict[str, float]:
        """모델 평가"""
        try:
            # 테스트 데이터 준비
            X_test, y_test = self.prepare_data(test_data)
            
            # 예측
            predictions = self.model.predict(X_test)
            
            # 역정규화
            y_test_actual = self.scaler.inverse_transform(
                np.zeros((len(y_test), len(self.feature_columns)))
            )
            y_test_actual[:, 3] = y_test.flatten()
            
            predictions_actual = self.scaler.inverse_transform(
                np.zeros((len(predictions), len(self.feature_columns)))
            )
            predictions_actual[:, 3] = predictions.flatten()
            
            # 메트릭 계산
            mse = np.mean((y_test_actual[:, 3] - predictions_actual[:, 3]) ** 2)
            mae = np.mean(np.abs(y_test_actual[:, 3] - predictions_actual[:, 3]))
            rmse = np.sqrt(mse)
            
            # 방향 정확도
            direction_accuracy = np.mean(
                np.sign(np.diff(y_test_actual[:, 3])) == 
                np.sign(np.diff(predictions_actual[:, 3]))
            )
            
            metrics = {
                'mse': mse,
                'mae': mae,
                'rmse': rmse,
                'direction_accuracy': direction_accuracy
            }
            
            logger.info(f"Model evaluation completed: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Model evaluation failed: {e}")
            raise
    
    def save_model(self, filepath: str):
        """모델 저장"""
        try:
            self.model.save(filepath)
            logger.info(f"Model saved to: {filepath}")
        except Exception as e:
            logger.error(f"Model save failed: {e}")
            raise
    
    def load_model(self, filepath: str):
        """모델 로드"""
        try:
            self.model = tf.keras.models.load_model(filepath)
            logger.info(f"Model loaded from: {filepath}")
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            raise
```

### 📦 **Transformer 기반 예측**

```python
# ai-ml-system/prediction-models/transformer/transformer_predictor.py
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class MultiHeadAttention(layers.Layer):
    """멀티헤드 어텐션 레이어"""
    
    def __init__(self, d_model: int, num_heads: int):
        super(MultiHeadAttention, self).__init__()
        self.num_heads = num_heads
        self.d_model = d_model
        
        assert d_model % self.num_heads == 0
        
        self.depth = d_model // self.num_heads
        
        self.wq = layers.Dense(d_model)
        self.wk = layers.Dense(d_model)
        self.wv = layers.Dense(d_model)
        
        self.dense = layers.Dense(d_model)
    
    def split_heads(self, x, batch_size):
        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.depth))
        return tf.transpose(x, perm=[0, 2, 1, 3])
    
    def call(self, v, k, q, mask):
        batch_size = tf.shape(q)[0]
        
        q = self.wq(q)
        k = self.wk(k)
        v = self.wv(v)
        
        q = self.split_heads(q, batch_size)
        k = self.split_heads(k, batch_size)
        v = self.split_heads(v, batch_size)
        
        scaled_attention = scaled_dot_product_attention(q, k, v, mask)
        
        scaled_attention = tf.transpose(scaled_attention, perm=[0, 2, 1, 3])
        concat_attention = tf.reshape(scaled_attention, (batch_size, -1, self.d_model))
        
        output = self.dense(concat_attention)
        
        return output

def scaled_dot_product_attention(q, k, v, mask):
    """스케일드 닷 프로덕트 어텐션"""
    matmul_qk = tf.matmul(q, k, transpose_b=True)
    
    dk = tf.cast(tf.shape(k)[-1], tf.float32)
    scaled_attention_logits = matmul_qk / tf.math.sqrt(dk)
    
    if mask is not None:
        scaled_attention_logits += (mask * -1e9)
    
    attention_weights = tf.nn.softmax(scaled_attention_logits, axis=-1)
    output = tf.matmul(attention_weights, v)
    
    return output

class TransformerPredictor:
    """Transformer 기반 가격 예측 모델"""
    
    def __init__(self, d_model: int = 128, num_heads: int = 8, num_layers: int = 4,
                 sequence_length: int = 60, prediction_horizon: int = 1):
        self.d_model = d_model
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.feature_columns = [
            'open', 'high', 'low', 'close', 'volume',
            'rsi', 'macd', 'bollinger_upper', 'bollinger_lower',
            'sma_20', 'sma_50', 'ema_12', 'ema_26'
        ]
        
        logger.info(f"Initialized Transformer predictor: d_model={d_model}, heads={num_heads}")
    
    def positional_encoding(self, position, d_model):
        """포지셔널 인코딩"""
        angle_rads = self.get_angles(np.arange(position)[:, np.newaxis],
                                   np.arange(d_model)[np.newaxis, :],
                                   d_model)
        
        angle_rads[:, 0::2] = np.sin(angle_rads[:, 0::2])
        angle_rads[:, 1::2] = np.cos(angle_rads[:, 1::2])
        
        pos_encoding = angle_rads[np.newaxis, ...]
        
        return tf.cast(pos_encoding, dtype=tf.float32)
    
    def get_angles(self, pos, i, d_model):
        angle_rates = 1 / np.power(10000, (2 * (i//2)) / np.float32(d_model))
        return pos * angle_rates
    
    def build_model(self, input_shape: Tuple[int, int]) -> tf.keras.Model:
        """Transformer 모델 구축"""
        inputs = layers.Input(shape=input_shape)
        
        # 임베딩 레이어
        embedding = layers.Dense(self.d_model)(inputs)
        
        # 포지셔널 인코딩
        pos_encoding = self.positional_encoding(input_shape[0], self.d_model)
        embedding += pos_encoding
        
        # Transformer 블록
        x = embedding
        for _ in range(self.num_layers):
            # 멀티헤드 어텐션
            attention_output = MultiHeadAttention(self.d_model, self.num_heads)(
                x, x, x, mask=None
            )
            x = layers.LayerNormalization(epsilon=1e-6)(x + attention_output)
            
            # 피드포워드 네트워크
            ffn_output = layers.Dense(self.d_model * 4, activation='relu')(x)
            ffn_output = layers.Dense(self.d_model)(ffn_output)
            x = layers.LayerNormalization(epsilon=1e-6)(x + ffn_output)
        
        # 출력 레이어
        x = layers.GlobalAveragePooling1D()(x)
        x = layers.Dropout(0.1)(x)
        x = layers.Dense(64, activation='relu')(x)
        x = layers.Dropout(0.1)(x)
        outputs = layers.Dense(self.prediction_horizon)(x)
        
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        
        # 모델 컴파일
        model.compile(
            optimizer=Adam(learning_rate=0.0001),
            loss='mean_squared_error',
            metrics=['mae']
        )
        
        logger.info("Transformer model built successfully")
        return model
    
    def prepare_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """데이터 준비"""
        try:
            # 특성 선택
            features = data[self.feature_columns].values
            
            # 정규화
            scaled_features = self.scaler.fit_transform(features)
            
            # 시퀀스 데이터 생성
            X, y = [], []
            
            for i in range(self.sequence_length, len(scaled_features) - self.prediction_horizon + 1):
                X.append(scaled_features[i-self.sequence_length:i])
                y.append(scaled_features[i:i+self.prediction_horizon, 3])  # close price
            
            X = np.array(X)
            y = np.array(y)
            
            logger.info(f"Prepared data: X shape {X.shape}, y shape {y.shape}")
            return X, y
            
        except Exception as e:
            logger.error(f"Data preparation failed: {e}")
            raise
    
    def train(self, data: pd.DataFrame, epochs: int = 100, batch_size: int = 32,
              validation_split: float = 0.2) -> Dict[str, List[float]]:
        """모델 학습"""
        try:
            # 데이터 준비
            X, y = self.prepare_data(data)
            
            # 모델 구축
            self.model = self.build_model((X.shape[1], X.shape[2]))
            
            # 조기 종료 콜백
            early_stopping = tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True
            )
            
            # 학습률 스케줄링
            lr_scheduler = tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7
            )
            
            # 학습
            history = self.model.fit(
                X, y,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=validation_split,
                callbacks=[early_stopping, lr_scheduler],
                verbose=1
            )
            
            logger.info("Transformer model training completed")
            return history.history
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """가격 예측"""
        try:
            if self.model is None:
                raise ValueError("Model not trained. Call train() first.")
            
            # 데이터 준비
            features = data[self.feature_columns].values
            scaled_features = self.scaler.transform(features)
            
            # 예측을 위한 시퀀스 생성
            last_sequence = scaled_features[-self.sequence_length:]
            X_pred = last_sequence.reshape(1, self.sequence_length, len(self.feature_columns))
            
            # 예측
            scaled_prediction = self.model.predict(X_pred)
            
            # 역정규화
            prediction = self.scaler.inverse_transform(
                np.zeros((1, len(self.feature_columns)))
            )
            prediction[0, 3] = scaled_prediction[0, 0]  # close price
            
            logger.info(f"Transformer prediction completed: {prediction[0, 3]}")
            return prediction[0, 3]
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
```

## 🔧 **강화학습 거래 에이전트**

### 📦 **Q-Learning 거래 에이전트**

```python
# ai-ml-system/reinforcement-learning/q-learning/trading_agent.py
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
import random

logger = logging.getLogger(__name__)

@dataclass
class TradingState:
    """거래 상태"""
    position: float  # 현재 포지션 (-1: 숏, 0: 중립, 1: 롱)
    cash: float     # 현금
    shares: float   # 보유 주식 수
    price: float    # 현재 가격
    timestamp: int  # 시간 스탬프

@dataclass
class TradingAction:
    """거래 액션"""
    action: int     # 0: 홀드, 1: 매수, 2: 매도
    amount: float   # 거래량

class QLearningTradingAgent:
    """Q-Learning 기반 거래 에이전트"""
    
    def __init__(self, state_size: int, action_size: int, learning_rate: float = 0.1,
                 discount_factor: float = 0.95, epsilon: float = 0.1):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        
        # Q-테이블 초기화
        self.q_table = {}
        
        # 거래 파라미터
        self.initial_cash = 10000
        self.commission = 0.001  # 0.1% 수수료
        
        logger.info(f"Initialized Q-Learning agent: states={state_size}, actions={action_size}")
    
    def get_state_key(self, state: TradingState) -> str:
        """상태를 키로 변환"""
        # 상태를 이산화
        position_bin = int(state.position * 2)  # -2, -1, 0, 1, 2
        cash_bin = int(state.cash / 1000)       # 1000 단위로 이산화
        price_bin = int(state.price / 10)       # 10 단위로 이산화
        
        return f"{position_bin}_{cash_bin}_{price_bin}"
    
    def get_action(self, state: TradingState) -> TradingAction:
        """액션 선택 (ε-greedy 정책)"""
        state_key = self.get_state_key(state)
        
        # Q-테이블에 상태가 없으면 초기화
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        
        # ε-greedy 정책
        if random.random() < self.epsilon:
            # 탐험: 랜덤 액션
            action = random.randint(0, self.action_size - 1)
        else:
            # 활용: 최적 액션
            action = np.argmax(self.q_table[state_key])
        
        # 액션을 거래량으로 변환
        amount = self._action_to_amount(action, state)
        
        return TradingAction(action=action, amount=amount)
    
    def _action_to_amount(self, action: int, state: TradingState) -> float:
        """액션을 거래량으로 변환"""
        if action == 0:  # 홀드
            return 0.0
        elif action == 1:  # 매수
            # 현금의 20% 매수
            return min(state.cash * 0.2 / state.price, state.cash / state.price)
        elif action == 2:  # 매도
            # 보유 주식의 20% 매도
            return state.shares * 0.2
        else:
            return 0.0
    
    def execute_trade(self, state: TradingState, action: TradingAction) -> Tuple[TradingState, float]:
        """거래 실행"""
        new_state = TradingState(
            position=state.position,
            cash=state.cash,
            shares=state.shares,
            price=state.price,
            timestamp=state.timestamp + 1
        )
        
        reward = 0.0
        
        if action.action == 1:  # 매수
            if action.amount > 0 and new_state.cash >= action.amount * new_state.price:
                cost = action.amount * new_state.price * (1 + self.commission)
                new_state.cash -= cost
                new_state.shares += action.amount
                new_state.position = 1 if new_state.shares > 0 else 0
                
        elif action.action == 2:  # 매도
            if action.amount > 0 and new_state.shares >= action.amount:
                revenue = action.amount * new_state.price * (1 - self.commission)
                new_state.cash += revenue
                new_state.shares -= action.amount
                new_state.position = -1 if new_state.shares < 0 else 0
        
        # 보상 계산 (포트폴리오 가치 변화)
        old_value = state.cash + state.shares * state.price
        new_value = new_state.cash + new_state.shares * new_state.price
        reward = (new_value - old_value) / old_value
        
        return new_state, reward
    
    def update_q_value(self, state: TradingState, action: TradingAction, 
                      reward: float, next_state: TradingState):
        """Q-값 업데이트"""
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        
        # Q-테이블 초기화
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.action_size)
        
        # Q-러닝 업데이트 공식
        current_q = self.q_table[state_key][action.action]
        max_next_q = np.max(self.q_table[next_state_key])
        
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state_key][action.action] = new_q
    
    def train(self, price_data: pd.DataFrame, episodes: int = 1000) -> List[float]:
        """에이전트 학습"""
        episode_rewards = []
        
        for episode in range(episodes):
            # 초기 상태
            state = TradingState(
                position=0,
                cash=self.initial_cash,
                shares=0,
                price=price_data.iloc[0]['close'],
                timestamp=0
            )
            
            total_reward = 0.0
            
            for i in range(len(price_data) - 1):
                # 현재 가격 업데이트
                state.price = price_data.iloc[i]['close']
                
                # 액션 선택
                action = self.get_action(state)
                
                # 거래 실행
                next_state, reward = self.execute_trade(state, action)
                
                # 다음 가격으로 업데이트
                next_state.price = price_data.iloc[i + 1]['close']
                
                # Q-값 업데이트
                self.update_q_value(state, action, reward, next_state)
                
                state = next_state
                total_reward += reward
            
            episode_rewards.append(total_reward)
            
            if episode % 100 == 0:
                avg_reward = np.mean(episode_rewards[-100:])
                logger.info(f"Episode {episode}, Average Reward: {avg_reward:.4f}")
        
        logger.info("Q-Learning training completed")
        return episode_rewards
    
    def get_portfolio_value(self, state: TradingState) -> float:
        """포트폴리오 가치 계산"""
        return state.cash + state.shares * state.price
    
    def save_q_table(self, filepath: str):
        """Q-테이블 저장"""
        try:
            np.save(filepath, self.q_table)
            logger.info(f"Q-table saved to: {filepath}")
        except Exception as e:
            logger.error(f"Q-table save failed: {e}")
            raise
    
    def load_q_table(self, filepath: str):
        """Q-테이블 로드"""
        try:
            self.q_table = np.load(filepath, allow_pickle=True).item()
            logger.info(f"Q-table loaded from: {filepath}")
        except Exception as e:
            logger.error(f"Q-table load failed: {e}")
            raise
```

## 🔧 **감정 분석 시스템**

### 📦 **뉴스 감정 분석**

```python
# ai-ml-system/sentiment-analysis/news-analysis/news_sentiment_analyzer.py
import pandas as pd
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, List, Tuple, Optional
import requests
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class NewsSentimentAnalyzer:
    """뉴스 감정 분석기"""
    
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.sentiment_pipeline = None
        
        # 감정 레이블
        self.sentiment_labels = ['negative', 'neutral', 'positive']
        
        logger.info(f"Initialized news sentiment analyzer with model: {model_name}")
    
    def load_model(self):
        """모델 로드"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer
            )
            
            logger.info("Sentiment analysis model loaded successfully")
            
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            raise
    
    def analyze_text(self, text: str) -> Dict[str, float]:
        """텍스트 감정 분석"""
        try:
            if self.sentiment_pipeline is None:
                self.load_model()
            
            # 텍스트 전처리
            cleaned_text = self._preprocess_text(text)
            
            # 감정 분석
            result = self.sentiment_pipeline(cleaned_text)
            
            # 결과 정규화
            sentiment_scores = {
                'negative': 0.0,
                'neutral': 0.0,
                'positive': 0.0
            }
            
            for item in result:
                label = item['label'].lower()
                score = item['score']
                sentiment_scores[label] = score
            
            # 종합 감정 점수 (-1 ~ 1)
            composite_score = (
                sentiment_scores['positive'] - sentiment_scores['negative']
            )
            
            sentiment_scores['composite'] = composite_score
            
            logger.debug(f"Sentiment analysis completed: {composite_score:.3f}")
            return sentiment_scores
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                'negative': 0.33,
                'neutral': 0.34,
                'positive': 0.33,
                'composite': 0.0
            }
    
    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        # 특수 문자 제거
        import re
        text = re.sub(r'[^\w\s]', '', text)
        
        # 여러 공백을 하나로
        text = re.sub(r'\s+', ' ', text)
        
        # 대소문자 정규화
        text = text.lower().strip()
        
        return text
    
    def fetch_crypto_news(self, symbol: str, hours: int = 24) -> List[Dict[str, any]]:
        """암호화폐 뉴스 수집"""
        try:
            # NewsAPI 사용 (실제 구현에서는 API 키 필요)
            api_key = "YOUR_NEWS_API_KEY"
            url = f"https://newsapi.org/v2/everything"
            
            # 검색 쿼리
            query = f"{symbol} cryptocurrency"
            
            # 시간 범위
            from_date = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d')
            
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'publishedAt',
                'apiKey': api_key,
                'language': 'en'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                # 뉴스 데이터 정리
                news_data = []
                for article in articles:
                    news_item = {
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'content': article.get('content', ''),
                        'published_at': article.get('publishedAt', ''),
                        'source': article.get('source', {}).get('name', ''),
                        'url': article.get('url', '')
                    }
                    news_data.append(news_item)
                
                logger.info(f"Fetched {len(news_data)} news articles for {symbol}")
                return news_data
                
            else:
                logger.error(f"News API request failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"News fetching failed: {e}")
            return []
    
    def analyze_news_sentiment(self, symbol: str, hours: int = 24) -> Dict[str, any]:
        """뉴스 감정 분석 실행"""
        try:
            # 뉴스 수집
            news_articles = self.fetch_crypto_news(symbol, hours)
            
            if not news_articles:
                return {
                    'symbol': symbol,
                    'sentiment_score': 0.0,
                    'confidence': 0.0,
                    'article_count': 0,
                    'timestamp': datetime.now().isoformat()
                }
            
            # 각 기사 감정 분석
            sentiment_scores = []
            for article in news_articles:
                # 제목과 설명 결합
                text = f"{article['title']} {article['description']}"
                
                sentiment = self.analyze_text(text)
                sentiment_scores.append(sentiment['composite'])
            
            # 종합 감정 점수 계산
            avg_sentiment = np.mean(sentiment_scores)
            sentiment_std = np.std(sentiment_scores)
            confidence = 1.0 - sentiment_std  # 표준편차가 작을수록 신뢰도 높음
            
            result = {
                'symbol': symbol,
                'sentiment_score': avg_sentiment,
                'confidence': max(0.0, min(1.0, confidence)),
                'article_count': len(news_articles),
                'sentiment_distribution': {
                    'negative': len([s for s in sentiment_scores if s < -0.1]),
                    'neutral': len([s for s in sentiment_scores if -0.1 <= s <= 0.1]),
                    'positive': len([s for s in sentiment_scores if s > 0.1])
                },
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"News sentiment analysis completed for {symbol}: {avg_sentiment:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"News sentiment analysis failed: {e}")
            return {
                'symbol': symbol,
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'article_count': 0,
                'timestamp': datetime.now().isoformat()
            }
```

## 🎯 **다음 단계**

### 📋 **완료된 작업**
- ✅ LSTM 기반 가격 예측 모델
- ✅ Transformer 기반 예측 모델
- ✅ Q-Learning 거래 에이전트
- ✅ 뉴스 감정 분석 시스템

### 🔄 **진행 중인 작업**
- 🔄 DDPG 강화학습 에이전트
- 🔄 소셜 미디어 감정 분석
- 🔄 포트폴리오 최적화

### ⏳ **다음 단계**
1. **Phase 3.1 예측 모델** 문서 생성
2. **Phase 3.2 강화학습** 문서 생성
3. **Phase 3.3 감정 분석** 문서 생성

---

**마지막 업데이트**: 2024-01-31
**다음 업데이트**: 2024-02-01 (Phase 3.1 예측 모델)
**AI/ML 목표**: > 65% 예측 정확도, > 20% 연간 수익률, > 2.0 샤프 비율
**모델 성능**: < 2시간 학습 시간, 실시간 예측 < 1초 