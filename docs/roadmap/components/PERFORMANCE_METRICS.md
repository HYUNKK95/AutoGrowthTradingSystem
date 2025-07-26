# 📊 성능 메트릭 가이드

## 📋 **개요**

### 🎯 **목적**
- **표준화**: 모든 Phase에서 일관된 성능 측정
- **모니터링**: 실시간 성능 추적 및 알림
- **최적화**: 성능 병목 지점 식별 및 개선
- **보고**: 성과 지표 및 트렌드 분석

### 📊 **적용 범위**
- **모든 Phase**: Phase 0-7 전체 적용
- **모든 시스템**: 핵심 시스템, 거래 시스템, 인프라
- **모든 환경**: 개발, 테스트, 운영 환경

## 📈 **핵심 성능 지표 (KPI)**

### ⚡ **응답 시간 (Response Time)**

#### **정의**
- **요청 시작**부터 **응답 완료**까지의 시간
- **단위**: 밀리초 (ms)
- **측정 지점**: 클라이언트 요청 → 서버 처리 → 응답 반환

#### **목표값**
```yaml
# Phase별 목표 응답 시간
Phase 0 (MVP):     P95 < 500ms
Phase 1 (확장):    P95 < 200ms
Phase 2 (마이크로서비스): P95 < 150ms
Phase 3 (AI/ML):   P95 < 300ms
Phase 4 (최적화):  P95 < 100ms
Phase 5-7 (고급):  P95 < 50ms
```

#### **측정 방법**
```python
import time
import logging
from functools import wraps

def measure_response_time(func):
    """응답 시간 측정 데코레이터"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            response_time = (time.time() - start_time) * 1000  # ms로 변환
            
            # 로깅
            logging.info(f"Response time: {response_time:.2f}ms", 
                        function=func.__name__,
                        response_time=response_time)
            
            # 메트릭 기록
            record_metric('response_time', response_time, {
                'function': func.__name__,
                'status': 'success'
            })
            
            return result
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logging.error(f"Response time (error): {response_time:.2f}ms", 
                         function=func.__name__,
                         error=str(e))
            
            record_metric('response_time', response_time, {
                'function': func.__name__,
                'status': 'error'
            })
            raise
    return wrapper
```

### 🔄 **처리량 (Throughput)**

#### **정의**
- **단위 시간**당 처리할 수 있는 **요청 수**
- **단위**: TPS (Transactions Per Second)
- **측정 지점**: 시스템 전체 또는 특정 컴포넌트

#### **목표값**
```yaml
# Phase별 목표 처리량
Phase 0 (MVP):     100 TPS
Phase 1 (확장):    500 TPS
Phase 2 (마이크로서비스): 1000 TPS
Phase 3 (AI/ML):   500 TPS
Phase 4 (최적화):  5000 TPS
Phase 5-7 (고급):  10000 TPS
```

#### **측정 방법**
```python
import asyncio
import time
from collections import deque

class ThroughputMonitor:
    """처리량 모니터링"""
    
    def __init__(self, window_size: int = 60):
        self.window_size = window_size  # 60초 윈도우
        self.requests = deque()
        self._lock = asyncio.Lock()
    
    async def record_request(self):
        """요청 기록"""
        async with self._lock:
            current_time = time.time()
            self.requests.append(current_time)
            
            # 윈도우 밖의 요청 제거
            while self.requests and current_time - self.requests[0] > self.window_size:
                self.requests.popleft()
    
    async def get_throughput(self) -> float:
        """현재 처리량 계산"""
        async with self._lock:
            current_time = time.time()
            
            # 윈도우 밖의 요청 제거
            while self.requests and current_time - self.requests[0] > self.window_size:
                self.requests.popleft()
            
            # 처리량 계산
            if self.requests:
                oldest_time = self.requests[0]
                time_window = current_time - oldest_time
                if time_window > 0:
                    return len(self.requests) / time_window
            
            return 0.0
```

### 🎯 **가용성 (Availability)**

#### **정의**
- **시스템이 정상 동작**하는 시간의 비율
- **단위**: 퍼센트 (%)
- **계산**: (정상 동작 시간 / 전체 시간) × 100

#### **목표값**
```yaml
# Phase별 목표 가용성
Phase 0 (MVP):     99.0%
Phase 1 (확장):    99.5%
Phase 2 (마이크로서비스): 99.7%
Phase 3 (AI/ML):   99.5%
Phase 4 (최적화):  99.9%
Phase 5-7 (고급):  99.99%
```

#### **측정 방법**
```python
import time
from datetime import datetime, timezone

class AvailabilityMonitor:
    """가용성 모니터링"""
    
    def __init__(self):
        self.start_time = time.time()
        self.downtime_start = None
        self.total_downtime = 0
        self._lock = asyncio.Lock()
    
    async def record_uptime(self):
        """정상 동작 기록"""
        async with self._lock:
            if self.downtime_start:
                # 다운타임 종료
                downtime_duration = time.time() - self.downtime_start
                self.total_downtime += downtime_duration
                self.downtime_start = None
    
    async def record_downtime(self):
        """다운타임 기록"""
        async with self._lock:
            if not self.downtime_start:
                self.downtime_start = time.time()
    
    async def get_availability(self) -> float:
        """가용성 계산"""
        async with self._lock:
            current_time = time.time()
            total_time = current_time - self.start_time
            
            # 현재 다운타임 계산
            current_downtime = 0
            if self.downtime_start:
                current_downtime = current_time - self.downtime_start
            
            total_downtime = self.total_downtime + current_downtime
            uptime = total_time - total_downtime
            
            if total_time > 0:
                return (uptime / total_time) * 100
            return 100.0
```

### ❌ **오류율 (Error Rate)**

#### **정의**
- **전체 요청** 중 **실패한 요청**의 비율
- **단위**: 퍼센트 (%)
- **계산**: (실패 요청 수 / 전체 요청 수) × 100

#### **목표값**
```yaml
# Phase별 목표 오류율
Phase 0 (MVP):     < 1.0%
Phase 1 (확장):    < 0.5%
Phase 2 (마이크로서비스): < 0.3%
Phase 3 (AI/ML):   < 0.5%
Phase 4 (최적화):  < 0.1%
Phase 5-7 (고급):  < 0.01%
```

#### **측정 방법**
```python
class ErrorRateMonitor:
    """오류율 모니터링"""
    
    def __init__(self):
        self.total_requests = 0
        self.failed_requests = 0
        self._lock = asyncio.Lock()
    
    async def record_request(self, success: bool):
        """요청 결과 기록"""
        async with self._lock:
            self.total_requests += 1
            if not success:
                self.failed_requests += 1
    
    async def get_error_rate(self) -> float:
        """오류율 계산"""
        async with self._lock:
            if self.total_requests > 0:
                return (self.failed_requests / self.total_requests) * 100
            return 0.0
```

## 🔧 **시스템별 성능 지표**

### 💰 **거래 시스템**

#### **주문 실행 성능**
```yaml
# 주문 실행 관련 지표
order_submission_time:    < 10ms    # 주문 제출 시간
order_execution_time:     < 100ms   # 주문 실행 시간
order_confirmation_time:  < 50ms    # 주문 확인 시간
order_cancellation_time:  < 30ms    # 주문 취소 시간
```

#### **거래소 연동 성능**
```yaml
# 거래소 API 관련 지표
api_response_time:        < 200ms   # API 응답 시간
websocket_latency:        < 50ms    # WebSocket 지연시간
connection_stability:     > 99.9%   # 연결 안정성
rate_limit_utilization:   < 80%     # 속도 제한 활용률
```

### 🗄️ **데이터베이스 성능**

#### **쿼리 성능**
```yaml
# 데이터베이스 쿼리 지표
query_execution_time:     < 50ms    # 쿼리 실행 시간
connection_pool_usage:    < 80%     # 연결 풀 사용률
slow_query_count:         < 1%      # 느린 쿼리 비율
deadlock_count:           < 0.1%    # 데드락 발생률
```

#### **저장소 성능**
```yaml
# 저장소 관련 지표
disk_io_latency:          < 10ms    # 디스크 I/O 지연시간
disk_utilization:         < 70%     # 디스크 사용률
backup_duration:          < 30min   # 백업 소요 시간
recovery_time:            < 5min    # 복구 소요 시간
```

### 🌐 **네트워크 성능**

#### **네트워크 지연**
```yaml
# 네트워크 관련 지표
network_latency:          < 100ms   # 네트워크 지연시간
bandwidth_utilization:    < 80%     # 대역폭 사용률
packet_loss_rate:         < 0.1%    # 패킷 손실률
connection_timeout:       < 5s      # 연결 타임아웃
```

## 📊 **성능 모니터링 도구**

### 🔍 **메트릭 수집**
```python
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge

# 메트릭 정의
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')
ERROR_COUNT = Counter('errors_total', 'Total errors', ['type'])

class MetricsCollector:
    """메트릭 수집기"""
    
    def __init__(self):
        self.request_count = REQUEST_COUNT
        self.request_duration = REQUEST_DURATION
        self.active_connections = ACTIVE_CONNECTIONS
        self.error_count = ERROR_COUNT
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """요청 메트릭 기록"""
        self.request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.observe(duration)
    
    def record_error(self, error_type: str):
        """오류 메트릭 기록"""
        self.error_count.labels(type=error_type).inc()
    
    def set_active_connections(self, count: int):
        """활성 연결 수 설정"""
        self.active_connections.set(count)
```

### 📈 **대시보드 구성**
```yaml
# Grafana 대시보드 구성
dashboard:
  title: "AutoGrowth Trading System Performance"
  panels:
    - title: "Response Time"
      type: "graph"
      metrics:
        - "http_request_duration_seconds"
      thresholds:
        - color: "green"
          value: 0.1
        - color: "yellow"
          value: 0.5
        - color: "red"
          value: 1.0
    
    - title: "Throughput"
      type: "graph"
      metrics:
        - "rate(http_requests_total[5m])"
      thresholds:
        - color: "green"
          value: 100
        - color: "yellow"
          value: 500
        - color: "red"
          value: 1000
    
    - title: "Error Rate"
      type: "graph"
      metrics:
        - "rate(errors_total[5m])"
      thresholds:
        - color: "green"
          value: 0.01
        - color: "yellow"
          value: 0.1
        - color: "red"
          value: 1.0
```

## 🚨 **성능 알림 설정**

### 📧 **알림 규칙**
```yaml
# Prometheus AlertManager 규칙
alerts:
  - name: "High Response Time"
    condition: "http_request_duration_seconds > 1.0"
    duration: "5m"
    severity: "warning"
    
  - name: "High Error Rate"
    condition: "rate(errors_total[5m]) > 0.1"
    duration: "2m"
    severity: "critical"
    
  - name: "Low Throughput"
    condition: "rate(http_requests_total[5m]) < 50"
    duration: "10m"
    severity: "warning"
    
  - name: "High CPU Usage"
    condition: "cpu_usage > 80"
    duration: "5m"
    severity: "warning"
    
  - name: "High Memory Usage"
    condition: "memory_usage > 85"
    duration: "5m"
    severity: "warning"
```

### 🔔 **알림 채널**
```yaml
# 알림 전송 채널
notification_channels:
  - type: "email"
    recipients: ["ops@autogrowth.com"]
    template: "performance_alert.html"
    
  - type: "slack"
    channel: "#alerts"
    template: "performance_alert.json"
    
  - type: "webhook"
    url: "https://api.autogrowth.com/alerts"
    method: "POST"
    
  - type: "sms"
    recipients: ["+1234567890"]
    template: "critical_alert.txt"
```

## 📋 **성능 테스트**

### 🧪 **부하 테스트**
```python
import asyncio
import aiohttp
import time
from typing import List, Dict

class LoadTester:
    """부하 테스트 도구"""
    
    def __init__(self, base_url: str, concurrent_users: int = 100):
        self.base_url = base_url
        self.concurrent_users = concurrent_users
        self.results = []
    
    async def run_load_test(self, duration: int = 300):
        """부하 테스트 실행"""
        start_time = time.time()
        tasks = []
        
        # 동시 사용자 시뮬레이션
        for i in range(self.concurrent_users):
            task = asyncio.create_task(self._simulate_user(i))
            tasks.append(task)
        
        # 테스트 실행
        await asyncio.gather(*tasks)
        
        # 결과 분석
        end_time = time.time()
        total_time = end_time - start_time
        
        return self._analyze_results(total_time)
    
    async def _simulate_user(self, user_id: int):
        """사용자 시뮬레이션"""
        async with aiohttp.ClientSession() as session:
            while True:
                start_time = time.time()
                
                try:
                    # API 요청
                    async with session.get(f"{self.base_url}/api/health") as response:
                        response_time = (time.time() - start_time) * 1000
                        
                        self.results.append({
                            'user_id': user_id,
                            'response_time': response_time,
                            'status': response.status,
                            'timestamp': start_time
                        })
                        
                        # 요청 간격
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    self.results.append({
                        'user_id': user_id,
                        'response_time': 0,
                        'status': 'error',
                        'error': str(e),
                        'timestamp': start_time
                    })
    
    def _analyze_results(self, total_time: float) -> Dict:
        """결과 분석"""
        response_times = [r['response_time'] for r in self.results if r['status'] == 200]
        error_count = len([r for r in self.results if r['status'] != 200])
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
            p99_response_time = sorted(response_times)[int(len(response_times) * 0.99)]
        else:
            avg_response_time = p95_response_time = p99_response_time = 0
        
        total_requests = len(self.results)
        throughput = total_requests / total_time
        error_rate = (error_count / total_requests) * 100 if total_requests > 0 else 0
        
        return {
            'total_requests': total_requests,
            'total_time': total_time,
            'throughput': throughput,
            'avg_response_time': avg_response_time,
            'p95_response_time': p95_response_time,
            'p99_response_time': p99_response_time,
            'error_rate': error_rate,
            'concurrent_users': self.concurrent_users
        }
```

## 📊 **성능 보고서**

### 📈 **일일 성능 보고서**
```yaml
# 일일 성능 요약
daily_report:
  period: "24h"
  metrics:
    - name: "Average Response Time"
      value: "125ms"
      target: "< 200ms"
      status: "✅"
    
    - name: "Peak Throughput"
      value: "850 TPS"
      target: "> 500 TPS"
      status: "✅"
    
    - name: "Error Rate"
      value: "0.15%"
      target: "< 0.5%"
      status: "✅"
    
    - name: "Uptime"
      value: "99.8%"
      target: "> 99.5%"
      status: "✅"
  
  alerts:
    - severity: "warning"
      count: 3
      description: "High response time spikes"
    
    - severity: "info"
      count: 12
      description: "Performance optimizations applied"
```

## 🔗 **관련 문서**

### **Phase별 성능 가이드**
- [Phase 0 성능 지표](../PHASE_0_FOUNDATION/0.1_CORE_SYSTEM.md#성능-지표)
- [Phase 1 성능 지표](../PHASE_1_EXPANSION/1.1_MULTI_EXCHANGE.md#성능-지표)
- [Phase 2 성능 지표](../PHASE_2_MICROSERVICES/2.1_ARCHITECTURE.md#성능-지표)

### **외부 참조**
- [아키텍처 문서](../../ARCHITECTURE.md)
- [개발자 가이드](../../DEVELOPER_GUIDE.md)
- [운영 가이드](../../OPERATIONS_GUIDE.md)

---

**성능 메트릭 가이드**: 모든 Phase에서 일관된 성능 측정 및 모니터링 표준 제공 