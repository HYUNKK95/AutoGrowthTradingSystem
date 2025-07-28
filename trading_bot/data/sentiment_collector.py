"""
기본 감정 데이터 수집기
"""

import requests
import feedparser
import re
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.config import Config
from data.database import Database

class SentimentCollector:
    """기본 감정 데이터 수집기"""
    
    def __init__(self, config: Config, database: Database):
        """감정 데이터 수집기 초기화"""
        self.config = config
        self.database = database
        self.logger = logging.getLogger(__name__)
        
        # 감정 키워드 정의
        self.positive_keywords = [
            'bullish', 'surge', 'rally', 'gain', 'up', 'rise', 'positive',
            'growth', 'adoption', 'partnership', 'launch', 'success',
            'breakthrough', 'innovation', 'strong', 'buy', 'long'
        ]
        
        self.negative_keywords = [
            'bearish', 'crash', 'drop', 'fall', 'down', 'decline', 'negative',
            'loss', 'sell', 'short', 'dump', 'fear', 'panic', 'weak',
            'failure', 'hack', 'scam', 'ban', 'regulation'
        ]
        
        # 암호화폐 관련 키워드
        self.crypto_keywords = [
            'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency',
            'blockchain', 'defi', 'nft', 'altcoin', 'token', 'coin'
        ]
        
        # RSS 피드 소스
        self.rss_sources = [
            'https://cointelegraph.com/rss',
            'https://coindesk.com/arc/outboundfeeds/rss/',
            'https://cryptonews.com/news/feed',
            'https://bitcoinmagazine.com/.rss/full/',
            'https://decrypt.co/feed'
        ]
        
        self.logger.info("감정 데이터 수집기 초기화 완료")
    
    def analyze_sentiment(self, text: str) -> float:
        """기본 키워드 기반 감정 분석"""
        text_lower = text.lower()
        
        positive_count = sum(1 for keyword in self.positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in self.negative_keywords if keyword in text_lower)
        
        # 감정 점수 계산 (-1 ~ 1)
        total_keywords = positive_count + negative_count
        if total_keywords == 0:
            return 0.0
        
        sentiment_score = (positive_count - negative_count) / total_keywords
        return sentiment_score
    
    def extract_crypto_keywords(self, text: str) -> List[str]:
        """암호화폐 관련 키워드 추출"""
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.crypto_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def collect_rss_news(self) -> List[Dict[str, Any]]:
        """RSS 뉴스 수집"""
        all_news = []
        
        for source in self.rss_sources:
            try:
                self.logger.info(f"RSS 수집 중: {source}")
                
                # RSS 피드 파싱
                feed = feedparser.parse(source)
                
                for entry in feed.entries[:10]:  # 최근 10개 기사
                    try:
                        # 기사 정보 추출
                        title = entry.get('title', '')
                        description = entry.get('summary', '')
                        link = entry.get('link', '')
                        published = entry.get('published', '')
                        
                        # 암호화폐 관련 키워드 확인
                        crypto_keywords = self.extract_crypto_keywords(title + ' ' + description)
                        
                        if crypto_keywords:  # 암호화폐 관련 기사만
                            # 감정 분석
                            sentiment_score = self.analyze_sentiment(title + ' ' + description)
                            
                            # 기사 정보 저장
                            news_item = {
                                'title': title,
                                'description': description,
                                'link': link,
                                'published': published,
                                'sentiment_score': sentiment_score,
                                'crypto_keywords': ','.join(crypto_keywords),
                                'source': source,
                                'timestamp': int(datetime.now().timestamp() * 1000)
                            }
                            
                            all_news.append(news_item)
                            
                            # 데이터베이스에 저장
                            self.database.save_sentiment_data(
                                source=source,
                                headline=title,
                                sentiment_score=sentiment_score,
                                keywords=','.join(crypto_keywords),
                                timestamp=news_item['timestamp']
                            )
                    
                    except Exception as e:
                        self.logger.error(f"기사 처리 오류: {e}")
                        continue
                
                # API 호출 제한 방지
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"RSS 수집 오류 ({source}): {e}")
                continue
        
        self.logger.info(f"RSS 뉴스 수집 완료: {len(all_news)}개 기사")
        return all_news
    
    def get_sentiment_summary(self, hours: int = 24) -> Dict[str, Any]:
        """감정 요약 조회"""
        try:
            # 최근 N시간 데이터 조회
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = int((datetime.now() - timedelta(hours=hours)).timestamp() * 1000)
            
            # 데이터베이스에서 감정 데이터 조회
            with self.database.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT sentiment_score, keywords, timestamp 
                    FROM sentiment_data 
                    WHERE timestamp BETWEEN ? AND ?
                    ORDER BY timestamp DESC
                """, (start_time, end_time))
                
                rows = cursor.fetchall()
            
            if not rows:
                return {
                    'total_articles': 0,
                    'average_sentiment': 0.0,
                    'positive_articles': 0,
                    'negative_articles': 0,
                    'neutral_articles': 0,
                    'top_keywords': []
                }
            
            # 감정 분석
            sentiment_scores = [row[0] for row in rows if row[0] is not None]
            keywords_list = [row[1] for row in rows if row[1]]
            
            # 통계 계산
            total_articles = len(rows)
            average_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
            positive_articles = sum(1 for score in sentiment_scores if score > 0.1)
            negative_articles = sum(1 for score in sentiment_scores if score < -0.1)
            neutral_articles = total_articles - positive_articles - negative_articles
            
            # 키워드 빈도 분석
            keyword_freq = {}
            for keywords in keywords_list:
                for keyword in keywords.split(','):
                    keyword = keyword.strip()
                    if keyword:
                        keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
            
            top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'total_articles': total_articles,
                'average_sentiment': average_sentiment,
                'positive_articles': positive_articles,
                'negative_articles': negative_articles,
                'neutral_articles': neutral_articles,
                'top_keywords': top_keywords
            }
            
        except Exception as e:
            self.logger.error(f"감정 요약 조회 오류: {e}")
            return {}
    
    def collect_and_analyze(self) -> List[Dict[str, Any]]:
        """감정 데이터 수집 및 분석 (integrated_bot에서 호출)"""
        try:
            self.logger.info("감정 데이터 수집 및 분석 시작")
            
            # RSS 뉴스 수집
            news_items = self.collect_rss_news()
            
            # 감정 요약 출력
            summary = self.get_sentiment_summary()
            if summary:
                self.logger.info(f"감정 요약: {summary['total_articles']}개 기사, "
                               f"평균 감정: {summary['average_sentiment']:.3f}")
            
            return news_items
            
        except Exception as e:
            self.logger.error(f"감정 데이터 수집 및 분석 오류: {e}")
            return []
    
    def start_collection(self, interval_minutes: int = 30):
        """정기적 감정 데이터 수집"""
        self.logger.info(f"감정 데이터 수집 시작 (간격: {interval_minutes}분)")
        
        while True:
            try:
                # RSS 뉴스 수집
                news_items = self.collect_rss_news()
                
                # 감정 요약 출력
                summary = self.get_sentiment_summary()
                if summary:
                    self.logger.info(f"감정 요약: {summary['total_articles']}개 기사, "
                                   f"평균 감정: {summary['average_sentiment']:.3f}")
                
                # 대기
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                self.logger.info("사용자에 의해 중단됨")
                break
            except Exception as e:
                self.logger.error(f"감정 데이터 수집 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기

# 사용 예시
if __name__ == "__main__":
    # 설정 로드
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    
    # 감정 데이터 수집기 생성
    sentiment_collector = SentimentCollector(config, database)
    
    # RSS 뉴스 수집 테스트
    print("RSS 뉴스 수집 테스트...")
    news_items = sentiment_collector.collect_rss_news()
    print(f"수집된 뉴스: {len(news_items)}개")
    
    # 감정 요약 테스트
    print("감정 요약 테스트...")
    summary = sentiment_collector.get_sentiment_summary()
    print(f"감정 요약: {summary}")
    
    # 감정 분석 테스트
    test_text = "Bitcoin surges to new highs as institutional adoption grows"
    sentiment = sentiment_collector.analyze_sentiment(test_text)
    print(f"테스트 텍스트: '{test_text}'")
    print(f"감정 점수: {sentiment:.3f}") 