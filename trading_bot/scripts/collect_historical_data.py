#!/usr/bin/env python3
"""
과거데이터 수집 스크립트
독립적으로 실행되어 3년치 모든 데이터를 1분봉부터 수집합니다.
최대한 빠른 다운로드를 위해 병렬 처리 및 배치 요청을 사용합니다.
"""

import sys
import os
import logging
import requests
import pandas as pd
import time
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.config import Config
from config.coins_config import CoinsConfig
from data.database import Database
from scripts.progress_tracker import ProgressTracker

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/historical_data_collection.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class FastHistoricalDataCollector:
    """고속 과거데이터 수집 클래스 - 병렬 처리 및 배치 요청"""
    
    def __init__(self, config: Config, coins_config: CoinsConfig, database: Database):
        """데이터 수집기 초기화"""
        self.config = config
        self.coins_config = coins_config
        self.database = database
        self.logger = logging.getLogger(__name__)
        
        # Binance API 설정
        self.base_url = "https://api.binance.com/api/v3"
        self.api_key = config.binance_api_key
        self.secret_key = config.binance_secret_key
        
        # 수집할 모든 시간대 간격
        self.intervals = [
            '1m', '3m', '5m', '15m', '30m',  # 분봉
            '1h', '2h', '4h', '6h', '8h', '12h',  # 시간봉
            '1d', '3d', '1w', '1M'  # 일봉, 주봉, 월봉
        ]
        
        # API 제한 설정
        self.max_requests_per_second = 10  # 초당 최대 요청 수
        self.max_concurrent_requests = 20  # 동시 요청 수
        self.request_delay = 0.1  # 요청 간 지연 (초)
        
        # 세마포어로 동시 요청 제한
        self.semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        self.request_count = 0
        self.request_lock = threading.Lock()
        
        # 진행 상황 추적기 추가
        self.progress_tracker = ProgressTracker()
        
        self.logger.info("고속 과거데이터 수집기 초기화 완료")
    
    async def get_historical_data_async(self, session: aiohttp.ClientSession, 
                                      symbol: str, interval: str, 
                                      start_time: int, end_time: int) -> pd.DataFrame:
        """비동기로 특정 간격의 과거 데이터 수집 - 3년치 모든 데이터 수집"""
        async with self.semaphore:
            try:
                all_data = []
                current_start = start_time
                
                while current_start < end_time:
                    # API 호출 제한 관리
                    await self._rate_limit()
                    
                    url = f"{self.base_url}/klines"
                    params = {
                        'symbol': symbol,
                        'interval': interval,
                        'startTime': current_start,
                        'endTime': end_time,
                        'limit': 1000  # Binance API 최대 제한
                    }
                    
                    async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if not data:
                                break
                            
                            all_data.extend(data)
                            
                            # 마지막 캔들의 종료 시간을 다음 시작 시간으로 설정
                            if data:
                                last_candle = data[-1]
                                current_start = int(last_candle[6]) + 1  # close_time + 1ms
                            else:
                                break
                        else:
                            self.logger.error(f"API 요청 실패: {response.status}")
                            break
                
                if not all_data:
                    return pd.DataFrame()
                
                # 데이터프레임 변환
                df = pd.DataFrame(all_data, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                    'taker_buy_quote', 'ignore'
                ])
                
                # 데이터 타입 변환
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # 필요한 컬럼만 선택
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                
                self.logger.info(f"{symbol} {interval}: {len(df)}개 캔들 수집 완료")
                return df
                        
            except Exception as e:
                self.logger.error(f"{symbol} {interval} 데이터 수집 실패: {e}")
                return pd.DataFrame()
    
    async def _rate_limit(self):
        """API 호출 제한 관리"""
        with self.request_lock:
            self.request_count += 1
            if self.request_count >= self.max_requests_per_second:
                await asyncio.sleep(1)
                self.request_count = 0
            else:
                await asyncio.sleep(self.request_delay)
    
    def get_historical_data_batch(self, symbol: str, interval: str, 
                                start_time: int, end_time: int) -> pd.DataFrame:
        """배치로 대용량 데이터 수집 (3년치 데이터를 여러 번에 나누어 수집)"""
        all_data = []
        current_start = start_time
        
        while current_start < end_time:
            # 배치 크기 계산 (간격별로 조정)
            batch_size = self._calculate_batch_size(interval)
            current_end = min(current_start + batch_size, end_time)
            
            try:
                # 동기 요청으로 배치 데이터 수집
                url = f"{self.base_url}/klines"
                params = {
                    'symbol': symbol,
                    'interval': interval,
                    'startTime': current_start,
                    'endTime': current_end,
                    'limit': 1000
                }
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                if data:
                    # 데이터프레임 변환
                    df = pd.DataFrame(data, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume',
                        'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                        'taker_buy_quote', 'ignore'
                    ])
                    
                    # 데이터 타입 변환
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # 필요한 컬럼만 선택
                    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                    all_data.append(df)
                
                # 다음 배치 시작 시간 설정
                if data:
                    last_timestamp = data[-1][0]  # 마지막 캔들의 타임스탬프
                    current_start = last_timestamp + 1
                else:
                    current_start = current_end
                
                # API 호출 제한 방지
                time.sleep(0.05)  # 50ms 지연
                
            except Exception as e:
                self.logger.error(f"{symbol} {interval} 배치 수집 실패: {e}")
                current_start = current_end
                continue
        
        if all_data:
            # 모든 배치 데이터 합치기
            combined_df = pd.concat(all_data, ignore_index=True)
            combined_df = combined_df.drop_duplicates(subset=['timestamp'])
            combined_df = combined_df.sort_values('timestamp')
            
            self.logger.info(f"{symbol} {interval}: 총 {len(combined_df)}개 캔들 수집 완료")
            return combined_df
        
        return pd.DataFrame()
    
    def _calculate_batch_size(self, interval: str) -> int:
        """간격별 배치 크기 계산 (밀리초 단위)"""
        batch_sizes = {
            '1m': 1000 * 60 * 1000,      # 1000분
            '3m': 1000 * 3 * 60 * 1000,  # 1000 * 3분
            '5m': 1000 * 5 * 60 * 1000,  # 1000 * 5분
            '15m': 1000 * 15 * 60 * 1000, # 1000 * 15분
            '30m': 1000 * 30 * 60 * 1000, # 1000 * 30분
            '1h': 1000 * 60 * 60 * 1000,  # 1000시간
            '2h': 1000 * 2 * 60 * 60 * 1000,  # 1000 * 2시간
            '4h': 1000 * 4 * 60 * 60 * 1000,  # 1000 * 4시간
            '6h': 1000 * 6 * 60 * 60 * 1000,  # 1000 * 6시간
            '8h': 1000 * 8 * 60 * 60 * 1000,  # 1000 * 8시간
            '12h': 1000 * 12 * 60 * 60 * 1000, # 1000 * 12시간
            '1d': 1000 * 24 * 60 * 60 * 1000,  # 1000일
            '3d': 1000 * 3 * 24 * 60 * 60 * 1000,  # 1000 * 3일
            '1w': 1000 * 7 * 24 * 60 * 60 * 1000,  # 1000주
            '1M': 1000 * 30 * 24 * 60 * 60 * 1000, # 1000 * 30일
        }
        return batch_sizes.get(interval, 1000 * 60 * 1000)  # 기본값: 1000분
    
    def collect_all_data_for_symbol_parallel(self, symbol: str, days: int = 1095) -> Dict[str, pd.DataFrame]:
        """단일 코인의 모든 간격 데이터 병렬 수집 (3년치)"""
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        all_data = {}
        
        self.logger.info(f"{symbol} 3년치 모든 간격 데이터 병렬 수집 시작")
        
        # ThreadPoolExecutor로 병렬 처리
        with ThreadPoolExecutor(max_workers=8) as executor:
            # 각 간격별로 작업 제출
            future_to_interval = {
                executor.submit(self.get_historical_data_batch, symbol, interval, start_time, end_time): interval
                for interval in self.intervals
            }
            
            # 완료된 작업 처리
            for future in as_completed(future_to_interval):
                interval = future_to_interval[future]
                try:
                    df = future.result()
                    if not df.empty:
                        all_data[interval] = df
                        
                        # 데이터베이스에 저장
                        data_list = []
                        for _, row in df.iterrows():
                            data = {
                                'timestamp': int(row['timestamp'].timestamp() * 1000),
                                'open': row['open'],
                                'high': row['high'],
                                'low': row['low'],
                                'close': row['close'],
                                'volume': row['volume']
                            }
                            data_list.append(data)
                        

                        
                        # 코인별 테이블에도 저장
                        self.database.save_price_data_to_coin_table(symbol, interval, data_list)
                        
                except Exception as e:
                    self.logger.error(f"{symbol} {interval} 병렬 수집 실패: {e}")
                    continue
        
        self.logger.info(f"{symbol} 데이터 수집 완료: {len(all_data)}개 간격")
        return all_data
    
    async def collect_all_coins_all_data_async(self, days: int = 1095) -> Dict[str, Dict[str, pd.DataFrame]]:
        """모든 코인의 모든 간격 데이터 비동기 수집 (3년치)"""
        coins = self.coins_config.coins
        all_coins_data = {}
        
        self.logger.info(f"50개 코인 3년치 모든 간격 데이터 비동기 수집 시작")
        self.logger.info(f"수집 간격: {self.intervals}")
        
        # aiohttp 세션 생성
        async with aiohttp.ClientSession() as session:
            # 코인별로 작업 생성
            tasks = []
            for symbol in coins:
                task = self._collect_single_coin_async(session, symbol, days)
                tasks.append(task)
            
            # 모든 작업 동시 실행
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 처리
            for i, result in enumerate(results):
                symbol = coins[i]
                if isinstance(result, Exception):
                    self.logger.error(f"{symbol} 수집 실패: {result}")
                elif result:
                    all_coins_data[symbol] = result
        
        self.logger.info(f"전체 데이터 수집 완료: {len(all_coins_data)}개 코인")
        return all_coins_data
    
    async def _collect_single_coin_async(self, session: aiohttp.ClientSession, 
                                       symbol: str, days: int) -> Dict[str, pd.DataFrame]:
        """단일 코인 비동기 수집"""
        try:
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            all_data = {}
            
            # 각 간격별로 배치 수집 (비동기 대신 배치 처리 사용)
            for interval in self.intervals:
                try:
                    self.logger.info(f"{symbol} {interval} 배치 수집 중...")
                    
                    # 배치로 데이터 수집
                    df = self.get_historical_data_batch(symbol, interval, start_time, end_time)
                    
                    if not df.empty:
                        all_data[interval] = df
                        
                        # 데이터베이스에 저장
                        data_list = []
                        for _, row in df.iterrows():
                            data = {
                                'timestamp': int(row['timestamp'].timestamp() * 1000),
                                'open': row['open'],
                                'high': row['high'],
                                'low': row['low'],
                                'close': row['close'],
                                'volume': row['volume']
                            }
                            data_list.append(data)
                        
                                                # 코인별 테이블에 저장
                        self.database.save_price_data_to_coin_table(symbol, interval, data_list)
                    
                except Exception as e:
                    self.logger.error(f"{symbol} {interval} 배치 수집 실패: {e}")
                    continue
            
            return all_data
            
        except Exception as e:
            self.logger.error(f"{symbol} 비동기 수집 실패: {e}")
            return {}

class HistoricalDataCollector:
    """과거데이터 수집 클래스 - 3년치 모든 데이터 수집"""
    
    def __init__(self, config: Config, coins_config: CoinsConfig, database: Database):
        """데이터 수집기 초기화"""
        self.config = config
        self.coins_config = coins_config
        self.database = database
        self.logger = logging.getLogger(__name__)
        
        # Binance API 설정
        self.base_url = "https://api.binance.com/api/v3"
        self.api_key = config.binance_api_key
        self.secret_key = config.binance_secret_key
        
        # 수집할 모든 시간대 간격
        self.intervals = [
            '1m', '3m', '5m', '15m', '30m',  # 분봉
            '1h', '2h', '4h', '6h', '8h', '12h',  # 시간봉
            '1d', '3d', '1w', '1M'  # 일봉, 주봉, 월봉
        ]
        
        # 각 간격별 최대 수집 개수 (3년치 데이터를 위해 제한 없음)
        self.limit = 1000000  # 100만개로 설정 (실제로는 시간 범위로 제한됨)
        
        # 진행 상황 추적기 추가
        self.progress_tracker = ProgressTracker()
        
        self.logger.info("3년치 과거데이터 수집기 초기화 완료")
    
    def get_historical_data(self, symbol: str, interval: str, start_time: int, end_time: int) -> pd.DataFrame:
        """특정 간격의 과거 데이터 수집 - 3년치 모든 데이터 수집"""
        try:
            all_data = []
            current_start = start_time
            
            while current_start < end_time:
                url = f"{self.base_url}/klines"
                params = {
                    'symbol': symbol,
                    'interval': interval,
                    'startTime': current_start,
                    'endTime': end_time,
                    'limit': 1000  # Binance API 최대 제한
                }
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                if not data:
                    break
                
                all_data.extend(data)
                
                # 마지막 캔들의 종료 시간을 다음 시작 시간으로 설정
                if data:
                    last_candle = data[-1]
                    current_start = int(last_candle[6]) + 1  # close_time + 1ms
                else:
                    break
                
                # API 제한 방지
                time.sleep(0.1)
            
            if not all_data:
                return pd.DataFrame()
            
            # 데이터프레임 변환
            df = pd.DataFrame(all_data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # 데이터 타입 변환
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 필요한 컬럼만 선택
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
            self.logger.info(f"{symbol} {interval}: {len(df)}개 캔들 수집 완료")
            return df
            
        except Exception as e:
            self.logger.error(f"{symbol} {interval} 데이터 수집 실패: {e}")
            return pd.DataFrame()
    
    def collect_all_data_for_symbol(self, symbol: str, days: int = 1095) -> Dict[str, pd.DataFrame]:
        """단일 코인의 모든 간격 데이터 수집 (3년치)"""
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        all_data = {}
        
        self.logger.info(f"{symbol} 3년치 모든 간격 데이터 수집 시작")
        
        for interval in self.intervals:
            try:
                self.logger.info(f"{symbol} {interval} 수집 중...")
                
                # 해당 간격의 데이터 수집
                df = self.get_historical_data(symbol, interval, start_time, end_time)
                
                if not df.empty:
                    all_data[interval] = df
                    
                    # 데이터베이스에 저장 - 리스트로 변환하여 전달
                    data_list = []
                    for _, row in df.iterrows():
                        data = {
                            'timestamp': int(row['timestamp'].timestamp() * 1000),
                            'open': row['open'],
                            'high': row['high'],
                            'low': row['low'],
                            'close': row['close'],
                            'volume': row['volume']
                        }
                        data_list.append(data)
                    
                    # 코인별 테이블에 저장 (새로운 구조)
                    self.database.save_price_data_to_coin_table(symbol, interval, data_list)
                
                # API 호출 제한 방지
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"{symbol} {interval} 수집 실패: {e}")
                continue
        
        self.logger.info(f"{symbol} 데이터 수집 완료: {len(all_data)}개 간격")
        return all_data
    
    def collect_all_coins_all_data(self, days: int = 1095) -> Dict[str, Dict[str, pd.DataFrame]]:
        """모든 코인의 모든 간격 데이터 수집 (3년치) - 재개 가능"""
        coins = self.coins_config.coins
        all_coins_data = {}
        
        # 진행 상황 표시
        self.progress_tracker.print_progress_summary()
        
        # 남은 코인 목록 조회
        remaining_coins = self.progress_tracker.get_remaining_coins(coins)
        
        self.logger.info(f"50개 코인 3년치 모든 간격 데이터 수집 시작")
        self.logger.info(f"수집 간격: {self.intervals}")
        self.logger.info(f"남은 코인 수: {len(remaining_coins)}개")
        
        for i, symbol in enumerate(remaining_coins, 1):
            try:
                self.logger.info(f"진행률: {i}/{len(remaining_coins)} - {symbol} 수집 중...")
                
                # 코인 수집 시작
                self.progress_tracker.start_coin_collection(symbol)
                
                # 해당 코인의 모든 간격 데이터 수집
                symbol_data = self.collect_all_data_for_symbol_with_progress(symbol, days)
                
                if symbol_data:
                    all_coins_data[symbol] = symbol_data
                    self.progress_tracker.complete_coin_collection(symbol)
                else:
                    self.progress_tracker.fail_coin_collection(symbol, "데이터 수집 실패")
                
                # 코인 간 API 호출 제한 방지
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"{symbol} 전체 수집 실패: {e}")
                self.progress_tracker.fail_coin_collection(symbol, str(e))
                continue
        
        self.logger.info(f"전체 데이터 수집 완료: {len(all_coins_data)}개 코인")
        return all_coins_data
    
    def collect_all_data_for_symbol_with_progress(self, symbol: str, days: int = 1095) -> Dict[str, pd.DataFrame]:
        """단일 코인의 모든 간격 데이터 수집 (진행 상황 추적 포함)"""
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        all_data = {}
        
        # 남은 간격 목록 조회
        remaining_intervals = self.progress_tracker.get_remaining_intervals(symbol, self.intervals)
        
        self.logger.info(f"{symbol} 3년치 모든 간격 데이터 수집 시작")
        self.logger.info(f"남은 간격 수: {len(remaining_intervals)}개")
        
        for interval in remaining_intervals:
            try:
                self.logger.info(f"{symbol} {interval} 수집 중...")
                
                # 간격 수집 시작
                self.progress_tracker.start_interval_collection(symbol, interval)
                
                # 해당 간격의 데이터 수집
                df = self.get_historical_data(symbol, interval, start_time, end_time)
                
                if not df.empty:
                    all_data[interval] = df
                    
                    # 데이터베이스에 저장
                    data_list = []
                    for _, row in df.iterrows():
                        data = {
                            'timestamp': int(row['timestamp'].timestamp() * 1000),
                            'open': row['open'],
                            'high': row['high'],
                            'low': row['low'],
                            'close': row['close'],
                            'volume': row['volume']
                        }
                        data_list.append(data)
                    
                    # 코인별 테이블에 저장
                    self.database.save_price_data_to_coin_table(symbol, interval, data_list)
                    
                    # 간격 수집 완료
                    self.progress_tracker.complete_interval_collection(symbol, interval)
                else:
                    self.progress_tracker.fail_interval_collection(symbol, interval, "데이터 없음")
                
                # API 호출 제한 방지
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"{symbol} {interval} 수집 실패: {e}")
                self.progress_tracker.fail_interval_collection(symbol, interval, str(e))
                continue
        
        self.logger.info(f"{symbol} 데이터 수집 완료: {len(all_data)}개 간격")
        return all_data
    
    def collect_single_coin_single_interval(self, symbol: str, interval: str, days: int = 30) -> pd.DataFrame:
        """단일 코인의 단일 간격 데이터 수집"""
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        self.logger.info(f"{symbol} {interval} {days}일 데이터 수집 시작")
        
        df = self.get_historical_data(symbol, interval, start_time, end_time)
        
        if not df.empty:
            # 데이터베이스에 저장
            data_list = []
            for _, row in df.iterrows():
                data = {
                    'timestamp': int(row['timestamp'].timestamp() * 1000),
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'close': row['close'],
                    'volume': row['volume']
                }
                data_list.append(data)
            
            # 코인별 테이블에 저장 (새로운 구조)
            self.database.save_price_data_to_coin_table(symbol, interval, data_list)
        
        return df

    def collect_missing_data(self, symbol: str, interval: str) -> pd.DataFrame:
        """누락된 데이터 수집 (과거 데이터와 실시간 데이터 사이의 갭 메우기)"""
        try:
            # 누락된 데이터 기간 조회
            missing_period = self.database.get_missing_data_period(symbol, interval)
            
            if not missing_period:
                self.logger.info(f"{symbol} {interval}: 누락된 데이터 없음")
                return pd.DataFrame()
            
            start_time = missing_period['start_time']
            end_time = missing_period['end_time']
            
            # 누락된 기간이 너무 짧으면 수집하지 않음 (1분 이하)
            if end_time - start_time < 60000:  # 1분 = 60,000ms
                self.logger.info(f"{symbol} {interval}: 누락 기간이 너무 짧음 (1분 이하)")
                return pd.DataFrame()
            
            self.logger.info(f"{symbol} {interval}: 누락된 데이터 수집 시작 ({start_time} ~ {end_time})")
            
            # 누락된 데이터 수집
            df = self.get_historical_data_batch(symbol, interval, start_time, end_time)
            
            if not df.empty:
                # 데이터베이스에 저장
                data_list = []
                for _, row in df.iterrows():
                    data = {
                        'timestamp': int(row['timestamp'].timestamp() * 1000),
                        'open': row['open'],
                        'high': row['high'],
                        'low': row['low'],
                        'close': row['close'],
                        'volume': row['volume']
                    }
                    data_list.append(data)
                
                # 코인별 테이블에 저장
                self.database.save_price_data_to_coin_table(symbol, interval, data_list)
                
                self.logger.info(f"{symbol} {interval}: 누락된 데이터 {len(df)}개 수집 완료")
            
            return df
            
        except Exception as e:
            self.logger.error(f"{symbol} {interval} 누락 데이터 수집 실패: {e}")
            return pd.DataFrame()
    
    def collect_all_missing_data(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """모든 코인의 모든 간격 누락 데이터 수집"""
        coins = self.coins_config.coins
        all_missing_data = {}
        
        self.logger.info("모든 코인의 누락된 데이터 수집 시작")
        
        for symbol in coins:
            symbol_missing_data = {}
            
            for interval in self.intervals:
                try:
                    df = self.collect_missing_data(symbol, interval)
                    if not df.empty:
                        symbol_missing_data[interval] = df
                except Exception as e:
                    self.logger.error(f"{symbol} {interval} 누락 데이터 수집 실패: {e}")
                    continue
            
            if symbol_missing_data:
                all_missing_data[symbol] = symbol_missing_data
        
        self.logger.info(f"누락된 데이터 수집 완료: {len(all_missing_data)}개 코인")
        return all_missing_data

def collect_historical_data_for_all_coins_all_intervals_fast(days: int = 1095):
    """모든 코인의 모든 간격 데이터 고속 수집 (3년치) - 병렬 처리"""
    try:
        logger.info("=== 3년치 모든 데이터 고속 수집 시작 (병렬 처리) ===")
        
        # 설정 로드
        config = Config.from_env()
        coins_config = CoinsConfig()
        database = Database()
        
        # 고속 데이터 수집기 초기화
        collector = FastHistoricalDataCollector(config, coins_config, database)
        
        # 전체 데이터 수집 (병렬 처리)
        logger.info(f"50개 코인 3년치 모든 간격 데이터 병렬 수집 시작")
        all_data = asyncio.run(collector.collect_all_coins_all_data_async(days=days))
        
        logger.info(f"=== 3년치 모든 데이터 고속 수집 완료 ===")
        logger.info(f"수집된 코인 수: {len(all_data)}")
        
        # 수집 결과 요약
        for symbol, intervals_data in all_data.items():
            logger.info(f"{symbol}: {len(intervals_data)}개 간격")
            for interval, df in intervals_data.items():
                logger.info(f"  {interval}: {len(df)}개 캔들")
        
        return all_data
        
    except Exception as e:
        logger.error(f"3년치 모든 데이터 고속 수집 실패: {e}")
        raise

def collect_historical_data_for_single_coin_all_intervals_fast(symbol: str, days: int = 1095):
    """단일 코인의 모든 간격 데이터 고속 수집 (3년치) - 병렬 처리"""
    try:
        logger.info(f"=== {symbol} 3년치 모든 간격 데이터 고속 수집 시작 (병렬 처리) ===")
        
        # 설정 로드
        config = Config.from_env()
        coins_config = CoinsConfig()
        database = Database()
        
        # 고속 데이터 수집기 초기화
        collector = FastHistoricalDataCollector(config, coins_config, database)
        
        # 단일 코인 모든 간격 데이터 수집 (병렬 처리)
        symbol_data = collector.collect_all_data_for_symbol_parallel(symbol, days=days)
        
        logger.info(f"=== {symbol} 3년치 모든 간격 데이터 고속 수집 완료 ===")
        logger.info(f"수집된 간격 수: {len(symbol_data)}")
        
        # 수집 결과 요약
        for interval, df in symbol_data.items():
            logger.info(f"  {interval}: {len(df)}개 캔들")
        
        return symbol_data
        
    except Exception as e:
        logger.error(f"{symbol} 3년치 모든 간격 데이터 고속 수집 실패: {e}")
        raise

def collect_historical_data_for_all_coins_all_intervals(days: int = 1095):
    """모든 코인의 모든 간격 데이터 수집 (3년치) - 재개 가능"""
    try:
        logger.info("=== 3년치 모든 데이터 수집 시작 (재개 가능) ===")
        
        # 설정 로드
        config = Config.from_env()
        coins_config = CoinsConfig()
        database = Database()
        
        # 데이터 수집기 초기화
        collector = HistoricalDataCollector(config, coins_config, database)
        
        # 전체 데이터 수집 (재개 가능)
        logger.info(f"50개 코인 3년치 모든 간격 데이터 수집 시작")
        all_data = collector.collect_all_coins_all_data(days=days)
        
        logger.info(f"=== 3년치 모든 데이터 수집 완료 ===")
        logger.info(f"수집된 코인 수: {len(all_data)}")
        
        # 수집 결과 요약
        for symbol, intervals_data in all_data.items():
            logger.info(f"{symbol}: {len(intervals_data)}개 간격")
            for interval, df in intervals_data.items():
                logger.info(f"  {interval}: {len(df)}개 캔들")
        
        return all_data
        
    except Exception as e:
        logger.error(f"3년치 모든 데이터 수집 실패: {e}")
        raise

def collect_historical_data_for_single_coin_all_intervals(symbol: str, days: int = 1095):
    """단일 코인의 모든 간격 데이터 수집 (3년치)"""
    try:
        logger.info(f"=== {symbol} 3년치 모든 간격 데이터 수집 시작 ===")
        
        # 설정 로드
        config = Config.from_env()
        coins_config = CoinsConfig()
        database = Database()
        
        # 데이터 수집기 초기화
        collector = HistoricalDataCollector(config, coins_config, database)
        
        # 단일 코인 모든 간격 데이터 수집
        symbol_data = collector.collect_all_data_for_symbol(symbol, days=days)
        
        logger.info(f"=== {symbol} 3년치 모든 간격 데이터 수집 완료 ===")
        logger.info(f"수집된 간격 수: {len(symbol_data)}")
        
        # 수집 결과 요약
        for interval, df in symbol_data.items():
            logger.info(f"  {interval}: {len(df)}개 캔들")
        
        return symbol_data
        
    except Exception as e:
        logger.error(f"{symbol} 3년치 모든 간격 데이터 수집 실패: {e}")
        raise

def collect_historical_data_for_single_coin_single_interval(symbol: str, interval: str, days: int = 30):
    """단일 코인의 단일 간격 데이터 수집 (배치 처리)"""
    try:
        logger.info(f"=== {symbol} {interval} {days}일 데이터 수집 시작 ===")
        
        # 설정 로드
        config = Config.from_env()
        coins_config = CoinsConfig()
        database = Database()
        
        # 고속 데이터 수집기 초기화 (배치 처리 지원)
        collector = FastHistoricalDataCollector(config, coins_config, database)
        
        # 단일 코인 단일 간격 데이터 수집 (배치 처리)
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        df = collector.get_historical_data_batch(symbol, interval, start_time, end_time)
        
        if not df.empty:
            # 데이터베이스에 저장
            data_list = []
            for _, row in df.iterrows():
                data = {
                    'timestamp': int(row['timestamp'].timestamp() * 1000),
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'close': row['close'],
                    'volume': row['volume']
                }
                data_list.append(data)
            
            # 코인별 테이블에 저장
            collector.database.save_price_data_to_coin_table(symbol, interval, data_list)
        
        logger.info(f"=== {symbol} {interval} {days}일 데이터 수집 완료 ===")
        logger.info(f"수집된 캔들 수: {len(df)}")
        
        return df
        
    except Exception as e:
        logger.error(f"{symbol} {interval} {days}일 데이터 수집 실패: {e}")
        raise

def collect_missing_data_for_all_coins():
    """모든 코인의 누락된 데이터 수집"""
    try:
        logger.info("=== 누락된 데이터 수집 시작 ===")
        
        # 설정 로드
        config = Config.from_env()
        coins_config = CoinsConfig()
        database = Database()
        
        # 고속 데이터 수집기 초기화
        collector = FastHistoricalDataCollector(config, coins_config, database)
        
        # 누락된 데이터 수집
        missing_data = collector.collect_all_missing_data()
        
        logger.info(f"=== 누락된 데이터 수집 완료 ===")
        logger.info(f"수집된 코인 수: {len(missing_data)}")
        
        # 수집 결과 요약
        for symbol, intervals_data in missing_data.items():
            logger.info(f"{symbol}: {len(intervals_data)}개 간격")
            for interval, df in intervals_data.items():
                logger.info(f"  {interval}: {len(df)}개 캔들")
        
        return missing_data
        
    except Exception as e:
        logger.error(f"누락된 데이터 수집 실패: {e}")
        raise

def collect_missing_data_for_single_coin(symbol: str):
    """단일 코인의 누락된 데이터 수집"""
    try:
        logger.info(f"=== {symbol} 누락된 데이터 수집 시작 ===")
        
        # 설정 로드
        config = Config.from_env()
        coins_config = CoinsConfig()
        database = Database()
        
        # 고속 데이터 수집기 초기화
        collector = FastHistoricalDataCollector(config, coins_config, database)
        
        # 단일 코인 누락 데이터 수집
        symbol_missing_data = {}
        
        for interval in collector.intervals:
            try:
                df = collector.collect_missing_data(symbol, interval)
                if not df.empty:
                    symbol_missing_data[interval] = df
            except Exception as e:
                logger.error(f"{symbol} {interval} 누락 데이터 수집 실패: {e}")
                continue
        
        logger.info(f"=== {symbol} 누락된 데이터 수집 완료 ===")
        logger.info(f"수집된 간격 수: {len(symbol_missing_data)}")
        
        # 수집 결과 요약
        for interval, df in symbol_missing_data.items():
            logger.info(f"  {interval}: {len(df)}개 캔들")
        
        return symbol_missing_data
        
    except Exception as e:
        logger.error(f"{symbol} 누락된 데이터 수집 실패: {e}")
        raise

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='3년치 과거데이터 수집 스크립트 (고속 버전)')
    parser.add_argument('--symbol', type=str, help='수집할 코인 심볼 (예: BTCUSDT)')
    parser.add_argument('--interval', type=str, help='수집할 간격 (예: 1m, 1h, 1d)')
    parser.add_argument('--days', type=int, default=1095, help='수집할 일수 (기본값: 1095일 = 3년)')
    parser.add_argument('--all', action='store_true', help='모든 코인 모든 간격 수집')
    parser.add_argument('--all-intervals', action='store_true', help='단일 코인 모든 간격 수집')
    parser.add_argument('--fast', action='store_true', help='고속 수집 (병렬 처리)')
    parser.add_argument('--missing', action='store_true', help='누락된 데이터만 수집')
    parser.add_argument('--resume', action='store_true', help='중단된 지점부터 재개')
    parser.add_argument('--reset', action='store_true', help='진행 상황 초기화')
    parser.add_argument('--status', action='store_true', help='진행 상황 확인')
    
    args = parser.parse_args()
    
    try:
        # 진행 상황 확인
        if args.status:
            config = Config.from_env()
            coins_config = CoinsConfig()
            database = Database()
            collector = HistoricalDataCollector(config, coins_config, database)
            collector.progress_tracker.print_progress_summary()
            return
        
        # 진행 상황 초기화
        if args.reset:
            config = Config.from_env()
            coins_config = CoinsConfig()
            database = Database()
            collector = HistoricalDataCollector(config, coins_config, database)
            collector.progress_tracker.reset_progress()
            logger.info("진행 상황 초기화 완료")
            return
        
        if args.missing:
            if args.symbol:
                # 단일 코인 누락 데이터 수집
                collect_missing_data_for_single_coin(args.symbol)
            else:
                # 모든 코인 누락 데이터 수집
                collect_missing_data_for_all_coins()
        elif args.fast:
            if args.all:
                # 모든 코인 모든 간격 고속 수집 (3년치)
                collect_historical_data_for_all_coins_all_intervals_fast(args.days)
            elif args.all_intervals and args.symbol:
                # 단일 코인 모든 간격 고속 수집 (3년치)
                collect_historical_data_for_single_coin_all_intervals_fast(args.symbol, args.days)
            else:
                logger.error("고속 수집은 --all 또는 --all-intervals와 함께 사용해야 합니다")
        else:
            if args.all:
                # 모든 코인 모든 간격 수집 (3년치) - 재개 가능
                collect_historical_data_for_all_coins_all_intervals(args.days)
            elif args.all_intervals and args.symbol:
                # 단일 코인 모든 간격 수집 (3년치)
                collect_historical_data_for_single_coin_all_intervals(args.symbol, args.days)
            elif args.symbol and args.interval:
                # 단일 코인 단일 간격 수집
                collect_historical_data_for_single_coin_single_interval(args.symbol, args.interval, args.days)
            elif args.symbol:
                # 단일 코인 모든 간격 수집 (기본값)
                collect_historical_data_for_single_coin_all_intervals(args.symbol, args.days)
            else:
                # 기본값: BTCUSDT 1분봉 7일 수집
                logger.info("기본값으로 BTCUSDT 1분봉 7일 데이터 수집")
                collect_historical_data_for_single_coin_single_interval("BTCUSDT", "1m", 7)
        
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
    except Exception as e:
        logger.error(f"스크립트 실행 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 