#!/usr/bin/env python3
"""
50개 코인 설정 테스트 스크립트
"""

import json
import sys
import os

def test_coins_config():
    """50개 코인 설정 테스트"""
    
    # selected_coins.json 파일 확인
    if not os.path.exists('selected_coins.json'):
        print("❌ selected_coins.json 파일을 찾을 수 없습니다.")
        return False
    
    try:
        # JSON 파일 로드
        with open('selected_coins.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 데이터 검증
        coins = data.get('coins', [])
        details = data.get('details', [])
        total_coins = data.get('total_coins', 0)
        
        print("="*60)
        print("🎯 50개 코인 설정 테스트 결과")
        print("="*60)
        
        # 기본 정보 출력
        print(f"📊 총 코인 수: {total_coins}개")
        print(f"📋 코인 리스트 길이: {len(coins)}개")
        print(f"📈 상세 정보 길이: {len(details)}개")
        
        # 검증
        if total_coins == 50 and len(coins) == 50 and len(details) == 50:
            print("✅ 모든 검증 통과!")
        else:
            print("❌ 검증 실패!")
            return False
        
        # 상위 10개 코인 출력
        print("\n🏆 상위 10개 코인:")
        print("-" * 40)
        for i, coin in enumerate(coins[:10], 1):
            base_asset = coin.replace('USDT', '')
            print(f"{i:2d}. {base_asset}")
        
        # 상세 정보 샘플 출력
        if details:
            print("\n📊 상위 5개 코인 상세 정보:")
            print("-" * 60)
            for i, detail in enumerate(details[:5], 1):
                print(f"{i}. {detail['base_asset']:8s} | "
                      f"가격: ${detail['price']:>10.4f} | "
                      f"거래량: ${detail['volume_24h']:>12,.0f} | "
                      f"변동률: {detail['price_change_24h']:>6.2f}%")
        
        print("\n🎉 50개 코인 설정 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    success = test_coins_config()
    sys.exit(0 if success else 1) 