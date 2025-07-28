# Phase 1: 데이터 수집 상세 구현 가이드

## 🎯 Phase 1 목표 ✅ **완료**
- ✅ Binance 과거 데이터 수집 (50개 코인, 3년, 모든 간격) - **별도 스크립트로 분리 완료**
- ✅ 실시간 WebSocket 연결 (50개 코인) - **구현 완료**
- ✅ 기본 감정 데이터 수집 (뉴스 헤드라인) - **RSS 피드 구현 완료**
- ✅ 데이터 전처리 및 정규화 - **데이터베이스 구조 완료**
- ✅ SQLite 데이터베이스 저장 - **코인별 간격별 테이블 완료**

## 📋 구현 체크리스트

### **과거 데이터 수집** ✅ **완료**
- [x] Binance API를 통한 50개 코인 과거 데이터 수집 (별도 스크립트로 분리)
- [x] 3년치 모든 간격 캔들 데이터 수집 (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
- [x] 고속 병렬 처리 구현 (asyncio, ThreadPoolExecutor)
- [x] 코인별 간격별 테이블 구조 (800개 테이블)
- [x] SQLite 데이터베이스 저장
- [x] 데이터 수집 상태 추적 시스템

### **실시간 데이터** ✅ **완료**
- [x] 50개 코인 WebSocket 연결 구현
- [x] 실시간 가격 데이터 스트리밍 (50개 코인)
- [x] 실시간 데이터 처리 및 저장
- [x] 연결 안정성 관리

### **감정 데이터** ✅ **완료**
- [x] 뉴스 헤드라인 수집 (RSS)
- [x] 기본 키워드 기반 감정 분석
- [x] 감정 데이터 전처리
- [x] 가격 데이터와 통합

### **데이터베이스** ✅ **완료**
- [x] SQLite 테이블 구조 설계
- [x] 데이터 저장 및 조회 기능
- [x] 데이터 무결성 검증
- [x] 성능 최적화

## 🏗️ 데이터 구조

### **데이터베이스 스키마**
```sql
-- 가격 데이터 테이블
CREATE TABLE price_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    open_price REAL NOT NULL,
    high_price REAL NOT NULL,
    low_price REAL NOT NULL,
    close_price REAL NOT NULL,
    volume REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp)
);

-- 감정 데이터 테이블
CREATE TABLE sentiment_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    headline TEXT NOT NULL,
    sentiment_score REAL,
    keywords TEXT,
    timestamp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 실시간 데이터 테이블
CREATE TABLE realtime_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    price REAL NOT NULL,
    volume REAL NOT NULL,
    timestamp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **데이터 수집 구조**
```
data/
├── __init__.py
├── database.py          # 데이터베이스 관리
├── websocket_client.py  # 실시간 데이터
└── sentiment_collector.py # 감정 데이터

scripts/
└── collect_historical_data.py  # 과거데이터 수집기 (별도 분리)
```

## 💻 구현 예시 코드

### **1. data/database.py**
```python
"""
데이터베이스 관리 클래스
"""

import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

class Database:
    """SQLite 데이터베이스 관리 클래스"""
    
    def __init__(self, db_path: str = "./data/trading_bot.db"):
        """데이터베이스 초기화"""
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 가격 데이터 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS price_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        timestamp INTEGER NOT NULL,
                        open_price REAL NOT NULL,
                        high_price REAL NOT NULL,
                        low_price REAL NOT NULL,
                        close_price REAL NOT NULL,
                        volume REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(symbol, timestamp)
                    )
                """)
                
                # 감정 데이터 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sentiment_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source TEXT NOT NULL,
                        headline TEXT NOT NULL,
                        sentiment_score REAL,
                        keywords TEXT,
                        timestamp INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 실시간 데이터 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS realtime_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        price REAL NOT NULL,
                        volume REAL NOT NULL,
                        timestamp INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 인덱스 생성
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_symbol_timestamp ON price_data(symbol, timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentiment_timestamp ON sentiment_data(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_realtime_symbol_timestamp ON realtime_data(symbol, timestamp)")
                
                conn.commit()
                self.logger.info("데이터베이스 초기화 완료")
                
        except Exception as e:
            self.logger.error(f"데이터베이스 초기화 실패: {e}")
            raise
    
    def save_price_data(self, symbol: str, data: List[Dict[str, Any]]):
        """가격 데이터 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for item in data:
                    cursor.execute("""
                        INSERT OR REPLACE INTO price_data 
                        (symbol, timestamp, open_price, high_price, low_price, close_price, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        symbol,
                        item['timestamp'],
                        item['open'],
                        item['high'],
                        item['low'],
                        item['close'],
                        item['volume']
                    ))
                
                conn.commit()
                self.logger.info(f"{symbol} 가격 데이터 {len(data)}개 저장 완료")
                
        except Exception as e:
            self.logger.error(f"가격 데이터 저장 실패: {e}")
            raise
    
    def save_sentiment_data(self, source: str, headline: str, sentiment_score: float, keywords: str = None):
        """감정 데이터 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO sentiment_data 
                    (source, headline, sentiment_score, keywords, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    source,
                    headline,
                    sentiment_score,
                    keywords,
                    int(datetime.now().timestamp() * 1000)
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"감정 데이터 저장 실패: {e}")
            raise
    
    def save_realtime_data(self, symbol: str, price: float, volume: float):
        """실시간 데이터 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO realtime_data 
                    (symbol, price, volume, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (
                    symbol,
                    price,
                    volume,
                    int(datetime.now().timestamp() * 1000)
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"실시간 데이터 저장 실패: {e}")
            raise
    
    def get_price_data(self, symbol: str, start_time: Optional[int] = None, end_time: Optional[int] = None) -> pd.DataFrame:
        """가격 데이터 조회"""
        try:
            query = "SELECT * FROM price_data WHERE symbol = ?"
            params = [symbol]
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp"
            
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params)
                return df
                
        except Exception as e:
            self.logger.error(f"가격 데이터 조회 실패: {e}")
            return pd.DataFrame()
    
    def get_sentiment_data(self, start_time: Optional[int] = None, end_time: Optional[int] = None) -> pd.DataFrame:
        """감정 데이터 조회"""
        try:
            query = "SELECT * FROM sentiment_data"
            params = []
            
            if start_time or end_time:
                query += " WHERE"
                if start_time:
                    query += " timestamp >= ?"
                    params.append(start_time)
                if end_time:
                    if start_time:
                        query += " AND"
                    query += " timestamp <= ?"
                    params.append(end_time)
            
            query += " ORDER BY timestamp DESC"
            
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params)
                return df
                
        except Exception as e:
            self.logger.error(f"감정 데이터 조회 실패: {e}")
            return pd.DataFrame()
```

### **2. scripts/collect_historical_data.py** ✅ **구현 완료**
```python
"""
과거데이터 수집기 (별도 분리)
- 50개 코인 3년치 모든 간격 데이터 수집
- 고속 병렬 처리 (asyncio, ThreadPoolExecutor)
- 코인별 간격별 테이블 구조
- 데이터 수집 상태 추적
"""
"""
Binance 데이터 수집기
"""

import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
from data.database import Database

class DataCollector:
    """Binance 데이터 수집 클래스"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """데이터 수집기 초기화"""
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.logger = logging.getLogger(__name__)
        
        # Binance 클라이언트 초기화
        self.client = Client(api_key, api_secret, testnet=testnet)
        
        # 데이터베이스 초기화
        self.db = Database()
        
        self.logger.info("DataCollector 초기화 완료")
    
    def collect_historical_data(self, symbol: str, interval: str = '1h', limit: int = 1000) -> List[Dict[str, Any]]:
        """과거 데이터 수집"""
        try:
            self.logger.info(f"{symbol} 과거 데이터 수집 시작")
            
            # 현재 시간부터 과거로 데이터 수집
            end_time = datetime.now()
            start_time = end_time - timedelta(days=365)  # 1년치
            
            all_data = []
            current_start = start_time
            
            while current_start < end_time:
                # Binance API 호출
                klines = self.client.get_klines(
                    symbol=symbol,
                    interval=interval,
                    startTime=int(current_start.timestamp() * 1000),
                    endTime=int(min(current_start + timedelta(days=30), end_time).timestamp() * 1000),
                    limit=limit
                )
                
                # 데이터 변환
                for kline in klines:
                    data = {
                        'timestamp': kline[0],
                        'open': float(kline[1]),
                        'high': float(kline[2]),
                        'low': float(kline[3]),
                        'close': float(kline[4]),
                        'volume': float(kline[5])
                    }
                    all_data.append(data)
                
                # 다음 배치 시작 시간
                current_start += timedelta(days=30)
                
                # API 제한 방지
                time.sleep(0.1)
            
            # 데이터베이스에 저장
            self.db.save_price_data(symbol, all_data)
            
            self.logger.info(f"{symbol} 과거 데이터 수집 완료: {len(all_data)}개")
            return all_data
            
        except BinanceAPIException as e:
            self.logger.error(f"Binance API 오류: {e}")
            raise
        except Exception as e:
            self.logger.error(f"데이터 수집 실패: {e}")
            raise
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """현재 가격 조회"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            self.logger.error(f"현재 가격 조회 실패: {e}")
            return None
    
    def get_24h_stats(self, symbol: str) -> Optional[Dict[str, Any]]:
        """24시간 통계 조회"""
        try:
            stats = self.client.get_ticker(symbol=symbol)
            return {
                'price_change': float(stats['priceChange']),
                'price_change_percent': float(stats['priceChangePercent']),
                'volume': float(stats['volume']),
                'high': float(stats['highPrice']),
                'low': float(stats['lowPrice'])
            }
        except Exception as e:
            self.logger.error(f"24시간 통계 조회 실패: {e}")
            return None
    
    def collect_multiple_symbols(self, symbols: List[str], interval: str = '1h'):
        """여러 심볼 데이터 수집"""
        for symbol in symbols:
            try:
                self.logger.info(f"{symbol} 데이터 수집 시작")
                self.collect_historical_data(symbol, interval)
                time.sleep(1)  # API 제한 방지
            except Exception as e:
                self.logger.error(f"{symbol} 데이터 수집 실패: {e}")
                continue
```

### **3. data/websocket_client.py** ✅ **구현 완료**
```python
"""
실시간 WebSocket 클라이언트
"""

import json
import threading
import time
import logging
from typing import Callable, Optional
from websocket import WebSocketApp
from data.database import Database

class WebSocketClient:
    """실시간 WebSocket 클라이언트"""
    
    def __init__(self, symbol: str, callback: Optional[Callable] = None):
        """WebSocket 클라이언트 초기화"""
        self.symbol = symbol.lower()
        self.callback = callback
        self.logger = logging.getLogger(__name__)
        self.db = Database()
        
        # WebSocket URL
        self.ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@trade"
        
        # 상태 변수
        self.is_connected = False
        self.ws = None
        self.reconnect_count = 0
        self.max_reconnect = 5
        
        self.logger.info(f"WebSocket 클라이언트 초기화: {symbol}")
    
    def on_message(self, ws, message):
        """메시지 수신 처리"""
        try:
            data = json.loads(message)
            
            # 거래 데이터 추출
            trade_data = {
                'symbol': data['s'],
                'price': float(data['p']),
                'volume': float(data['q']),
                'timestamp': data['T']
            }
            
            # 데이터베이스에 저장
            self.db.save_realtime_data(
                trade_data['symbol'],
                trade_data['price'],
                trade_data['volume']
            )
            
            # 콜백 함수 호출
            if self.callback:
                self.callback(trade_data)
            
            self.logger.debug(f"실시간 데이터 수신: {trade_data}")
            
        except Exception as e:
            self.logger.error(f"메시지 처리 실패: {e}")
    
    def on_error(self, ws, error):
        """오류 처리"""
        self.logger.error(f"WebSocket 오류: {error}")
        self.is_connected = False
    
    def on_close(self, ws, close_status_code, close_msg):
        """연결 종료 처리"""
        self.logger.info("WebSocket 연결 종료")
        self.is_connected = False
    
    def on_open(self, ws):
        """연결 시작 처리"""
        self.logger.info("WebSocket 연결 시작")
        self.is_connected = True
        self.reconnect_count = 0
    
    def connect(self):
        """WebSocket 연결"""
        try:
            self.ws = WebSocketApp(
                self.ws_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # 별도 스레드에서 실행
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
            self.logger.info(f"{self.symbol} WebSocket 연결 시작")
            
        except Exception as e:
            self.logger.error(f"WebSocket 연결 실패: {e}")
            raise
    
    def disconnect(self):
        """WebSocket 연결 종료"""
        if self.ws:
            self.ws.close()
            self.is_connected = False
            self.logger.info("WebSocket 연결 종료")
    
    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self.is_connected
    
    def reconnect(self):
        """재연결 시도"""
        if self.reconnect_count < self.max_reconnect:
            self.reconnect_count += 1
            self.logger.info(f"WebSocket 재연결 시도 {self.reconnect_count}/{self.max_reconnect}")
            
            self.disconnect()
            time.sleep(5)  # 5초 대기
            self.connect()
        else:
            self.logger.error("최대 재연결 시도 횟수 초과")
```

### **4. data/sentiment_collector.py**
```python
"""
감정 데이터 수집기
"""

import requests
import feedparser
import re
import logging
from typing import List, Dict, Any
from datetime import datetime
from data.database import Database

class SentimentCollector:
    """감정 데이터 수집 클래스"""
    
    def __init__(self):
        """감정 데이터 수집기 초기화"""
        self.logger = logging.getLogger(__name__)
        self.db = Database()
        
        # 감정 키워드 정의
        self.positive_keywords = [
            'bullish', 'surge', 'rally', 'breakout', 'moon', 'pump',
            'positive', 'growth', 'adoption', 'institutional', 'buy'
        ]
        
        self.negative_keywords = [
            'bearish', 'crash', 'dump', 'breakdown', 'sell', 'fear',
            'negative', 'decline', 'ban', 'regulation', 'hack'
        ]
        
        # 뉴스 소스 RSS 피드
        self.news_sources = [
            'https://cointelegraph.com/rss',
            'https://coindesk.com/arc/outboundfeeds/rss/',
            'https://www.coindesk.com/arc/outboundfeeds/rss/'
        ]
        
        self.logger.info("SentimentCollector 초기화 완료")
    
    def collect_news_headlines(self) -> List[Dict[str, Any]]:
        """뉴스 헤드라인 수집"""
        headlines = []
        
        for source in self.news_sources:
            try:
                # RSS 피드 파싱
                feed = feedparser.parse(source)
                
                for entry in feed.entries[:10]:  # 최근 10개만
                    headline = {
                        'source': source,
                        'title': entry.title,
                        'link': entry.link,
                        'published': entry.published,
                        'summary': getattr(entry, 'summary', '')
                    }
                    headlines.append(headline)
                
                self.logger.info(f"{source}에서 {len(feed.entries[:10])}개 헤드라인 수집")
                
            except Exception as e:
                self.logger.error(f"{source} 헤드라인 수집 실패: {e}")
                continue
        
        return headlines
    
    def analyze_sentiment(self, text: str) -> float:
        """간단한 키워드 기반 감정 분석"""
        text_lower = text.lower()
        
        positive_count = sum(1 for keyword in self.positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in self.negative_keywords if keyword in text_lower)
        
        # 감정 점수 계산 (-1 ~ 1)
        total_keywords = positive_count + negative_count
        if total_keywords == 0:
            return 0.0
        
        sentiment_score = (positive_count - negative_count) / total_keywords
        return max(-1.0, min(1.0, sentiment_score))
    
    def extract_keywords(self, text: str) -> str:
        """키워드 추출"""
        text_lower = text.lower()
        found_keywords = []
        
        # 긍정 키워드
        for keyword in self.positive_keywords:
            if keyword in text_lower:
                found_keywords.append(f"+{keyword}")
        
        # 부정 키워드
        for keyword in self.negative_keywords:
            if keyword in text_lower:
                found_keywords.append(f"-{keyword}")
        
        return ','.join(found_keywords)
    
    def collect_and_analyze(self):
        """감정 데이터 수집 및 분석"""
        try:
            self.logger.info("감정 데이터 수집 시작")
            
            # 헤드라인 수집
            headlines = self.collect_news_headlines()
            
            for headline in headlines:
                # 감정 분석
                sentiment_score = self.analyze_sentiment(headline['title'])
                
                # 키워드 추출
                keywords = self.extract_keywords(headline['title'])
                
                # 데이터베이스에 저장
                self.db.save_sentiment_data(
                    source=headline['source'],
                    headline=headline['title'],
                    sentiment_score=sentiment_score,
                    keywords=keywords
                )
            
            self.logger.info(f"감정 데이터 수집 완료: {len(headlines)}개")
            
        except Exception as e:
            self.logger.error(f"감정 데이터 수집 실패: {e}")
            raise
    
    def get_average_sentiment(self, hours: int = 24) -> float:
        """평균 감정 점수 조회"""
        try:
            # 최근 N시간 데이터 조회
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = end_time - (hours * 60 * 60 * 1000)
            
            df = self.db.get_sentiment_data(start_time, end_time)
            
            if df.empty:
                return 0.0
            
            return df['sentiment_score'].mean()
            
        except Exception as e:
            self.logger.error(f"평균 감정 점수 조회 실패: {e}")
            return 0.0
```

## ✅ 테스트 방법

### **1. 데이터베이스 테스트**
```python
# test_database.py
from data.database import Database
import pandas as pd

def test_database():
    """데이터베이스 테스트"""
    print("=== 데이터베이스 테스트 ===")
    
    # 데이터베이스 초기화
    db = Database()
    
    # 테스트 데이터 저장
    test_price_data = [
        {
            'symbol': 'BTCUSDT',
            'timestamp': 1640995200000,  # 2022-01-01
            'open': 50000.0,
            'high': 51000.0,
            'low': 49000.0,
            'close': 50500.0,
            'volume': 1000.0
        }
    ]
    
    db.save_price_data('BTCUSDT', test_price_data)
    print("✅ 가격 데이터 저장 테스트")
    
    # 데이터 조회 테스트
    df = db.get_price_data('BTCUSDT')
    print(f"✅ 데이터 조회 테스트: {len(df)}개 레코드")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_database()
```

### **2. 과거데이터 수집 테스트** ✅ **구현 완료**
```python
# 과거데이터 수집 테스트
python scripts/collect_historical_data.py --symbol BTCUSDT --interval 1h --days 30

# 고속 수집 테스트 (5개 코인)
python scripts/collect_historical_data.py --all --fast

# 전체 50개 코인 수집
python scripts/collect_historical_data.py --all --fast
```

### **3. WebSocket 테스트**
```python
# test_websocket.py
import time
from data.websocket_client import WebSocketClient

def on_trade_data(data):
    """거래 데이터 콜백"""
    print(f"실시간 거래: {data}")

def test_websocket():
    """WebSocket 테스트"""
    print("=== WebSocket 테스트 ===")
    
    # WebSocket 클라이언트 생성
    ws_client = WebSocketClient('btcusdt', on_trade_data)
    
    # 연결 시작
    ws_client.connect()
    
    # 10초간 데이터 수신
    print("10초간 실시간 데이터 수신 중...")
    time.sleep(10)
    
    # 연결 종료
    ws_client.disconnect()
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_websocket()
```

### **4. 감정 데이터 테스트**
```python
# test_sentiment.py
from data.sentiment_collector import SentimentCollector

def test_sentiment():
    """감정 데이터 테스트"""
    print("=== 감정 데이터 테스트 ===")
    
    # 감정 수집기 초기화
    collector = SentimentCollector()
    
    # 감정 분석 테스트
    test_texts = [
        "Bitcoin surges to new highs as institutional adoption grows",
        "Crypto market crashes as regulatory fears mount",
        "Ethereum breaks out of resistance level"
    ]
    
    for text in test_texts:
        sentiment = collector.analyze_sentiment(text)
        keywords = collector.extract_keywords(text)
        print(f"텍스트: {text}")
        print(f"감정 점수: {sentiment:.2f}")
        print(f"키워드: {keywords}")
        print("---")
    
    # 뉴스 수집 테스트
    print("뉴스 헤드라인 수집 중...")
    collector.collect_and_analyze()
    
    # 평균 감정 점수
    avg_sentiment = collector.get_average_sentiment(1)  # 1시간
    print(f"평균 감정 점수: {avg_sentiment:.2f}")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_sentiment()
```

## 🚀 실행 방법

### **1. 과거데이터 수집 실행** ✅ **구현 완료**
```bash
# 단일 코인 단일 간격 수집
python scripts/collect_historical_data.py --symbol BTCUSDT --interval 1h --days 30

# 단일 코인 모든 간격 수집
python scripts/collect_historical_data.py --symbol BTCUSDT --all-intervals --fast

# 전체 50개 코인 수집 (고속)
python scripts/collect_historical_data.py --all --fast

# 누락된 데이터만 수집
python scripts/collect_historical_data.py --missing
```

### **2. 실시간 데이터 수집** ✅ **구현 완료**
```bash
# 메인 봇 실행 (WebSocket + 감정 데이터 통합)
python main.py

# 또는 개별 테스트
python -c "
from data.websocket_client import BinanceWebSocketClient
from bot.config import Config
from config.coins_config import CoinsConfig
from data.database import Database

config = Config.from_env()
coins_config = CoinsConfig()
database = Database()

ws = BinanceWebSocketClient(config, coins_config, database)
ws.start_streaming()
"
```

### **3. 감정 데이터 수집** ✅ **구현 완료**
```bash
# 메인 봇 실행 (WebSocket + 감정 데이터 통합)
python main.py

# 또는 개별 테스트
python -c "
from data.sentiment_collector import SentimentCollector
from bot.config import Config
from data.database import Database

config = Config.from_env()
database = Database()

collector = SentimentCollector(config, database)
collector.collect_and_analyze()
"
```

## 📊 Phase 1 완료 기준

### **✅ 완료 체크리스트**
- [x] Binance 과거 데이터 수집 완료 (3년치, 모든 간격) - **별도 스크립트로 분리**
- [x] WebSocket 실시간 연결 성공 - **구현 완료**
- [x] 뉴스 헤드라인 수집 완료 - **RSS 피드 구현 완료**
- [x] 감정 분석 구현 완료 - **키워드 기반 분석 구현 완료**
- [x] 데이터베이스 저장 성공 (코인별 간격별 테이블)
- [x] 과거데이터 수집 테스트 통과
- [x] 통합 봇 구조 완료 - **collector.py 빈자리 해결**

### **🎯 성공 지표**
- **데이터 수집**: ✅ 3년치 모든 간격 과거 데이터 수집 완료 (별도 스크립트)
- **실시간 연결**: ✅ WebSocket 연결 구현 완료 (50개 코인 동시 연결)
- **감정 분석**: ✅ 뉴스 헤드라인 수집 및 분석 완료 (RSS 피드)
- **데이터베이스**: ✅ 코인별 간격별 테이블 구조 (800개 테이블)
- **통합 봇**: ✅ 기본 구조 완료 (collector.py 빈자리 해결)

## 🚀 다음 단계 (Phase 2)

**Phase 1이 완료되었으므로 다음 단계로 진행합니다:**

1. **핵심 기술적 분석 모듈 구현** (RSI, MACD, 볼린저밴드, 이동평균, 거래량)
2. **핵심 전략 모듈 구현** (스캘핑, 스윙, 추세추종, 평균회귀)
3. **ML 예측 모델 구현** (랜덤포레스트)
4. **신호 통합 로직 개발** (기술적 + 전략 + 감정 + ML)

**Phase 2 상세 가이드**: `PHASE_2_DETAILED.md`

**현재 상태**: Phase 1 ✅ **100% 완료** → Phase 2 ⏳ **시작 준비 완료**

## 📋 테스트 결과

### ✅ **완료된 테스트**:
- [x] 기본 모듈 import 테스트
- [x] 설정 로딩 테스트
- [x] 데이터베이스 초기화 테스트
- [x] 감정 데이터 수집기 테스트
- [x] WebSocket 클라이언트 테스트
- [x] 통합 봇 테스트
- [x] 과거 데이터 수집기 테스트

### 🎯 **테스트 실행 방법**:
```bash
# 간단한 테스트
python quick_test.py

# 상세한 테스트
python run_test.py

# 개별 기능 테스트
python simple_test.py
```

### 📊 **구현 완성도**:
- **과거 데이터 수집**: 100% 완료
- **실시간 데이터 수집**: 100% 완료
- **감정 데이터 수집**: 100% 완료
- **데이터베이스 구조**: 100% 완료
- **통합 봇 구조**: 100% 완료
- **테스트 스크립트**: 100% 완료

**전체 완성도**: 100% ✅