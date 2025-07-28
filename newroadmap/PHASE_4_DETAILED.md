# Phase 4: 실시간 운영 상세 구현 가이드

## 🎯 Phase 4 목표
- 50개 코인 24/7 실시간 봇 실행
- Telegram 알림 시스템 구축
- 실시간 PnL 추적 (핵심 지표 + 전략)
- 자동 재시작 시스템
- 로그 관리 및 성과 분석

## 📋 구현 체크리스트

### **실시간 운영**
- [ ] 50개 코인 24/7 봇 실행 시스템
- [ ] 실시간 시장 데이터 처리 (50개 코인)
- [ ] 실시간 거래 실행 (핵심 지표 + 전략)
- [ ] 운영 상태 모니터링

### **알림 시스템**
- [ ] Telegram 봇 연동
- [ ] 거래 결과 알림
- [ ] 성과 리포트 알림
- [ ] 오류 및 경고 알림

### **성과 추적**
- [ ] 실시간 PnL 계산
- [ ] 일간/주간 성과 분석
- [ ] 성과 지표 대시보드
- [ ] 성과 리포트 생성

### **운영 관리**
- [ ] 자동 재시작 시스템
- [ ] 로그 관리 및 분석
- [ ] 오류 처리 및 복구
- [ ] 시스템 안정성 모니터링

## 🏗️ 실시간 운영 구조

### **운영 모듈 구조**
```
operations/
├── __init__.py
├── realtime_bot.py    # 실시간 봇
├── telegram_bot.py    # Telegram 알림
├── performance_tracker.py  # 성과 추적
└── system_monitor.py  # 시스템 모니터링
```

### **알림 시스템 구조**
```
notifications/
├── __init__.py
├── telegram_notifier.py  # Telegram 알림
├── alert_manager.py      # 알림 관리
└── report_generator.py   # 리포트 생성
```

## 💻 구현 예시 코드

### **1. operations/realtime_bot.py**
```python
"""
실시간 봇 운영 시스템
"""

import time
import threading
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from bot.integrated_bot import IntegratedTradingBot
from bot.config import Config
from operations.performance_tracker import PerformanceTracker
from operations.system_monitor import SystemMonitor

class RealtimeBot:
    """실시간 봇 운영 클래스"""
    
    def __init__(self, config: Config):
        """실시간 봇 초기화"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 봇 초기화
        self.bot = IntegratedTradingBot(config)
        
        # 성과 추적기
        self.performance_tracker = PerformanceTracker(config)
        
        # 시스템 모니터
        self.system_monitor = SystemMonitor()
        
        # 운영 상태
        self.is_running = False
        self.start_time = None
        self.last_trade_time = None
        self.error_count = 0
        self.max_errors = 10
        
        # 스레드 관리
        self.main_thread = None
        self.monitor_thread = None
        
        self.logger.info("RealtimeBot 초기화 완료")
    
    def start(self):
        """봇 시작"""
        try:
            self.logger.info("실시간 봇 시작")
            self.is_running = True
            self.start_time = datetime.now()
            
            # 메인 봇 스레드 시작
            self.main_thread = threading.Thread(target=self._run_main_loop)
            self.main_thread.daemon = True
            self.main_thread.start()
            
            # 모니터링 스레드 시작
            self.monitor_thread = threading.Thread(target=self._run_monitoring)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            self.logger.info("실시간 봇 스레드 시작 완료")
            
        except Exception as e:
            self.logger.error(f"봇 시작 실패: {e}")
            raise
    
    def stop(self):
        """봇 중지"""
        self.logger.info("봇 중지 요청")
        self.is_running = False
        
        if self.main_thread:
            self.main_thread.join(timeout=10)
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        
        self.logger.info("봇 중지 완료")
    
    def _run_main_loop(self):
        """메인 봇 루프"""
        while self.is_running:
            try:
                # 1. 시장 데이터 처리
                market_data = self.bot.process_market_data()
                
                if 'error' in market_data:
                    self.logger.warning(f"시장 데이터 처리 오류: {market_data['error']}")
                    time.sleep(60)
                    continue
                
                # 2. 거래 결정 실행
                trade_result = self.bot.execute_trading_decision(market_data)
                
                # 3. 거래 결과 처리
                if trade_result:
                    self.last_trade_time = datetime.now()
                    self.performance_tracker.update_trade(trade_result)
                    self.logger.info(f"거래 실행: {trade_result}")
                
                # 4. 성과 업데이트
                self.performance_tracker.update_performance()
                
                # 5. 대기 (1분)
                time.sleep(60)
                
            except Exception as e:
                self.error_count += 1
                self.logger.error(f"메인 루프 오류: {e}")
                
                if self.error_count >= self.max_errors:
                    self.logger.critical("최대 오류 횟수 초과, 봇 중지")
                    self.stop()
                    break
                
                time.sleep(60)  # 오류 후 1분 대기
    
    def _run_monitoring(self):
        """모니터링 루프"""
        while self.is_running:
            try:
                # 1. 시스템 상태 확인
                system_status = self.system_monitor.check_system_status()
                
                # 2. 성과 지표 확인
                performance_metrics = self.performance_tracker.get_current_metrics()
                
                # 3. 알림 조건 확인
                self._check_alerts(system_status, performance_metrics)
                
                # 4. 로그 정리
                self._cleanup_logs()
                
                # 5. 대기 (5분)
                time.sleep(300)
                
            except Exception as e:
                self.logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(60)
    
    def _check_alerts(self, system_status: Dict[str, Any], performance_metrics: Dict[str, Any]):
        """알림 조건 확인"""
        try:
            # 시스템 상태 알림
            if not system_status['is_healthy']:
                self._send_alert(f"시스템 상태 이상: {system_status['issues']}")
            
            # 성과 알림
            daily_pnl = performance_metrics.get('daily_pnl', 0)
            if daily_pnl < -100000:  # 일일 손실 10만원 초과
                self._send_alert(f"일일 손실 경고: {daily_pnl:,.0f} KRW")
            
            # 거래 부재 알림
            if self.last_trade_time:
                hours_since_trade = (datetime.now() - self.last_trade_time).total_seconds() / 3600
                if hours_since_trade > 24:  # 24시간 거래 없음
                    self._send_alert(f"거래 부재 경고: {hours_since_trade:.1f}시간")
            
        except Exception as e:
            self.logger.error(f"알림 확인 오류: {e}")
    
    def _send_alert(self, message: str):
        """알림 전송"""
        try:
            # Telegram 알림 전송
            from notifications.telegram_notifier import TelegramNotifier
            notifier = TelegramNotifier(self.config)
            notifier.send_message(message)
            
            self.logger.info(f"알림 전송: {message}")
            
        except Exception as e:
            self.logger.error(f"알림 전송 실패: {e}")
    
    def _cleanup_logs(self):
        """로그 정리"""
        try:
            # 7일 이상 된 로그 파일 삭제
            import os
            import glob
            from datetime import datetime, timedelta
            
            log_dir = "./logs"
            if os.path.exists(log_dir):
                cutoff_date = datetime.now() - timedelta(days=7)
                
                for log_file in glob.glob(f"{log_dir}/*.log"):
                    file_time = datetime.fromtimestamp(os.path.getctime(log_file))
                    if file_time < cutoff_date:
                        os.remove(log_file)
                        self.logger.info(f"오래된 로그 파일 삭제: {log_file}")
            
        except Exception as e:
            self.logger.error(f"로그 정리 실패: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """봇 상태 반환"""
        uptime = (datetime.now() - self.start_time).total_seconds() / 3600 if self.start_time else 0
        
        return {
            'is_running': self.is_running,
            'uptime_hours': uptime,
            'error_count': self.error_count,
            'last_trade_time': self.last_trade_time.isoformat() if self.last_trade_time else None,
            'performance': self.performance_tracker.get_current_metrics(),
            'system_status': self.system_monitor.check_system_status()
        }
```

### **2. operations/performance_tracker.py**
```python
"""
성과 추적 시스템
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from bot.config import Config

class PerformanceTracker:
    """성과 추적 클래스"""
    
    def __init__(self, config: Config):
        """성과 추적기 초기화"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 성과 데이터
        self.trades = []
        self.daily_performance = {}
        self.initial_capital = config.initial_capital
        self.current_capital = config.initial_capital
        
        # 성과 지표
        self.total_pnl = 0.0
        self.daily_pnl = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        
        self.logger.info("PerformanceTracker 초기화 완료")
    
    def update_trade(self, trade_result: Dict[str, Any]):
        """거래 결과 업데이트"""
        try:
            # 거래 정보 추출
            trade_info = {
                'timestamp': datetime.now(),
                'action': trade_result.get('order', {}).get('side', 'UNKNOWN'),
                'price': trade_result.get('order', {}).get('price', 0),
                'quantity': trade_result.get('order', {}).get('executedQty', 0),
                'commission': trade_result.get('order', {}).get('commission', 0),
                'signal': trade_result.get('signal', {}).get('final_signal', 0)
            }
            
            # PnL 계산
            if trade_info['action'] == 'SELL':
                # 매도 시 수익 계산
                entry_price = self._get_entry_price()
                if entry_price > 0:
                    pnl = (trade_info['price'] - entry_price) * trade_info['quantity']
                    pnl -= trade_info['commission']
                    trade_info['pnl'] = pnl
                    
                    self.total_pnl += pnl
                    self.daily_pnl += pnl
                    self.total_trades += 1
                    
                    if pnl > 0:
                        self.winning_trades += 1
            
            # 거래 기록 저장
            self.trades.append(trade_info)
            
            # 일간 성과 업데이트
            self._update_daily_performance()
            
            self.logger.info(f"거래 업데이트: {trade_info}")
            
        except Exception as e:
            self.logger.error(f"거래 업데이트 실패: {e}")
    
    def _get_entry_price(self) -> float:
        """진입 가격 조회"""
        # 최근 매수 거래의 가격 반환
        for trade in reversed(self.trades):
            if trade['action'] == 'BUY':
                return trade['price']
        return 0.0
    
    def _update_daily_performance(self):
        """일간 성과 업데이트"""
        try:
            today = datetime.now().date()
            
            if today not in self.daily_performance:
                self.daily_performance[today] = {
                    'trades': 0,
                    'pnl': 0.0,
                    'winning_trades': 0,
                    'volume': 0.0
                }
            
            # 오늘 거래만 집계
            today_trades = [t for t in self.trades if t['timestamp'].date() == today]
            
            daily_data = self.daily_performance[today]
            daily_data['trades'] = len(today_trades)
            daily_data['pnl'] = sum(t.get('pnl', 0) for t in today_trades)
            daily_data['winning_trades'] = len([t for t in today_trades if t.get('pnl', 0) > 0])
            daily_data['volume'] = sum(t.get('quantity', 0) * t.get('price', 0) for t in today_trades)
            
        except Exception as e:
            self.logger.error(f"일간 성과 업데이트 실패: {e}")
    
    def update_performance(self):
        """성과 지표 업데이트"""
        try:
            # 일일 PnL 초기화 (새로운 날)
            current_date = datetime.now().date()
            if current_date not in self.daily_performance:
                self.daily_pnl = 0.0
            
            # 성과 지표 계산
            self._calculate_performance_metrics()
            
        except Exception as e:
            self.logger.error(f"성과 업데이트 실패: {e}")
    
    def _calculate_performance_metrics(self):
        """성과 지표 계산"""
        try:
            # 기본 지표
            total_return = self.total_pnl / self.initial_capital if self.initial_capital > 0 else 0
            win_rate = self.winning_trades / self.total_trades if self.total_trades > 0 else 0
            
            # 일간 지표
            today = datetime.now().date()
            daily_data = self.daily_performance.get(today, {})
            daily_return = daily_data.get('pnl', 0) / self.initial_capital if self.initial_capital > 0 else 0
            
            # 주간 지표
            week_ago = today - timedelta(days=7)
            weekly_pnl = sum(d.get('pnl', 0) for d in self.daily_performance.values() 
                           if d.get('date', today) >= week_ago)
            weekly_return = weekly_pnl / self.initial_capital if self.initial_capital > 0 else 0
            
            # 성과 지표 저장
            self.current_metrics = {
                'total_return': total_return,
                'daily_return': daily_return,
                'weekly_return': weekly_return,
                'total_pnl': self.total_pnl,
                'daily_pnl': self.daily_pnl,
                'total_trades': self.total_trades,
                'winning_trades': self.winning_trades,
                'win_rate': win_rate,
                'current_capital': self.initial_capital + self.total_pnl
            }
            
        except Exception as e:
            self.logger.error(f"성과 지표 계산 실패: {e}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """현재 성과 지표 반환"""
        return getattr(self, 'current_metrics', {})
    
    def get_daily_report(self) -> Dict[str, Any]:
        """일간 리포트 생성"""
        try:
            today = datetime.now().date()
            daily_data = self.daily_performance.get(today, {})
            
            return {
                'date': today.isoformat(),
                'trades': daily_data.get('trades', 0),
                'pnl': daily_data.get('pnl', 0),
                'winning_trades': daily_data.get('winning_trades', 0),
                'volume': daily_data.get('volume', 0),
                'win_rate': daily_data.get('winning_trades', 0) / max(daily_data.get('trades', 1), 1)
            }
            
        except Exception as e:
            self.logger.error(f"일간 리포트 생성 실패: {e}")
            return {}
    
    def get_weekly_report(self) -> Dict[str, Any]:
        """주간 리포트 생성"""
        try:
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            weekly_data = {
                'trades': 0,
                'pnl': 0.0,
                'winning_trades': 0,
                'volume': 0.0
            }
            
            for date, data in self.daily_performance.items():
                if date >= week_ago:
                    weekly_data['trades'] += data.get('trades', 0)
                    weekly_data['pnl'] += data.get('pnl', 0)
                    weekly_data['winning_trades'] += data.get('winning_trades', 0)
                    weekly_data['volume'] += data.get('volume', 0)
            
            weekly_data['win_rate'] = weekly_data['winning_trades'] / max(weekly_data['trades'], 1)
            weekly_data['return'] = weekly_data['pnl'] / self.initial_capital if self.initial_capital > 0 else 0
            
            return weekly_data
            
        except Exception as e:
            self.logger.error(f"주간 리포트 생성 실패: {e}")
            return {}
```

### **3. notifications/telegram_notifier.py**
```python
"""
Telegram 알림 시스템
"""

import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from bot.config import Config

class TelegramNotifier:
    """Telegram 알림 클래스"""
    
    def __init__(self, config: Config):
        """Telegram 알림기 초기화"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.bot_token = config.telegram_bot_token
        self.chat_id = config.telegram_chat_id
        
        if not self.bot_token or not self.chat_id:
            self.logger.warning("Telegram 설정이 없습니다")
        
        self.logger.info("TelegramNotifier 초기화 완료")
    
    def send_message(self, message: str) -> bool:
        """메시지 전송"""
        try:
            if not self.bot_token or not self.chat_id:
                return False
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                self.logger.info(f"Telegram 메시지 전송 성공: {message[:50]}...")
                return True
            else:
                self.logger.error(f"Telegram 메시지 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Telegram 메시지 전송 오류: {e}")
            return False
    
    def send_trade_notification(self, trade_result: Dict[str, Any]) -> bool:
        """거래 알림 전송"""
        try:
            order = trade_result.get('order', {})
            signal = trade_result.get('signal', {})
            
            message = f"""
🤖 <b>거래 실행 알림</b>

📊 <b>거래 정보</b>
• 액션: {order.get('side', 'UNKNOWN')}
• 가격: {order.get('price', 0):,.0f} KRW
• 수량: {order.get('executedQty', 0):.4f}
• 수수료: {order.get('commission', 0):.4f}

📈 <b>신호 정보</b>
• 최종 신호: {signal.get('final_signal', 0):.3f}
• 기술적: {signal.get('signal_breakdown', {}).get('technical', 0):.3f}
• 감정: {signal.get('signal_breakdown', {}).get('sentiment', 0):.3f}
• ML: {signal.get('signal_breakdown', {}).get('ml', 0):.3f}

⏰ <b>시간</b>
• {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            return self.send_message(message.strip())
            
        except Exception as e:
            self.logger.error(f"거래 알림 전송 실패: {e}")
            return False
    
    def send_performance_report(self, metrics: Dict[str, Any]) -> bool:
        """성과 리포트 전송"""
        try:
            message = f"""
📊 <b>성과 리포트</b>

💰 <b>수익률</b>
• 총 수익률: {metrics.get('total_return', 0):.2%}
• 일간 수익률: {metrics.get('daily_return', 0):.2%}
• 주간 수익률: {metrics.get('weekly_return', 0):.2%}

📈 <b>거래 통계</b>
• 총 거래: {metrics.get('total_trades', 0)}회
• 승리 거래: {metrics.get('winning_trades', 0)}회
• 승률: {metrics.get('win_rate', 0):.1%}

💵 <b>PnL</b>
• 총 PnL: {metrics.get('total_pnl', 0):,.0f} KRW
• 일간 PnL: {metrics.get('daily_pnl', 0):,.0f} KRW

⏰ <b>시간</b>
• {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            return self.send_message(message.strip())
            
        except Exception as e:
            self.logger.error(f"성과 리포트 전송 실패: {e}")
            return False
    
    def send_alert(self, alert_type: str, message: str) -> bool:
        """경고 알림 전송"""
        try:
            emoji_map = {
                'error': '🚨',
                'warning': '⚠️',
                'info': 'ℹ️',
                'success': '✅'
            }
            
            emoji = emoji_map.get(alert_type, '📢')
            
            alert_message = f"""
{alert_type.upper()} {emoji}

{message}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            return self.send_message(alert_message.strip())
            
        except Exception as e:
            self.logger.error(f"경고 알림 전송 실패: {e}")
            return False
```

### **4. operations/system_monitor.py**
```python
"""
시스템 모니터링
"""

import psutil
import logging
from typing import Dict, Any
from datetime import datetime

class SystemMonitor:
    """시스템 모니터링 클래스"""
    
    def __init__(self):
        """시스템 모니터 초기화"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("SystemMonitor 초기화 완료")
    
    def check_system_status(self) -> Dict[str, Any]:
        """시스템 상태 확인"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # 네트워크 상태
            network = psutil.net_io_counters()
            
            # 상태 판단
            is_healthy = True
            issues = []
            
            if cpu_percent > 80:
                is_healthy = False
                issues.append(f"CPU 사용률 높음: {cpu_percent:.1f}%")
            
            if memory_percent > 80:
                is_healthy = False
                issues.append(f"메모리 사용률 높음: {memory_percent:.1f}%")
            
            if disk_percent > 90:
                is_healthy = False
                issues.append(f"디스크 사용률 높음: {disk_percent:.1f}%")
            
            return {
                'is_healthy': is_healthy,
                'issues': issues,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"시스템 상태 확인 실패: {e}")
            return {
                'is_healthy': False,
                'issues': [f'시스템 모니터링 오류: {e}'],
                'timestamp': datetime.now().isoformat()
            }
    
    def check_process_status(self, process_name: str = 'python') -> Dict[str, Any]:
        """프로세스 상태 확인"""
        try:
            process_count = 0
            total_cpu = 0
            total_memory = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if process_name in proc.info['name'].lower():
                        process_count += 1
                        total_cpu += proc.info['cpu_percent']
                        total_memory += proc.info['memory_percent']
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                'process_count': process_count,
                'total_cpu_percent': total_cpu,
                'total_memory_percent': total_memory,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"프로세스 상태 확인 실패: {e}")
            return {
                'process_count': 0,
                'total_cpu_percent': 0,
                'total_memory_percent': 0,
                'timestamp': datetime.now().isoformat()
            }
```

## ✅ 테스트 방법

### **1. 실시간 봇 테스트**
```python
# test_realtime_bot.py
import os
from dotenv import load_dotenv
from bot.config import Config
from operations.realtime_bot import RealtimeBot

def test_realtime_bot():
    """실시간 봇 테스트"""
    print("=== 실시간 봇 테스트 ===")
    
    # 환경 변수 로드
    load_dotenv()
    
    # 설정 로드
    config = Config()
    
    # 실시간 봇 초기화
    realtime_bot = RealtimeBot(config)
    
    # 상태 확인
    status = realtime_bot.get_status()
    print(f"봇 상태: {status}")
    
    # 봇 시작 (테스트용 5분)
    print("봇 시작 (5분간 테스트)...")
    realtime_bot.start()
    
    import time
    time.sleep(300)  # 5분 대기
    
    # 봇 중지
    realtime_bot.stop()
    
    # 최종 상태 확인
    final_status = realtime_bot.get_status()
    print(f"최종 상태: {final_status}")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_realtime_bot()
```

### **2. Telegram 알림 테스트**
```python
# test_telegram.py
import os
from dotenv import load_dotenv
from bot.config import Config
from notifications.telegram_notifier import TelegramNotifier

def test_telegram():
    """Telegram 알림 테스트"""
    print("=== Telegram 알림 테스트 ===")
    
    # 환경 변수 로드
    load_dotenv()
    
    # 설정 로드
    config = Config()
    
    # Telegram 알림기 초기화
    notifier = TelegramNotifier(config)
    
    # 테스트 메시지 전송
    test_message = "🤖 트레이딩 봇 테스트 메시지입니다!"
    success = notifier.send_message(test_message)
    
    if success:
        print("✅ Telegram 메시지 전송 성공")
    else:
        print("❌ Telegram 메시지 전송 실패")
    
    # 거래 알림 테스트
    test_trade = {
        'order': {
            'side': 'BUY',
            'price': 50000000,
            'executedQty': 0.001,
            'commission': 0.0001
        },
        'signal': {
            'final_signal': 0.8,
            'signal_breakdown': {
                'technical': 0.6,
                'sentiment': 0.7,
                'ml': 0.9
            }
        }
    }
    
    trade_success = notifier.send_trade_notification(test_trade)
    print(f"거래 알림: {'성공' if trade_success else '실패'}")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_telegram()
```

### **3. 성과 추적 테스트**
```python
# test_performance.py
from bot.config import Config
from operations.performance_tracker import PerformanceTracker

def test_performance():
    """성과 추적 테스트"""
    print("=== 성과 추적 테스트 ===")
    
    # 설정 로드
    config = Config()
    
    # 성과 추적기 초기화
    tracker = PerformanceTracker(config)
    
    # 테스트 거래 추가
    test_trades = [
        {
            'order': {'side': 'BUY', 'price': 50000000, 'executedQty': 0.001, 'commission': 0.0001},
            'signal': {'final_signal': 0.8}
        },
        {
            'order': {'side': 'SELL', 'price': 51000000, 'executedQty': 0.001, 'commission': 0.0001},
            'signal': {'final_signal': -0.6}
        }
    ]
    
    for trade in test_trades:
        tracker.update_trade(trade)
    
    # 성과 업데이트
    tracker.update_performance()
    
    # 현재 지표 확인
    metrics = tracker.get_current_metrics()
    print(f"성과 지표: {metrics}")
    
    # 일간 리포트
    daily_report = tracker.get_daily_report()
    print(f"일간 리포트: {daily_report}")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_performance()
```

## 🚀 실행 방법

### **1. 실시간 봇 실행**
```bash
# 실시간 봇 실행
python -c "
import os
from dotenv import load_dotenv
from bot.config import Config
from operations.realtime_bot import RealtimeBot

load_dotenv()
config = Config()
realtime_bot = RealtimeBot(config)
realtime_bot.start()
"
```

### **2. Telegram 알림 테스트**
```bash
# Telegram 알림 테스트
python test_telegram.py
```

### **3. 성과 추적 테스트**
```bash
# 성과 추적 테스트
python test_performance.py
```

## 📊 Phase 4 완료 기준

### **✅ 완료 체크리스트**
- [ ] 24/7 실시간 봇 실행 완료
- [ ] Telegram 알림 시스템 구축 완료
- [ ] 실시간 PnL 추적 완료
- [ ] 자동 재시작 시스템 구현 완료
- [ ] 로그 관리 및 분석 완료
- [ ] 모든 테스트 통과

### **🎯 성공 지표**
- **실시간 운영**: 24/7 안정적 운영
- **알림 시스템**: Telegram 알림 정상 작동
- **성과 추적**: 실시간 PnL 정확한 계산
- **시스템 모니터링**: 자동 재시작 및 오류 복구
- **운영 안정성**: 95% 이상 가동률

## 🎉 전체 프로젝트 완료!

Phase 4까지 완료되면 **완전한 트레이딩 봇 시스템**이 구축됩니다!

### **최종 성과**
- ✅ **기본 환경**: Python + Binance API + SQLite
- ✅ **데이터 수집**: 과거 데이터 + 실시간 WebSocket + 감정 데이터
- ✅ **통합 봇**: 기술적 분석 + 감정분석 + ML + 거래 실행
- ✅ **백테스팅**: 성능 평가 + 파라미터 최적화 + 결과 시각화
- ✅ **실시간 운영**: 24/7 운영 + Telegram 알림 + 성과 추적

### **다음 단계**
이제 실제 거래를 시작할 수 있습니다! 🚀 