"""
바이낸스 API를 통한 50개 코인 선정 스크립트
"""

import requests
import json
import pandas as pd
from typing import List, Dict, Any
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BinanceCoinSelector:
    """바이낸스 API를 통한 코인 선정 클래스"""
    
    def __init__(self):
        """초기화"""
        self.base_url = "https://api.binance.com/api/v3"
        self.selected_coins = []
        
    def get_all_usdt_pairs(self) -> List[Dict[str, Any]]:
        """모든 USDT 페어 조회"""
        try:
            url = f"{self.base_url}/ticker/24hr"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # USDT 페어만 필터링 (스테이블코인 제외)
            stablecoins = ['USDC', 'FDUSD', 'USD1', 'TUSD', 'BUSD', 'DAI', 'FRAX', 'USDP', 'USDD']
            usdt_pairs = [
                item for item in data 
                if item['symbol'].endswith('USDT') and 
                not item['symbol'].startswith('USDT') and  # USDTUSDT 제외
                not any(stable in item['symbol'] for stable in stablecoins)  # 스테이블코인 제외
            ]
            
            logger.info(f"총 {len(usdt_pairs)}개의 USDT 페어 발견 (스테이블코인 제외)")
            return usdt_pairs
            
        except Exception as e:
            logger.error(f"USDT 페어 조회 실패: {e}")
            return []
    
    def get_market_cap_top_25(self) -> List[str]:
        """시가총액 기준 상위 25개 코인 선정"""
        try:
            usdt_pairs = self.get_all_usdt_pairs()
            
            # 거래량 기준으로 정렬 (시가총액 대용)
            sorted_by_volume = sorted(
                usdt_pairs, 
                key=lambda x: float(x['quoteVolume']), 
                reverse=True
            )
            
            # 상위 25개 선정
            top_25 = sorted_by_volume[:25]
            
            selected = [item['symbol'] for item in top_25]
            logger.info(f"시가총액 기준 상위 25개: {selected}")
            
            return selected
            
        except Exception as e:
            logger.error(f"시가총액 기준 선정 실패: {e}")
            return []
    
    def get_volume_top_50(self) -> List[str]:
        """거래량 기준 상위 50개 코인 선정"""
        try:
            usdt_pairs = self.get_all_usdt_pairs()
            
            # 거래량 기준으로 정렬
            sorted_by_volume = sorted(
                usdt_pairs, 
                key=lambda x: float(x['quoteVolume']), 
                reverse=True
            )
            
            # 상위 50개 선정
            top_50 = sorted_by_volume[:50]
            
            selected = [item['symbol'] for item in top_50]
            logger.info(f"거래량 기준 상위 50개: {selected}")
            
            return selected
            
        except Exception as e:
            logger.error(f"거래량 기준 선정 실패: {e}")
            return []
    
    def get_combined_top_50(self) -> List[str]:
        """시가총액 + 거래량 기준 상위 50개 코인 선정"""
        try:
            # 시가총액 기준 상위 25개
            market_cap_25 = self.get_market_cap_top_25()
            
            # 거래량 기준 상위 50개
            volume_50 = self.get_volume_top_50()
            
            # 중복 제거 후 합치기
            combined = list(set(market_cap_25 + volume_50))
            
            # 거래량 기준으로 재정렬
            usdt_pairs = self.get_all_usdt_pairs()
            pair_dict = {item['symbol']: float(item['quoteVolume']) for item in usdt_pairs}
            
            # 결합된 리스트를 거래량 기준으로 정렬
            combined_sorted = sorted(
                combined, 
                key=lambda x: pair_dict.get(x, 0), 
                reverse=True
            )
            
            # 상위 50개 선정
            top_50 = combined_sorted[:50]
            
            logger.info(f"최종 선정된 50개 코인: {top_50}")
            return top_50
            
        except Exception as e:
            logger.error(f"통합 선정 실패: {e}")
            return []
    
    def get_coin_details(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """선정된 코인들의 상세 정보 조회"""
        try:
            usdt_pairs = self.get_all_usdt_pairs()
            pair_dict = {item['symbol']: item for item in usdt_pairs}
            
            details = []
            for symbol in symbols:
                if symbol in pair_dict:
                    pair_info = pair_dict[symbol]
                    details.append({
                        'symbol': symbol,
                        'base_asset': symbol.replace('USDT', ''),
                        'quote_asset': 'USDT',
                        'price': float(pair_info['lastPrice']),
                        'volume_24h': float(pair_info['quoteVolume']),
                        'price_change_24h': float(pair_info['priceChangePercent']),
                        'high_24h': float(pair_info['highPrice']),
                        'low_24h': float(pair_info['lowPrice']),
                        'count_24h': int(pair_info['count'])
                    })
            
            return details
            
        except Exception as e:
            logger.error(f"코인 상세 정보 조회 실패: {e}")
            return []
    
    def save_selected_coins(self, coins: List[str], filename: str = "selected_coins.json"):
        """선정된 코인 리스트 저장"""
        try:
            # 상세 정보 조회
            details = self.get_coin_details(coins)
            
            # 저장할 데이터
            data = {
                'selection_date': datetime.now().isoformat(),
                'total_coins': len(coins),
                'coins': coins,
                'details': details
            }
            
            # JSON 파일로 저장
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"선정된 코인 리스트 저장 완료: {filename}")
            
            # CSV 파일로도 저장
            if details:
                df = pd.DataFrame(details)
                csv_filename = filename.replace('.json', '.csv')
                df.to_csv(csv_filename, index=False, encoding='utf-8')
                logger.info(f"상세 정보 CSV 저장 완료: {csv_filename}")
            
            return True
            
        except Exception as e:
            logger.error(f"코인 리스트 저장 실패: {e}")
            return False
    
    def print_selection_summary(self, coins: List[str]):
        """선정 결과 요약 출력"""
        try:
            details = self.get_coin_details(coins)
            
            print("\n" + "="*60)
            print("🎯 바이낸스 50개 코인 선정 결과")
            print("="*60)
            print(f"선정 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"선정된 코인 수: {len(coins)}개")
            print()
            
            print("📊 상위 10개 코인 (거래량 기준):")
            print("-" * 40)
            for i, detail in enumerate(details[:10], 1):
                print(f"{i:2d}. {detail['base_asset']:8s} | "
                      f"가격: ${detail['price']:>10.4f} | "
                      f"거래량: ${detail['volume_24h']:>12,.0f} | "
                      f"변동률: {detail['price_change_24h']:>6.2f}%")
            
            print()
            print("📋 전체 선정 코인 리스트:")
            print("-" * 40)
            for i, coin in enumerate(coins, 1):
                base_asset = coin.replace('USDT', '')
                print(f"{i:2d}. {base_asset}")
            
            print("="*60)
            
        except Exception as e:
            logger.error(f"요약 출력 실패: {e}")

def main():
    """메인 실행 함수"""
    print("🚀 바이낸스 50개 코인 선정 시작")
    print("="*50)
    
    # 코인 선정기 초기화
    selector = BinanceCoinSelector()
    
    # 50개 코인 선정
    print("1️⃣ USDT 페어 조회 중...")
    selected_coins = selector.get_combined_top_50()
    
    if not selected_coins:
        print("❌ 코인 선정 실패")
        return
    
    print(f"✅ {len(selected_coins)}개 코인 선정 완료")
    
    # 결과 출력
    print("\n2️⃣ 선정 결과 분석 중...")
    selector.print_selection_summary(selected_coins)
    
    # 파일 저장
    print("\n3️⃣ 결과 저장 중...")
    success = selector.save_selected_coins(selected_coins)
    
    if success:
        print("✅ 선정 결과 저장 완료")
        print("📁 저장된 파일:")
        print("   - selected_coins.json (전체 데이터)")
        print("   - selected_coins.csv (상세 정보)")
    else:
        print("❌ 결과 저장 실패")
    
    print("\n🎉 코인 선정 작업 완료!")
    print("다음 단계: Phase 0 개발 환경 설정")

if __name__ == "__main__":
    main() 