#!/usr/bin/env python3
"""
50개 코인 설정 파일
"""

import json
import os
from typing import List, Dict, Any

class CoinsConfig:
    """50개 코인 설정 관리 클래스"""
    
    def __init__(self, config_file: str = "selected_coins.json"):
        self.config_file = config_file
        self.coins = self.load_selected_coins()
    
    def load_selected_coins(self) -> List[str]:
        """선정된 50개 코인 로드"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('coins', [])
        except FileNotFoundError:
            print(f"⚠️ {self.config_file} 파일을 찾을 수 없습니다.")
            return []
        except Exception as e:
            print(f"❌ 코인 설정 로드 실패: {e}")
            return []
    
    def get_coin_details(self) -> List[Dict[str, Any]]:
        """코인 상세 정보 조회"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('details', [])
        except Exception as e:
            print(f"❌ 코인 상세 정보 로드 실패: {e}")
            return []
    
    def get_top_coins(self, count: int = 10) -> List[str]:
        """상위 N개 코인 조회"""
        return self.coins[:count]
    
    def get_coin_by_index(self, index: int) -> str:
        """인덱스로 코인 조회"""
        if 0 <= index < len(self.coins):
            return self.coins[index]
        return None
    
    def get_total_coins(self) -> int:
        """총 코인 수 조회"""
        return len(self.coins)
    
    def print_coins_summary(self):
        """코인 요약 출력"""
        print(f"📊 총 {len(self.coins)}개 코인 등록됨")
        print("상위 10개 코인:")
        for i, coin in enumerate(self.coins[:10], 1):
            print(f"  {i:2d}. {coin.replace('USDT', '')}")

# 사용 예시
if __name__ == "__main__":
    config = CoinsConfig()
    config.print_coins_summary() 