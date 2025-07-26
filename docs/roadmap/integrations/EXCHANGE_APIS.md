# 🔗 거래소 API 통합 가이드 (Exchange API Integration Guide)

## 🎯 개요
이 문서는 AutoGrowthTradingSystem에서 다양한 암호화폐 거래소와의 API 통합 방법을 설명합니다.

## 📊 지원 거래소 목록

### 🌍 글로벌 거래소
- **Binance**: 세계 최대 거래소
- **Coinbase**: 미국 최대 거래소
- **Kraken**: 유럽 주요 거래소
- **Bitfinex**: 유동성 높은 거래소
- **OKX**: 아시아 주요 거래소

### 🇰🇷 국내 거래소
- **Upbit**: 한국 최대 거래소
- **Bithumb**: 한국 주요 거래소
- **Korbit**: 한국 거래소
- **Coinone**: 한국 거래소

## 🔧 API 통합 아키텍처

### 📊 전체 구조
```python
# 거래소 API 통합 아키텍처
class ExchangeAPIManager:
    def __init__(self):
        self.exchanges = {}
        self.rate_limiters = {}
        self.connection_pools = {}
    
    def register_exchange(self, exchange_name: str, api_config: Dict):
        """거래소 등록"""
        exchange_class = self.get_exchange_class(exchange_name)
        self.exchanges[exchange_name] = exchange_class(api_config)
        self.rate_limiters[exchange_name] = RateLimiter(api_config['rate_limits'])
        self.connection_pools[exchange_name] = ConnectionPool(api_config['pool_size'])
    
    def get_exchange(self, exchange_name: str):
        """거래소 인스턴스 반환"""
        return self.exchanges.get(exchange_name)
    
    def execute_order(self, exchange_name: str, order_data: Dict):
        """주문 실행"""
        exchange = self.get_exchange(exchange_name)
        rate_limiter = self.rate_limiters[exchange_name]
        
        # Rate Limiting 확인
        if not rate_limiter.check_limit('order'):
            raise RateLimitExceeded(f"Rate limit exceeded for {exchange_name}")
        
        # 주문 실행
        return exchange.place_order(order_data)
```

### 🔄 공통 인터페이스
```python
# 거래소 공통 인터페이스
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class ExchangeInterface(ABC):
    """거래소 공통 인터페이스"""
    
    @abstractmethod
    def get_ticker(self, symbol: str) -> Dict:
        """현재가 조회"""
        pass
    
    @abstractmethod
    def get_orderbook(self, symbol: str, depth: int = 20) -> Dict:
        """호가창 조회"""
        pass
    
    @abstractmethod
    def place_order(self, order_data: Dict) -> Dict:
        """주문 실행"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str) -> Dict:
        """주문 취소"""
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str, symbol: str) -> Dict:
        """주문 상태 조회"""
        pass
    
    @abstractmethod
    def get_balance(self) -> Dict:
        """잔고 조회"""
        pass
    
    @abstractmethod
    def get_trade_history(self, symbol: str, limit: int = 100) -> List[Dict]:
        """거래 내역 조회"""
        pass
```

## 🔐 인증 및 보안

### 🔑 API 키 관리
```python
# API 키 관리 시스템
import os
import base64
from cryptography.fernet import Fernet
from typing import Dict

class APIKeyManager:
    def __init__(self):
        self.encryption_key = self.load_or_generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def load_or_generate_key(self) -> bytes:
        """암호화 키 로드 또는 생성"""
        key_file = "api_keys.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key
    
    def encrypt_api_key(self, api_key: str) -> str:
        """API 키 암호화"""
        encrypted = self.cipher_suite.encrypt(api_key.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """API 키 복호화"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_key.encode())
        decrypted = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    def store_api_keys(self, exchange_name: str, api_keys: Dict):
        """API 키 저장"""
        encrypted_keys = {}
        for key_name, key_value in api_keys.items():
            encrypted_keys[key_name] = self.encrypt_api_key(key_value)
        
        # 데이터베이스에 저장
        self.save_to_database(exchange_name, encrypted_keys)
    
    def get_api_keys(self, exchange_name: str) -> Dict:
        """API 키 조회"""
        encrypted_keys = self.load_from_database(exchange_name)
        decrypted_keys = {}
        for key_name, encrypted_value in encrypted_keys.items():
            decrypted_keys[key_name] = self.decrypt_api_key(encrypted_value)
        return decrypted_keys
```

### 🔒 요청 서명
```python
# 요청 서명 생성
import hmac
import hashlib
import time
from urllib.parse import urlencode

class RequestSigner:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
    
    def sign_request(self, method: str, endpoint: str, params: Dict, timestamp: int = None) -> str:
        """요청 서명 생성"""
        if timestamp is None:
            timestamp = int(time.time() * 1000)
        
        # 쿼리 문자열 생성
        query_string = urlencode(params)
        
        # 서명할 문자열 생성
        sign_string = f"{method}&{endpoint}&{query_string}&{timestamp}"
        
        # HMAC-SHA256 서명 생성
        signature = hmac.new(
            self.secret_key,
            sign_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_signature(self, method: str, endpoint: str, params: Dict, signature: str, timestamp: int) -> bool:
        """서명 검증"""
        expected_signature = self.sign_request(method, endpoint, params, timestamp)
        return hmac.compare_digest(signature, expected_signature)
```

## 📊 거래소별 구현

### 🟡 Binance API
```python
# Binance API 구현
import requests
import time
from typing import Dict, List

class BinanceAPI(ExchangeInterface):
    def __init__(self, api_config: Dict):
        self.api_key = api_config['api_key']
        self.secret_key = api_config['secret_key']
        self.base_url = "https://api.binance.com"
        self.testnet = api_config.get('testnet', False)
        
        if self.testnet:
            self.base_url = "https://testnet.binance.vision"
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key
        })
    
    def get_ticker(self, symbol: str) -> Dict:
        """현재가 조회"""
        endpoint = "/api/v3/ticker/price"
        params = {'symbol': symbol}
        
        response = self.session.get(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_orderbook(self, symbol: str, depth: int = 20) -> Dict:
        """호가창 조회"""
        endpoint = "/api/v3/depth"
        params = {
            'symbol': symbol,
            'limit': depth
        }
        
        response = self.session.get(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
        
        return response.json()
    
    def place_order(self, order_data: Dict) -> Dict:
        """주문 실행"""
        endpoint = "/api/v3/order"
        
        # 필수 파라미터 검증
        required_fields = ['symbol', 'side', 'type', 'quantity']
        for field in required_fields:
            if field not in order_data:
                raise ValueError(f"Missing required field: {field}")
        
        # 타임스탬프 추가
        order_data['timestamp'] = int(time.time() * 1000)
        
        # 서명 생성
        signer = RequestSigner(self.secret_key)
        signature = signer.sign_request('POST', endpoint, order_data, order_data['timestamp'])
        order_data['signature'] = signature
        
        response = self.session.post(f"{self.base_url}{endpoint}", data=order_data)
        response.raise_for_status()
        
        return response.json()
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict:
        """주문 취소"""
        endpoint = "/api/v3/order"
        params = {
            'symbol': symbol,
            'orderId': order_id,
            'timestamp': int(time.time() * 1000)
        }
        
        # 서명 생성
        signer = RequestSigner(self.secret_key)
        signature = signer.sign_request('DELETE', endpoint, params, params['timestamp'])
        params['signature'] = signature
        
        response = self.session.delete(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_order_status(self, order_id: str, symbol: str) -> Dict:
        """주문 상태 조회"""
        endpoint = "/api/v3/order"
        params = {
            'symbol': symbol,
            'orderId': order_id,
            'timestamp': int(time.time() * 1000)
        }
        
        # 서명 생성
        signer = RequestSigner(self.secret_key)
        signature = signer.sign_request('GET', endpoint, params, params['timestamp'])
        params['signature'] = signature
        
        response = self.session.get(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_balance(self) -> Dict:
        """잔고 조회"""
        endpoint = "/api/v3/account"
        params = {'timestamp': int(time.time() * 1000)}
        
        # 서명 생성
        signer = RequestSigner(self.secret_key)
        signature = signer.sign_request('GET', endpoint, params, params['timestamp'])
        params['signature'] = signature
        
        response = self.session.get(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_trade_history(self, symbol: str, limit: int = 100) -> List[Dict]:
        """거래 내역 조회"""
        endpoint = "/api/v3/myTrades"
        params = {
            'symbol': symbol,
            'limit': limit,
            'timestamp': int(time.time() * 1000)
        }
        
        # 서명 생성
        signer = RequestSigner(self.secret_key)
        signature = signer.sign_request('GET', endpoint, params, params['timestamp'])
        params['signature'] = signature
        
        response = self.session.get(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
        
        return response.json()
```

### 🔵 Upbit API
```python
# Upbit API 구현
import jwt
import uuid
from typing import Dict, List

class UpbitAPI(ExchangeInterface):
    def __init__(self, api_config: Dict):
        self.access_key = api_config['access_key']
        self.secret_key = api_config['secret_key']
        self.base_url = "https://api.upbit.com/v1"
        
        self.session = requests.Session()
    
    def _create_jwt_token(self, query: str = None) -> str:
        """JWT 토큰 생성"""
        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4())
        }
        
        if query:
            payload['query'] = query
        
        jwt_token = jwt.encode(payload, self.secret_key)
        return jwt_token
    
    def get_ticker(self, symbol: str) -> Dict:
        """현재가 조회"""
        endpoint = "/ticker"
        params = {'markets': symbol}
        
        response = self.session.get(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
        
        return response.json()[0]  # Upbit는 배열로 반환
    
    def get_orderbook(self, symbol: str, depth: int = 20) -> Dict:
        """호가창 조회"""
        endpoint = "/orderbook"
        params = {'markets': symbol}
        
        response = self.session.get(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
        
        return response.json()[0]
    
    def place_order(self, order_data: Dict) -> Dict:
        """주문 실행"""
        endpoint = "/orders"
        
        # 필수 파라미터 검증
        required_fields = ['market', 'side', 'ord_type', 'volume']
        for field in required_fields:
            if field not in order_data:
                raise ValueError(f"Missing required field: {field}")
        
        # JWT 토큰 생성
        jwt_token = self._create_jwt_token()
        
        headers = {
            'Authorization': f'Bearer {jwt_token}'
        }
        
        response = self.session.post(f"{self.base_url}{endpoint}", json=order_data, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict:
        """주문 취소"""
        endpoint = "/order"
        
        data = {
            'uuid': order_id
        }
        
        # JWT 토큰 생성
        jwt_token = self._create_jwt_token()
        
        headers = {
            'Authorization': f'Bearer {jwt_token}'
        }
        
        response = self.session.delete(f"{self.base_url}{endpoint}", json=data, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_order_status(self, order_id: str, symbol: str) -> Dict:
        """주문 상태 조회"""
        endpoint = "/order"
        params = {'uuid': order_id}
        
        # JWT 토큰 생성
        jwt_token = self._create_jwt_token()
        
        headers = {
            'Authorization': f'Bearer {jwt_token}'
        }
        
        response = self.session.get(f"{self.base_url}{endpoint}", params=params, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_balance(self) -> Dict:
        """잔고 조회"""
        endpoint = "/accounts"
        
        # JWT 토큰 생성
        jwt_token = self._create_jwt_token()
        
        headers = {
            'Authorization': f'Bearer {jwt_token}'
        }
        
        response = self.session.get(f"{self.base_url}{endpoint}", headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_trade_history(self, symbol: str, limit: int = 100) -> List[Dict]:
        """거래 내역 조회"""
        endpoint = "/orders"
        params = {
            'market': symbol,
            'state': 'done',
            'limit': limit
        }
        
        # JWT 토큰 생성
        jwt_token = self._create_jwt_token()
        
        headers = {
            'Authorization': f'Bearer {jwt_token}'
        }
        
        response = self.session.get(f"{self.base_url}{endpoint}", params=params, headers=headers)
        response.raise_for_status()
        
        return response.json()
```

## 🔄 Rate Limiting 및 에러 처리

### ⏱️ Rate Limiting
```python
# Rate Limiting 구현
import time
from collections import defaultdict
from typing import Dict, Optional

class RateLimiter:
    def __init__(self, rate_limits: Dict):
        self.rate_limits = rate_limits
        self.request_counts = defaultdict(list)
    
    def check_limit(self, endpoint: str) -> bool:
        """Rate Limit 확인"""
        current_time = time.time()
        window_size = self.rate_limits.get(endpoint, {}).get('window', 60)  # 60초
        max_requests = self.rate_limits.get(endpoint, {}).get('max_requests', 100)
        
        # 현재 윈도우의 요청 수 계산
        window_start = current_time - window_size
        requests_in_window = [
            req_time for req_time in self.request_counts[endpoint]
            if req_time > window_start
        ]
        
        # 윈도우 정리
        self.request_counts[endpoint] = requests_in_window
        
        # Rate Limit 확인
        if len(requests_in_window) >= max_requests:
            return False
        
        # 요청 기록
        self.request_counts[endpoint].append(current_time)
        return True
    
    def wait_if_needed(self, endpoint: str):
        """필요시 대기"""
        while not self.check_limit(endpoint):
            time.sleep(1)  # 1초 대기
```

### ❌ 에러 처리
```python
# 에러 처리 클래스
class ExchangeAPIError(Exception):
    """거래소 API 에러 기본 클래스"""
    def __init__(self, message: str, error_code: str = None, exchange: str = None):
        super().__init__(message)
        self.error_code = error_code
        self.exchange = exchange

class RateLimitExceeded(ExchangeAPIError):
    """Rate Limit 초과 에러"""
    pass

class InsufficientBalance(ExchangeAPIError):
    """잔고 부족 에러"""
    pass

class InvalidOrder(ExchangeAPIError):
    """잘못된 주문 에러"""
    pass

class NetworkError(ExchangeAPIError):
    """네트워크 에러"""
    pass

# 에러 처리 함수
def handle_exchange_error(response, exchange_name: str):
    """거래소 에러 처리"""
    if response.status_code == 429:
        raise RateLimitExceeded("Rate limit exceeded", exchange=exchange_name)
    elif response.status_code == 400:
        error_data = response.json()
        if 'insufficient balance' in error_data.get('msg', '').lower():
            raise InsufficientBalance("Insufficient balance", exchange=exchange_name)
        else:
            raise InvalidOrder(f"Invalid order: {error_data.get('msg', '')}", exchange=exchange_name)
    elif response.status_code >= 500:
        raise NetworkError("Server error", exchange=exchange_name)
    else:
        raise ExchangeAPIError(f"API error: {response.status_code}", exchange=exchange_name)
```

## 📊 데이터 동기화

### 🔄 실시간 데이터 수집
```python
# WebSocket 실시간 데이터 수집
import asyncio
import websockets
import json
from typing import Dict, Callable

class WebSocketManager:
    def __init__(self):
        self.connections = {}
        self.callbacks = {}
    
    async def connect(self, exchange: str, url: str, channels: List[str]):
        """WebSocket 연결"""
        try:
            websocket = await websockets.connect(url)
            self.connections[exchange] = websocket
            
            # 구독 메시지 전송
            for channel in channels:
                subscribe_message = self.create_subscribe_message(exchange, channel)
                await websocket.send(json.dumps(subscribe_message))
            
            # 메시지 수신 루프 시작
            asyncio.create_task(self.message_loop(exchange, websocket))
            
        except Exception as e:
            print(f"WebSocket connection failed for {exchange}: {e}")
    
    async def message_loop(self, exchange: str, websocket):
        """메시지 수신 루프"""
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.process_message(exchange, data)
        except websockets.exceptions.ConnectionClosed:
            print(f"WebSocket connection closed for {exchange}")
        except Exception as e:
            print(f"Error in message loop for {exchange}: {e}")
    
    async def process_message(self, exchange: str, data: Dict):
        """메시지 처리"""
        if exchange in self.callbacks:
            for callback in self.callbacks[exchange]:
                try:
                    await callback(data)
                except Exception as e:
                    print(f"Error in callback for {exchange}: {e}")
    
    def add_callback(self, exchange: str, callback: Callable):
        """콜백 함수 추가"""
        if exchange not in self.callbacks:
            self.callbacks[exchange] = []
        self.callbacks[exchange].append(callback)
    
    def create_subscribe_message(self, exchange: str, channel: str) -> Dict:
        """구독 메시지 생성"""
        if exchange == 'binance':
            return {
                "method": "SUBSCRIBE",
                "params": [channel],
                "id": 1
            }
        elif exchange == 'upbit':
            return [{"ticket": "UNIQUE_TICKET"}, {"type": "ticker", "codes": [channel]}]
        else:
            return {}
```

## 📋 통합 체크리스트

### ✅ 설정 단계
- [ ] **API 키 발급**: 각 거래소에서 API 키 발급
- [ ] **권한 설정**: 필요한 권한 설정 (거래, 조회 등)
- [ ] **IP 화이트리스트**: 허용된 IP 등록
- [ ] **테스트넷 설정**: 테스트 환경에서 먼저 테스트

### ✅ 구현 단계
- [ ] **공통 인터페이스**: ExchangeInterface 구현
- [ ] **거래소별 구현**: 각 거래소별 API 클래스 구현
- [ ] **인증 시스템**: API 키 관리 및 서명 생성
- [ ] **에러 처리**: 거래소별 에러 처리 구현
- [ ] **Rate Limiting**: 요청 제한 구현

### ✅ 테스트 단계
- [ ] **단위 테스트**: 각 API 메서드 테스트
- [ ] **통합 테스트**: 전체 플로우 테스트
- [ ] **성능 테스트**: Rate Limiting 테스트
- [ ] **에러 테스트**: 다양한 에러 상황 테스트
- [ ] **보안 테스트**: API 키 보안 테스트

### ✅ 운영 단계
- [ ] **모니터링**: API 호출 모니터링
- [ ] **로깅**: 모든 API 호출 로깅
- [ ] **알림**: 에러 발생 시 알림
- [ ] **백업**: API 키 백업 및 복구
- [ ] **문서화**: API 사용법 문서화

## 📚 참고 자료

- [Binance API 문서](https://binance-docs.github.io/apidocs/spot/en/)
- [Upbit API 문서](https://docs.upbit.com/)
- [Coinbase API 문서](https://docs.cloud.coinbase.com/)
- [Kraken API 문서](https://www.kraken.com/features/api)
- [암호화폐 거래소 API 비교](https://github.com/ccxt/ccxt)

---

**마지막 업데이트**: 2024-01-15
**버전**: 1.0.0
**담당자**: 개발팀 