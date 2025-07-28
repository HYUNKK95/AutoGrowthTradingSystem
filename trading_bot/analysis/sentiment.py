"""
감정분석 모듈
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List
from data.database import Database

class SentimentAnalyzer:
    """감정분석 클래스"""
    
    def __init__(self):
        """감정분석기 초기화"""
        self.logger = logging.getLogger(__name__)
        self.db = Database()
        
        # 감정 키워드 확장
        self.positive_keywords = [
            'bullish', 'surge', 'rally', 'breakout', 'moon', 'pump',
            'positive', 'growth', 'adoption', 'institutional', 'buy',
            'accumulate', 'hodl', 'diamond hands', 'to the moon',
            'partnership', 'upgrade', 'innovation', 'success',
            'bitcoin', 'ethereum', 'crypto', 'blockchain', 'defi',
            'nft', 'metaverse', 'web3', 'smart contract'
        ]
        
        self.negative_keywords = [
            'bearish', 'crash', 'dump', 'breakdown', 'sell', 'fear',
            'negative', 'decline', 'ban', 'regulation', 'hack',
            'scam', 'bubble', 'correction', 'panic', 'fud',
            'regulation', 'ban', 'restriction', 'warning',
            'crypto winter', 'bear market', 'correction'
        ]
        
        # 감정 가중치
        self.keyword_weights = {
            'bullish': 2.0, 'surge': 1.5, 'rally': 1.5,
            'crash': -2.0, 'dump': -1.5, 'bearish': -1.5,
            'moon': 1.0, 'pump': 1.0, 'scam': -2.0,
            'bitcoin': 0.5, 'ethereum': 0.5, 'crypto': 0.3,
            'blockchain': 0.3, 'defi': 0.5, 'nft': 0.3
        }
        
        self.logger.info("SentimentAnalyzer 초기화 완료")
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """텍스트 감정 분석"""
        text_lower = text.lower()
        
        # 키워드 매칭
        positive_score = 0
        negative_score = 0
        found_keywords = []
        
        # 긍정 키워드 검사
        for keyword in self.positive_keywords:
            if keyword in text_lower:
                weight = self.keyword_weights.get(keyword, 1.0)
                positive_score += weight
                found_keywords.append(f"+{keyword}")
        
        # 부정 키워드 검사
        for keyword in self.negative_keywords:
            if keyword in text_lower:
                weight = self.keyword_weights.get(keyword, -1.0)
                negative_score += abs(weight)
                found_keywords.append(f"-{keyword}")
        
        # 감정 점수 계산
        total_score = positive_score - negative_score
        total_keywords = len(found_keywords)
        
        if total_keywords == 0:
            sentiment_score = 0.0
        else:
            sentiment_score = total_score / total_keywords
        
        # -1 ~ 1 범위로 정규화
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        return {
            'sentiment_score': sentiment_score,
            'positive_score': positive_score,
            'negative_score': negative_score,
            'keywords': found_keywords,
            'total_keywords': total_keywords
        }
    
    def get_recent_sentiment(self, hours: int = 24) -> Dict[str, Any]:
        """최근 감정 데이터 분석"""
        try:
            # 최근 N시간 감정 데이터 조회
            end_time = int(pd.Timestamp.now().timestamp() * 1000)
            start_time = end_time - (hours * 60 * 60 * 1000)
            
            # 데이터베이스에서 감정 데이터 조회
            df = self.db.get_sentiment_data(limit=1000)  # 최근 1000개 데이터 조회
            
            if df.empty:
                return {
                    'sentiment_score': 0.0,
                    'sentiment_trend': 0.0,
                    'headline_count': 0
                }
            
            # 평균 감정 점수
            avg_sentiment = df['sentiment_score'].mean()
            
            # 감정 트렌드 (최근 vs 이전)
            recent_half = df.tail(len(df) // 2)
            earlier_half = df.head(len(df) // 2)
            
            recent_avg = recent_half['sentiment_score'].mean() if not recent_half.empty else 0
            earlier_avg = earlier_half['sentiment_score'].mean() if not earlier_half.empty else 0
            
            sentiment_trend = recent_avg - earlier_avg
            
            return {
                'sentiment_score': avg_sentiment,
                'sentiment_trend': sentiment_trend,
                'headline_count': len(df),
                'recent_sentiment': recent_avg,
                'earlier_sentiment': earlier_avg
            }
            
        except Exception as e:
            self.logger.error(f"최근 감정 데이터 분석 실패: {e}")
            return {
                'sentiment_score': 0.0,
                'sentiment_trend': 0.0,
                'headline_count': 0
            }
    
    def analyze(self, market_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """감정분석 실행"""
        try:
            # 최근 24시간 감정 데이터 분석
            sentiment_data = self.get_recent_sentiment(24)
            
            # 감정 신호 생성
            sentiment_signal = sentiment_data['sentiment_score']
            
            # 트렌드 가중치 적용
            trend_weight = 0.3
            sentiment_signal += sentiment_data['sentiment_trend'] * trend_weight
            
            # -1 ~ 1 범위로 정규화
            sentiment_signal = max(-1.0, min(1.0, sentiment_signal))
            
            result = {
                'sentiment_signal': sentiment_signal,
                'sentiment_data': sentiment_data,
                'analysis_time': pd.Timestamp.now().isoformat()
            }
            
            self.logger.info(f"감정분석 완료: 신호={sentiment_signal:.3f}")
            return result
            
        except Exception as e:
            self.logger.error(f"감정분석 실패: {e}")
            return {
                'sentiment_signal': 0.0,
                'sentiment_data': {},
                'analysis_time': pd.Timestamp.now().isoformat()
            } 