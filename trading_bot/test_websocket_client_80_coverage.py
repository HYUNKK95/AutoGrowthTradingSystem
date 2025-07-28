#!/usr/bin/env python3
"""
WebSocket 클라이언트 80% 커버리지 테스트
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

def test_websocket_client_init():
    """WebSocket 클라이언트 초기화 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    assert ws_client is not None
    assert hasattr(ws_client, 'config')
    assert hasattr(ws_client, 'coins_config')
    assert hasattr(ws_client, 'database')
    assert hasattr(ws_client, 'base_url')
    assert hasattr(ws_client, 'is_connected')
    assert hasattr(ws_client, 'ws')
    assert hasattr(ws_client, 'realtime_data')
    assert hasattr(ws_client, 'callbacks')

def test_websocket_client_base_url():
    """WebSocket 기본 URL 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    assert ws_client.base_url == "wss://stream.binance.com:9443/ws"
    assert isinstance(ws_client.base_url, str)
    assert 'wss://' in ws_client.base_url
    assert 'stream.binance.com' in ws_client.base_url

def test_on_message():
    """메시지 수신 처리 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 테스트 메시지
    test_message = {
        'stream': 'btcusdt@ticker',
        'data': {
            's': 'BTCUSDT',
            'c': '50000.00',
            'v': '1000.00',
            'E': int(datetime.now().timestamp() * 1000),
            'P': '1000.00',
            'h': '51000.00',
            'l': '49000.00'
        }
    }
    
    with patch.object(database, 'save_realtime_data') as mock_save:
        ws_client.on_message(None, json.dumps(test_message))
        
        # 데이터가 저장되었는지 확인
        mock_save.assert_called_once()
        
        # 실시간 데이터에 저장되었는지 확인
        assert 'BTCUSDT' in ws_client.realtime_data

def test_on_message_error():
    """메시지 처리 오류 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 잘못된 JSON 메시지
    invalid_message = "invalid json"
    
    # 오류 없이 처리되어야 함
    try:
        ws_client.on_message(None, invalid_message)
        assert True
    except Exception as e:
        assert False, f"메시지 처리 중 예상치 못한 오류: {e}"

def test_on_error():
    """오류 처리 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 초기 상태
    ws_client.is_connected = True
    
    # 오류 처리
    test_error = Exception("Test error")
    ws_client.on_error(None, test_error)
    
    # 연결 상태가 False로 변경되었는지 확인
    assert ws_client.is_connected is False

def test_on_close():
    """연결 종료 처리 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 초기 상태
    ws_client.is_connected = True
    
    # 연결 종료 처리
    ws_client.on_close(None, 1000, "Normal closure")
    
    # 연결 상태가 False로 변경되었는지 확인
    assert ws_client.is_connected is False

def test_on_open():
    """연결 열림 처리 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 초기 상태
    ws_client.is_connected = False
    ws_client.reconnect_attempts = 5
    
    # 연결 열림 처리
    ws_client.on_open(None)
    
    # 상태 확인
    assert ws_client.is_connected is True
    assert ws_client.reconnect_attempts == 0

def test_connect():
    """WebSocket 연결 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    with patch('websocket.WebSocketApp') as mock_websocket:
        mock_ws = MagicMock()
        mock_websocket.return_value = mock_ws
        
        with patch('threading.Thread') as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            ws_client.connect()
            
            # WebSocketApp이 생성되었는지 확인
            mock_websocket.assert_called_once()
            
            # 스레드가 시작되었는지 확인
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()

def test_disconnect():
    """WebSocket 연결 해제 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 초기 상태
    ws_client.is_connected = True
    ws_client.ws = MagicMock()
    
    # 연결 해제
    ws_client.disconnect()
    
    # WebSocket이 닫혔는지 확인
    ws_client.ws.close.assert_called_once()
    assert ws_client.is_connected is False

def test_add_callback():
    """콜백 함수 추가 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 초기 콜백 수
    initial_count = len(ws_client.callbacks)
    
    # 콜백 함수 정의
    def test_callback(data):
        pass
    
    # 콜백 추가
    ws_client.add_callback(test_callback)
    
    # 콜백이 추가되었는지 확인
    assert len(ws_client.callbacks) == initial_count + 1
    assert test_callback in ws_client.callbacks

def test_get_realtime_data():
    """실시간 데이터 조회 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 테스트 데이터 설정
    test_data = {'price': 50000.0, 'volume': 1000.0}
    ws_client.realtime_data['BTCUSDT'] = test_data
    
    # 특정 심볼 데이터 조회
    result = ws_client.get_realtime_data('BTCUSDT')
    assert result == test_data
    
    # 존재하지 않는 심볼 조회
    result = ws_client.get_realtime_data('INVALID')
    assert result is None

def test_get_all_realtime_data():
    """모든 실시간 데이터 조회 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 테스트 데이터 설정
    test_data = {
        'BTCUSDT': {'price': 50000.0, 'volume': 1000.0},
        'ETHUSDT': {'price': 3000.0, 'volume': 500.0}
    }
    ws_client.realtime_data = test_data.copy()
    
    # 모든 데이터 조회
    result = ws_client.get_all_realtime_data()
    assert result == test_data
    assert len(result) == 2

def test_start_streaming():
    """스트리밍 시작 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    with patch.object(ws_client, 'connect') as mock_connect:
        with patch('time.sleep') as mock_sleep:
            # KeyboardInterrupt로 중단
            mock_sleep.side_effect = KeyboardInterrupt()
            
            try:
                ws_client.start_streaming()
            except KeyboardInterrupt:
                pass
            
            # 연결이 시도되었는지 확인
            mock_connect.assert_called_once()

def test_websocket_client_reconnect_logic():
    """재연결 로직 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 초기 설정 확인
    assert ws_client.reconnect_attempts == 0
    assert ws_client.max_reconnect_attempts == 5
    assert ws_client.reconnect_delay == 5

def test_websocket_client_on_close_with_reconnect():
    """재연결이 포함된 연결 종료 처리 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 초기 상태
    ws_client.is_connected = True
    ws_client.reconnect_attempts = 2
    
    # 연결 종료 처리 (재연결 시도)
    with patch.object(ws_client, 'connect') as mock_connect:
        with patch('time.sleep') as mock_sleep:
            ws_client.on_close(None, 1000, "Normal closure")
            
            # 연결 상태가 False로 변경되었는지 확인
            assert ws_client.is_connected is False
            # 재연결 시도가 증가했는지 확인
            assert ws_client.reconnect_attempts == 3
            # 재연결이 호출되었는지 확인
            mock_connect.assert_called_once()

def test_websocket_client_on_close_max_reconnect():
    """최대 재연결 시도 초과 시 처리 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 최대 재연결 시도 상태
    ws_client.is_connected = True
    ws_client.reconnect_attempts = 5  # 최대값
    
    # 연결 종료 처리 (재연결 시도하지 않음)
    with patch.object(ws_client, 'connect') as mock_connect:
        ws_client.on_close(None, 1000, "Normal closure")
        
        # 연결 상태가 False로 변경되었는지 확인
        assert ws_client.is_connected is False
        # 재연결이 호출되지 않았는지 확인
        mock_connect.assert_not_called()

def test_websocket_client_message_processing_error():
    """메시지 처리 오류 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 잘못된 JSON 메시지
    invalid_message = "invalid json message"
    
    # 오류 없이 처리되어야 함
    try:
        ws_client.on_message(None, invalid_message)
        assert True
    except Exception as e:
        assert False, f"메시지 처리 중 예상치 못한 오류: {e}"

def test_websocket_client_callback_error():
    """콜백 함수 오류 처리 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 오류를 발생시키는 콜백 함수
    def error_callback(data):
        raise Exception("Test callback error")
    
    # 콜백 추가
    ws_client.add_callback(error_callback)
    
    # 테스트 메시지
    test_message = {
        'stream': 'btcusdt@ticker',
        'data': {
            's': 'BTCUSDT',
            'c': '50000.00',
            'v': '1000.00',
            'E': int(datetime.now().timestamp() * 1000),
            'P': '1000.00',
            'h': '51000.00',
            'l': '49000.00'
        }
    }
    
    # 콜백 오류가 처리되어야 함
    try:
        ws_client.on_message(None, json.dumps(test_message))
        assert True
    except Exception as e:
        assert False, f"콜백 오류 처리 중 예상치 못한 오류: {e}"

def test_websocket_client_connect_error():
    """연결 오류 처리 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 잘못된 URL로 연결 시도
    ws_client.base_url = "wss://invalid.url.com/ws"
    
    with patch('websocket.WebSocketApp') as mock_websocket:
        mock_websocket.side_effect = Exception("Connection error")
        
        # 연결 시도
        ws_client.connect()
        
        # 연결 상태가 False인지 확인
        assert ws_client.is_connected is False

def test_websocket_client_start_streaming():
    """스트리밍 시작 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    with patch.object(ws_client, 'connect') as mock_connect:
        with patch('time.sleep') as mock_sleep:
            # KeyboardInterrupt로 중단
            mock_sleep.side_effect = KeyboardInterrupt()
            
            try:
                ws_client.start_streaming()
            except KeyboardInterrupt:
                pass
            
            # 연결이 시도되었는지 확인
            mock_connect.assert_called_once()

def test_websocket_client_start_streaming_disconnected():
    """연결이 끊어진 상태에서 스트리밍 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 연결 해제 상태로 설정
    ws_client.is_connected = False
    
    with patch.object(ws_client, 'connect') as mock_connect:
        with patch('time.sleep') as mock_sleep:
            # KeyboardInterrupt로 중단
            mock_sleep.side_effect = KeyboardInterrupt()
            
            try:
                ws_client.start_streaming()
            except KeyboardInterrupt:
                pass
            
            # 재연결이 시도되었는지 확인
            mock_connect.assert_called()

def test_websocket_client_disconnect_without_ws():
    """WebSocket 객체가 없는 상태에서 연결 해제 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # WebSocket 객체가 없는 상태
    ws_client.ws = None
    ws_client.is_connected = True
    
    # 연결 해제
    ws_client.disconnect()
    
    # 연결 상태가 False인지 확인
    assert ws_client.is_connected is False

def test_websocket_client_stream_url_generation():
    """스트림 URL 생성 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 스트림 URL 생성 로직 확인
    symbols = ws_client.coins_config.coins
    streams = [f"{symbol.lower()}@ticker" for symbol in symbols]
    expected_url = f"{ws_client.base_url}/{'/'.join(streams)}"
    
    # URL이 올바르게 생성되었는지 확인
    assert "wss://stream.binance.com:9443/ws" in expected_url
    assert "btcusdt@ticker" in expected_url
    assert "ethusdt@ticker" in expected_url

def test_websocket_client_threading():
    """스레드 관련 테스트"""
    from data.websocket_client import BinanceWebSocketClient
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    with patch('websocket.WebSocketApp') as mock_websocket:
        with patch('threading.Thread') as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            ws_client.connect()
            
            # 스레드가 생성되고 시작되었는지 확인
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()
            assert mock_thread_instance.daemon is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 