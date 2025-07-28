# Phase 1: 데이터 수집 실행 가이드

## 📋 개요

Phase 1에서는 과거데이터 수집과 실시간 봇이 분리되어 있습니다:

- **과거데이터 수집**: 독립적인 스크립트로 실행
- **실시간 봇**: main.py로 실행

## 🚀 실행 방법

### 1. 과거데이터 수집 (독립 실행)

#### 모든 코인 1년치 데이터 수집
```bash
cd trading_bot
python scripts/collect_historical_data.py --all --days 365
```

#### 단일 코인 데이터 수집
```bash
# BTCUSDT 30일 데이터 수집
python scripts/collect_historical_data.py --symbol BTCUSDT --days 30

# ETHUSDT 7일 데이터 수집
python scripts/collect_historical_data.py --symbol ETHUSDT --days 7
```

#### 기본 실행 (BTCUSDT 7일)
```bash
python scripts/collect_historical_data.py
```

### 2. 실시간 봇 실행

```bash
cd trading_bot
python main.py
```

## 📊 데이터 수집 옵션

### 과거데이터 수집 스크립트 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--all` | 모든 코인 수집 | `--all --days 365` |
| `--symbol` | 특정 코인 수집 | `--symbol BTCUSDT` |
| `--days` | 수집할 일수 | `--days 30` |

### 수집 대상 코인

50개 주요 코인이 설정되어 있습니다:
- BTCUSDT, ETHUSDT, BNBUSDT, ADAUSDT, SOLUSDT
- DOTUSDT, DOGEUSDT, AVAXUSDT, MATICUSDT, LINKUSDT
- 기타 40개 코인...

## 📁 파일 구조

```
trading_bot/
├── main.py                           # 실시간 봇 (main)
├── scripts/
│   └── collect_historical_data.py    # 과거데이터 수집 (독립)
├── data/
│   ├── collector.py                  # 데이터 수집 클래스
│   ├── database.py                   # 데이터베이스 관리
│   ├── websocket_client.py          # 실시간 데이터
│   └── sentiment_collector.py       # 감정 데이터
├── logs/
│   └── historical_data_collection.log # 수집 로그
└── data/
    └── trading_bot.db               # SQLite 데이터베이스
```

## 🔧 설정

### 환경 변수 설정
```bash
# .env 파일 생성
cp env.example .env

# 필수 설정
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
```

### 데이터베이스 설정
- **위치**: `./data/trading_bot.db`
- **자동 생성**: 스크립트 실행 시 자동 생성
- **테이블**: price_data, sentiment_data, realtime_data, trades

## 📈 수집 데이터

### 가격 데이터 (price_data)
- **기간**: 1년치 (1시간 캔들)
- **컬럼**: timestamp, open, high, low, close, volume
- **코인**: 50개

### 감정 데이터 (sentiment_data)
- **소스**: 뉴스 헤드라인
- **분석**: 키워드 기반 감정 점수
- **저장**: 실시간 수집

### 실시간 데이터 (realtime_data)
- **스트림**: WebSocket 실시간 거래
- **저장**: 실시간 업데이트

## 🚨 주의사항

### 1. API 제한
- Binance API 호출 제한 준수
- 과거데이터 수집 시 0.1초 간격 유지

### 2. 저장 공간
- 1년치 50개 코인 데이터: 약 500MB
- 충분한 디스크 공간 확보 필요

### 3. 네트워크
- 안정적인 인터넷 연결 필요
- 방화벽 설정 확인

## 🔍 로그 확인

### 과거데이터 수집 로그
```bash
tail -f logs/historical_data_collection.log
```

### 실시간 봇 로그
```bash
tail -f logs/trading_bot.log
```

## ✅ 완료 확인

### 데이터베이스 상태 확인
```python
from data.database import Database

db = Database()
info = db.get_database_info()
print(f"가격 데이터: {info['price_data']}개 레코드")
print(f"감정 데이터: {info['sentiment_data']}개 레코드")
```

### 수집 결과 확인
```python
import pandas as pd
from data.database import Database

db = Database()
df = db.get_price_data('BTCUSDT', start_time, end_time)
print(f"BTCUSDT 데이터: {len(df)}개 캔들")
```

## 🚀 다음 단계

Phase 1 완료 후:
1. **Phase 2**: 기술적 분석 모듈 구현
2. **Phase 3**: ML 예측 모델 구현
3. **Phase 4**: 통합 봇 개발

## 🆘 문제 해결

### 일반적인 오류

1. **API 키 오류**
   ```bash
   # .env 파일 확인
   cat .env | grep BINANCE
   ```

2. **데이터베이스 오류**
   ```bash
   # 데이터베이스 파일 확인
   ls -la data/trading_bot.db
   ```

3. **네트워크 오류**
   ```bash
   # 인터넷 연결 확인
   ping api.binance.com
   ```

### 로그 분석
```bash
# 오류 로그 확인
grep ERROR logs/historical_data_collection.log
grep ERROR logs/trading_bot.log
``` 