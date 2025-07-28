"""
SQLite 데이터베이스 관리 클래스
"""

import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import os

class Database:
    """SQLite 데이터베이스 관리 클래스"""
    
    def __init__(self, db_path: str = None):
        """데이터베이스 초기화"""
        if db_path is None:
            # 기존 4.9GB 데이터베이스 사용 - 절대 경로
            current_dir = os.getcwd()
            db_path = os.path.join(current_dir, "trading_bot", "data", "trading_bot.db")
        
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # 데이터베이스 디렉토리 생성 (기존 파일이 있으면 건너뛰기)
        dir_path = os.path.dirname(db_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
        # 데이터베이스 연결 및 테이블 생성
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 기본 가격 데이터 테이블
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
                
                # 코인별 간격별 가격 데이터 테이블 생성 (3년치 모든 데이터용)
                # 50개 코인 × 16개 간격 = 800개 테이블
                coins = [
                    "ETHUSDT", "BTCUSDT", "SUIUSDT", "SOLUSDT", "XRPUSDT", "ERAUSDT", "ENAUSDT", 
                    "PENGUUSDT", "DOGEUSDT", "HBARUSDT", "PEPEUSDT", "ADAUSDT", "CRVUSDT", 
                    "TRXUSDT", "BONKUSDT", "AVAXUSDT", "UNIUSDT", "OMUSDT", "LINKUSDT", 
                    "CFXUSDT", "BCHUSDT", "WIFUSDT", "XLMUSDT", "CUSDT", "SPKUSDT", 
                    "SEIUSDT", "KERNELUSDT", "IDEXUSDT", "LTCUSDT", "CAKEUSDT", 
                    "SYRUPUSDT", "REIUSDT", "WLDUSDT", "FISUSDT", "TRUMPUSDT", 
                    "ASRUSDT", "FLOKIUSDT", "ENSUSDT", "ETHFIUSDT", "AAVEUSDT", 
                    "NEARUSDT", "SAHARAUSDT", "INJUSDT", "ONDOUSDT", "NEIROUSDT", 
                    "TAOUSDT", "CVXUSDT", "TONUSDT", "BIGTIMEUSDT", "SLPUSDT"
                ]
                
                intervals = [
                    '1m', '3m', '5m', '15m', '30m',  # 분봉
                    '1h', '2h', '4h', '6h', '8h', '12h',  # 시간봉
                    '1d', '3d', '1w', '1month'  # 일봉, 주봉, 월봉
                ]
                
                # 코인별 간격별 테이블 생성
                for coin in coins:
                    for interval in intervals:
                        table_name = f"{coin}_{interval}"
                        cursor.execute(f"""
                            CREATE TABLE IF NOT EXISTS {table_name} (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                timestamp INTEGER NOT NULL,
                                open_price REAL NOT NULL,
                                high_price REAL NOT NULL,
                                low_price REAL NOT NULL,
                                close_price REAL NOT NULL,
                                volume REAL NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                UNIQUE(timestamp)
                            )
                        """)
                        
                        # 인덱스 생성
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_timestamp ON {table_name}(timestamp)")
                
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
                
                # 거래 기록 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        side TEXT NOT NULL,
                        quantity REAL NOT NULL,
                        price REAL NOT NULL,
                        timestamp INTEGER NOT NULL,
                        status TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 데이터 수집 상태 추적 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS data_collection_status (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        interval TEXT NOT NULL,
                        last_collected_timestamp INTEGER,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(symbol, interval)
                    )
                """)
                
                conn.commit()
                self.logger.info("데이터베이스 초기화 완료")
                
        except Exception as e:
            self.logger.error(f"데이터베이스 초기화 실패: {e}")
            raise
    
    def save_price_data(self, symbol: str, data: Dict[str, Any]):
        """가격 데이터 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO price_data 
                    (symbol, timestamp, open_price, high_price, low_price, close_price, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol,
                    data['timestamp'],
                    data['open'],
                    data['high'],
                    data['low'],
                    data['close'],
                    data['volume']
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"가격 데이터 저장 실패: {e}")
    
    def save_price_data_to_table(self, symbol: str, data: List[Dict[str, Any]], table_name: str):
        """특정 테이블에 가격 데이터 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for item in data:
                    cursor.execute(f"""
                        INSERT OR REPLACE INTO {table_name} 
                        (timestamp, open_price, high_price, low_price, close_price, volume)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        item['timestamp'],
                        item['open'],
                        item['high'],
                        item['low'],
                        item['close'],
                        item['volume']
                    ))
                
                conn.commit()
                self.logger.info(f"{symbol} {table_name} 테이블에 {len(data)}개 데이터 저장 완료")
                
        except Exception as e:
            self.logger.error(f"{table_name} 테이블에 가격 데이터 저장 실패: {e}")
            raise
    
    def save_price_data_to_coin_table(self, symbol: str, interval: str, data: List[Dict[str, Any]]):
        """코인별 간격별 테이블에 가격 데이터 저장"""
        try:
            table_name = f"{symbol}_{interval}"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for item in data:
                    cursor.execute(f"""
                        INSERT OR REPLACE INTO {table_name} 
                        (timestamp, open_price, high_price, low_price, close_price, volume)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        item['timestamp'],
                        item['open'],
                        item['high'],
                        item['low'],
                        item['close'],
                        item['volume']
                    ))
                
                # 마지막 수집 타임스탬프 업데이트
                if data:
                    last_timestamp = data[-1]['timestamp']
                    cursor.execute("""
                        INSERT OR REPLACE INTO data_collection_status 
                        (symbol, interval, last_collected_timestamp, last_updated)
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    """, (symbol, interval, last_timestamp))
                
                conn.commit()
                self.logger.info(f"{symbol} {interval}: {len(data)}개 캔들 저장 완료")
                
        except Exception as e:
            self.logger.error(f"{symbol} {interval} 데이터 저장 실패: {e}")
            raise
    
    def get_price_data(self, symbol: str, start_time: int = None, end_time: int = None, limit: int = None) -> pd.DataFrame:
        """가격 데이터 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if start_time and end_time:
                    query = """
                        SELECT * FROM price_data 
                        WHERE symbol = ? AND timestamp BETWEEN ? AND ?
                        ORDER BY timestamp ASC
                    """
                    df = pd.read_sql_query(query, conn, params=(symbol, start_time, end_time))
                elif limit:
                    query = """
                        SELECT * FROM price_data 
                        WHERE symbol = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    """
                    df = pd.read_sql_query(query, conn, params=(symbol, limit))
                else:
                    query = """
                        SELECT * FROM price_data 
                        WHERE symbol = ?
                        ORDER BY timestamp DESC
                        LIMIT 100
                    """
                    df = pd.read_sql_query(query, conn, params=(symbol,))
                
                return df
                
        except Exception as e:
            self.logger.error(f"가격 데이터 조회 실패: {e}")
            return pd.DataFrame()
    
    def save_sentiment_data(self, source: str, headline: str, sentiment_score: float, 
                           keywords: str, timestamp: int):
        """감정 데이터 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO sentiment_data 
                    (source, headline, sentiment_score, keywords, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (source, headline, sentiment_score, keywords, timestamp))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"감정 데이터 저장 실패: {e}")
    
    def get_sentiment_data(self, limit: int = 100) -> pd.DataFrame:
        """감정 데이터 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT * FROM sentiment_data 
                    ORDER BY timestamp DESC
                    LIMIT ?
                """
                df = pd.read_sql_query(query, conn, params=(limit,))
                return df
                
        except Exception as e:
            self.logger.error(f"감정 데이터 조회 실패: {e}")
            return pd.DataFrame()
    
    def save_realtime_data(self, symbol: str, price: float, volume: float, timestamp: int):
        """실시간 데이터 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO realtime_data 
                    (symbol, price, volume, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (symbol, price, volume, timestamp))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"실시간 데이터 저장 실패: {e}")
    
    def save_trade(self, symbol: str, side: str, quantity: float, 
                   price: float, timestamp: int, status: str):
        """거래 기록 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO trades 
                    (symbol, side, quantity, price, timestamp, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (symbol, side, quantity, price, timestamp, status))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"거래 기록 저장 실패: {e}")
    
    def get_trades(self, symbol: str = None, limit: int = 100) -> pd.DataFrame:
        """거래 기록 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if symbol:
                    query = """
                        SELECT * FROM trades 
                        WHERE symbol = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    """
                    df = pd.read_sql_query(query, conn, params=(symbol, limit))
                else:
                    query = """
                        SELECT * FROM trades 
                        ORDER BY timestamp DESC
                        LIMIT ?
                    """
                    df = pd.read_sql_query(query, conn, params=(limit,))
                
                return df
                
        except Exception as e:
            self.logger.error(f"거래 기록 조회 실패: {e}")
            return pd.DataFrame()
    
    def get_last_collected_timestamp(self, symbol: str, interval: str) -> Optional[int]:
        """마지막으로 수집된 타임스탬프 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT last_collected_timestamp 
                    FROM data_collection_status 
                    WHERE symbol = ? AND interval = ?
                """, (symbol, interval))
                
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            self.logger.error(f"마지막 수집 타임스탬프 조회 실패: {e}")
            return None
    
    def get_missing_data_period(self, symbol: str, interval: str) -> Optional[Dict[str, int]]:
        """누락된 데이터 기간 조회"""
        try:
            last_timestamp = self.get_last_collected_timestamp(symbol, interval)
            current_time = int(datetime.now().timestamp() * 1000)
            
            if last_timestamp:
                return {
                    'start_time': last_timestamp + 1,
                    'end_time': current_time
                }
            else:
                # 처음 수집하는 경우
                return {
                    'start_time': int((datetime.now() - timedelta(days=1095)).timestamp() * 1000),
                    'end_time': current_time
                }
                
        except Exception as e:
            self.logger.error(f"누락 데이터 기간 조회 실패: {e}")
            return None
    
    def connect(self):
        """데이터베이스 연결"""
        return sqlite3.connect(self.db_path)
    
    def get_database_info(self) -> Dict[str, Any]:
        """데이터베이스 정보 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 기본 테이블별 레코드 수 조회
                basic_tables = ['price_data', 'sentiment_data', 'realtime_data', 'trades']
                info = {}
                
                for table in basic_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    info[table] = count
                
                # 간격별 테이블 레코드 수 조회
                intervals = [
                    '1m', '3m', '5m', '15m', '30m',  # 분봉
                    '1h', '2h', '4h', '6h', '8h', '12h',  # 시간봉
                    '1d', '3d', '1w', '1month'  # 일봉, 주봉, 월봉
                ]
                
                for interval in intervals:
                    table_name = f"price_data_{interval}"
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        info[table_name] = count
                    except:
                        info[table_name] = 0
                
                return info
                
        except Exception as e:
            self.logger.error(f"데이터베이스 정보 조회 실패: {e}")
            return {}

# 사용 예시
if __name__ == "__main__":
    # 데이터베이스 테스트
    db = Database()
    
    # 데이터베이스 정보 출력
    info = db.get_database_info()
    print("데이터베이스 정보:")
    for table, count in info.items():
        print(f"  {table}: {count}개 레코드") 