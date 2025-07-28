#!/usr/bin/env python3
"""
SentimentCollector 클래스 80% 커버리지 테스트
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

def test_sentiment_collector_init():
    """SentimentCollector 초기화 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    
    sentiment_collector = SentimentCollector(config, database)
    assert sentiment_collector is not None
    assert hasattr(sentiment_collector, 'config')
    assert hasattr(sentiment_collector, 'database')
    assert hasattr(sentiment_collector, 'positive_keywords')
    assert hasattr(sentiment_collector, 'negative_keywords')
    assert hasattr(sentiment_collector, 'crypto_keywords')
    assert hasattr(sentiment_collector, 'rss_sources')

def test_analyze_sentiment_positive():
    """긍정적 감정 분석 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # 긍정적 텍스트
    positive_texts = [
        "Bitcoin reaches new all-time high",
        "Ethereum upgrade successful",
        "Major adoption by institutions",
        "Crypto market bullish trend continues"
    ]
    
    for text in positive_texts:
        sentiment = sentiment_collector.analyze_sentiment(text)
        assert isinstance(sentiment, float)
        assert -1.0 <= sentiment <= 1.0
        assert sentiment >= 0.0  # 긍정적이어야 함

def test_analyze_sentiment_negative():
    """부정적 감정 분석 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # 부정적 텍스트
    negative_texts = [
        "Crypto market crashes",
        "Regulatory crackdown on crypto",
        "Bitcoin price drops significantly",
        "Fear and panic in crypto market"
    ]
    
    for text in negative_texts:
        sentiment = sentiment_collector.analyze_sentiment(text)
        assert isinstance(sentiment, float)
        assert -1.0 <= sentiment <= 1.0
        assert sentiment <= 0.0  # 부정적이어야 함

def test_analyze_sentiment_neutral():
    """중립적 감정 분석 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # 중립적 텍스트
    neutral_texts = [
        "Bitcoin price remains stable",
        "Crypto market shows mixed signals",
        "New cryptocurrency launched",
        "Blockchain technology development"
    ]
    
    for text in neutral_texts:
        sentiment = sentiment_collector.analyze_sentiment(text)
        assert isinstance(sentiment, float)
        assert -1.0 <= sentiment <= 1.0

def test_extract_crypto_keywords():
    """암호화폐 키워드 추출 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # 키워드가 포함된 텍스트
    test_texts = [
        "Bitcoin price surges",
        "Ethereum blockchain upgrade",
        "Crypto market analysis",
        "DeFi protocols growing",
        "NFT marketplace booming"
    ]
    
    for text in test_texts:
        keywords = sentiment_collector.extract_crypto_keywords(text)
        assert isinstance(keywords, list)
        assert len(keywords) > 0

def test_extract_crypto_keywords_no_match():
    """암호화폐 키워드 없음 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # 키워드가 없는 텍스트
    text = "Stock market analysis and economic trends"
    keywords = sentiment_collector.extract_crypto_keywords(text)
    assert isinstance(keywords, list)
    assert len(keywords) == 0

def test_collect_rss_news():
    """RSS 뉴스 수집 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # Mock RSS 피드 데이터
    mock_feed_data = [
        {
            'title': 'Bitcoin price surges',
            'summary': 'Bitcoin reaches new highs',
            'link': 'https://example.com/article1',
            'published': '2025-07-27T10:00:00Z'
        },
        {
            'title': 'Ethereum upgrade successful',
            'summary': 'Ethereum blockchain upgrade completed',
            'link': 'https://example.com/article2',
            'published': '2025-07-27T11:00:00Z'
        }
    ]
    
    with patch('feedparser.parse') as mock_parse:
        mock_parse.return_value.entries = mock_feed_data
        
        news = sentiment_collector.collect_rss_news()
        assert isinstance(news, list)
        assert len(news) > 0

def test_collect_rss_news_error():
    """RSS 뉴스 수집 오류 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    with patch('feedparser.parse', side_effect=Exception("Network error")):
        news = sentiment_collector.collect_rss_news()
        assert isinstance(news, list)
        assert len(news) == 0

def test_collect_and_analyze():
    """수집 및 분석 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # Mock RSS 뉴스 데이터
    mock_news = [
        {
            'title': 'Bitcoin price surges',
            'description': 'Bitcoin reaches new highs',
            'published': '2025-07-27T10:00:00Z'
        }
    ]
    
    with patch.object(sentiment_collector, 'collect_rss_news', return_value=mock_news):
        with patch.object(database, 'save_sentiment_data') as mock_save:
            result = sentiment_collector.collect_and_analyze()
            assert isinstance(result, list)
            assert len(result) > 0
            mock_save.assert_called()

def test_get_sentiment_summary():
    """감정 요약 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # Mock 데이터베이스 조회 결과
    mock_data = [
        {'sentiment_score': 0.8, 'headline': 'Positive news'},
        {'sentiment_score': -0.5, 'headline': 'Negative news'},
        {'sentiment_score': 0.2, 'headline': 'Neutral news'}
    ]
    
    with patch.object(database, 'connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_data
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        summary = sentiment_collector.get_sentiment_summary(hours=24)
        assert isinstance(summary, dict)
        assert 'total_articles' in summary
        assert 'average_sentiment' in summary
        assert 'positive_count' in summary
        assert 'negative_count' in summary

def test_start_collection():
    """수집 시작 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    with patch.object(sentiment_collector, 'collect_and_analyze') as mock_collect:
        with patch('time.sleep') as mock_sleep:
            # KeyboardInterrupt로 중단
            mock_sleep.side_effect = KeyboardInterrupt()
            
            try:
                sentiment_collector.start_collection(interval_minutes=1)
            except KeyboardInterrupt:
                pass
            
            mock_collect.assert_called()

def test_sentiment_collector_keywords():
    """키워드 설정 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # 긍정적 키워드 확인
    assert len(sentiment_collector.positive_keywords) > 0
    assert 'bullish' in sentiment_collector.positive_keywords
    assert 'surge' in sentiment_collector.positive_keywords
    
    # 부정적 키워드 확인
    assert len(sentiment_collector.negative_keywords) > 0
    assert 'bearish' in sentiment_collector.negative_keywords
    assert 'crash' in sentiment_collector.negative_keywords
    
    # 암호화폐 키워드 확인
    assert len(sentiment_collector.crypto_keywords) > 0
    assert 'bitcoin' in sentiment_collector.crypto_keywords
    assert 'ethereum' in sentiment_collector.crypto_keywords

def test_sentiment_collector_rss_sources():
    """RSS 소스 설정 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # RSS 소스 확인
    assert len(sentiment_collector.rss_sources) > 0
    for source in sentiment_collector.rss_sources:
        assert isinstance(source, str)
        assert source.startswith('http')

def test_analyze_sentiment_edge_cases():
    """감정 분석 엣지 케이스 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # 빈 텍스트
    sentiment = sentiment_collector.analyze_sentiment("")
    assert sentiment == 0.0
    
    # 키워드가 없는 텍스트
    sentiment = sentiment_collector.analyze_sentiment("The weather is nice today")
    assert sentiment == 0.0
    
    # 대소문자 혼합
    sentiment = sentiment_collector.analyze_sentiment("Bitcoin SURGES and ETHEREUM CRASHES")
    assert isinstance(sentiment, float)
    assert -1.0 <= sentiment <= 1.0

def test_extract_crypto_keywords_edge_cases():
    """암호화폐 키워드 추출 엣지 케이스 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # 빈 텍스트
    keywords = sentiment_collector.extract_crypto_keywords("")
    assert keywords == []
    
    # 대소문자 혼합
    keywords = sentiment_collector.extract_crypto_keywords("BITCOIN and Ethereum are popular")
    assert 'bitcoin' in keywords
    assert 'ethereum' in keywords
    
    # 중복 키워드
    keywords = sentiment_collector.extract_crypto_keywords("bitcoin bitcoin ethereum")
    assert len(keywords) == 2  # 중복 제거되지 않음
    assert keywords.count('bitcoin') == 2

def test_collect_rss_news_empty_feed():
    """빈 RSS 피드 처리 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # 빈 피드로 모킹
    with patch('feedparser.parse') as mock_parse:
        mock_parse.return_value.entries = []
        
        news = sentiment_collector.collect_rss_news()
        assert isinstance(news, list)
        assert len(news) == 0

def test_collect_rss_news_with_crypto_content():
    """암호화폐 관련 콘텐츠가 있는 RSS 피드 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # 암호화폐 관련 콘텐츠가 있는 피드로 모킹
    mock_entries = [
        {
            'title': 'Bitcoin surges to new highs',
            'summary': 'Bitcoin reaches new all-time high',
            'link': 'https://example.com/article1',
            'published': '2025-07-27T10:00:00Z'
        },
        {
            'title': 'Weather forecast for today',
            'summary': 'Sunny weather expected',
            'link': 'https://example.com/article2',
            'published': '2025-07-27T11:00:00Z'
        }
    ]
    
    with patch('feedparser.parse') as mock_parse:
        mock_parse.return_value.entries = mock_entries
        
        news = sentiment_collector.collect_rss_news()
        assert isinstance(news, list)
        assert len(news) == 1  # 암호화폐 관련 기사만 포함

def test_get_sentiment_summary_with_data():
    """데이터가 있는 감정 요약 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    from datetime import datetime
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # 테스트 데이터 저장
    timestamp = int(datetime.now().timestamp() * 1000)
    database.save_sentiment_data('test_source', 'Positive Bitcoin news', 0.8, 'bitcoin,positive', timestamp)
    database.save_sentiment_data('test_source', 'Negative Ethereum news', -0.5, 'ethereum,negative', timestamp)
    database.save_sentiment_data('test_source', 'Neutral crypto news', 0.1, 'crypto,neutral', timestamp)
    
    # 감정 요약 조회
    summary = sentiment_collector.get_sentiment_summary(hours=24)
    
    assert isinstance(summary, dict)
    assert 'total_articles' in summary
    assert 'average_sentiment' in summary
    assert 'positive_articles' in summary
    assert 'negative_articles' in summary
    assert 'neutral_articles' in summary
    assert 'top_keywords' in summary
    assert summary['total_articles'] >= 3

def test_collect_and_analyze_success():
    """성공적인 수집 및 분석 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # Mock RSS 뉴스 데이터
    mock_news = [
        {
            'title': 'Bitcoin price surges',
            'description': 'Bitcoin reaches new highs',
            'published': '2025-07-27T10:00:00Z'
        }
    ]
    
    with patch.object(sentiment_collector, 'collect_rss_news', return_value=mock_news):
        with patch.object(sentiment_collector, 'get_sentiment_summary', return_value={'total_articles': 1, 'average_sentiment': 0.8}):
            result = sentiment_collector.collect_and_analyze()
            assert isinstance(result, list)
            assert len(result) == 1

def test_collect_and_analyze_exception():
    """예외가 발생하는 수집 및 분석 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # 예외 발생하도록 모킹
    with patch.object(sentiment_collector, 'collect_rss_news', side_effect=Exception("Test error")):
        result = sentiment_collector.collect_and_analyze()
        assert isinstance(result, list)
        assert len(result) == 0

def test_start_collection_success():
    """성공적인 수집 시작 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    with patch.object(sentiment_collector, 'collect_rss_news', return_value=[]):
        with patch.object(sentiment_collector, 'get_sentiment_summary', return_value={'total_articles': 0}):
            with patch('time.sleep') as mock_sleep:
                # KeyboardInterrupt로 중단
                mock_sleep.side_effect = KeyboardInterrupt()
                
                try:
                    sentiment_collector.start_collection(interval_minutes=1)
                except KeyboardInterrupt:
                    pass
                
                # collect_rss_news가 호출되었는지 확인
                sentiment_collector.collect_rss_news.assert_called()

def test_start_collection_exception():
    """예외가 발생하는 수집 시작 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    with patch.object(sentiment_collector, 'collect_rss_news', side_effect=Exception("Test error")):
        with patch('time.sleep') as mock_sleep:
            # KeyboardInterrupt로 중단
            mock_sleep.side_effect = KeyboardInterrupt()
            
            try:
                sentiment_collector.start_collection(interval_minutes=1)
            except KeyboardInterrupt:
                pass
            
            # collect_rss_news가 호출되었는지 확인
            sentiment_collector.collect_rss_news.assert_called()

def test_sentiment_collector_main():
    """메인 실행 테스트"""
    from data.sentiment_collector import SentimentCollector
    from bot.config import Config
    from data.database import Database
    
    config = Config.from_env()
    database = Database()
    sentiment_collector = SentimentCollector(config, database)
    
    # 기본 기능 테스트
    test_text = "Bitcoin surges to new highs as institutional adoption grows"
    sentiment = sentiment_collector.analyze_sentiment(test_text)
    assert isinstance(sentiment, float)
    assert -1.0 <= sentiment <= 1.0
    
    keywords = sentiment_collector.extract_crypto_keywords(test_text)
    assert isinstance(keywords, list)
    assert 'bitcoin' in keywords

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 