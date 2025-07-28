"""
진행 상황 추적 클래스
과거 데이터 수집 중단/재개를 위한 진행 상황 관리
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class ProgressTracker:
    """진행 상황 추적 클래스"""
    
    def __init__(self, progress_file: str = None):
        """진행 상황 추적기 초기화"""
        if progress_file is None:
            # 기본 경로 설정 - /data 디렉토리에 저장
            progress_file = os.path.join("trading_bot", "data", "data_collection_progress.json")
        
        self.progress_file = progress_file
        self.logger = logging.getLogger(__name__)
        
        # 진행 상황 로드
        self.progress = self.load_progress()
        
        self.logger.info("진행 상황 추적기 초기화 완료")
    
    def load_progress(self) -> Dict[str, Any]:
        """진행 상황 파일 로드"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                self.logger.info(f"진행 상황 파일 로드: {self.progress_file}")
                return progress
            else:
                # 새로운 진행 상황 초기화
                progress = {
                    'start_time': datetime.now().isoformat(),
                    'total_coins': 50,
                    'total_intervals': 16,
                    'completed_coins': [],
                    'current_coin': None,
                    'current_coin_progress': {},
                    'completed_intervals': {},
                    'failed_coins': [],
                    'failed_intervals': {},
                    'last_successful_time': None,
                    'total_completed': 0,
                    'total_failed': 0
                }
                self.save_progress(progress)
                return progress
                
        except Exception as e:
            self.logger.error(f"진행 상황 파일 로드 실패: {e}")
            return self._create_default_progress()
    
    def _create_default_progress(self) -> Dict[str, Any]:
        """기본 진행 상황 생성"""
        return {
            'start_time': datetime.now().isoformat(),
            'total_coins': 50,
            'total_intervals': 16,
            'completed_coins': [],
            'current_coin': None,
            'current_coin_progress': {},
            'completed_intervals': {},
            'failed_coins': [],
            'failed_intervals': {},
            'last_successful_time': None,
            'total_completed': 0,
            'total_failed': 0
        }
    
    def save_progress(self, progress: Dict[str, Any] = None):
        """진행 상황 파일 저장"""
        try:
            if progress is None:
                progress = self.progress
            
            # 디렉토리가 있는 경우에만 생성
            dir_path = os.path.dirname(self.progress_file)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"진행 상황 저장: {self.progress_file}")
            
        except Exception as e:
            self.logger.error(f"진행 상황 파일 저장 실패: {e}")
    
    def start_coin_collection(self, symbol: str):
        """코인 수집 시작"""
        self.progress['current_coin'] = symbol
        self.progress['current_coin_progress'] = {
            'start_time': datetime.now().isoformat(),
            'completed_intervals': [],
            'failed_intervals': [],
            'current_interval': None
        }
        self.save_progress()
        self.logger.info(f"코인 수집 시작: {symbol}")
    
    def complete_coin_collection(self, symbol: str):
        """코인 수집 완료"""
        if symbol not in self.progress['completed_coins']:
            self.progress['completed_coins'].append(symbol)
        
        if symbol in self.progress['failed_coins']:
            self.progress['failed_coins'].remove(symbol)
        
        self.progress['current_coin'] = None
        self.progress['current_coin_progress'] = {}
        self.progress['last_successful_time'] = datetime.now().isoformat()
        self.progress['total_completed'] += 1
        
        self.save_progress()
        self.logger.info(f"코인 수집 완료: {symbol}")
    
    def fail_coin_collection(self, symbol: str, error: str):
        """코인 수집 실패"""
        if symbol not in self.progress['failed_coins']:
            self.progress['failed_coins'].append(symbol)
        
        self.progress['current_coin'] = None
        self.progress['current_coin_progress'] = {}
        self.progress['total_failed'] += 1
        
        self.save_progress()
        self.logger.error(f"코인 수집 실패: {symbol} - {error}")
    
    def start_interval_collection(self, symbol: str, interval: str):
        """간격 수집 시작"""
        if symbol not in self.progress['completed_intervals']:
            self.progress['completed_intervals'][symbol] = []
        
        self.progress['current_coin_progress']['current_interval'] = interval
        self.save_progress()
        self.logger.info(f"간격 수집 시작: {symbol} {interval}")
    
    def complete_interval_collection(self, symbol: str, interval: str):
        """간격 수집 완료"""
        if symbol not in self.progress['completed_intervals']:
            self.progress['completed_intervals'][symbol] = []
        
        if interval not in self.progress['completed_intervals'][symbol]:
            self.progress['completed_intervals'][symbol].append(interval)
        
        if symbol in self.progress['failed_intervals'] and interval in self.progress['failed_intervals'][symbol]:
            self.progress['failed_intervals'][symbol].remove(interval)
        
        self.progress['current_coin_progress']['completed_intervals'].append(interval)
        self.progress['current_coin_progress']['current_interval'] = None
        
        self.save_progress()
        self.logger.info(f"간격 수집 완료: {symbol} {interval}")
    
    def fail_interval_collection(self, symbol: str, interval: str, error: str):
        """간격 수집 실패"""
        if symbol not in self.progress['failed_intervals']:
            self.progress['failed_intervals'][symbol] = []
        
        if interval not in self.progress['failed_intervals'][symbol]:
            self.progress['failed_intervals'][symbol].append(interval)
        
        self.progress['current_coin_progress']['failed_intervals'].append(interval)
        self.progress['current_coin_progress']['current_interval'] = None
        
        self.save_progress()
        self.logger.error(f"간격 수집 실패: {symbol} {interval} - {error}")
    
    def get_remaining_coins(self, all_coins: List[str]) -> List[str]:
        """남은 코인 목록 조회"""
        completed = set(self.progress['completed_coins'])
        failed = set(self.progress['failed_coins'])
        
        remaining = [coin for coin in all_coins if coin not in completed and coin not in failed]
        
        # 현재 진행 중인 코인이 있으면 추가
        if self.progress['current_coin'] and self.progress['current_coin'] not in remaining:
            remaining.insert(0, self.progress['current_coin'])
        
        return remaining
    
    def get_remaining_intervals(self, symbol: str, all_intervals: List[str]) -> List[str]:
        """남은 간격 목록 조회"""
        completed = set(self.progress['completed_intervals'].get(symbol, []))
        failed = set(self.progress['failed_intervals'].get(symbol, []))
        
        remaining = [interval for interval in all_intervals if interval not in completed and interval not in failed]
        
        # 현재 진행 중인 간격이 있으면 추가
        current_interval = self.progress['current_coin_progress'].get('current_interval')
        if current_interval and current_interval not in remaining:
            remaining.insert(0, current_interval)
        
        return remaining
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """진행 상황 요약"""
        total_coins = self.progress['total_coins']
        total_intervals = self.progress['total_intervals']
        completed_coins = len(self.progress['completed_coins'])
        failed_coins = len(self.progress['failed_coins'])
        
        total_completed_intervals = sum(len(intervals) for intervals in self.progress['completed_intervals'].values())
        total_failed_intervals = sum(len(intervals) for intervals in self.progress['failed_intervals'].values())
        
        coin_progress = (completed_coins / total_coins) * 100 if total_coins > 0 else 0
        interval_progress = (total_completed_intervals / (total_coins * total_intervals)) * 100 if total_coins * total_intervals > 0 else 0
        
        return {
            'coin_progress': coin_progress,
            'interval_progress': interval_progress,
            'completed_coins': completed_coins,
            'failed_coins': failed_coins,
            'total_completed_intervals': total_completed_intervals,
            'total_failed_intervals': total_failed_intervals,
            'current_coin': self.progress['current_coin'],
            'current_interval': self.progress['current_coin_progress'].get('current_interval'),
            'start_time': self.progress['start_time'],
            'last_successful_time': self.progress['last_successful_time']
        }
    
    def print_progress_summary(self):
        """진행 상황 요약 출력"""
        summary = self.get_progress_summary()
        
        print("="*60)
        print("📊 데이터 수집 진행 상황")
        print("="*60)
        print(f"코인 진행률: {summary['coin_progress']:.1f}% ({summary['completed_coins']}/{self.progress['total_coins']})")
        print(f"간격 진행률: {summary['interval_progress']:.1f}% ({summary['total_completed_intervals']}/{self.progress['total_coins'] * self.progress['total_intervals']})")
        print(f"완료된 코인: {summary['completed_coins']}개")
        print(f"실패한 코인: {summary['failed_coins']}개")
        print(f"완료된 간격: {summary['total_completed_intervals']}개")
        print(f"실패한 간격: {summary['total_failed_intervals']}개")
        
        if summary['current_coin']:
            print(f"현재 진행 중: {summary['current_coin']}")
            if summary['current_interval']:
                print(f"현재 간격: {summary['current_interval']}")
        
        if summary['start_time']:
            start_time = datetime.fromisoformat(summary['start_time'])
            print(f"시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if summary['last_successful_time']:
            last_time = datetime.fromisoformat(summary['last_successful_time'])
            print(f"마지막 성공: {last_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("="*60)
    
    def reset_progress(self):
        """진행 상황 초기화"""
        self.progress = self._create_default_progress()
        self.save_progress()
        self.logger.info("진행 상황 초기화 완료")
    
    def cleanup_progress_file(self):
        """진행 상황 파일 삭제"""
        try:
            if os.path.exists(self.progress_file):
                os.remove(self.progress_file)
                self.logger.info(f"진행 상황 파일 삭제: {self.progress_file}")
        except Exception as e:
            self.logger.error(f"진행 상황 파일 삭제 실패: {e}") 