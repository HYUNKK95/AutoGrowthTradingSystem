#!/usr/bin/env python3
"""
Phase 2 감정분석 모듈 테스트
"""

from analysis.sentiment import SentimentAnalyzer

def test_sentiment_analysis():
    """감정분석 테스트"""
    print("=== Phase 2 감정분석 테스트 ===")
    
    analyzer = SentimentAnalyzer()
    
    # 텍스트 감정분석 테스트
    test_texts = [
        "Bitcoin surges to new highs as institutional adoption grows",
        "Crypto market crashes as regulatory fears mount",
        "Ethereum breaks out of resistance level",
        "Bitcoin and Ethereum show bullish momentum in crypto market"
    ]
    
    for text in test_texts:
        result = analyzer.analyze_text(text)
        print(f"텍스트: {text}")
        print(f"감정 점수: {result['sentiment_score']:.3f}")
        print(f"키워드: {result['keywords']}")
        print("---")
    
    # 감정분석 실행
    sentiment_result = analyzer.analyze()
    print(f"감정분석 신호: {sentiment_result['sentiment_signal']:.3f}")
    print(f"감정 데이터: {sentiment_result['sentiment_data']}")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_sentiment_analysis() 