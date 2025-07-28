#!/usr/bin/env python3
"""
CoinsConfig 클래스 80% 커버리지 테스트
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, mock_open

def test_coins_config_init():
    """CoinsConfig 초기화 테스트"""
    from config.coins_config import CoinsConfig
    
    coins_config = CoinsConfig()
    assert coins_config is not None
    assert hasattr(coins_config, 'coins')
    assert hasattr(coins_config, 'config_file')
    assert coins_config.config_file == "selected_coins.json"

def test_load_selected_coins_success():
    """선택된 코인 로드 성공 테스트"""
    from config.coins_config import CoinsConfig
    
    test_data = {
        "coins": ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"]
    }
    
    with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
        with patch("json.load", return_value=test_data):
            coins_config = CoinsConfig()
            assert len(coins_config.coins) == 5
            assert "BTCUSDT" in coins_config.coins
            assert "ETHUSDT" in coins_config.coins

def test_load_selected_coins_file_not_found():
    """파일 없음 테스트"""
    from config.coins_config import CoinsConfig
    
    with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
        coins_config = CoinsConfig()
        assert coins_config.coins == []

def test_load_selected_coins_json_error():
    """JSON 파싱 오류 테스트"""
    from config.coins_config import CoinsConfig
    
    with patch("builtins.open", mock_open(read_data="invalid json")):
        with patch("json.load", side_effect=json.JSONDecodeError("Invalid JSON", "", 0)):
            coins_config = CoinsConfig()
            assert coins_config.coins == []

def test_get_coin_details():
    """코인 상세 정보 조회 테스트"""
    from config.coins_config import CoinsConfig
    
    test_data = {
        "coins": ["BTCUSDT", "ETHUSDT"],
        "details": [
            {"symbol": "BTCUSDT", "name": "Bitcoin", "category": "Layer 1"},
            {"symbol": "ETHUSDT", "name": "Ethereum", "category": "Layer 1"}
        ]
    }
    
    with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
        with patch("json.load", return_value=test_data):
            coins_config = CoinsConfig()
            details = coins_config.get_coin_details()
            assert len(details) == 2
            assert details[0]["symbol"] == "BTCUSDT"
            assert details[1]["symbol"] == "ETHUSDT"

def test_get_coin_details_error():
    """코인 상세 정보 조회 오류 테스트"""
    from config.coins_config import CoinsConfig
    
    with patch("builtins.open", side_effect=Exception("Test error")):
        coins_config = CoinsConfig()
        details = coins_config.get_coin_details()
        assert details == []

def test_get_top_coins():
    """상위 N개 코인 조회 테스트"""
    from config.coins_config import CoinsConfig
    
    test_data = {
        "coins": ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"]
    }
    
    with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
        with patch("json.load", return_value=test_data):
            coins_config = CoinsConfig()
            
            # 상위 3개 코인 조회
            top_3 = coins_config.get_top_coins(3)
            assert len(top_3) == 3
            assert top_3 == ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
            
            # 상위 10개 코인 조회 (전체보다 많음)
            top_10 = coins_config.get_top_coins(10)
            assert len(top_10) == 5
            assert top_10 == ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"]

def test_get_coin_by_index():
    """인덱스로 코인 조회 테스트"""
    from config.coins_config import CoinsConfig
    
    test_data = {
        "coins": ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"]
    }
    
    with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
        with patch("json.load", return_value=test_data):
            coins_config = CoinsConfig()
            
            # 유효한 인덱스
            assert coins_config.get_coin_by_index(0) == "BTCUSDT"
            assert coins_config.get_coin_by_index(2) == "ADAUSDT"
            assert coins_config.get_coin_by_index(4) == "LINKUSDT"
            
            # 범위 밖 인덱스
            assert coins_config.get_coin_by_index(-1) is None
            assert coins_config.get_coin_by_index(5) is None
            assert coins_config.get_coin_by_index(10) is None

def test_get_total_coins():
    """총 코인 수 조회 테스트"""
    from config.coins_config import CoinsConfig
    
    test_data = {
        "coins": ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"]
    }
    
    with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
        with patch("json.load", return_value=test_data):
            coins_config = CoinsConfig()
            assert coins_config.get_total_coins() == 5

def test_print_coins_summary():
    """코인 요약 출력 테스트"""
    from config.coins_config import CoinsConfig
    
    test_data = {
        "coins": ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"]
    }
    
    with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
        with patch("json.load", return_value=test_data):
            coins_config = CoinsConfig()
            
            # 출력 테스트 (예외 없이 실행되는지 확인)
            try:
                coins_config.print_coins_summary()
                assert True  # 예외 없이 실행됨
            except Exception as e:
                assert False, f"출력 중 오류 발생: {e}"

def test_coins_config_with_empty_list():
    """빈 코인 리스트 테스트"""
    from config.coins_config import CoinsConfig
    
    test_data = {
        "coins": []
    }
    
    with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
        with patch("json.load", return_value=test_data):
            coins_config = CoinsConfig()
            assert coins_config.coins == []
            assert coins_config.get_total_coins() == 0
            assert coins_config.get_top_coins(5) == []
            assert coins_config.get_coin_by_index(0) is None

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 