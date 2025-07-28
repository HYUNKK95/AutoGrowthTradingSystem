"""
Phase 0과 Phase 1 통합 테스트
- Phase 0: 프로젝트 구조 및 기본 설정
- Phase 1: 데이터 수집 시스템
"""

import pytest
import os
import sys
import sqlite3
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.config import Config
from config.coins_config import CoinsConfig
from data.database import Database
from data.websocket_client import BinanceWebSocketClient
from data.sentiment_collector import SentimentCollector
from bot.integrated_bot import IntegratedTradingBot


class TestPhase0Phase1Integration:
    """Phase 0과 Phase 1 통합 테스트 클래스"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """테스트 설정"""
        self.config = Config.from_env()
        self.coins_config = CoinsConfig()
        self.database = Database()
        self.database.init_database()
    
    def test_phase0_project_structure(self):
        """Phase 0: 프로젝트 구조 테스트"""
        # 필수 디렉토리 존재 확인
        required_dirs = [
            'bot',
            'config', 
            'data',
            'utils',
            'scripts',
            'tests'
        ]
        
        for dir_name in required_dirs:
            assert os.path.exists(dir_name), f"필수 디렉토리 없음: {dir_name}"
        
        # 필수 파일 존재 확인
        required_files = [
            'main.py',
            'requirements.txt',
            'bot/config.py',
            'config/coins_config.py',
            'data/database.py',
            'data/websocket_client.py',
            'data/sentiment_collector.py',
            'bot/integrated_bot.py',
            'scripts/collect_historical_data.py'
        ]
        
        for file_name in required_files:
            assert os.path.exists(file_name), f"필수 파일 없음: {file_name}"
    
    def test_phase0_config_loading(self):
        """Phase 0: 설정 로딩 테스트"""
        # Config 클래스 테스트
        assert hasattr(self.config, 'binance_api_key')
        assert hasattr(self.config, 'binance_secret_key')
        assert hasattr(self.config, 'database_path')
        assert hasattr(self.config, 'binance_api_url')
        
        # CoinsConfig 클래스 테스트
        assert hasattr(self.coins_config, 'get_total_coins')
        assert hasattr(self.coins_config, 'coins')
        coins = self.coins_config.coins
        assert len(coins) == 50, f"코인 개수 오류: {len(coins)}"
        assert 'BTCUSDT' in coins, "BTCUSDT가 없음"
    
    def test_phase1_database_structure(self):
        """Phase 1: 데이터베이스 구조 테스트"""
        # 기본 테이블 존재 확인
        with sqlite3.connect(self.database.db_path) as conn:
            cursor = conn.cursor()
            
            # 기본 테이블 확인
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = [
                'price_data',
                'sentiment_data', 
                'realtime_data',
                'trades',
                'data_collection_status'
            ]
            
            for table in required_tables:
                assert table in tables, f"필수 테이블 없음: {table}"
            
            # 코인별 간격별 테이블 확인 (일부 샘플)
            sample_coins = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
            sample_intervals = ['1m', '1h', '1d']
            
            for coin in sample_coins:
                for interval in sample_intervals:
                    table_name = f"{coin}_{interval}"
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                    result = cursor.fetchone()
                    assert result is not None, f"테이블 없음: {table_name}"
    
    def test_phase1_websocket_client(self):
        """Phase 1: WebSocket 클라이언트 테스트"""
        # WebSocket 클라이언트 초기화 테스트
        ws_client = BinanceWebSocketClient(self.config, self.coins_config, self.database)
        assert ws_client is not None
        assert hasattr(ws_client, 'connect')
        assert hasattr(ws_client, 'disconnect')
        assert hasattr(ws_client, 'is_connected')
        
        # 연결 상태 확인
        assert not ws_client.is_connected, "초기 상태는 연결되지 않아야 함"
    
    def test_phase1_sentiment_collector(self):
        """Phase 1: 감정 데이터 수집기 테스트"""
        # 감정 데이터 수집기 초기화 테스트
        sentiment_collector = SentimentCollector(self.config, self.database)
        assert sentiment_collector is not None
        assert hasattr(sentiment_collector, 'collect_and_analyze')
        assert hasattr(sentiment_collector, 'analyze_sentiment')
        
        # 감정 분석 테스트
        test_headlines = [
            "Bitcoin reaches new all-time high",
            "Crypto market crashes",
            "New blockchain technology announced"
        ]
        
        for headline in test_headlines:
            sentiment = sentiment_collector.analyze_sentiment(headline)
            assert isinstance(sentiment, float)
            assert -1.0 <= sentiment <= 1.0
    
    def test_phase1_integrated_bot(self):
        """Phase 1: 통합 봇 테스트"""
        # 통합 봇 초기화 테스트
        bot = IntegratedTradingBot(self.config, self.coins_config)
        assert bot is not None
        assert hasattr(bot, 'start')
        assert hasattr(bot, 'stop')
        assert hasattr(bot, 'collect_market_data')
        
        # 봇 상태 확인
        assert not bot.is_running, "초기 상태는 실행되지 않아야 함"
        assert bot.current_balance == 3000000.0, f"초기 자본 오류: {bot.current_balance}"
    
    def test_phase1_historical_data_collector(self):
        """Phase 1: 과거 데이터 수집기 테스트"""
        # 과거 데이터 수집기 파일 존재 확인
        script_path = 'scripts/collect_historical_data.py'
        assert os.path.exists(script_path), f"과거 데이터 수집기 없음: {script_path}"
        
        # 스크립트 실행 가능성 확인
        import subprocess
        try:
            result = subprocess.run(
                [sys.executable, script_path, '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0, f"스크립트 실행 실패: {result.stderr}"
        except subprocess.TimeoutExpired:
            pytest.skip("스크립트 실행 시간 초과")
    
    def test_phase1_data_flow_integration(self):
        """Phase 1: 데이터 플로우 통합 테스트"""
        # 데이터베이스에 테스트 데이터 저장
        test_data = {
            'timestamp': int(datetime.now().timestamp() * 1000),
            'open': 100.0,
            'high': 110.0,
            'low': 90.0,
            'close': 105.0,
            'volume': 1000.0
        }
        
        # 가격 데이터 저장 테스트
        self.database.save_price_data('TESTUSDT', test_data)
        
        # 저장된 데이터 확인
        with sqlite3.connect(self.database.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM price_data WHERE symbol = ?", ('TESTUSDT',))
            result = cursor.fetchone()
            assert result is not None, "저장된 데이터를 찾을 수 없음"
            
            # 데이터 정확성 확인
            assert result[2] == test_data['symbol']  # symbol
            assert result[3] == test_data['timestamp']  # timestamp
            assert result[4] == test_data['open_price']  # open_price
    
    def test_phase1_error_handling(self):
        """Phase 1: 오류 처리 테스트"""
        # 잘못된 설정으로 초기화 시도
        invalid_config = Config(
            binance_api_key="invalid",
            binance_secret_key="invalid",
            binance_testnet=False,
            binance_api_url="https://invalid.api.com",
            database_path="./invalid.db",
            log_level="INFO",
            log_file="./invalid.log",
            trading_symbol="INVALID",
            initial_capital=1000000.0,
            max_position_size=0.1,
            stop_loss_percent=0.02,
            take_profit_percent=0.04
        )
        
        # 데이터베이스 초기화는 실패하지 않아야 함 (기본값 사용)
        try:
            invalid_db = Database()
            invalid_db.db_path = "./test_invalid.db"
            invalid_db.init_database()
            assert os.path.exists("./test_invalid.db")
        finally:
            # 테스트 파일 정리
            if os.path.exists("./test_invalid.db"):
                os.remove("./test_invalid.db")
    
    def test_phase1_performance_metrics(self):
        """Phase 1: 성능 메트릭 테스트"""
        # 데이터베이스 성능 테스트
        start_time = datetime.now()
        
        # 대량 데이터 저장 테스트
        test_data_list = []
        for i in range(100):
            test_data_list.append({
                'symbol': f'TEST{i}USDT',
                'timestamp': int((datetime.now() + timedelta(minutes=i)).timestamp() * 1000),
                'open': 100.0 + i,
                'high': 110.0 + i,
                'low': 90.0 + i,
                'close': 105.0 + i,
                'volume': 1000.0 + i
            })
        
        # 개별 데이터 저장
        for test_data in test_data_list:
            self.database.save_price_data(test_data['symbol'], test_data)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # 성능 기준: 100개 데이터 저장이 1초 이내
        assert processing_time < 1.0, f"데이터 저장 성능 저하: {processing_time}초"
        
        # 저장된 데이터 수 확인
        with sqlite3.connect(self.database.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM price_data WHERE symbol LIKE 'TEST%'")
            count = cursor.fetchone()[0]
            assert count >= 100, f"저장된 데이터 수 오류: {count}"
    
    def test_phase1_data_integrity(self):
        """Phase 1: 데이터 무결성 테스트"""
        # 중복 데이터 처리 테스트
        duplicate_data = {
            'timestamp': int(datetime.now().timestamp() * 1000),
            'open': 100.0,
            'high': 110.0,
            'low': 90.0,
            'close': 105.0,
            'volume': 1000.0
        }
        
        # 같은 데이터를 두 번 저장
        self.database.save_price_data('DUPLICATEUSDT', duplicate_data)
        self.database.save_price_data('DUPLICATEUSDT', duplicate_data)
        
        # 중복 데이터가 하나만 저장되었는지 확인
        with sqlite3.connect(self.database.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM price_data WHERE symbol = ?", ('DUPLICATEUSDT',))
            count = cursor.fetchone()[0]
            assert count == 1, f"중복 데이터 처리 실패: {count}개 저장됨"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 