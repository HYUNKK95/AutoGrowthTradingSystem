# 📝 작업 템플릿

## 📋 **작업 개요**

### 🎯 **작업 목표**
- **작업명**: [작업 이름]
- **작업 ID**: [작업 ID]
- **우선순위**: [High/Medium/Low]
- **예상 소요 시간**: [시간]
- **담당자**: [담당자명]

### 📊 **성과 지표**
- **완료 기준**: 명확한 완료 기준 정의
- **성능 목표**: 성능 지표 및 목표값
- **품질 기준**: 품질 요구사항

## 🔧 **구현 계획**

### 📋 **구현 단계**
1. **분석 단계**: 요구사항 분석 및 설계
2. **구현 단계**: 코드 구현
3. **테스트 단계**: 단위 테스트 및 통합 테스트
4. **검증 단계**: 성능 및 품질 검증
5. **배포 단계**: 배포 및 모니터링

### 🏗️ **기술 스택**
- **언어**: Python 3.11+
- **프레임워크**: FastAPI, SQLAlchemy
- **데이터베이스**: PostgreSQL, Redis
- **테스트**: pytest, pytest-asyncio
- **모니터링**: Prometheus, Grafana

## 💻 **코드 구현**

### 📦 **주요 클래스**

```python
# 주요 클래스 예시
class TaskComponent:
    """작업 컴포넌트"""
    
    def __init__(self, config: dict):
        """초기화"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector()
    
    async def execute_task(self, task_data: dict) -> dict:
        """작업 실행"""
        try:
            # 1. 입력 검증
            self._validate_input(task_data)
            
            # 2. 비즈니스 로직 실행
            result = await self._process_business_logic(task_data)
            
            # 3. 결과 검증
            self._validate_result(result)
            
            # 4. 메트릭 기록
            self.metrics.record_success()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            self.metrics.record_error()
            raise
    
    def _validate_input(self, task_data: dict) -> bool:
        """입력 검증"""
        # 입력 데이터 검증 로직
        required_fields = ['field1', 'field2', 'field3']
        
        for field in required_fields:
            if field not in task_data:
                raise ValueError(f"Missing required field: {field}")
        
        return True
    
    async def _process_business_logic(self, task_data: dict) -> dict:
        """비즈니스 로직 처리"""
        # 실제 비즈니스 로직 구현
        result = {
            'status': 'success',
            'data': task_data,
            'processed_at': datetime.now().isoformat()
        }
        
        return result
    
    def _validate_result(self, result: dict) -> bool:
        """결과 검증"""
        # 결과 데이터 검증 로직
        if 'status' not in result:
            raise ValueError("Missing status in result")
        
        return True
```

### 🔧 **유틸리티 함수**

```python
# 유틸리티 함수 예시
def format_task_data(raw_data: dict) -> dict:
    """작업 데이터 포맷팅"""
    formatted_data = {}
    
    # 데이터 정규화
    for key, value in raw_data.items():
        formatted_key = key.lower().replace(' ', '_')
        formatted_data[formatted_key] = value
    
    return formatted_data

def calculate_task_metrics(task_results: List[dict]) -> dict:
    """작업 메트릭 계산"""
    total_tasks = len(task_results)
    successful_tasks = len([r for r in task_results if r.get('status') == 'success'])
    
    return {
        'total_tasks': total_tasks,
        'successful_tasks': successful_tasks,
        'success_rate': (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        'avg_processing_time': calculate_avg_processing_time(task_results)
    }

def calculate_avg_processing_time(task_results: List[dict]) -> float:
    """평균 처리 시간 계산"""
    processing_times = []
    
    for result in task_results:
        if 'processing_time' in result:
            processing_times.append(result['processing_time'])
    
    return sum(processing_times) / len(processing_times) if processing_times else 0.0
```

## 🧪 **테스트 구현**

### 📋 **테스트 계획**
- **단위 테스트**: 각 함수별 테스트
- **통합 테스트**: 전체 워크플로우 테스트
- **성능 테스트**: 성능 및 부하 테스트
- **예외 처리 테스트**: 오류 상황 테스트

### 🔧 **테스트 코드**

```python
# 테스트 예시
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

class TestTaskComponent:
    """작업 컴포넌트 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.config = {
            'timeout': 30,
            'retry_count': 3,
            'max_concurrent': 10
        }
        self.component = TaskComponent(self.config)
    
    def test_validate_input_success(self):
        """입력 검증 성공 테스트"""
        valid_data = {
            'field1': 'value1',
            'field2': 'value2',
            'field3': 'value3'
        }
        
        result = self.component._validate_input(valid_data)
        assert result is True
    
    def test_validate_input_missing_field(self):
        """입력 검증 실패 테스트 - 필수 필드 누락"""
        invalid_data = {
            'field1': 'value1',
            'field2': 'value2'
            # field3 누락
        }
        
        with pytest.raises(ValueError, match="Missing required field: field3"):
            self.component._validate_input(invalid_data)
    
    @pytest.mark.asyncio
    async def test_process_business_logic_success(self):
        """비즈니스 로직 처리 성공 테스트"""
        task_data = {
            'field1': 'value1',
            'field2': 'value2',
            'field3': 'value3'
        }
        
        result = await self.component._process_business_logic(task_data)
        
        assert result['status'] == 'success'
        assert result['data'] == task_data
        assert 'processed_at' in result
    
    @pytest.mark.asyncio
    async def test_execute_task_success(self):
        """작업 실행 성공 테스트"""
        task_data = {
            'field1': 'value1',
            'field2': 'value2',
            'field3': 'value3'
        }
        
        result = await self.component.execute_task(task_data)
        
        assert result['status'] == 'success'
        assert result['data'] == task_data
    
    @pytest.mark.asyncio
    async def test_execute_task_validation_failure(self):
        """작업 실행 실패 테스트 - 검증 실패"""
        invalid_data = {
            'field1': 'value1'
            # 필수 필드 누락
        }
        
        with pytest.raises(ValueError):
            await self.component.execute_task(invalid_data)

class TestUtilityFunctions:
    """유틸리티 함수 테스트"""
    
    def test_format_task_data(self):
        """작업 데이터 포맷팅 테스트"""
        raw_data = {
            'User Name': 'John Doe',
            'Email Address': 'john@example.com',
            'Phone Number': '123-456-7890'
        }
        
        formatted_data = format_task_data(raw_data)
        
        expected_data = {
            'user_name': 'John Doe',
            'email_address': 'john@example.com',
            'phone_number': '123-456-7890'
        }
        
        assert formatted_data == expected_data
    
    def test_calculate_task_metrics(self):
        """작업 메트릭 계산 테스트"""
        task_results = [
            {'status': 'success', 'processing_time': 1.0},
            {'status': 'success', 'processing_time': 2.0},
            {'status': 'error', 'processing_time': 0.5},
            {'status': 'success', 'processing_time': 1.5}
        ]
        
        metrics = calculate_task_metrics(task_results)
        
        assert metrics['total_tasks'] == 4
        assert metrics['successful_tasks'] == 3
        assert metrics['success_rate'] == 75.0
        assert metrics['avg_processing_time'] == 1.25
```

## 📊 **성능 최적화**

### 🎯 **성능 목표**
- **응답 시간**: < 50ms
- **처리량**: > 1000 TPS
- **메모리 사용량**: < 100MB
- **CPU 사용률**: < 70%

### 🔧 **최적화 기법**
- **비동기 처리**: asyncio 활용
- **캐싱**: Redis 캐싱 구현
- **메모리 풀**: 객체 재사용
- **배치 처리**: 대량 데이터 처리 최적화

```python
# 성능 최적화 예시
import asyncio
from typing import List
import redis

class OptimizedTaskProcessor:
    """최적화된 작업 프로세서"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.cache_ttl = 300  # 5분
    
    async def process_batch_tasks(self, tasks: List[dict]) -> List[dict]:
        """배치 작업 처리"""
        # 캐시 확인
        cached_results = await self._get_cached_results(tasks)
        
        # 캐시되지 않은 작업만 처리
        uncached_tasks = [task for task in tasks if task['id'] not in cached_results]
        
        if uncached_tasks:
            # 병렬 처리
            processing_tasks = [
                self._process_single_task(task) for task in uncached_tasks
            ]
            
            new_results = await asyncio.gather(*processing_tasks)
            
            # 결과 캐싱
            await self._cache_results(new_results)
            
            # 캐시된 결과와 새 결과 병합
            all_results = cached_results + new_results
        else:
            all_results = cached_results
        
        return all_results
    
    async def _process_single_task(self, task: dict) -> dict:
        """단일 작업 처리"""
        # 실제 작업 처리 로직
        await asyncio.sleep(0.01)  # 시뮬레이션
        
        return {
            'id': task['id'],
            'status': 'success',
            'result': f"Processed {task['id']}",
            'processing_time': 0.01
        }
    
    async def _get_cached_results(self, tasks: List[dict]) -> List[dict]:
        """캐시된 결과 조회"""
        cached_results = []
        
        for task in tasks:
            cache_key = f"task_result:{task['id']}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                cached_results.append(json.loads(cached_data))
        
        return cached_results
    
    async def _cache_results(self, results: List[dict]):
        """결과 캐싱"""
        for result in results:
            cache_key = f"task_result:{result['id']}"
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(result)
            )
```

## 🔒 **보안 고려사항**

### 🛡️ **보안 요구사항**
- **입력 검증**: 모든 입력 데이터 검증
- **인증**: 사용자 인증 확인
- **권한**: 작업 실행 권한 확인
- **데이터 보호**: 민감한 데이터 암호화

### 🔧 **보안 구현**

```python
# 보안 구현 예시
import hashlib
import hmac
from cryptography.fernet import Fernet

class SecureTaskProcessor:
    """보안 작업 프로세서"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
        self.cipher = Fernet(Fernet.generate_key())
    
    def validate_task_signature(self, task_data: dict, signature: str) -> bool:
        """작업 서명 검증"""
        expected_signature = self._calculate_signature(task_data)
        return hmac.compare_digest(signature, expected_signature)
    
    def _calculate_signature(self, task_data: dict) -> str:
        """서명 계산"""
        data_string = json.dumps(task_data, sort_keys=True)
        return hmac.new(
            self.secret_key,
            data_string.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """민감한 데이터 암호화"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """민감한 데이터 복호화"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

## 📈 **모니터링 및 로깅**

### 📊 **모니터링 지표**
- **작업 처리량**: 초당 처리된 작업 수
- **성공률**: 작업 성공 비율
- **응답 시간**: 작업 처리 시간
- **에러율**: 작업 실패 비율

### 🔧 **모니터링 구현**

```python
# 모니터링 구현 예시
import time
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class TaskMetrics:
    """작업 메트릭"""
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    avg_processing_time: float
    success_rate: float

class TaskMonitor:
    """작업 모니터"""
    
    def __init__(self):
        self.metrics_history: List[TaskMetrics] = []
        self.current_metrics = TaskMetrics(0, 0, 0, 0.0, 0.0)
        self.lock = threading.Lock()
    
    def record_task_start(self, task_id: str):
        """작업 시작 기록"""
        with self.lock:
            self.current_metrics.total_tasks += 1
    
    def record_task_success(self, task_id: str, processing_time: float):
        """작업 성공 기록"""
        with self.lock:
            self.current_metrics.successful_tasks += 1
            self._update_avg_processing_time(processing_time)
            self._update_success_rate()
    
    def record_task_failure(self, task_id: str, processing_time: float):
        """작업 실패 기록"""
        with self.lock:
            self.current_metrics.failed_tasks += 1
            self._update_avg_processing_time(processing_time)
            self._update_success_rate()
    
    def _update_avg_processing_time(self, processing_time: float):
        """평균 처리 시간 업데이트"""
        total_tasks = self.current_metrics.successful_tasks + self.current_metrics.failed_tasks
        if total_tasks > 0:
            current_avg = self.current_metrics.avg_processing_time
            self.current_metrics.avg_processing_time = (
                (current_avg * (total_tasks - 1) + processing_time) / total_tasks
            )
    
    def _update_success_rate(self):
        """성공률 업데이트"""
        total_tasks = self.current_metrics.total_tasks
        if total_tasks > 0:
            self.current_metrics.success_rate = (
                self.current_metrics.successful_tasks / total_tasks * 100
            )
    
    def get_current_metrics(self) -> TaskMetrics:
        """현재 메트릭 조회"""
        with self.lock:
            return TaskMetrics(
                self.current_metrics.total_tasks,
                self.current_metrics.successful_tasks,
                self.current_metrics.failed_tasks,
                self.current_metrics.avg_processing_time,
                self.current_metrics.success_rate
            )
    
    def save_metrics_snapshot(self):
        """메트릭 스냅샷 저장"""
        with self.lock:
            self.metrics_history.append(
                TaskMetrics(
                    self.current_metrics.total_tasks,
                    self.current_metrics.successful_tasks,
                    self.current_metrics.failed_tasks,
                    self.current_metrics.avg_processing_time,
                    self.current_metrics.success_rate
                )
            )
```

## 📋 **체크리스트**

### ✅ **완료 기준**
- [ ] 코드 구현 완료
- [ ] 단위 테스트 작성 및 통과
- [ ] 통합 테스트 작성 및 통과
- [ ] 성능 테스트 통과
- [ ] 보안 검증 완료
- [ ] 문서화 완료
- [ ] 코드 리뷰 완료
- [ ] 배포 테스트 완료

### 📊 **품질 지표**
- **코드 커버리지**: > 90%
- **테스트 통과율**: 100%
- **성능 목표 달성**: 모든 성능 지표 달성
- **보안 취약점**: 0건
- **문서 완성도**: 100%

---

**템플릿 버전**: 1.0
**최종 업데이트**: 2024-01-31
**다음 검토**: 2024-02-01 