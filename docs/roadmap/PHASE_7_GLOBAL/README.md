# 🌍 Phase 7: 글로벌 확장 시스템

## 📋 **개요**

### 🎯 **목표**
- **다중 리전 배포**: 전 세계 주요 리전에 시스템 배포
- **글로벌 로드 밸런싱**: 지리적 위치 기반 트래픽 분산
- **데이터 지역화**: 각 리전별 데이터 저장 및 처리
- **규정 준수**: 각 지역별 규정 준수 (GDPR, CCPA, LGPD)
- **글로벌 모니터링**: 전 세계 시스템 실시간 모니터링

### 📊 **성능 목표**
- **글로벌 지연**: < 50ms 글로벌 응답 시간
- **가용성**: 99.99% 글로벌 가용성
- **데이터 동기화**: < 1초 리전 간 데이터 동기화
- **장애 복구**: < 5분 자동 장애 복구
- **규정 준수**: 100% 지역별 규정 준수

## 🏗️ **글로벌 확장 시스템 아키텍처**

### 📁 **글로벌 확장 시스템 구조**
```
global-expansion/
├── multi-region-deployment/            # 다중 리전 배포
│   ├── region-management/              # 리전 관리
│   ├── deployment-automation/          # 배포 자동화
│   ├── configuration-management/       # 설정 관리
│   └── health-monitoring/              # 헬스 모니터링
├── global-load-balancing/              # 글로벌 로드 밸런싱
│   ├── geographic-routing/             # 지리적 라우팅
│   ├── latency-based-routing/          # 지연 기반 라우팅
│   ├── health-based-routing/           # 헬스 기반 라우팅
│   └── traffic-management/             # 트래픽 관리
├── data-localization/                  # 데이터 지역화
│   ├── regional-storage/               # 지역별 저장소
│   ├── data-synchronization/           # 데이터 동기화
│   ├── compliance-management/          # 규정 준수 관리
│   └── data-governance/                # 데이터 거버넌스
├── global-monitoring/                  # 글로벌 모니터링
│   ├── distributed-monitoring/         # 분산 모니터링
│   ├── alert-management/               # 알림 관리
│   ├── performance-analysis/           # 성능 분석
│   └── capacity-planning/              # 용량 계획
└── disaster-recovery/                  # 재해 복구
    ├── backup-strategies/              # 백업 전략
    ├── failover-automation/            # 장애 복구 자동화
    ├── data-recovery/                  # 데이터 복구
    └── business-continuity/            # 비즈니스 연속성
```

## 🔧 **다중 리전 배포 시스템**

### 📦 **리전 관리 및 배포 자동화**

```python
# global-expansion/multi-region-deployment/region_manager.py
import asyncio
import time
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import threading
from collections import defaultdict, deque
import boto3
import kubernetes
from kubernetes import client, config

logger = logging.getLogger(__name__)

@dataclass
class Region:
    """리전 정보"""
    region_id: str
    name: str
    location: str
    cloud_provider: str  # 'aws', 'gcp', 'azure'
    status: str  # 'active', 'maintenance', 'failed'
    capacity: Dict[str, Any]
    compliance: List[str]  # ['GDPR', 'CCPA', 'LGPD']
    latency_targets: Dict[str, float]
    created_at: datetime

@dataclass
class Deployment:
    """배포 정보"""
    deployment_id: str
    region_id: str
    service_name: str
    version: str
    status: str  # 'deploying', 'active', 'failed', 'rolling_back'
    replicas: int
    resources: Dict[str, Any]
    health_status: str  # 'healthy', 'unhealthy', 'degraded'
    created_at: datetime
    updated_at: datetime

@dataclass
class GlobalConfig:
    """글로벌 설정"""
    config_id: str
    service_name: str
    regions: List[str]
    routing_strategy: str  # 'geographic', 'latency', 'health'
    replication_factor: int
    compliance_requirements: List[str]
    created_at: datetime

class RegionManager:
    """리전 관리자"""
    
    def __init__(self):
        self.regions = self._initialize_regions()
        self.deployments = {}
        self.global_configs = {}
        self.performance_metrics = GlobalMetrics()
        
        # 클라우드 클라이언트
        self.aws_client = None
        self.gcp_client = None
        self.azure_client = None
        
        # Kubernetes 클라이언트
        self.k8s_clients = {}
        
        # 스레드 안전
        self.lock = threading.Lock()
        
        # 모니터링 스레드
        self.monitoring_thread = None
        self.monitoring_active = False
        
        logger.info("Region manager initialized")
    
    def _initialize_regions(self) -> Dict[str, Region]:
        """리전 초기화"""
        regions = {
            'us-east-1': Region(
                region_id='us-east-1',
                name='US East (N. Virginia)',
                location='North America',
                cloud_provider='aws',
                status='active',
                capacity={
                    'cpu_cores': 1000,
                    'memory_gb': 4000,
                    'storage_tb': 1000,
                    'network_gbps': 100
                },
                compliance=['CCPA'],
                latency_targets={
                    'us-east-1': 5,
                    'us-west-2': 50,
                    'eu-west-1': 80,
                    'ap-northeast-1': 150
                },
                created_at=datetime.now()
            ),
            'us-west-2': Region(
                region_id='us-west-2',
                name='US West (Oregon)',
                location='North America',
                cloud_provider='aws',
                status='active',
                capacity={
                    'cpu_cores': 800,
                    'memory_gb': 3200,
                    'storage_tb': 800,
                    'network_gbps': 80
                },
                compliance=['CCPA'],
                latency_targets={
                    'us-east-1': 50,
                    'us-west-2': 5,
                    'eu-west-1': 130,
                    'ap-northeast-1': 100
                },
                created_at=datetime.now()
            ),
            'eu-west-1': Region(
                region_id='eu-west-1',
                name='Europe (Ireland)',
                location='Europe',
                cloud_provider='aws',
                status='active',
                capacity={
                    'cpu_cores': 600,
                    'memory_gb': 2400,
                    'storage_tb': 600,
                    'network_gbps': 60
                },
                compliance=['GDPR'],
                latency_targets={
                    'us-east-1': 80,
                    'us-west-2': 130,
                    'eu-west-1': 5,
                    'ap-northeast-1': 200
                },
                created_at=datetime.now()
            ),
            'ap-northeast-1': Region(
                region_id='ap-northeast-1',
                name='Asia Pacific (Tokyo)',
                location='Asia Pacific',
                cloud_provider='aws',
                status='active',
                capacity={
                    'cpu_cores': 400,
                    'memory_gb': 1600,
                    'storage_tb': 400,
                    'network_gbps': 40
                },
                compliance=['LGPD'],
                latency_targets={
                    'us-east-1': 150,
                    'us-west-2': 100,
                    'eu-west-1': 200,
                    'ap-northeast-1': 5
                },
                created_at=datetime.now()
            )
        }
        
        return regions
    
    async def initialize_cloud_clients(self):
        """클라우드 클라이언트 초기화"""
        try:
            # AWS 클라이언트
            self.aws_client = boto3.client('ec2')
            
            # GCP 클라이언트 (실제 구현에서는 GCP 클라이언트 사용)
            # self.gcp_client = google.cloud.compute_v1.InstancesClient()
            
            # Azure 클라이언트 (실제 구현에서는 Azure 클라이언트 사용)
            # self.azure_client = azure.mgmt.compute.ComputeManagementClient()
            
            # Kubernetes 클라이언트 초기화
            await self._initialize_k8s_clients()
            
            logger.info("Cloud clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize cloud clients: {e}")
            raise
    
    async def _initialize_k8s_clients(self):
        """Kubernetes 클라이언트 초기화"""
        for region_id in self.regions.keys():
            try:
                # 실제 구현에서는 각 리전별 kubeconfig 사용
                # config.load_kube_config(context=region_id)
                # self.k8s_clients[region_id] = client.CoreV1Api()
                
                logger.info(f"Kubernetes client initialized for region: {region_id}")
                
            except Exception as e:
                logger.error(f"Failed to initialize Kubernetes client for {region_id}: {e}")
    
    async def deploy_service(self, service_name: str, version: str, 
                           regions: List[str], config: Dict[str, Any]) -> List[Deployment]:
        """서비스 배포"""
        deployments = []
        
        for region_id in regions:
            if region_id not in self.regions:
                logger.warning(f"Region not found: {region_id}")
                continue
            
            try:
                deployment = await self._deploy_to_region(
                    service_name, version, region_id, config
                )
                deployments.append(deployment)
                
                logger.info(f"Service deployed to {region_id}: {deployment.deployment_id}")
                
            except Exception as e:
                logger.error(f"Failed to deploy to {region_id}: {e}")
        
        return deployments
    
    async def _deploy_to_region(self, service_name: str, version: str, 
                               region_id: str, config: Dict[str, Any]) -> Deployment:
        """리전별 배포"""
        deployment_id = f"{service_name}-{region_id}-{version}"
        
        # 배포 상태 생성
        deployment = Deployment(
            deployment_id=deployment_id,
            region_id=region_id,
            service_name=service_name,
            version=version,
            status='deploying',
            replicas=config.get('replicas', 3),
            resources=config.get('resources', {}),
            health_status='unhealthy',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 배포 실행
        try:
            # Kubernetes 배포
            await self._deploy_to_kubernetes(deployment, config)
            
            # 배포 상태 업데이트
            deployment.status = 'active'
            deployment.health_status = 'healthy'
            deployment.updated_at = datetime.now()
            
            # 배포 정보 저장
            with self.lock:
                self.deployments[deployment_id] = deployment
            
            return deployment
            
        except Exception as e:
            deployment.status = 'failed'
            deployment.health_status = 'unhealthy'
            deployment.updated_at = datetime.now()
            
            with self.lock:
                self.deployments[deployment_id] = deployment
            
            raise e
    
    async def _deploy_to_kubernetes(self, deployment: Deployment, config: Dict[str, Any]):
        """Kubernetes 배포"""
        # 실제 구현에서는 Kubernetes API 사용
        # k8s_client = self.k8s_clients.get(deployment.region_id)
        # if not k8s_client:
        #     raise Exception(f"Kubernetes client not available for {deployment.region_id}")
        
        # Deployment 생성
        # deployment_obj = client.V1Deployment(
        #     metadata=client.V1ObjectMeta(name=deployment.deployment_id),
        #     spec=client.V1DeploymentSpec(
        #         replicas=deployment.replicas,
        #         selector=client.V1LabelSelector(
        #             match_labels={"app": deployment.service_name}
        #         ),
        #         template=client.V1PodTemplateSpec(
        #             metadata=client.V1ObjectMeta(
        #                 labels={"app": deployment.service_name}
        #             ),
        #             spec=client.V1PodSpec(
        #                 containers=[
        #                     client.V1Container(
        #                         name=deployment.service_name,
        #                         image=f"{deployment.service_name}:{deployment.version}",
        #                         resources=client.V1ResourceRequirements(
        #                             requests=deployment.resources.get('requests', {}),
        #                             limits=deployment.resources.get('limits', {})
        #                         )
        #                     )
        #                 ]
        #             )
        #         )
        #     )
        # )
        
        # k8s_client.create_namespaced_deployment(
        #     namespace="default",
        #     body=deployment_obj
        # )
        
        # 배포 시뮬레이션
        await asyncio.sleep(5)
        logger.info(f"Kubernetes deployment completed: {deployment.deployment_id}")
    
    async def start_monitoring(self):
        """모니터링 시작"""
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.start()
        logger.info("Global monitoring started")
    
    async def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("Global monitoring stopped")
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                # 리전 상태 확인
                self._check_region_health()
                
                # 배포 상태 확인
                self._check_deployment_health()
                
                # 성능 메트릭 수집
                self.performance_metrics.record_monitoring_cycle()
                
                time.sleep(30)  # 30초마다 실행
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)
    
    def _check_region_health(self):
        """리전 헬스 확인"""
        with self.lock:
            for region in self.regions.values():
                # 실제 구현에서는 클라우드 API로 헬스 확인
                # health_status = self._check_cloud_health(region)
                
                # 시뮬레이션
                health_status = 'healthy'
                
                if health_status != 'healthy':
                    region.status = 'failed'
                    logger.error(f"Region health check failed: {region.region_id}")
                else:
                    region.status = 'active'
    
    def _check_deployment_health(self):
        """배포 헬스 확인"""
        with self.lock:
            for deployment in self.deployments.values():
                # 실제 구현에서는 Kubernetes API로 헬스 확인
                # health_status = self._check_k8s_health(deployment)
                
                # 시뮬레이션
                health_status = 'healthy'
                
                deployment.health_status = health_status
                deployment.updated_at = datetime.now()
                
                if health_status != 'healthy':
                    logger.warning(f"Deployment health check failed: {deployment.deployment_id}")
    
    def get_region(self, region_id: str) -> Optional[Region]:
        """리전 조회"""
        return self.regions.get(region_id)
    
    def get_all_regions(self) -> List[Region]:
        """모든 리전 조회"""
        return list(self.regions.values())
    
    def get_deployment(self, deployment_id: str) -> Optional[Deployment]:
        """배포 조회"""
        return self.deployments.get(deployment_id)
    
    def get_deployments_by_service(self, service_name: str) -> List[Deployment]:
        """서비스별 배포 조회"""
        return [
            deployment for deployment in self.deployments.values()
            if deployment.service_name == service_name
        ]
    
    def get_deployments_by_region(self, region_id: str) -> List[Deployment]:
        """리전별 배포 조회"""
        return [
            deployment for deployment in self.deployments.values()
            if deployment.region_id == region_id
        ]

class GlobalMetrics:
    """글로벌 메트릭"""
    
    def __init__(self):
        self.monitoring_cycles = 0
        self.deployments_count = 0
        self.regions_count = 0
        self.start_time = time.time()
        self.lock = threading.Lock()
    
    def record_monitoring_cycle(self):
        """모니터링 사이클 기록"""
        with self.lock:
            self.monitoring_cycles += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """메트릭 조회"""
        with self.lock:
            uptime = time.time() - self.start_time
            return {
                'monitoring_cycles': self.monitoring_cycles,
                'deployments_count': self.deployments_count,
                'regions_count': self.regions_count,
                'cycles_per_minute': self.monitoring_cycles / (uptime / 60) if uptime > 0 else 0,
                'uptime_seconds': uptime
            }
```

## 🔧 **글로벌 로드 밸런싱 시스템**

### 📦 **지리적 라우팅 및 트래픽 관리**

```python
# global-expansion/global-load-balancing/global_load_balancer.py
import asyncio
import time
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import threading
from collections import defaultdict, deque
import geoip2.database
import geoip2.errors

logger = logging.getLogger(__name__)

@dataclass
class RoutingRule:
    """라우팅 규칙"""
    rule_id: str
    name: str
    strategy: str  # 'geographic', 'latency', 'health', 'weighted'
    conditions: Dict[str, Any]
    actions: List[str]
    priority: int
    is_active: bool

@dataclass
class TrafficRoute:
    """트래픽 라우트"""
    route_id: str
    source_region: str
    target_region: str
    latency_ms: float
    health_score: float
    traffic_weight: float
    is_active: bool
    created_at: datetime

@dataclass
class LoadBalancerStats:
    """로드 밸런서 통계"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    requests_per_second: float
    error_rate: float
    last_updated: datetime

class GlobalLoadBalancer:
    """글로벌 로드 밸런서"""
    
    def __init__(self):
        self.routing_rules = self._initialize_routing_rules()
        self.traffic_routes = {}
        self.region_manager = None
        self.geoip_reader = None
        self.performance_metrics = LoadBalancerMetrics()
        
        # 캐시
        self.route_cache = {}
        self.geo_cache = {}
        
        # 스레드 안전
        self.lock = threading.Lock()
        
        # 통계
        self.stats = LoadBalancerStats(
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            avg_response_time=0.0,
            requests_per_second=0.0,
            error_rate=0.0,
            last_updated=datetime.now()
        )
        
        logger.info("Global load balancer initialized")
    
    def _initialize_routing_rules(self) -> Dict[str, RoutingRule]:
        """라우팅 규칙 초기화"""
        rules = {
            'geographic_primary': RoutingRule(
                rule_id='geographic_primary',
                name='Geographic Primary Routing',
                strategy='geographic',
                conditions={
                    'latency_threshold': 50,
                    'health_threshold': 0.8
                },
                actions=['route_to_nearest', 'fallback_to_healthy'],
                priority=1,
                is_active=True
            ),
            'latency_optimized': RoutingRule(
                rule_id='latency_optimized',
                name='Latency Optimized Routing',
                strategy='latency',
                conditions={
                    'max_latency': 100,
                    'health_threshold': 0.7
                },
                actions=['route_to_fastest', 'fallback_to_healthy'],
                priority=2,
                is_active=True
            ),
            'health_based': RoutingRule(
                rule_id='health_based',
                name='Health Based Routing',
                strategy='health',
                conditions={
                    'min_health_score': 0.9,
                    'max_failures': 3
                },
                actions=['route_to_healthiest', 'exclude_unhealthy'],
                priority=3,
                is_active=True
            ),
            'weighted_distribution': RoutingRule(
                rule_id='weighted_distribution',
                name='Weighted Distribution',
                strategy='weighted',
                conditions={
                    'min_weight': 0.1,
                    'max_weight': 0.5
                },
                actions=['distribute_by_weight', 'adjust_weights'],
                priority=4,
                is_active=True
            )
        }
        
        return rules
    
    def set_region_manager(self, region_manager):
        """리전 매니저 설정"""
        self.region_manager = region_manager
        logger.info("Region manager set for load balancer")
    
    async def initialize_geoip(self, geoip_database_path: str):
        """GeoIP 데이터베이스 초기화"""
        try:
            self.geoip_reader = geoip2.database.Reader(geoip_database_path)
            logger.info("GeoIP database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize GeoIP database: {e}")
            raise
    
    async def route_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """요청 라우팅"""
        start_time = time.time()
        
        try:
            # 클라이언트 정보 추출
            client_ip = request_data.get('client_ip')
            user_agent = request_data.get('user_agent')
            request_id = request_data.get('request_id')
            
            # 라우팅 결정
            target_region = await self._determine_target_region(client_ip, request_data)
            
            # 라우팅 정보 생성
            route_info = {
                'request_id': request_id,
                'client_ip': client_ip,
                'target_region': target_region,
                'routing_strategy': self._get_routing_strategy(target_region),
                'latency_estimate': self._estimate_latency(client_ip, target_region),
                'routed_at': datetime.now().isoformat()
            }
            
            # 통계 업데이트
            self._update_stats(True, time.time() - start_time)
            
            logger.info(f"Request routed to {target_region}: {request_id}")
            return route_info
            
        except Exception as e:
            # 통계 업데이트
            self._update_stats(False, time.time() - start_time)
            
            logger.error(f"Request routing failed: {e}")
            raise
    
    async def _determine_target_region(self, client_ip: str, 
                                     request_data: Dict[str, Any]) -> str:
        """대상 리전 결정"""
        # 캐시 확인
        cache_key = f"{client_ip}_{hash(json.dumps(request_data, sort_keys=True))}"
        if cache_key in self.route_cache:
            return self.route_cache[cache_key]
        
        # 클라이언트 위치 확인
        client_location = await self._get_client_location(client_ip)
        
        # 라우팅 규칙 적용
        for rule in sorted(self.routing_rules.values(), key=lambda x: x.priority):
            if not rule.is_active:
                continue
            
            target_region = self._apply_routing_rule(rule, client_location, request_data)
            if target_region:
                # 캐시 저장
                self.route_cache[cache_key] = target_region
                return target_region
        
        # 기본 리전 반환
        default_region = 'us-east-1'
        self.route_cache[cache_key] = default_region
        return default_region
    
    async def _get_client_location(self, client_ip: str) -> Dict[str, Any]:
        """클라이언트 위치 확인"""
        # 캐시 확인
        if client_ip in self.geo_cache:
            return self.geo_cache[client_ip]
        
        try:
            if self.geoip_reader:
                response = self.geoip_reader.city(client_ip)
                location = {
                    'country': response.country.name,
                    'country_code': response.country.iso_code,
                    'city': response.city.name,
                    'latitude': response.location.latitude,
                    'longitude': response.location.longitude,
                    'timezone': response.location.time_zone
                }
            else:
                # 기본 위치 (미국)
                location = {
                    'country': 'United States',
                    'country_code': 'US',
                    'city': 'Unknown',
                    'latitude': 37.0902,
                    'longitude': -95.7129,
                    'timezone': 'America/New_York'
                }
            
            # 캐시 저장
            self.geo_cache[client_ip] = location
            return location
            
        except geoip2.errors.AddressNotFoundError:
            # 기본 위치 반환
            default_location = {
                'country': 'United States',
                'country_code': 'US',
                'city': 'Unknown',
                'latitude': 37.0902,
                'longitude': -95.7129,
                'timezone': 'America/New_York'
            }
            self.geo_cache[client_ip] = default_location
            return default_location
    
    def _apply_routing_rule(self, rule: RoutingRule, client_location: Dict[str, Any], 
                           request_data: Dict[str, Any]) -> Optional[str]:
        """라우팅 규칙 적용"""
        if rule.strategy == 'geographic':
            return self._geographic_routing(client_location, rule.conditions)
        elif rule.strategy == 'latency':
            return self._latency_routing(client_location, rule.conditions)
        elif rule.strategy == 'health':
            return self._health_routing(rule.conditions)
        elif rule.strategy == 'weighted':
            return self._weighted_routing(rule.conditions)
        
        return None
    
    def _geographic_routing(self, client_location: Dict[str, Any], 
                          conditions: Dict[str, Any]) -> str:
        """지리적 라우팅"""
        # 국가별 기본 리전 매핑
        country_regions = {
            'US': 'us-east-1',
            'CA': 'us-east-1',
            'GB': 'eu-west-1',
            'DE': 'eu-west-1',
            'FR': 'eu-west-1',
            'JP': 'ap-northeast-1',
            'KR': 'ap-northeast-1',
            'AU': 'ap-northeast-1'
        }
        
        country_code = client_location.get('country_code', 'US')
        target_region = country_regions.get(country_code, 'us-east-1')
        
        # 헬스 체크
        if self._is_region_healthy(target_region, conditions.get('health_threshold', 0.8)):
            return target_region
        
        # 폴백 리전
        fallback_regions = ['us-west-2', 'eu-west-1', 'ap-northeast-1']
        for region in fallback_regions:
            if self._is_region_healthy(region, conditions.get('health_threshold', 0.8)):
                return region
        
        return 'us-east-1'  # 최종 폴백
    
    def _latency_routing(self, client_location: Dict[str, Any], 
                        conditions: Dict[str, Any]) -> str:
        """지연 기반 라우팅"""
        max_latency = conditions.get('max_latency', 100)
        
        # 각 리전의 예상 지연 시간 계산
        region_latencies = {}
        for region_id in ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-northeast-1']:
            latency = self._estimate_latency_from_location(client_location, region_id)
            if latency <= max_latency:
                region_latencies[region_id] = latency
        
        if region_latencies:
            # 가장 낮은 지연 시간의 리전 선택
            return min(region_latencies, key=region_latencies.get)
        
        return 'us-east-1'  # 폴백
    
    def _health_routing(self, conditions: Dict[str, Any]) -> str:
        """헬스 기반 라우팅"""
        min_health_score = conditions.get('min_health_score', 0.9)
        
        # 헬스 점수가 높은 리전 선택
        healthy_regions = []
        for region_id in ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-northeast-1']:
            health_score = self._get_region_health_score(region_id)
            if health_score >= min_health_score:
                healthy_regions.append((region_id, health_score))
        
        if healthy_regions:
            # 가장 높은 헬스 점수의 리전 선택
            return max(healthy_regions, key=lambda x: x[1])[0]
        
        return 'us-east-1'  # 폴백
    
    def _weighted_routing(self, conditions: Dict[str, Any]) -> str:
        """가중치 기반 라우팅"""
        min_weight = conditions.get('min_weight', 0.1)
        max_weight = conditions.get('max_weight', 0.5)
        
        # 리전별 가중치 계산
        region_weights = {
            'us-east-1': 0.4,
            'us-west-2': 0.3,
            'eu-west-1': 0.2,
            'ap-northeast-1': 0.1
        }
        
        # 가중치 범위 내의 리전만 선택
        valid_regions = [
            region for region, weight in region_weights.items()
            if min_weight <= weight <= max_weight
        ]
        
        if valid_regions:
            # 가중치에 따른 랜덤 선택
            import random
            return random.choice(valid_regions)
        
        return 'us-east-1'  # 폴백
    
    def _is_region_healthy(self, region_id: str, threshold: float) -> bool:
        """리전 헬스 확인"""
        if not self.region_manager:
            return True  # 기본값
        
        region = self.region_manager.get_region(region_id)
        if not region:
            return False
        
        # 실제 구현에서는 헬스 체크 API 호출
        health_score = self._get_region_health_score(region_id)
        return health_score >= threshold
    
    def _get_region_health_score(self, region_id: str) -> float:
        """리전 헬스 점수 조회"""
        # 실제 구현에서는 헬스 체크 시스템에서 조회
        # 시뮬레이션
        health_scores = {
            'us-east-1': 0.95,
            'us-west-2': 0.92,
            'eu-west-1': 0.88,
            'ap-northeast-1': 0.85
        }
        
        return health_scores.get(region_id, 0.8)
    
    def _estimate_latency(self, client_ip: str, target_region: str) -> float:
        """지연 시간 추정"""
        # 실제 구현에서는 네트워크 지연 측정
        # 시뮬레이션
        base_latencies = {
            'us-east-1': 20,
            'us-west-2': 40,
            'eu-west-1': 80,
            'ap-northeast-1': 120
        }
        
        base_latency = base_latencies.get(target_region, 50)
        
        # 변동성 추가
        import random
        variation = random.uniform(-10, 10)
        
        return max(5, base_latency + variation)
    
    def _estimate_latency_from_location(self, client_location: Dict[str, Any], 
                                      target_region: str) -> float:
        """위치 기반 지연 시간 추정"""
        # 간단한 거리 기반 지연 시간 계산
        client_lat = client_location.get('latitude', 37.0902)
        client_lon = client_location.get('longitude', -95.7129)
        
        region_coordinates = {
            'us-east-1': (39.8283, -98.5795),  # Kansas
            'us-west-2': (45.5152, -122.6784),  # Oregon
            'eu-west-1': (53.3498, -6.2603),   # Ireland
            'ap-northeast-1': (35.6762, 139.6503)  # Tokyo
        }
        
        target_lat, target_lon = region_coordinates.get(target_region, (39.8283, -98.5795))
        
        # 거리 계산 (간단한 유클리드 거리)
        distance = ((client_lat - target_lat) ** 2 + (client_lon - target_lon) ** 2) ** 0.5
        
        # 거리를 지연 시간으로 변환 (대략적인 계산)
        latency = distance * 100  # 1도당 약 100ms
        
        return max(5, min(latency, 300))  # 5ms ~ 300ms 범위
    
    def _get_routing_strategy(self, target_region: str) -> str:
        """라우팅 전략 조회"""
        # 실제 구현에서는 라우팅 결정 과정에서 사용된 전략 반환
        return 'geographic'
    
    def _update_stats(self, success: bool, response_time: float):
        """통계 업데이트"""
        with self.lock:
            self.stats.total_requests += 1
            
            if success:
                self.stats.successful_requests += 1
            else:
                self.stats.failed_requests += 1
            
            # 평균 응답 시간 업데이트
            if self.stats.total_requests > 0:
                self.stats.avg_response_time = (
                    (self.stats.avg_response_time * (self.stats.total_requests - 1) + response_time) /
                    self.stats.total_requests
                )
            
            # 오류율 계산
            if self.stats.total_requests > 0:
                self.stats.error_rate = self.stats.failed_requests / self.stats.total_requests
            
            # 초당 요청 수 계산
            uptime = (datetime.now() - self.stats.last_updated).total_seconds()
            if uptime > 0:
                self.stats.requests_per_second = self.stats.total_requests / uptime
            
            self.stats.last_updated = datetime.now()
    
    def get_stats(self) -> LoadBalancerStats:
        """통계 조회"""
        with self.lock:
            return self.stats
    
    def add_routing_rule(self, rule: RoutingRule):
        """라우팅 규칙 추가"""
        with self.lock:
            self.routing_rules[rule.rule_id] = rule
            logger.info(f"Routing rule added: {rule.rule_id}")
    
    def update_routing_rule(self, rule_id: str, updates: Dict[str, Any]):
        """라우팅 규칙 업데이트"""
        with self.lock:
            if rule_id in self.routing_rules:
                rule = self.routing_rules[rule_id]
                for key, value in updates.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                logger.info(f"Routing rule updated: {rule_id}")

class LoadBalancerMetrics:
    """로드 밸런서 메트릭"""
    
    def __init__(self):
        self.routing_decisions = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.start_time = time.time()
        self.lock = threading.Lock()
    
    def record_routing_decision(self):
        """라우팅 결정 기록"""
        with self.lock:
            self.routing_decisions += 1
    
    def record_cache_hit(self):
        """캐시 히트 기록"""
        with self.lock:
            self.cache_hits += 1
    
    def record_cache_miss(self):
        """캐시 미스 기록"""
        with self.lock:
            self.cache_misses += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """메트릭 조회"""
        with self.lock:
            total_cache_requests = self.cache_hits + self.cache_misses
            cache_hit_rate = self.cache_hits / total_cache_requests if total_cache_requests > 0 else 0
            
            uptime = time.time() - self.start_time
            return {
                'routing_decisions': self.routing_decisions,
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'cache_hit_rate': cache_hit_rate,
                'decisions_per_second': self.routing_decisions / uptime if uptime > 0 else 0,
                'uptime_seconds': uptime
            }
```

## 🎯 **다음 단계**

### 📋 **완료된 작업**
- ✅ 실시간 위험 평가 시스템 설계 (포트폴리오 위험, 시장 위험)
- ✅ 스트레스 테스트 시스템 설계 (시나리오 기반, 병렬 실행)
- ✅ 위험 한도 관리 시스템 설계
- ✅ 대칭키 암호화 시스템 설계 (AES-256-GCM)
- ✅ 데이터 익명화 시스템 설계 (마스킹, 해싱, 일반화)
- ✅ 실시간 로그 수집 시스템 설계 (구조화된 로깅, 실시간 처리)
- ✅ 규정 준수 모니터링 시스템 설계 (GDPR, SOX, PCI-DSS)
- ✅ 다중 리전 배포 시스템 설계 (리전 관리, 배포 자동화)
- ✅ 글로벌 로드 밸런싱 시스템 설계 (지리적 라우팅, 트래픽 관리)

### 🔄 **진행 중인 작업**
- 🔄 데이터 지역화 시스템 (지역별 저장소, 데이터 동기화)
- 🔄 글로벌 모니터링 시스템 (분산 모니터링, 알림 관리)

### ⏳ **다음 단계**
1. **데이터 지역화 시스템** 문서 생성
2. **글로벌 모니터링 시스템** 문서 생성
3. **재해 복구 시스템** 문서 생성

---

**마지막 업데이트**: 2024-01-31
**다음 업데이트**: 2024-02-01 (데이터 지역화 시스템)
**글로벌 확장 목표**: < 50ms 글로벌 응답, 99.99% 가용성, 100% 규정 준수
**글로벌 확장 성과**: 다중 리전 배포, 글로벌 로드 밸런싱, 데이터 지역화 