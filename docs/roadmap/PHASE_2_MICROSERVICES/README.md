# 🏗️ Phase 2: 마이크로서비스 아키텍처

## 📋 **개요**

### 🎯 **목표**
- **서비스 분리**: 모놀리식을 마이크로서비스로 분해
- **독립적 배포**: 각 서비스의 독립적인 개발 및 배포
- **확장성**: 서비스별 독립적 스케일링
- **장애 격리**: 서비스별 장애 격리 및 복구

### 📊 **성능 목표**
- **서비스 응답 시간**: < 100ms (95th percentile)
- **서비스 가용성**: 99.9% (각 서비스별)
- **배포 시간**: < 5분 (각 서비스별)
- **장애 복구 시간**: < 30초 (자동 복구)

## 🏗️ **마이크로서비스 아키텍처**

### 📁 **서비스 구조**
```
microservices/
├── trading-service/              # 거래 서비스
│   ├── order-management/         # 주문 관리
│   ├── position-management/      # 포지션 관리
│   └── risk-management/          # 리스크 관리
├── user-service/                 # 사용자 서비스
│   ├── authentication/           # 인증
│   ├── authorization/            # 권한 관리
│   └── profile-management/       # 프로필 관리
├── market-data-service/          # 시장 데이터 서비스
│   ├── real-time-data/           # 실시간 데이터
│   ├── historical-data/          # 히스토리 데이터
│   └── data-aggregation/         # 데이터 집계
├── notification-service/          # 알림 서비스
│   ├── email-service/            # 이메일
│   ├── push-notification/        # 푸시 알림
│   └── sms-service/              # SMS
├── analytics-service/            # 분석 서비스
│   ├── performance-analysis/     # 성능 분석
│   ├── risk-analysis/            # 리스크 분석
│   └── reporting/                # 리포팅
└── infrastructure/               # 인프라 서비스
    ├── service-discovery/        # 서비스 디스커버리
    ├── api-gateway/              # API 게이트웨이
    ├── load-balancer/            # 로드 밸런서
    └── monitoring/               # 모니터링
```

## 🔧 **핵심 서비스 상세**

### 📦 **거래 서비스 (Trading Service)**

#### **주문 관리 서비스**
```python
# microservices/trading-service/order-management/order_service.py
from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)

class OrderService:
    """주문 관리 서비스"""
    
    def __init__(self):
        self.app = FastAPI(title="Order Management Service")
        self.setup_routes()
        self.order_repository = OrderRepository()
        self.event_bus = EventBus()
    
    def setup_routes(self):
        """API 라우트 설정"""
        
        @self.app.post("/orders/")
        async def create_order(order_data: OrderCreate):
            """주문 생성"""
            try:
                order = await self.order_repository.create_order(order_data)
                await self.event_bus.publish("order.created", order)
                return order
            except Exception as e:
                logger.error(f"Failed to create order: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/orders/{order_id}")
        async def get_order(order_id: str):
            """주문 조회"""
            try:
                order = await self.order_repository.get_order(order_id)
                if not order:
                    raise HTTPException(status_code=404, detail="Order not found")
                return order
            except Exception as e:
                logger.error(f"Failed to get order: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.put("/orders/{order_id}/status")
        async def update_order_status(order_id: str, status: OrderStatus):
            """주문 상태 업데이트"""
            try:
                order = await self.order_repository.update_order_status(order_id, status)
                await self.event_bus.publish("order.status_updated", order)
                return order
            except Exception as e:
                logger.error(f"Failed to update order status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/orders/user/{user_id}")
        async def get_user_orders(user_id: str, limit: int = 100, offset: int = 0):
            """사용자 주문 목록 조회"""
            try:
                orders = await self.order_repository.get_user_orders(user_id, limit, offset)
                return orders
            except Exception as e:
                logger.error(f"Failed to get user orders: {e}")
                raise HTTPException(status_code=500, detail=str(e))

class OrderRepository:
    """주문 저장소"""
    
    def __init__(self):
        self.db = Database()
    
    async def create_order(self, order_data: OrderCreate) -> Order:
        """주문 생성"""
        order = Order(
            id=generate_order_id(),
            user_id=order_data.user_id,
            symbol=order_data.symbol,
            side=order_data.side,
            quantity=order_data.quantity,
            price=order_data.price,
            order_type=order_data.order_type,
            status=OrderStatus.PENDING,
            created_at=datetime.now()
        )
        
        await self.db.insert("orders", order.dict())
        return order
    
    async def get_order(self, order_id: str) -> Optional[Order]:
        """주문 조회"""
        result = await self.db.find_one("orders", {"id": order_id})
        return Order(**result) if result else None
    
    async def update_order_status(self, order_id: str, status: OrderStatus) -> Order:
        """주문 상태 업데이트"""
        order = await self.get_order(order_id)
        if not order:
            raise ValueError("Order not found")
        
        order.status = status
        order.updated_at = datetime.now()
        
        await self.db.update("orders", {"id": order_id}, order.dict())
        return order
    
    async def get_user_orders(self, user_id: str, limit: int, offset: int) -> List[Order]:
        """사용자 주문 목록 조회"""
        results = await self.db.find(
            "orders", 
            {"user_id": user_id},
            limit=limit,
            offset=offset,
            sort=[("created_at", -1)]
        )
        
        return [Order(**result) for result in results]

class EventBus:
    """이벤트 버스"""
    
    def __init__(self):
        self.kafka_producer = KafkaProducer()
    
    async def publish(self, event_type: str, data: Any):
        """이벤트 발행"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "id": generate_event_id()
        }
        
        await self.kafka_producer.send("trading-events", event)
        logger.info(f"Published event: {event_type}")

# Pydantic 모델
class OrderCreate(BaseModel):
    user_id: str
    symbol: str
    side: str  # BUY, SELL
    quantity: float
    price: Optional[float] = None
    order_type: str  # MARKET, LIMIT, STOP

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class Order(BaseModel):
    id: str
    user_id: str
    symbol: str
    side: str
    quantity: float
    price: Optional[float]
    order_type: str
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
```

#### **포지션 관리 서비스**
```python
# microservices/trading-service/position-management/position_service.py
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import asyncio

class PositionService:
    """포지션 관리 서비스"""
    
    def __init__(self):
        self.app = FastAPI(title="Position Management Service")
        self.setup_routes()
        self.position_repository = PositionRepository()
        self.risk_manager = RiskManager()
    
    def setup_routes(self):
        """API 라우트 설정"""
        
        @self.app.get("/positions/{user_id}")
        async def get_user_positions(user_id: str):
            """사용자 포지션 조회"""
            try:
                positions = await self.position_repository.get_user_positions(user_id)
                return positions
            except Exception as e:
                logger.error(f"Failed to get user positions: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/positions/update")
        async def update_position(position_data: PositionUpdate):
            """포지션 업데이트"""
            try:
                # 리스크 검증
                risk_check = await self.risk_manager.validate_position(position_data)
                if not risk_check['valid']:
                    raise HTTPException(status_code=400, detail=risk_check['reason'])
                
                position = await self.position_repository.update_position(position_data)
                return position
            except Exception as e:
                logger.error(f"Failed to update position: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/positions/{user_id}/pnl")
        async def get_user_pnl(user_id: str):
            """사용자 P&L 조회"""
            try:
                pnl = await self.position_repository.calculate_user_pnl(user_id)
                return pnl
            except Exception as e:
                logger.error(f"Failed to get user PnL: {e}")
                raise HTTPException(status_code=500, detail=str(e))

class PositionRepository:
    """포지션 저장소"""
    
    def __init__(self):
        self.db = Database()
    
    async def get_user_positions(self, user_id: str) -> List[Position]:
        """사용자 포지션 조회"""
        results = await self.db.find("positions", {"user_id": user_id})
        return [Position(**result) for result in results]
    
    async def update_position(self, position_data: PositionUpdate) -> Position:
        """포지션 업데이트"""
        existing_position = await self.db.find_one(
            "positions", 
            {"user_id": position_data.user_id, "symbol": position_data.symbol}
        )
        
        if existing_position:
            # 기존 포지션 업데이트
            position = Position(**existing_position)
            position.quantity += position_data.quantity_change
            position.avg_price = self._calculate_avg_price(
                position.quantity, position.avg_price,
                position_data.quantity_change, position_data.price
            )
            position.updated_at = datetime.now()
        else:
            # 새 포지션 생성
            position = Position(
                user_id=position_data.user_id,
                symbol=position_data.symbol,
                quantity=position_data.quantity_change,
                avg_price=position_data.price,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        await self.db.upsert("positions", {"user_id": position.user_id, "symbol": position.symbol}, position.dict())
        return position
    
    async def calculate_user_pnl(self, user_id: str) -> Dict[str, float]:
        """사용자 P&L 계산"""
        positions = await self.get_user_positions(user_id)
        total_pnl = 0.0
        
        for position in positions:
            # 현재 가격 조회 (실제로는 시장 데이터 서비스에서 조회)
            current_price = await self._get_current_price(position.symbol)
            pnl = (current_price - position.avg_price) * position.quantity
            total_pnl += pnl
        
        return {
            "total_pnl": total_pnl,
            "positions_count": len(positions)
        }
    
    def _calculate_avg_price(self, current_qty: float, current_avg: float, 
                           new_qty: float, new_price: float) -> float:
        """평균 가격 계산"""
        total_qty = current_qty + new_qty
        if total_qty == 0:
            return 0.0
        
        return (current_qty * current_avg + new_qty * new_price) / total_qty
    
    async def _get_current_price(self, symbol: str) -> float:
        """현재 가격 조회"""
        # 실제로는 시장 데이터 서비스 호출
        return 50000.0  # 예시 값

class RiskManager:
    """리스크 관리자"""
    
    def __init__(self):
        self.position_limits = {
            "max_position_size": 1000000,  # 100만 달러
            "max_leverage": 10,  # 10배 레버리지
            "max_daily_loss": 100000  # 10만 달러
        }
    
    async def validate_position(self, position_data: PositionUpdate) -> Dict[str, Any]:
        """포지션 검증"""
        try:
            # 포지션 크기 검증
            position_value = abs(position_data.quantity_change * position_data.price)
            if position_value > self.position_limits["max_position_size"]:
                return {
                    "valid": False,
                    "reason": f"Position size {position_value} exceeds limit {self.position_limits['max_position_size']}"
                }
            
            # 레버리지 검증
            user_balance = await self._get_user_balance(position_data.user_id)
            leverage = position_value / user_balance if user_balance > 0 else float('inf')
            if leverage > self.position_limits["max_leverage"]:
                return {
                    "valid": False,
                    "reason": f"Leverage {leverage} exceeds limit {self.position_limits['max_leverage']}"
                }
            
            # 일일 손실 한도 검증
            daily_pnl = await self._get_daily_pnl(position_data.user_id)
            if daily_pnl < -self.position_limits["max_daily_loss"]:
                return {
                    "valid": False,
                    "reason": f"Daily loss {abs(daily_pnl)} exceeds limit {self.position_limits['max_daily_loss']}"
                }
            
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Position validation failed: {e}")
            return {"valid": False, "reason": str(e)}
    
    async def _get_user_balance(self, user_id: str) -> float:
        """사용자 잔고 조회"""
        # 실제로는 사용자 서비스 호출
        return 100000.0  # 예시 값
    
    async def _get_daily_pnl(self, user_id: str) -> float:
        """일일 P&L 조회"""
        # 실제로는 분석 서비스 호출
        return -50000.0  # 예시 값

# Pydantic 모델
class PositionUpdate(BaseModel):
    user_id: str
    symbol: str
    quantity_change: float  # 양수: 매수, 음수: 매도
    price: float

class Position(BaseModel):
    user_id: str
    symbol: str
    quantity: float
    avg_price: float
    created_at: datetime
    updated_at: datetime
```

### 📦 **사용자 서비스 (User Service)**

#### **인증 서비스**
```python
# microservices/user-service/authentication/auth_service.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import bcrypt
import asyncio

class AuthService:
    """인증 서비스"""
    
    def __init__(self):
        self.app = FastAPI(title="Authentication Service")
        self.setup_routes()
        self.user_repository = UserRepository()
        self.jwt_secret = "your-secret-key"
        self.jwt_algorithm = "HS256"
        self.access_token_expire_minutes = 30
        
        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    
    def setup_routes(self):
        """API 라우트 설정"""
        
        @self.app.post("/register")
        async def register(user_data: UserRegister):
            """사용자 등록"""
            try:
                # 이메일 중복 확인
                existing_user = await self.user_repository.get_user_by_email(user_data.email)
                if existing_user:
                    raise HTTPException(status_code=400, detail="Email already registered")
                
                # 비밀번호 해싱
                hashed_password = bcrypt.hashpw(
                    user_data.password.encode('utf-8'), 
                    bcrypt.gensalt()
                ).decode('utf-8')
                
                # 사용자 생성
                user = User(
                    email=user_data.email,
                    username=user_data.username,
                    hashed_password=hashed_password,
                    created_at=datetime.now()
                )
                
                created_user = await self.user_repository.create_user(user)
                return {"message": "User registered successfully", "user_id": created_user.id}
                
            except Exception as e:
                logger.error(f"Registration failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/token")
        async def login(form_data: OAuth2PasswordRequestForm = Depends()):
            """로그인"""
            try:
                user = await self.user_repository.get_user_by_email(form_data.username)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Incorrect email or password",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                if not bcrypt.checkpw(form_data.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Incorrect email or password",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                # JWT 토큰 생성
                access_token = self.create_access_token(
                    data={"sub": user.email}
                )
                
                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user_id": user.id,
                    "email": user.email
                }
                
            except Exception as e:
                logger.error(f"Login failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/me")
        async def get_current_user(token: str = Depends(oauth2_scheme)):
            """현재 사용자 정보 조회"""
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
                email: str = payload.get("sub")
                if email is None:
                    raise HTTPException(status_code=401, detail="Invalid token")
                
                user = await self.user_repository.get_user_by_email(email)
                if user is None:
                    raise HTTPException(status_code=401, detail="User not found")
                
                return user
                
            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=401, detail="Token expired")
            except jwt.JWTError:
                raise HTTPException(status_code=401, detail="Invalid token")
            except Exception as e:
                logger.error(f"Get current user failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/refresh")
        async def refresh_token(token: str = Depends(oauth2_scheme)):
            """토큰 갱신"""
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
                email: str = payload.get("sub")
                if email is None:
                    raise HTTPException(status_code=401, detail="Invalid token")
                
                # 새 토큰 생성
                new_token = self.create_access_token(data={"sub": email})
                
                return {
                    "access_token": new_token,
                    "token_type": "bearer"
                }
                
            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=401, detail="Token expired")
            except jwt.JWTError:
                raise HTTPException(status_code=401, detail="Invalid token")
    
    def create_access_token(self, data: dict):
        """액세스 토큰 생성"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.jwt_secret, algorithm=self.jwt_algorithm)
        return encoded_jwt

class UserRepository:
    """사용자 저장소"""
    
    def __init__(self):
        self.db = Database()
    
    async def create_user(self, user: User) -> User:
        """사용자 생성"""
        user.id = generate_user_id()
        await self.db.insert("users", user.dict())
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        result = await self.db.find_one("users", {"email": email})
        return User(**result) if result else None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """ID로 사용자 조회"""
        result = await self.db.find_one("users", {"id": user_id})
        return User(**result) if result else None

# Pydantic 모델
class UserRegister(BaseModel):
    email: str
    username: str
    password: str

class User(BaseModel):
    id: Optional[str] = None
    email: str
    username: str
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None
```

### 📦 **시장 데이터 서비스 (Market Data Service)**

#### **실시간 데이터 서비스**
```python
# microservices/market-data-service/real-time-data/market_data_service.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class MarketDataService:
    """시장 데이터 서비스"""
    
    def __init__(self):
        self.app = FastAPI(title="Market Data Service")
        self.setup_routes()
        self.data_providers = {}
        self.subscribers = {}
        self.price_cache = {}
        
    def setup_routes(self):
        """API 라우트 설정"""
        
        @self.app.get("/prices/{symbol}")
        async def get_current_price(symbol: str):
            """현재 가격 조회"""
            try:
                price = await self.get_price(symbol)
                if not price:
                    raise HTTPException(status_code=404, detail="Symbol not found")
                return price
            except Exception as e:
                logger.error(f"Failed to get price for {symbol}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/prices")
        async def get_multiple_prices(symbols: str):
            """여러 심볼 가격 조회"""
            try:
                symbol_list = symbols.split(',')
                prices = {}
                for symbol in symbol_list:
                    price = await self.get_price(symbol.strip())
                    if price:
                        prices[symbol.strip()] = price
                return prices
            except Exception as e:
                logger.error(f"Failed to get multiple prices: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.websocket("/ws/prices/{symbol}")
        async def websocket_price_feed(websocket: WebSocket, symbol: str):
            """웹소켓 가격 피드"""
            await websocket.accept()
            try:
                # 구독자 등록
                if symbol not in self.subscribers:
                    self.subscribers[symbol] = []
                self.subscribers[symbol].append(websocket)
                
                # 초기 가격 전송
                current_price = await self.get_price(symbol)
                if current_price:
                    await websocket.send_text(json.dumps(current_price))
                
                # 실시간 업데이트 수신
                while True:
                    data = await websocket.receive_text()
                    # 클라이언트로부터의 메시지 처리 (필요시)
                    
            except WebSocketDisconnect:
                # 구독자 제거
                if symbol in self.subscribers:
                    self.subscribers[symbol].remove(websocket)
                logger.info(f"WebSocket disconnected for {symbol}")
            except Exception as e:
                logger.error(f"WebSocket error for {symbol}: {e}")
    
    async def get_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """가격 조회"""
        try:
            # 캐시 확인
            if symbol in self.price_cache:
                cached_price = self.price_cache[symbol]
                if (datetime.now() - cached_price['timestamp']).seconds < 5:  # 5초 캐시
                    return cached_price['data']
            
            # 데이터 제공자에서 조회
            price_data = await self._fetch_price_from_provider(symbol)
            if price_data:
                # 캐시 업데이트
                self.price_cache[symbol] = {
                    'data': price_data,
                    'timestamp': datetime.now()
                }
                
                # 구독자들에게 브로드캐스트
                await self._broadcast_price_update(symbol, price_data)
                
                return price_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
            return None
    
    async def _fetch_price_from_provider(self, symbol: str) -> Optional[Dict[str, Any]]:
        """데이터 제공자에서 가격 조회"""
        try:
            # 실제 구현에서는 여러 거래소 API 호출
            # 여기서는 예시 데이터 반환
            return {
                "symbol": symbol,
                "price": 50000.0,
                "volume": 1000.0,
                "change_24h": 2.5,
                "high_24h": 52000.0,
                "low_24h": 48000.0,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to fetch price from provider: {e}")
            return None
    
    async def _broadcast_price_update(self, symbol: str, price_data: Dict[str, Any]):
        """가격 업데이트 브로드캐스트"""
        if symbol in self.subscribers:
            message = json.dumps(price_data)
            disconnected_subscribers = []
            
            for websocket in self.subscribers[symbol]:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Failed to send to subscriber: {e}")
                    disconnected_subscribers.append(websocket)
            
            # 연결이 끊어진 구독자 제거
            for websocket in disconnected_subscribers:
                self.subscribers[symbol].remove(websocket)
    
    async def start_data_feed(self):
        """데이터 피드 시작"""
        while True:
            try:
                # 주요 심볼들의 가격 업데이트
                symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT", "DOT/USDT"]
                
                for symbol in symbols:
                    await self.get_price(symbol)
                
                await asyncio.sleep(1)  # 1초마다 업데이트
                
            except Exception as e:
                logger.error(f"Data feed error: {e}")
                await asyncio.sleep(5)

class DataProvider:
    """데이터 제공자"""
    
    def __init__(self, name: str, api_url: str):
        self.name = name
        self.api_url = api_url
        self.session = aiohttp.ClientSession()
    
    async def get_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """가격 조회"""
        try:
            url = f"{self.api_url}/prices/{symbol}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "provider": self.name,
                        "symbol": symbol,
                        "price": data["price"],
                        "volume": data["volume"],
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    logger.warning(f"Failed to get price from {self.name}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching from {self.name}: {e}")
            return None
    
    async def close(self):
        """세션 종료"""
        await self.session.close()
```

## 🔧 **서비스 간 통신**

### 📦 **API 게이트웨이**

```python
# microservices/infrastructure/api-gateway/gateway.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import httpx
import asyncio
import logging

logger = logging.getLogger(__name__)

class APIGateway:
    """API 게이트웨이"""
    
    def __init__(self):
        self.app = FastAPI(title="API Gateway")
        self.setup_middleware()
        self.setup_routes()
        self.service_registry = ServiceRegistry()
        self.circuit_breaker = CircuitBreaker()
        
    def setup_middleware(self):
        """미들웨어 설정"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """라우트 설정"""
        
        @self.app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def proxy_request(request: Request, path: str):
            """요청 프록시"""
            try:
                # 서비스 라우팅
                service_name = self._get_service_name(path)
                service_url = await self.service_registry.get_service_url(service_name)
                
                if not service_url:
                    raise HTTPException(status_code=404, detail="Service not found")
                
                # 서킷 브레이커 확인
                if not self.circuit_breaker.is_available(service_name):
                    raise HTTPException(status_code=503, detail="Service temporarily unavailable")
                
                # 요청 전달
                response = await self._forward_request(request, service_url, path)
                return response
                
            except Exception as e:
                logger.error(f"Gateway error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _get_service_name(self, path: str) -> str:
        """경로에서 서비스 이름 추출"""
        path_parts = path.split('/')
        if path_parts[0] == 'api':
            return path_parts[1] if len(path_parts) > 1 else 'default'
        return path_parts[0] if path_parts else 'default'
    
    async def _forward_request(self, request: Request, service_url: str, path: str):
        """요청 전달"""
        try:
            # 요청 본문 읽기
            body = await request.body()
            
            # 헤더 준비
            headers = dict(request.headers)
            headers.pop('host', None)  # host 헤더 제거
            
            # URL 구성
            target_url = f"{service_url}/{path}"
            
            # HTTP 클라이언트로 요청 전달
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                    params=request.query_params
                )
                
                return response
                
        except Exception as e:
            logger.error(f"Request forwarding failed: {e}")
            raise

class ServiceRegistry:
    """서비스 레지스트리"""
    
    def __init__(self):
        self.services = {
            'trading': 'http://trading-service:8000',
            'user': 'http://user-service:8001',
            'market-data': 'http://market-data-service:8002',
            'notification': 'http://notification-service:8003',
            'analytics': 'http://analytics-service:8004'
        }
    
    async def get_service_url(self, service_name: str) -> Optional[str]:
        """서비스 URL 조회"""
        return self.services.get(service_name)

class CircuitBreaker:
    """서킷 브레이커"""
    
    def __init__(self):
        self.failure_counts = {}
        self.last_failure_times = {}
        self.threshold = 5
        self.timeout = 60  # 60초
    
    def is_available(self, service_name: str) -> bool:
        """서비스 사용 가능 여부 확인"""
        if service_name not in self.failure_counts:
            return True
        
        failure_count = self.failure_counts[service_name]
        last_failure_time = self.last_failure_times.get(service_name)
        
        # 임계값 초과 시 타임아웃 확인
        if failure_count >= self.threshold:
            if last_failure_time:
                time_since_failure = (datetime.now() - last_failure_time).seconds
                if time_since_failure < self.timeout:
                    return False
                else:
                    # 타임아웃 후 리셋
                    self.failure_counts[service_name] = 0
                    return True
        
        return True
    
    def record_failure(self, service_name: str):
        """실패 기록"""
        if service_name not in self.failure_counts:
            self.failure_counts[service_name] = 0
        
        self.failure_counts[service_name] += 1
        self.last_failure_times[service_name] = datetime.now()
    
    def record_success(self, service_name: str):
        """성공 기록"""
        if service_name in self.failure_counts:
            self.failure_counts[service_name] = 0
```

## 📚 **관련 문서**

### **Phase 2 상세 문서**
- [2.1 마이크로서비스 아키텍처](2.1_ARCHITECTURE.md) - 아키텍처 설계 및 서비스 분리
- [2.2 서비스 디스커버리](2.2_SERVICE_DISCOVERY.md) - 서비스 등록 및 발견
- [2.3 로드 밸런싱](2.3_LOAD_BALANCING.md) - 트래픽 분산 및 고가용성
- [2.4 모니터링](2.4_MONITORING.md) - 서비스 모니터링 및 관찰성

### **다른 Phase 문서**
- [Phase 1: 기능 확장](../PHASE_1_EXPANSION/README.md)
- [Phase 3: AI/ML 플랫폼](../PHASE_3_AI_ML/README.md)

## 🎯 **다음 단계**

### 📋 **완료된 작업**
- ✅ 마이크로서비스 아키텍처 설계
- ✅ 핵심 서비스 구조 정의
- ✅ 서비스 간 통신 설계
- ✅ API 게이트웨이 구현
- ✅ 모든 Phase 2 문서 생성 완료

### 🔄 **진행 중인 작업**
- 🔄 실제 서비스 개발 준비
- 🔄 개발 환경 설정

### ⏳ **다음 단계**
1. **Phase 0 개발 시작** (2025-02-01)
2. **실제 마이크로서비스 구현**
3. **서비스별 독립적 개발 및 배포**

---

**마지막 업데이트**: 2025-07-26
**다음 업데이트**: 2025-02-01 (Phase 0 개발 시작)
**문서화 상태**: 완료 ✅
**개발 상태**: 시작 전 ⏳
**마이크로서비스 목표**: < 100ms 응답시간, 99.9% 가용성, < 5분 배포시간
**장애 복구**: < 30초 자동 복구 