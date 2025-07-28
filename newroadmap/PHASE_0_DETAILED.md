# Phase 0: 기본 환경 상세 구현 가이드

## 🎯 Phase 0 목표
- Python 개발 환경 구축
- Binance API 연동
- 기본 프로젝트 구조 생성
- 환경 변수 설정
- 로깅 시스템 구축
- **50개 코인 리스트 등록 및 설정**

## 📋 구현 체크리스트

### **환경 설정**
- [x] Python 3.8+ 설치 확인 (완료: 2024-07-27)
- [x] 가상환경 생성 및 활성화 (완료: 2024-07-27)
- [x] 기본 패키지 설치 (완료: 2024-07-27)
- [x] 프로젝트 디렉토리 구조 생성 (완료: 2024-07-27)

### **API 설정**
- [x] Binance 계정 생성 (완료: 2024-07-27)
- [x] API 키 발급 (읽기/거래 권한) (완료: 2024-07-27)
- [x] API 키 테스트 (완료: 2024-07-27)
- [x] 환경 변수 설정 (완료: 2024-07-27)

### **기본 구조**
- [x] 프로젝트 파일 구조 생성 (완료: 2024-07-27)
- [x] 기본 클래스 구조 작성 (완료: 2024-07-27)
- [x] 설정 파일 생성 (완료: 2024-07-27)
- [x] 로깅 시스템 구현 (완료: 2024-07-27)
- [x] **50개 코인 리스트 등록** (완료: 2024-07-27)
- [x] **코인별 설정 파일 생성** (완료: 2024-07-27)
- [x] **SQLite 데이터베이스** (완료: 2024-07-27)
- [x] **단일 봇 클래스** (완료: 2024-07-27)

## 🏗️ 프로젝트 구조

### **디렉토리 구조**
```
trading_bot/
├── .env.example          # 환경 변수 샘플
├── .env                  # 실제 환경 변수 (gitignore)
├── requirements.txt      # Python 의존성
├── main.py              # 메인 실행 파일
├── selected_coins.json   # 선정된 50개 코인 리스트
├── selected_coins.csv    # 코인 상세 정보
├── bot/
│   ├── __init__.py
│   ├── integrated_bot.py
│   └── config.py
├── data/
│   ├── __init__.py
│   ├── collector.py
│   └── database.py
├── analysis/
│   ├── __init__.py
│   ├── technical.py
│   ├── sentiment.py
│   └── ml.py
├── trading/
│   ├── __init__.py
│   ├── executor.py
│   └── risk_manager.py
└── utils/
    ├── __init__.py
    ├── logger.py
    └── helpers.py
├── config/
    ├── __init__.py
    ├── coins_config.py    # 50개 코인 설정
    └── trading_config.py  # 거래 설정
```

### **파일별 역할**
- **main.py**: 봇 실행 진입점
- **bot/**: 봇 핵심 로직
- **data/**: 데이터 수집 및 저장
- **analysis/**: 분석 모듈들
- **trading/**: 거래 실행 및 리스크 관리
- **utils/**: 공통 유틸리티
- **config/**: 설정 파일들 (50개 코인 포함)

## 💻 구현 예시 코드

### **1. requirements.txt**
```txt
# API 및 데이터 처리
python-binance==1.0.19
websocket-client==1.6.4
requests==2.31.0

# 데이터 분석
pandas==2.1.4
numpy==1.24.3
scikit-learn==1.3.2

# 데이터베이스
sqlite3

# 로깅 및 유틸리티
python-dotenv==1.0.0
logging

# 추가 분석 도구
ta==0.10.2  # 기술적 분석
```

### **2. .env.example**
```env
# ========================================
# Binance API 설정
# ========================================
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here
BINANCE_TESTNET=false

# ========================================
# 데이터베이스 설정
# ========================================
DATABASE_PATH=./data/trading_bot.db

# ========================================
# 로깅 설정
# ========================================
LOG_LEVEL=INFO
LOG_FILE=./logs/trading_bot.log

# ========================================
# 거래 설정
# ========================================
TRADING_SYMBOL=BTCUSDT
INITIAL_CAPITAL=3000000  # 3M KRW
MAX_POSITION_SIZE=0.1    # 10% per trade
STOP_LOSS_PERCENT=0.02   # 2%
TAKE_PROFIT_PERCENT=0.04 # 4%

# ========================================
# 알림 설정
# ========================================
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# ========================================
# 개발 환경 설정
# ========================================
DEBUG_MODE=true
BACKTEST_MODE=false

# ========================================
# 50개 코인 설정
# ========================================
SELECTED_COINS_FILE=./selected_coins.json
MAX_COINS=50

### **3. config/coins_config.py**
```python
#!/usr/bin/env python3
"""
50개 코인 설정 파일
"""

import json
import os
from typing import List, Dict, Any

class CoinsConfig:
    """50개 코인 설정 관리 클래스"""
    
    def __init__(self, config_file: str = "selected_coins.json"):
        self.config_file = config_file
        self.coins = self.load_selected_coins()
    
    def load_selected_coins(self) -> List[str]:
        """선정된 50개 코인 로드"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('coins', [])
        except FileNotFoundError:
            print(f"⚠️ {self.config_file} 파일을 찾을 수 없습니다.")
            return []
        except Exception as e:
            print(f"❌ 코인 설정 로드 실패: {e}")
            return []
    
    def get_coin_details(self) -> List[Dict[str, Any]]:
        """코인 상세 정보 조회"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('details', [])
        except Exception as e:
            print(f"❌ 코인 상세 정보 로드 실패: {e}")
            return []
    
    def get_top_coins(self, count: int = 10) -> List[str]:
        """상위 N개 코인 조회"""
        return self.coins[:count]
    
    def get_coin_by_index(self, index: int) -> str:
        """인덱스로 코인 조회"""
        if 0 <= index < len(self.coins):
            return self.coins[index]
        return None
    
    def get_total_coins(self) -> int:
        """총 코인 수 조회"""
        return len(self.coins)
    
    def print_coins_summary(self):
        """코인 요약 출력"""
        print(f"📊 총 {len(self.coins)}개 코인 등록됨")
        print("상위 10개 코인:")
        for i, coin in enumerate(self.coins[:10], 1):
            print(f"  {i:2d}. {coin.replace('USDT', '')}")

# 사용 예시
if __name__ == "__main__":
    config = CoinsConfig()
    config.print_coins_summary()
```

### **4. main.py**
```python
#!/usr/bin/env python3
"""
트레이딩 봇 메인 실행 파일
"""

import os
import sys
import logging
from dotenv import load_dotenv
from bot.integrated_bot import IntegratedTradingBot
from utils.logger import setup_logger
from bot.config import Config

def main():
    """메인 실행 함수"""
    try:
        # 1. 환경 변수 로드
        load_dotenv()
        
        # 2. 로거 설정
        logger = setup_logger()
        logger.info("트레이딩 봇 시작")
        
        # 3. 설정 로드
        config = Config()
        logger.info(f"설정 로드 완료: {config.trading_symbol}")
        
        # 3-1. 50개 코인 설정 로드
        from config.coins_config import CoinsConfig
        coins_config = CoinsConfig()
        logger.info(f"50개 코인 설정 로드 완료: {coins_config.get_total_coins()}개")
        
        # 4. 봇 초기화 (50개 코인 설정 포함)
        bot = IntegratedTradingBot(config, coins_config)
        logger.info("봇 초기화 완료")
        
        # 5. 봇 실행
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
    except Exception as e:
        logger.error(f"오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### **4. bot/config.py**
```python
"""
봇 설정 관리 클래스
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class Config:
    """봇 설정 클래스"""
    
    # Binance API 설정
    binance_api_key: str
    binance_secret_key: str
    binance_testnet: bool
    
    # 데이터베이스 설정
    database_path: str
    
    # 로깅 설정
    log_level: str
    log_file: str
    
    # 거래 설정
    trading_symbol: str
    initial_capital: float
    max_position_size: float
    stop_loss_percent: float
    take_profit_percent: float
    
    # 알림 설정
    telegram_bot_token: Optional[str]
    telegram_chat_id: Optional[str]
    
    # 개발 환경 설정
    debug_mode: bool
    backtest_mode: bool
    
    def __init__(self):
        """환경 변수에서 설정 로드"""
        # Binance API 설정
        self.binance_api_key = os.getenv('BINANCE_API_KEY', '')
        self.binance_secret_key = os.getenv('BINANCE_SECRET_KEY', '')
        self.binance_testnet = os.getenv('BINANCE_TESTNET', 'false').lower() == 'true'
        
        # 데이터베이스 설정
        self.database_path = os.getenv('DATABASE_PATH', './data/trading_bot.db')
        
        # 로깅 설정
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', './logs/trading_bot.log')
        
        # 거래 설정
        self.trading_symbol = os.getenv('TRADING_SYMBOL', 'BTCUSDT')
        self.initial_capital = float(os.getenv('INITIAL_CAPITAL', '3000000'))
        self.max_position_size = float(os.getenv('MAX_POSITION_SIZE', '0.1'))
        self.stop_loss_percent = float(os.getenv('STOP_LOSS_PERCENT', '0.02'))
        self.take_profit_percent = float(os.getenv('TAKE_PROFIT_PERCENT', '0.04'))
        
        # 알림 설정
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # 개발 환경 설정
        self.debug_mode = os.getenv('DEBUG_MODE', 'true').lower() == 'true'
        self.backtest_mode = os.getenv('BACKTEST_MODE', 'false').lower() == 'true'
    
    def validate(self) -> bool:
        """설정 유효성 검증"""
        required_fields = [
            self.binance_api_key,
            self.binance_secret_key,
            self.trading_symbol
        ]
        
        if not all(required_fields):
            return False
        
        if self.initial_capital <= 0:
            return False
        
        if not (0 < self.max_position_size <= 1):
            return False
        
        return True
    
    def __str__(self) -> str:
        """설정 정보 문자열 반환"""
        return f"Config(trading_symbol={self.trading_symbol}, initial_capital={self.initial_capital})"
```

### **5. utils/logger.py**
```python
"""
로깅 시스템 설정
"""

import logging
import os
from datetime import datetime

def setup_logger(name: str = 'trading_bot', log_file: str = None) -> logging.Logger:
    """로거 설정"""
    
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 이미 핸들러가 설정되어 있으면 추가하지 않음
    if logger.handlers:
        return logger
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (선택사항)
    if log_file:
        # 로그 디렉토리 생성
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = 'trading_bot') -> logging.Logger:
    """로거 가져오기"""
    return logging.getLogger(name)
```

### **6. bot/integrated_bot.py**
```python
"""
통합 트레이딩 봇 클래스
"""

import logging
from typing import Dict, Any, Optional
from bot.config import Config
from utils.logger import get_logger

class IntegratedTradingBot:
    """통합 트레이딩 봇 클래스"""
    
    def __init__(self, config: Config):
        """봇 초기화"""
        self.config = config
        self.logger = get_logger('IntegratedTradingBot')
        
        # 상태 변수
        self.is_running = False
        self.current_position = 0.0
        self.total_pnl = 0.0
        
        # 컴포넌트 초기화 (Phase 2에서 구현)
        self.data_collector = None
        self.technical_analyzer = None
        self.sentiment_analyzer = None
        self.ml_predictor = None
        self.order_executor = None
        self.risk_manager = None
        self.performance_tracker = None
        
        self.logger.info("IntegratedTradingBot 초기화 완료")
    
    def initialize_components(self):
        """컴포넌트 초기화 (Phase 2에서 구현)"""
        self.logger.info("컴포넌트 초기화 시작")
        
        # Phase 2에서 구현할 컴포넌트들
        # self.data_collector = DataCollector(self.config)
        # self.technical_analyzer = TechnicalAnalyzer()
        # self.sentiment_analyzer = SentimentAnalyzer()
        # self.ml_predictor = MLPredictor()
        # self.order_executor = OrderExecutor(self.config)
        # self.risk_manager = RiskManager(self.config)
        # self.performance_tracker = PerformanceTracker()
        
        self.logger.info("컴포넌트 초기화 완료")
    
    def run(self):
        """봇 실행 (Phase 4에서 구현)"""
        self.logger.info("봇 실행 시작")
        self.is_running = True
        
        try:
            # Phase 4에서 구현할 실제 거래 로직
            self.logger.info("봇이 실행 중입니다... (Phase 4에서 실제 구현)")
            
            # 임시로 무한 루프 (Phase 4에서 실제 로직으로 교체)
            while self.is_running:
                import time
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("봇 실행 중단")
        except Exception as e:
            self.logger.error(f"봇 실행 중 오류: {e}")
        finally:
            self.is_running = False
            self.logger.info("봇 실행 종료")
    
    def stop(self):
        """봇 중지"""
        self.logger.info("봇 중지 요청")
        self.is_running = False
    
    def get_status(self) -> Dict[str, Any]:
        """봇 상태 반환"""
        return {
            'is_running': self.is_running,
            'current_position': self.current_position,
            'total_pnl': self.total_pnl,
            'trading_symbol': self.config.trading_symbol
        }
```

## ✅ 테스트 방법

### **1. 환경 설정 테스트**
```python
# test_environment.py
import os
import sys
from dotenv import load_dotenv

def test_environment():
    """환경 설정 테스트"""
    print("=== 환경 설정 테스트 ===")
    
    # 1. Python 버전 확인
    print(f"Python 버전: {sys.version}")
    
    # 2. 환경 변수 로드 테스트
    load_dotenv()
    api_key = os.getenv('BINANCE_API_KEY')
    print(f"API 키 설정: {'✅' if api_key else '❌'}")
    
    # 3. 필수 패키지 확인
    required_packages = ['pandas', 'numpy', 'requests']
    for package in required_packages:
        try:
            __import__(package)
            print(f"{package}: ✅")
        except ImportError:
            print(f"{package}: ❌")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_environment()
```

### **2. 설정 파일 테스트**
```python
# test_config.py
from bot.config import Config

def test_config():
    """설정 파일 테스트"""
    print("=== 설정 파일 테스트 ===")
    
    config = Config()
    
    # 설정 유효성 검증
    is_valid = config.validate()
    print(f"설정 유효성: {'✅' if is_valid else '❌'}")
    
    # 주요 설정 출력
    print(f"거래 심볼: {config.trading_symbol}")
    print(f"초기 자본: {config.initial_capital:,} KRW")
    print(f"최대 포지션 크기: {config.max_position_size * 100}%")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_config()
```

### **3. 봇 기본 구조 테스트**
```python
# test_bot_structure.py
from bot.config import Config
from bot.integrated_bot import IntegratedTradingBot

def test_bot_structure():
    """봇 기본 구조 테스트"""
    print("=== 봇 기본 구조 테스트 ===")
    
    # 설정 로드
    config = Config()
    
    # 봇 초기화
    bot = IntegratedTradingBot(config)
    
    # 상태 확인
    status = bot.get_status()
    print(f"봇 상태: {status}")
    
    # 컴포넌트 초기화 테스트
    bot.initialize_components()
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_bot_structure()
```

## 🚀 실행 방법

### **1. 환경 설정**
```bash
# 1. 가상환경 생성
python -m venv venv

# 2. 가상환경 활성화 (Windows)
venv\Scripts\activate

# 3. 가상환경 활성화 (Linux/Mac)
source venv/bin/activate

# 4. 패키지 설치
pip install -r requirements.txt
```

### **2. 환경 변수 설정**
```bash
# 1. .env.example을 .env로 복사
cp .env.example .env

# 2. .env 파일 편집하여 실제 값 입력
# BINANCE_API_KEY=your_actual_api_key
# BINANCE_SECRET_KEY=your_actual_secret_key
```

### **3. 테스트 실행**
```bash
# 환경 설정 테스트
python test_environment.py

# 설정 파일 테스트
python test_config.py

# 봇 구조 테스트
python test_bot_structure.py
```

### **4. 봇 실행**
```bash
# 메인 봇 실행
python main.py
```

## 📊 Phase 0 완료 기준

### **✅ 완료 체크리스트**
- [ ] Python 가상환경 설정 완료
- [ ] Binance API 키 발급 및 연동 완료
- [ ] 프로젝트 디렉토리 구조 생성 완료
- [ ] 기본 클래스 구조 작성 완료
- [ ] 설정 파일 (.env) 생성 완료
- [ ] 로깅 시스템 구현 완료
- [ ] 모든 테스트 통과

### **🎯 성공 지표**
- **환경 설정**: 모든 패키지 설치 완료
- **API 연동**: Binance API 연결 성공
- **기본 구조**: 봇 클래스 초기화 성공
- **로깅**: 로그 파일 생성 및 기록 성공

## 🚀 다음 단계 (Phase 1)

Phase 0이 완료되면 다음 단계로 진행합니다:

1. **데이터 수집 모듈 구현**
2. **Binance 과거 데이터 수집**
3. **실시간 WebSocket 연결**
4. **기본 감정 데이터 수집**

Phase 1 상세 가이드는 `PHASE_1_DETAILED.md`에서 확인할 수 있습니다. 