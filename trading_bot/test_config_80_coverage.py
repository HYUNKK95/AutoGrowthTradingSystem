#!/usr/bin/env python3
"""
Config 클래스 80% 커버리지 테스트
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

def test_config_from_env():
    """Config.from_env() 메서드 테스트"""
    from bot.config import Config
    
    # 환경 변수 설정
    with patch.dict(os.environ, {
        'BINANCE_API_KEY': 'test_api_key',
        'BINANCE_SECRET_KEY': 'test_secret_key',
        'BINANCE_TESTNET': 'true',
        'BINANCE_API_URL': 'https://test.api.com',
        'DATABASE_PATH': './test.db',
        'LOG_LEVEL': 'DEBUG',
        'LOG_FILE': './test.log',
        'TRADING_SYMBOL': 'BTCUSDT',
        'INITIAL_CAPITAL': '1000000.0',
        'MAX_POSITION_SIZE': '0.1',
        'STOP_LOSS_PERCENT': '0.02',
        'TAKE_PROFIT_PERCENT': '0.04'
    }):
        config = Config.from_env()
        
        assert config.binance_api_key == 'test_api_key'
        assert config.binance_secret_key == 'test_secret_key'
        assert config.binance_testnet is True
        assert config.binance_api_url == 'https://test.api.com'
        assert config.database_path == './test.db'
        assert config.log_level == 'DEBUG'
        assert config.log_file == './test.log'
        assert config.trading_symbol == 'BTCUSDT'
        assert config.initial_capital == 1000000.0
        assert config.max_position_size == 0.1
        assert config.stop_loss_percent == 0.02
        assert config.take_profit_percent == 0.04

def test_config_direct_init():
    """Config 직접 초기화 테스트"""
    from bot.config import Config
    
    config = Config(
        binance_api_key="direct_key",
        binance_secret_key="direct_secret",
        binance_testnet=False,
        binance_api_url="https://direct.api.com",
        database_path="./direct.db",
        log_level="INFO",
        log_file="./direct.log",
        trading_symbol="ETHUSDT",
        initial_capital=2000000.0,
        max_position_size=0.2,
        stop_loss_percent=0.03,
        take_profit_percent=0.05
    )
    
    assert config.binance_api_key == "direct_key"
    assert config.binance_secret_key == "direct_secret"
    assert config.binance_testnet is False
    assert config.binance_api_url == "https://direct.api.com"
    assert config.database_path == "./direct.db"
    assert config.log_level == "INFO"
    assert config.log_file == "./direct.log"
    assert config.trading_symbol == "ETHUSDT"
    assert config.initial_capital == 2000000.0
    assert config.max_position_size == 0.2
    assert config.stop_loss_percent == 0.03
    assert config.take_profit_percent == 0.05

def test_config_default_values():
    """Config 기본값 테스트"""
    from bot.config import Config
    
    # 환경 변수 제거
    with patch.dict(os.environ, {}, clear=True):
        config = Config.from_env()
        
        # 기본값 확인
        assert config.binance_api_key == ""
        assert config.binance_secret_key == ""
        assert config.binance_testnet is False
        assert config.binance_api_url == "https://api.binance.com"
        assert config.database_path == "./data/trading_bot.db"
        assert config.log_level == "INFO"
        assert config.log_file == "./logs/trading_bot.log"
        assert config.trading_symbol == "BTCUSDT"
        assert config.initial_capital == 3000000.0
        assert config.max_position_size == 0.1
        assert config.stop_loss_percent == 0.02
        assert config.take_profit_percent == 0.04

def test_config_float_conversion():
    """Config float 변환 테스트"""
    from bot.config import Config
    
    with patch.dict(os.environ, {
        'BINANCE_API_KEY': 'test_key',
        'BINANCE_SECRET_KEY': 'test_secret',
        'BINANCE_TESTNET': 'false',
        'BINANCE_API_URL': 'https://test.api.com',
        'DATABASE_PATH': './test.db',
        'LOG_LEVEL': 'DEBUG',
        'LOG_FILE': './test.log',
        'TRADING_SYMBOL': 'BTCUSDT',
        'INITIAL_CAPITAL': '5000000.5',
        'MAX_POSITION_SIZE': '0.15',
        'STOP_LOSS_PERCENT': '0.025',
        'TAKE_PROFIT_PERCENT': '0.045'
    }):
        config = Config.from_env()
        
        assert config.initial_capital == 5000000.5
        assert config.max_position_size == 0.15
        assert config.stop_loss_percent == 0.025
        assert config.take_profit_percent == 0.045

def test_config_boolean_conversion():
    """Config boolean 변환 테스트"""
    from bot.config import Config
    
    # True 테스트
    with patch.dict(os.environ, {
        'BINANCE_API_KEY': 'test_key',
        'BINANCE_SECRET_KEY': 'test_secret',
        'BINANCE_TESTNET': 'true',
        'BINANCE_API_URL': 'https://test.api.com',
        'DATABASE_PATH': './test.db',
        'LOG_LEVEL': 'DEBUG',
        'LOG_FILE': './test.log',
        'TRADING_SYMBOL': 'BTCUSDT',
        'INITIAL_CAPITAL': '1000000.0',
        'MAX_POSITION_SIZE': '0.1',
        'STOP_LOSS_PERCENT': '0.02',
        'TAKE_PROFIT_PERCENT': '0.04'
    }):
        config = Config.from_env()
        assert config.binance_testnet is True
    
    # False 테스트
    with patch.dict(os.environ, {
        'BINANCE_API_KEY': 'test_key',
        'BINANCE_SECRET_KEY': 'test_secret',
        'BINANCE_TESTNET': 'false',
        'BINANCE_API_URL': 'https://test.api.com',
        'DATABASE_PATH': './test.db',
        'LOG_LEVEL': 'DEBUG',
        'LOG_FILE': './test.log',
        'TRADING_SYMBOL': 'BTCUSDT',
        'INITIAL_CAPITAL': '1000000.0',
        'MAX_POSITION_SIZE': '0.1',
        'STOP_LOSS_PERCENT': '0.02',
        'TAKE_PROFIT_PERCENT': '0.04'
    }):
        config = Config.from_env()
        assert config.binance_testnet is False

def test_config_validate_required():
    """필수 설정 검증 테스트"""
    from bot.config import Config
    
    # 유효한 설정
    valid_config = Config(
        binance_api_key="test_key",
        binance_secret_key="test_secret",
        binance_testnet=False,
        binance_api_url="https://api.binance.com",
        database_path="./test.db",
        log_level="INFO",
        log_file="./test.log",
        trading_symbol="BTCUSDT",
        initial_capital=1000000.0,
        max_position_size=0.1,
        stop_loss_percent=0.02,
        take_profit_percent=0.04
    )
    
    assert valid_config.validate_required() is True
    
    # 무효한 설정 (빈 API 키)
    invalid_config = Config(
        binance_api_key="",
        binance_secret_key="test_secret",
        binance_testnet=False,
        binance_api_url="https://api.binance.com",
        database_path="./test.db",
        log_level="INFO",
        log_file="./test.log",
        trading_symbol="BTCUSDT",
        initial_capital=1000000.0,
        max_position_size=0.1,
        stop_loss_percent=0.02,
        take_profit_percent=0.04
    )
    
    assert invalid_config.validate_required() is False

def test_config_print_summary():
    """설정 요약 출력 테스트"""
    from bot.config import Config
    from io import StringIO
    import sys
    
    config = Config(
        binance_api_key="test_key",
        binance_secret_key="test_secret",
        binance_testnet=False,
        binance_api_url="https://api.binance.com",
        database_path="./test.db",
        log_level="INFO",
        log_file="./test.log",
        trading_symbol="BTCUSDT",
        initial_capital=1000000.0,
        max_position_size=0.1,
        stop_loss_percent=0.02,
        take_profit_percent=0.04,
        debug_mode=True,
        backtest_mode=False
    )
    
    # 출력 캡처
    captured_output = StringIO()
    sys.stdout = captured_output
    
    try:
        config.print_config_summary()
        output = captured_output.getvalue()
        
        # 출력 내용 확인
        assert "트레이딩 봇 설정 요약" in output
        assert "BTCUSDT" in output
        assert "1,000,000" in output
        assert "10.0%" in output  # max_position_size
        assert "2.0%" in output   # stop_loss_percent
        assert "4.0%" in output   # take_profit_percent
        assert "True" in output   # debug_mode
        assert "False" in output  # backtest_mode
    finally:
        sys.stdout = sys.__stdout__

def test_config_optional_fields():
    """선택적 필드 테스트"""
    from bot.config import Config
    
    # 선택적 필드가 있는 설정
    config = Config(
        binance_api_key="test_key",
        binance_secret_key="test_secret",
        binance_testnet=False,
        binance_api_url="https://api.binance.com",
        database_path="./test.db",
        log_level="INFO",
        log_file="./test.log",
        trading_symbol="BTCUSDT",
        initial_capital=1000000.0,
        max_position_size=0.1,
        stop_loss_percent=0.02,
        take_profit_percent=0.04,
        telegram_bot_token="test_token",
        telegram_chat_id="test_chat_id"
    )
    
    assert config.telegram_bot_token == "test_token"
    assert config.telegram_chat_id == "test_chat_id"
    assert config.selected_coins_file == "./selected_coins.json"  # 기본값
    assert config.max_coins == 50  # 기본값

def test_config_debug_backtest_modes():
    """디버그 및 백테스트 모드 테스트"""
    from bot.config import Config
    
    # 디버그 모드 True, 백테스트 모드 True
    with patch.dict(os.environ, {
        'BINANCE_API_KEY': 'test_key',
        'BINANCE_SECRET_KEY': 'test_secret',
        'BINANCE_TESTNET': 'false',
        'BINANCE_API_URL': 'https://test.api.com',
        'DATABASE_PATH': './test.db',
        'LOG_LEVEL': 'DEBUG',
        'LOG_FILE': './test.log',
        'TRADING_SYMBOL': 'BTCUSDT',
        'INITIAL_CAPITAL': '1000000.0',
        'MAX_POSITION_SIZE': '0.1',
        'STOP_LOSS_PERCENT': '0.02',
        'TAKE_PROFIT_PERCENT': '0.04',
        'DEBUG_MODE': 'true',
        'BACKTEST_MODE': 'true'
    }):
        config = Config.from_env()
        assert config.debug_mode is True
        assert config.backtest_mode is True
    
    # 디버그 모드 False, 백테스트 모드 False
    with patch.dict(os.environ, {
        'BINANCE_API_KEY': 'test_key',
        'BINANCE_SECRET_KEY': 'test_secret',
        'BINANCE_TESTNET': 'false',
        'BINANCE_API_URL': 'https://test.api.com',
        'DATABASE_PATH': './test.db',
        'LOG_LEVEL': 'DEBUG',
        'LOG_FILE': './test.log',
        'TRADING_SYMBOL': 'BTCUSDT',
        'INITIAL_CAPITAL': '1000000.0',
        'MAX_POSITION_SIZE': '0.1',
        'STOP_LOSS_PERCENT': '0.02',
        'TAKE_PROFIT_PERCENT': '0.04',
        'DEBUG_MODE': 'false',
        'BACKTEST_MODE': 'false'
    }):
        config = Config.from_env()
        assert config.debug_mode is False
        assert config.backtest_mode is False

def test_config_custom_coins_settings():
    """커스텀 코인 설정 테스트"""
    from bot.config import Config
    
    with patch.dict(os.environ, {
        'BINANCE_API_KEY': 'test_key',
        'BINANCE_SECRET_KEY': 'test_secret',
        'BINANCE_TESTNET': 'false',
        'BINANCE_API_URL': 'https://test.api.com',
        'DATABASE_PATH': './test.db',
        'LOG_LEVEL': 'DEBUG',
        'LOG_FILE': './test.log',
        'TRADING_SYMBOL': 'BTCUSDT',
        'INITIAL_CAPITAL': '1000000.0',
        'MAX_POSITION_SIZE': '0.1',
        'STOP_LOSS_PERCENT': '0.02',
        'TAKE_PROFIT_PERCENT': '0.04',
        'SELECTED_COINS_FILE': './custom_coins.json',
        'MAX_COINS': '100'
    }):
        config = Config.from_env()
        assert config.selected_coins_file == "./custom_coins.json"
        assert config.max_coins == 100

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 