"""
실시간 WebSocket 클라이언트
"""

import json
import threading
import time
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import websocket
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.config import Config
from config.coins_config import CoinsConfig
from data.database import Database

class BinanceWebSocketClient:
    """Binance WebSocket 클라이언트"""
    
    def __init__(self, config: Config, coins_config: CoinsConfig, database: Database):
        """WebSocket 클라이언트 초기화"""
        self.config = config
        self.coins_config = coins_config
        self.database = database
        self.logger = logging.getLogger(__name__)
        
        # WebSocket 설정
        self.base_url = "wss://stream.binance.com:9443/ws"
        self.is_connected = False
        self.ws = None
        
        # 데이터 저장소
        self.realtime_data = {}
        self.callbacks = []
        
        # 연결 관리
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5  # 초
        
        self.logger.info("Binance WebSocket 클라이언트 초기화 완료")
    
    def on_message(self, ws, message):
        """메시지 수신 처리"""
        try:
            data = json.loads(message)
            
            # 스트림 타입 확인
            if 'stream' in data:
                stream_data = data['data']
                symbol = stream_data['s']
                
                # 실시간 데이터 저장
                realtime_info = {
                    'symbol': symbol,
                    'price': float(stream_data['c']),  # 현재 가격
                    'volume': float(stream_data['v']),  # 거래량
                    'timestamp': int(stream_data['E']),  # 이벤트 시간
                    'price_change': float(stream_data['P']),  # 가격 변화
                    'price_change_percent': float(stream_data['P']),  # 가격 변화율
                    'high_24h': float(stream_data['h']),  # 24시간 최고가
                    'low_24h': float(stream_data['l']),  # 24시간 최저가
                }
                
                # 데이터베이스에 저장
                self.database.save_realtime_data(
                    symbol, 
                    realtime_info['price'], 
                    realtime_info['volume'], 
                    realtime_info['timestamp']
                )
                
                # 메모리에 저장
                self.realtime_data[symbol] = realtime_info
                
                # 콜백 실행
                for callback in self.callbacks:
                    try:
                        callback(realtime_info)
                    except Exception as e:
                        self.logger.error(f"콜백 실행 오류: {e}")
                
                self.logger.debug(f"{symbol}: ${realtime_info['price']:.4f}")
                
        except Exception as e:
            self.logger.error(f"메시지 처리 오류: {e}")
    
    def on_error(self, ws, error):
        """오류 처리"""
        self.logger.error(f"WebSocket 오류: {error}")
        self.is_connected = False
    
    def on_close(self, ws, close_status_code, close_msg):
        """연결 종료 처리"""
        self.logger.warning("WebSocket 연결 종료")
        self.is_connected = False
        
        # 재연결 시도
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            self.logger.info(f"재연결 시도 {self.reconnect_attempts}/{self.max_reconnect_attempts}")
            time.sleep(self.reconnect_delay)
            self.connect()
    
    def on_open(self, ws):
        """연결 시작 처리"""
        self.logger.info("WebSocket 연결 성공")
        self.is_connected = True
        self.reconnect_attempts = 0
    
    def connect(self):
        """WebSocket 연결"""
        try:
            # 50개 코인 스트림 구독
            symbols = self.coins_config.coins
            streams = [f"{symbol.lower()}@ticker" for symbol in symbols]
            
            # 스트림 URL 생성 (최대 200개 스트림)
            stream_url = f"{self.base_url}/{'/'.join(streams)}"
            
            self.logger.info(f"WebSocket 연결 시도: {len(symbols)}개 코인")
            
            # WebSocket 연결
            self.ws = websocket.WebSocketApp(
                stream_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # 별도 스레드에서 실행
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
        except Exception as e:
            self.logger.error(f"WebSocket 연결 실패: {e}")
            self.is_connected = False
    
    def disconnect(self):
        """WebSocket 연결 해제"""
        if self.ws:
            self.ws.close()
        self.is_connected = False
        self.logger.info("WebSocket 연결 해제")
    
    def add_callback(self, callback: Callable):
        """콜백 함수 추가"""
        self.callbacks.append(callback)
    
    def get_realtime_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """실시간 데이터 조회"""
        return self.realtime_data.get(symbol)
    
    def get_all_realtime_data(self) -> Dict[str, Any]:
        """모든 실시간 데이터 조회"""
        return self.realtime_data.copy()
    
    def start_streaming(self):
        """실시간 스트리밍 시작"""
        self.logger.info("실시간 데이터 스트리밍 시작")
        self.connect()
        
        # 연결 상태 모니터링
        while True:
            try:
                if not self.is_connected:
                    self.logger.warning("연결이 끊어짐, 재연결 시도...")
                    time.sleep(5)
                    continue
                
                # 연결 상태 로그 (1분마다)
                time.sleep(60)
                self.logger.info(f"연결 상태: {len(self.realtime_data)}개 코인 데이터 수신 중")
                
            except KeyboardInterrupt:
                self.logger.info("사용자에 의해 중단됨")
                break
            except Exception as e:
                self.logger.error(f"스트리밍 오류: {e}")
                time.sleep(5)
        
        self.disconnect()

# 사용 예시
if __name__ == "__main__":
    # 설정 로드
    from bot.config import Config
    from config.coins_config import CoinsConfig
    from data.database import Database
    
    config = Config.from_env()
    coins_config = CoinsConfig()
    database = Database()
    
    # WebSocket 클라이언트 생성
    ws_client = BinanceWebSocketClient(config, coins_config, database)
    
    # 콜백 함수 정의
    def on_data_received(data):
        print(f"실시간 데이터: {data['symbol']} - ${data['price']:.4f}")
    
    # 콜백 등록
    ws_client.add_callback(on_data_received)
    
    # 스트리밍 시작 (10초만 테스트)
    print("실시간 데이터 스트리밍 테스트 (10초)...")
    ws_client.connect()
    
    time.sleep(10)
    
    # 실시간 데이터 조회
    all_data = ws_client.get_all_realtime_data()
    print(f"수집된 실시간 데이터: {len(all_data)}개 코인")
    
    # 연결 해제
    ws_client.disconnect() 