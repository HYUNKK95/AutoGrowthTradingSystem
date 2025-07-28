#!/usr/bin/env python3
"""
진행 상황 설정 스크립트
완료된 20개 코인을 진행 상황에 추가
"""

import json
import os
from datetime import datetime

def setup_completed_progress():
    """완료된 20개 코인을 진행 상황에 추가"""
    
    # 완료된 20개 코인
    completed_coins = [
        "ETHUSDT", "BTCUSDT", "SUIUSDT", "SOLUSDT", "XRPUSDT", 
        "DOGEUSDT", "HBARUSDT", "PEPEUSDT", "ADAUSDT", "CRVUSDT", 
        "TRXUSDT", "BONKUSDT", "AVAXUSDT", "UNIUSDT", "OMUSDT", 
        "LINKUSDT", "CFXUSDT", "ERAUSDT", "ENAUSDT", "PENGUUSDT"
    ]
    
    # 모든 간격
    all_intervals = [
        "1m", "3m", "5m", "15m", "30m", 
        "1h", "2h", "4h", "6h", "8h", "12h", 
        "1d", "3d", "1w", "1M"
    ]
    
    # 진행 상황 파일 경로
    progress_file = "trading_bot/data/data_collection_progress.json"
    
    # 진행 상황 로드
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress = json.load(f)
    else:
        progress = {
            "start_time": datetime.now().isoformat(),
            "total_coins": 50,
            "total_intervals": 16,
            "completed_coins": [],
            "current_coin": None,
            "current_coin_progress": {},
            "completed_intervals": {}
        }
    
    # 완료된 코인들을 진행 상황에 추가
    for coin in completed_coins:
        if coin not in progress["completed_coins"]:
            progress["completed_coins"].append(coin)
        
        # 모든 간격을 완료된 것으로 표시
        progress["completed_intervals"][coin] = all_intervals.copy()
    
    # 진행 상황 저장
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 완료된 20개 코인을 진행 상황에 추가했습니다:")
    for coin in completed_coins:
        print(f"  - {coin}")
    
    print(f"\n📊 현재 진행 상황:")
    print(f"  - 완료된 코인: {len(progress['completed_coins'])}개")
    print(f"  - 남은 코인: {50 - len(progress['completed_coins'])}개")

if __name__ == "__main__":
    setup_completed_progress() 