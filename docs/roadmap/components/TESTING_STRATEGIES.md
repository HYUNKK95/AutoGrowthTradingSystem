# 🧪 테스트 전략

## 📋 **개요**

### 🎯 **목표**
- **테스트 커버리지**: 95% 이상 코드 커버리지 달성
- **테스트 자동화**: CI/CD 파이프라인 통합 자동화
- **성능 테스트**: 부하 테스트 및 성능 벤치마크
- **보안 테스트**: 취약점 스캔 및 보안 테스트
- **통합 테스트**: 전체 시스템 통합 테스트

### 📊 **테스트 목표**
- **단위 테스트**: 100% 핵심 로직 테스트
- **통합 테스트**: 100% API 엔드포인트 테스트
- **성능 테스트**: P95 < 200ms 응답 시간
- **보안 테스트**: 0건 보안 취약점
- **E2E 테스트**: 100% 사용자 시나리오 테스트

## 🏗️ **테스트 시스템 아키텍처**

### 📁 **테스트 시스템 구조**
```
testing/
├── unit-tests/                        # 단위 테스트
│   ├── models/                       # 모델 테스트
│   ├── services/                     # 서비스 테스트
│   ├── validators/                   # 검증기 테스트
│   └── utilities/                    # 유틸리티 테스트
├── integration-tests/                 # 통합 테스트
│   ├── api-tests/                    # API 테스트
│   ├── database-tests/               # 데이터베이스 테스트
│   ├── external-service-tests/       # 외부 서비스 테스트
│   └── end-to-end-tests/             # E2E 테스트
├── performance-tests/                 # 성능 테스트
│   ├── load-tests/                   # 부하 테스트
│   ├── stress-tests/                 # 스트레스 테스트
│   ├── scalability-tests/            # 확장성 테스트
│   └── benchmark-tests/              # 벤치마크 테스트
├── security-tests/                    # 보안 테스트
│   ├── vulnerability-scanning/       # 취약점 스캔
│   ├── penetration-tests/            # 침투 테스트
│   ├── security-audit/               # 보안 감사
│   └── compliance-tests/             # 규정 준수 테스트
└── test-automation/                   # 테스트 자동화
    ├── ci-cd-integration/            # CI/CD 통합
    ├── test-reporting/               # 테스트 리포트
    ├── test-monitoring/              # 테스트 모니터링
    └── test-maintenance/             # 테스트 유지보수
```

## 🔧 **단위 테스트 시스템**

### 📦 **모델 및 서비스 테스트**

```python
# testing/unit-tests/test_models.py
import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from decimal import Decimal
import json

from src.models.order import Order, OrderType, OrderStatus
from src.models.user import User
from src.models.portfolio import Portfolio
from src.exceptions import ValidationError, InsufficientBalanceError

class TestOrderModel:
    """주문 모델 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.user = User(
            user_id="test_user_001",
            username="testuser",
            email="test@example.com",
            balance=Decimal("10000.00")
        )
        
        self.valid_order_data = {
            "user_id": "test_user_001",
            "symbol": "BTC/USDT",
            "order_type": OrderType.LIMIT,
            "side": "BUY",
            "quantity": Decimal("1.0"),
            "price": Decimal("50000.00"),
            "timestamp": datetime.now()
        }
    
    def test_order_creation_valid_data(self):
        """유효한 데이터로 주문 생성 테스트"""
        order = Order(**self.valid_order_data)
        
        assert order.user_id == "test_user_001"
        assert order.symbol == "BTC/USDT"
        assert order.order_type == OrderType.LIMIT
        assert order.side == "BUY"
        assert order.quantity == Decimal("1.0")
        assert order.price == Decimal("50000.00")
        assert order.status == OrderStatus.PENDING
        assert order.order_id is not None
        assert len(order.order_id) > 0
    
    def test_order_creation_invalid_symbol(self):
        """잘못된 심볼로 주문 생성 테스트"""
        invalid_data = self.valid_order_data.copy()
        invalid_data["symbol"] = "INVALID/PAIR"
        
        with pytest.raises(ValidationError, match="Invalid trading pair"):
            Order(**invalid_data)
    
    def test_order_creation_invalid_quantity(self):
        """잘못된 수량으로 주문 생성 테스트"""
        invalid_data = self.valid_order_data.copy()
        invalid_data["quantity"] = Decimal("-1.0")
        
        with pytest.raises(ValidationError, match="Quantity must be positive"):
            Order(**invalid_data)
    
    def test_order_creation_invalid_price(self):
        """잘못된 가격으로 주문 생성 테스트"""
        invalid_data = self.valid_order_data.copy()
        invalid_data["price"] = Decimal("0.0")
        
        with pytest.raises(ValidationError, match="Price must be positive"):
            Order(**invalid_data)
    
    def test_order_status_transitions(self):
        """주문 상태 전환 테스트"""
        order = Order(**self.valid_order_data)
        
        # PENDING -> FILLED
        assert order.status == OrderStatus.PENDING
        order.fill(Decimal("1.0"), Decimal("50000.00"))
        assert order.status == OrderStatus.FILLED
        assert order.filled_quantity == Decimal("1.0")
        assert order.filled_price == Decimal("50000.00")
        
        # FILLED -> CANCELLED (이미 체결된 주문은 취소 불가)
        with pytest.raises(ValidationError, match="Cannot cancel filled order"):
            order.cancel()
    
    def test_order_partial_fill(self):
        """부분 체결 테스트"""
        order = Order(**self.valid_order_data)
        
        # 부분 체결
        order.fill(Decimal("0.5"), Decimal("50000.00"))
        assert order.status == OrderStatus.PARTIALLY_FILLED
        assert order.filled_quantity == Decimal("0.5")
        assert order.remaining_quantity == Decimal("0.5")
        
        # 나머지 체결
        order.fill(Decimal("0.5"), Decimal("50000.00"))
        assert order.status == OrderStatus.FILLED
        assert order.filled_quantity == Decimal("1.0")
        assert order.remaining_quantity == Decimal("0.0")
    
    def test_order_cancellation(self):
        """주문 취소 테스트"""
        order = Order(**self.valid_order_data)
        
        assert order.status == OrderStatus.PENDING
        order.cancel()
        assert order.status == OrderStatus.CANCELLED
        assert order.cancelled_at is not None
    
    def test_order_serialization(self):
        """주문 직렬화 테스트"""
        order = Order(**self.valid_order_data)
        
        # JSON 직렬화
        order_dict = order.to_dict()
        assert isinstance(order_dict, dict)
        assert order_dict["user_id"] == "test_user_001"
        assert order_dict["symbol"] == "BTC/USDT"
        
        # JSON 문자열 직렬화
        order_json = order.to_json()
        assert isinstance(order_json, str)
        
        # 역직렬화
        order_from_dict = Order.from_dict(order_dict)
        assert order_from_dict.user_id == order.user_id
        assert order_from_dict.symbol == order.symbol
    
    def test_order_validation_rules(self):
        """주문 검증 규칙 테스트"""
        # 최소 주문 수량
        invalid_data = self.valid_order_data.copy()
        invalid_data["quantity"] = Decimal("0.001")  # 최소 수량 미만
        
        with pytest.raises(ValidationError, match="Minimum order quantity"):
            Order(**invalid_data)
        
        # 최대 주문 수량
        invalid_data = self.valid_order_data.copy()
        invalid_data["quantity"] = Decimal("1000000.0")  # 최대 수량 초과
        
        with pytest.raises(ValidationError, match="Maximum order quantity"):
            Order(**invalid_data)
        
        # 가격 정밀도
        invalid_data = self.valid_order_data.copy()
        invalid_data["price"] = Decimal("50000.123456")  # 정밀도 초과
        
        with pytest.raises(ValidationError, match="Price precision"):
            Order(**invalid_data)

class TestUserModel:
    """사용자 모델 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.valid_user_data = {
            "user_id": "test_user_001",
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "hashed_password_123"
        }
    
    def test_user_creation(self):
        """사용자 생성 테스트"""
        user = User(**self.valid_user_data)
        
        assert user.user_id == "test_user_001"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active == True
        assert user.created_at is not None
    
    def test_user_email_validation(self):
        """사용자 이메일 검증 테스트"""
        invalid_data = self.valid_user_data.copy()
        invalid_data["email"] = "invalid-email"
        
        with pytest.raises(ValidationError, match="Invalid email format"):
            User(**invalid_data)
    
    def test_user_balance_operations(self):
        """사용자 잔고 작업 테스트"""
        user = User(**self.valid_user_data)
        user.balance = Decimal("1000.00")
        
        # 잔고 증가
        user.add_balance(Decimal("500.00"))
        assert user.balance == Decimal("1500.00")
        
        # 잔고 감소
        user.subtract_balance(Decimal("200.00"))
        assert user.balance == Decimal("1300.00")
        
        # 잔고 부족
        with pytest.raises(InsufficientBalanceError):
            user.subtract_balance(Decimal("2000.00"))
    
    def test_user_deactivation(self):
        """사용자 비활성화 테스트"""
        user = User(**self.valid_user_data)
        
        assert user.is_active == True
        user.deactivate()
        assert user.is_active == False
        assert user.deactivated_at is not None

class TestPortfolioModel:
    """포트폴리오 모델 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.user = User(
            user_id="test_user_001",
            username="testuser",
            email="test@example.com"
        )
        
        self.portfolio = Portfolio(user_id="test_user_001")
    
    def test_portfolio_creation(self):
        """포트폴리오 생성 테스트"""
        assert self.portfolio.user_id == "test_user_001"
        assert self.portfolio.positions == {}
        assert self.portfolio.total_value == Decimal("0.00")
    
    def test_add_position(self):
        """포지션 추가 테스트"""
        self.portfolio.add_position("BTC", Decimal("1.0"), Decimal("50000.00"))
        
        assert "BTC" in self.portfolio.positions
        assert self.portfolio.positions["BTC"].quantity == Decimal("1.0")
        assert self.portfolio.positions["BTC"].avg_price == Decimal("50000.00")
    
    def test_update_position(self):
        """포지션 업데이트 테스트"""
        # 초기 포지션
        self.portfolio.add_position("BTC", Decimal("1.0"), Decimal("50000.00"))
        
        # 포지션 업데이트
        self.portfolio.update_position("BTC", Decimal("0.5"), Decimal("55000.00"))
        
        position = self.portfolio.positions["BTC"]
        assert position.quantity == Decimal("1.5")
        assert position.avg_price == Decimal("51666.67")  # (50000 + 27500) / 1.5
    
    def test_remove_position(self):
        """포지션 제거 테스트"""
        self.portfolio.add_position("BTC", Decimal("1.0"), Decimal("50000.00"))
        
        self.portfolio.remove_position("BTC", Decimal("1.0"))
        assert "BTC" not in self.portfolio.positions
    
    def test_portfolio_value_calculation(self):
        """포트폴리오 가치 계산 테스트"""
        # 여러 포지션 추가
        self.portfolio.add_position("BTC", Decimal("1.0"), Decimal("50000.00"))
        self.portfolio.add_position("ETH", Decimal("10.0"), Decimal("3000.00"))
        
        # 현재 가격으로 가치 계산
        current_prices = {
            "BTC": Decimal("55000.00"),
            "ETH": Decimal("3200.00")
        }
        
        total_value = self.portfolio.calculate_total_value(current_prices)
        expected_value = Decimal("55000.00") + Decimal("32000.00")  # 87000.00
        
        assert total_value == expected_value
```

## 🔧 **통합 테스트 시스템**

### 📦 **API 및 데이터베이스 테스트**

```python
# testing/integration-tests/test_api.py
import pytest
import requests
import json
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock

from src.api.app import create_app
from src.database.connection import get_database_connection
from src.models.order import Order, OrderType, OrderStatus

class TestAPIEndpoints:
    """API 엔드포인트 테스트"""
    
    @pytest.fixture
    def app(self):
        """테스트 앱 생성"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['DATABASE_URL'] = 'sqlite:///:memory:'
        return app
    
    @pytest.fixture
    def client(self, app):
        """테스트 클라이언트 생성"""
        return app.test_client()
    
    @pytest.fixture
    def auth_headers(self):
        """인증 헤더 생성"""
        return {
            'Authorization': 'Bearer test_token_123',
            'Content-Type': 'application/json'
        }
    
    def test_health_check(self, client):
        """헬스 체크 엔드포인트 테스트"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_create_order_success(self, client, auth_headers):
        """주문 생성 성공 테스트"""
        order_data = {
            "symbol": "BTC/USDT",
            "order_type": "LIMIT",
            "side": "BUY",
            "quantity": "1.0",
            "price": "50000.00"
        }
        
        with patch('src.services.order_service.OrderService.create_order') as mock_create:
            mock_order = MagicMock()
            mock_order.order_id = "order_123"
            mock_order.status = OrderStatus.PENDING
            mock_create.return_value = mock_order
            
            response = client.post(
                '/api/orders',
                data=json.dumps(order_data),
                headers=auth_headers
            )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['order_id'] == "order_123"
        assert data['status'] == "PENDING"
    
    def test_create_order_invalid_data(self, client, auth_headers):
        """잘못된 데이터로 주문 생성 테스트"""
        invalid_order_data = {
            "symbol": "INVALID/PAIR",
            "order_type": "LIMIT",
            "side": "BUY",
            "quantity": "-1.0",  # 음수 수량
            "price": "50000.00"
        }
        
        response = client.post(
            '/api/orders',
            data=json.dumps(invalid_order_data),
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_orders(self, client, auth_headers):
        """주문 조회 테스트"""
        with patch('src.services.order_service.OrderService.get_orders') as mock_get:
            mock_orders = [
                MagicMock(
                    order_id="order_123",
                    symbol="BTC/USDT",
                    status=OrderStatus.PENDING
                ),
                MagicMock(
                    order_id="order_124",
                    symbol="ETH/USDT",
                    status=OrderStatus.FILLED
                )
            ]
            mock_get.return_value = mock_orders
            
            response = client.get('/api/orders', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['orders']) == 2
        assert data['orders'][0]['order_id'] == "order_123"
    
    def test_get_order_by_id(self, client, auth_headers):
        """특정 주문 조회 테스트"""
        order_id = "order_123"
        
        with patch('src.services.order_service.OrderService.get_order_by_id') as mock_get:
            mock_order = MagicMock(
                order_id=order_id,
                symbol="BTC/USDT",
                status=OrderStatus.PENDING
            )
            mock_get.return_value = mock_order
            
            response = client.get(f'/api/orders/{order_id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['order_id'] == order_id
        assert data['symbol'] == "BTC/USDT"
    
    def test_cancel_order(self, client, auth_headers):
        """주문 취소 테스트"""
        order_id = "order_123"
        
        with patch('src.services.order_service.OrderService.cancel_order') as mock_cancel:
            mock_cancel.return_value = True
            
            response = client.delete(f'/api/orders/{order_id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == "Order cancelled successfully"
    
    def test_unauthorized_access(self, client):
        """인증되지 않은 접근 테스트"""
        response = client.get('/api/orders')
        
        assert response.status_code == 401
    
    def test_invalid_token(self, client):
        """잘못된 토큰 테스트"""
        headers = {
            'Authorization': 'Bearer invalid_token',
            'Content-Type': 'application/json'
        }
        
        response = client.get('/api/orders', headers=headers)
        
        assert response.status_code == 401

class TestDatabaseIntegration:
    """데이터베이스 통합 테스트"""
    
    @pytest.fixture
    def db_connection(self):
        """테스트 데이터베이스 연결"""
        connection = get_database_connection('sqlite:///:memory:')
        # 테이블 생성
        connection.execute("""
            CREATE TABLE orders (
                order_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                order_type TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity DECIMAL NOT NULL,
                price DECIMAL NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL
            )
        """)
        return connection
    
    def test_order_persistence(self, db_connection):
        """주문 저장 테스트"""
        order = Order(
            user_id="test_user_001",
            symbol="BTC/USDT",
            order_type=OrderType.LIMIT,
            side="BUY",
            quantity=Decimal("1.0"),
            price=Decimal("50000.00")
        )
        
        # 주문 저장
        db_connection.execute("""
            INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order.order_id,
            order.user_id,
            order.symbol,
            order.order_type.value,
            order.side,
            order.quantity,
            order.price,
            order.status.value,
            order.created_at
        ))
        
        # 주문 조회
        result = db_connection.execute("""
            SELECT * FROM orders WHERE order_id = ?
        """, (order.order_id,)).fetchone()
        
        assert result is not None
        assert result[1] == "test_user_001"
        assert result[2] == "BTC/USDT"
        assert result[3] == "LIMIT"
    
    def test_order_update(self, db_connection):
        """주문 업데이트 테스트"""
        # 초기 주문 저장
        order = Order(
            user_id="test_user_001",
            symbol="BTC/USDT",
            order_type=OrderType.LIMIT,
            side="BUY",
            quantity=Decimal("1.0"),
            price=Decimal("50000.00")
        )
        
        db_connection.execute("""
            INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order.order_id,
            order.user_id,
            order.symbol,
            order.order_type.value,
            order.side,
            order.quantity,
            order.price,
            order.status.value,
            order.created_at
        ))
        
        # 주문 상태 업데이트
        db_connection.execute("""
            UPDATE orders SET status = ? WHERE order_id = ?
        """, ("FILLED", order.order_id))
        
        # 업데이트 확인
        result = db_connection.execute("""
            SELECT status FROM orders WHERE order_id = ?
        """, (order.order_id,)).fetchone()
        
        assert result[0] == "FILLED"
    
    def test_order_deletion(self, db_connection):
        """주문 삭제 테스트"""
        # 주문 저장
        order = Order(
            user_id="test_user_001",
            symbol="BTC/USDT",
            order_type=OrderType.LIMIT,
            side="BUY",
            quantity=Decimal("1.0"),
            price=Decimal("50000.00")
        )
        
        db_connection.execute("""
            INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order.order_id,
            order.user_id,
            order.symbol,
            order.order_type.value,
            order.side,
            order.quantity,
            order.price,
            order.status.value,
            order.created_at
        ))
        
        # 주문 삭제
        db_connection.execute("""
            DELETE FROM orders WHERE order_id = ?
        """, (order.order_id,))
        
        # 삭제 확인
        result = db_connection.execute("""
            SELECT * FROM orders WHERE order_id = ?
        """, (order.order_id,)).fetchone()
        
        assert result is None
```

## 🔧 **성능 테스트 시스템**

### 📦 **부하 테스트 및 벤치마크**

```python
# testing/performance-tests/load_test.py
import asyncio
import time
import statistics
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import aiohttp
import asyncio
import concurrent.futures
import threading

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """테스트 결과"""
    test_id: str
    endpoint: str
    method: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    error_message: Optional[str]

@dataclass
class PerformanceMetrics:
    """성능 메트릭"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    min_response_time: float
    max_response_time: float
    requests_per_second: float
    error_rate: float

class LoadTester:
    """부하 테스트"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = []
        self.lock = threading.Lock()
        
        # 테스트 설정
        self.concurrent_users = 100
        self.test_duration = 300  # 5분
        self.ramp_up_time = 60   # 1분
        
        logger.info(f"Load tester initialized for {base_url}")
    
    async def run_load_test(self, endpoint: str, method: str = "GET", 
                          payload: Optional[Dict] = None) -> PerformanceMetrics:
        """부하 테스트 실행"""
        logger.info(f"Starting load test for {endpoint}")
        
        start_time = time.time()
        tasks = []
        
        # 동시 사용자 시뮬레이션
        for i in range(self.concurrent_users):
            task = asyncio.create_task(
                self._simulate_user(endpoint, method, payload, i)
            )
            tasks.append(task)
        
        # 모든 태스크 완료 대기
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        test_duration = end_time - start_time
        
        # 성능 메트릭 계산
        metrics = self._calculate_metrics(test_duration)
        
        logger.info(f"Load test completed. RPS: {metrics.requests_per_second:.2f}")
        return metrics
    
    async def _simulate_user(self, endpoint: str, method: str, 
                           payload: Optional[Dict], user_id: int):
        """사용자 시뮬레이션"""
        session = aiohttp.ClientSession()
        
        try:
            # 램프업 시간 동안 점진적 증가
            ramp_up_delay = self.ramp_up_time / self.concurrent_users * user_id
            await asyncio.sleep(ramp_up_delay)
            
            # 테스트 기간 동안 요청 전송
            end_time = time.time() + self.test_duration
            
            while time.time() < end_time:
                await self._send_request(session, endpoint, method, payload)
                
                # 요청 간 간격 (0.1초)
                await asyncio.sleep(0.1)
                
        finally:
            await session.close()
    
    async def _send_request(self, session: aiohttp.ClientSession, endpoint: str, 
                          method: str, payload: Optional[Dict]):
        """요청 전송"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                async with session.get(url) as response:
                    response_time = time.time() - start_time
                    await self._record_result(endpoint, method, response_time, 
                                            response.status, True)
            elif method.upper() == "POST":
                async with session.post(url, json=payload) as response:
                    response_time = time.time() - start_time
                    await self._record_result(endpoint, method, response_time, 
                                            response.status, True)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
        except Exception as e:
            response_time = time.time() - start_time
            await self._record_result(endpoint, method, response_time, 0, False, str(e))
    
    async def _record_result(self, endpoint: str, method: str, response_time: float,
                           status_code: int, success: bool, error_message: Optional[str] = None):
        """결과 기록"""
        result = TestResult(
            test_id=f"test_{int(time.time() * 1000)}",
            endpoint=endpoint,
            method=method,
            response_time=response_time,
            status_code=status_code,
            success=success,
            timestamp=datetime.now(),
            error_message=error_message
        )
        
        with self.lock:
            self.results.append(result)
    
    def _calculate_metrics(self, test_duration: float) -> PerformanceMetrics:
        """성능 메트릭 계산"""
        with self.lock:
            response_times = [r.response_time for r in self.results]
            successful_requests = len([r for r in self.results if r.success])
            failed_requests = len([r for r in self.results if not r.success])
            
            if not response_times:
                return PerformanceMetrics(
                    total_requests=0,
                    successful_requests=0,
                    failed_requests=0,
                    avg_response_time=0.0,
                    p50_response_time=0.0,
                    p95_response_time=0.0,
                    p99_response_time=0.0,
                    min_response_time=0.0,
                    max_response_time=0.0,
                    requests_per_second=0.0,
                    error_rate=0.0
                )
            
            sorted_times = sorted(response_times)
            
            metrics = PerformanceMetrics(
                total_requests=len(self.results),
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                avg_response_time=statistics.mean(response_times),
                p50_response_time=statistics.quantiles(sorted_times, n=2)[0],
                p95_response_time=statistics.quantiles(sorted_times, n=20)[18],
                p99_response_time=statistics.quantiles(sorted_times, n=100)[98],
                min_response_time=min(response_times),
                max_response_time=max(response_times),
                requests_per_second=len(self.results) / test_duration,
                error_rate=failed_requests / len(self.results) if self.results else 0.0
            )
            
            return metrics
    
    def get_detailed_results(self) -> List[TestResult]:
        """상세 결과 조회"""
        with self.lock:
            return self.results.copy()
    
    def clear_results(self):
        """결과 초기화"""
        with self.lock:
            self.results.clear()

class StressTester:
    """스트레스 테스트"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.load_tester = LoadTester(base_url)
        
        # 스트레스 테스트 설정
        self.max_concurrent_users = 1000
        self.step_size = 50
        self.step_duration = 60  # 1분
        
        logger.info(f"Stress tester initialized for {base_url}")
    
    async def run_stress_test(self, endpoint: str, method: str = "GET",
                            payload: Optional[Dict] = None) -> Dict[str, PerformanceMetrics]:
        """스트레스 테스트 실행"""
        logger.info(f"Starting stress test for {endpoint}")
        
        results = {}
        
        # 단계별로 부하 증가
        for concurrent_users in range(self.step_size, self.max_concurrent_users + 1, self.step_size):
            logger.info(f"Testing with {concurrent_users} concurrent users")
            
            # 부하 테스트 설정 조정
            self.load_tester.concurrent_users = concurrent_users
            self.load_tester.test_duration = self.step_duration
            
            # 부하 테스트 실행
            metrics = await self.load_tester.run_load_test(endpoint, method, payload)
            results[f"{concurrent_users}_users"] = metrics
            
            # 성능 임계값 확인
            if metrics.error_rate > 0.05 or metrics.p95_response_time > 1.0:
                logger.warning(f"Performance threshold exceeded at {concurrent_users} users")
                break
            
            # 결과 초기화
            self.load_tester.clear_results()
        
        return results

class BenchmarkTester:
    """벤치마크 테스트"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.load_tester = LoadTester(base_url)
        
        logger.info(f"Benchmark tester initialized for {base_url}")
    
    async def run_benchmark(self, endpoints: List[Dict]) -> Dict[str, PerformanceMetrics]:
        """벤치마크 테스트 실행"""
        logger.info("Starting benchmark test")
        
        results = {}
        
        for endpoint_config in endpoints:
            endpoint = endpoint_config['endpoint']
            method = endpoint_config.get('method', 'GET')
            payload = endpoint_config.get('payload')
            
            logger.info(f"Benchmarking {method} {endpoint}")
            
            # 벤치마크 실행
            metrics = await self.load_tester.run_load_test(endpoint, method, payload)
            results[endpoint] = metrics
            
            # 결과 초기화
            self.load_tester.clear_results()
        
        return results
    
    def generate_benchmark_report(self, results: Dict[str, PerformanceMetrics]) -> str:
        """벤치마크 리포트 생성"""
        report = "=== Benchmark Test Report ===\n\n"
        
        for endpoint, metrics in results.items():
            report += f"Endpoint: {endpoint}\n"
            report += f"  Total Requests: {metrics.total_requests}\n"
            report += f"  Successful Requests: {metrics.successful_requests}\n"
            report += f"  Failed Requests: {metrics.failed_requests}\n"
            report += f"  Error Rate: {metrics.error_rate:.2%}\n"
            report += f"  Requests/Second: {metrics.requests_per_second:.2f}\n"
            report += f"  Average Response Time: {metrics.avg_response_time:.3f}s\n"
            report += f"  P95 Response Time: {metrics.p95_response_time:.3f}s\n"
            report += f"  P99 Response Time: {metrics.p99_response_time:.3f}s\n"
            report += f"  Min Response Time: {metrics.min_response_time:.3f}s\n"
            report += f"  Max Response Time: {metrics.max_response_time:.3f}s\n\n"
        
        return report
```

## 🎯 **다음 단계**

### 📋 **완료된 작업**
- ✅ 단위 테스트 시스템 설계 (모델, 서비스, 검증기 테스트)
- ✅ 통합 테스트 시스템 설계 (API, 데이터베이스, E2E 테스트)
- ✅ 성능 테스트 시스템 설계 (부하 테스트, 스트레스 테스트, 벤치마크)

### 🔄 **진행 중인 작업**
- 🔄 보안 테스트 시스템 (취약점 스캔, 침투 테스트, 보안 감사)
- 🔄 테스트 자동화 시스템 (CI/CD 통합, 테스트 리포트, 모니터링)

### ⏳ **다음 단계**
1. **보안 테스트 시스템** 문서 생성
2. **테스트 자동화 시스템** 문서 생성
3. **공통 컴포넌트 완료**: 모든 공통 컴포넌트 문서 완성

---

**마지막 업데이트**: 2024-01-31
**다음 업데이트**: 2024-02-01 (보안 테스트 시스템)
**테스트 목표**: 95% 코드 커버리지, P95 < 200ms, 0건 보안 취약점
**테스트 성과**: 단위 테스트, 통합 테스트, 성능 테스트, 보안 테스트 