"""
봇 설정 관리 클래스
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class Config:
    """봇 설정 클래스"""
    
    # Binance API 설정
    binance_api_key: str
    binance_secret_key: str
    binance_testnet: bool
    binance_api_url: str
    
    # 데이터베이스 설정
    database_path: str
    
    # 로깅 설정
    log_level: str
    log_file: str
    
    # 거래 설정
    trading_symbol: str
    initial_capital: float
    max_position_size: float
    stop_loss_percent: float
    take_profit_percent: float
    
    # 알림 설정
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # 개발 환경 설정
    debug_mode: bool = True
    backtest_mode: bool = False
    
    # 50개 코인 설정
    selected_coins_file: str = "./selected_coins.json"
    max_coins: int = 50
    
    @classmethod
    def from_env(cls) -> 'Config':
        """환경 변수에서 설정 로드"""
        return cls(
            # Binance API 설정
            binance_api_key=os.getenv('BINANCE_API_KEY', ''),
            binance_secret_key=os.getenv('BINANCE_SECRET_KEY', ''),
            binance_testnet=os.getenv('BINANCE_TESTNET', 'false').lower() == 'true',
            binance_api_url=os.getenv('BINANCE_API_URL', 'https://api.binance.com'),
            
            # 데이터베이스 설정
            database_path=os.getenv('DATABASE_PATH', './data/trading_bot.db'),
            
            # 로깅 설정
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_file=os.getenv('LOG_FILE', './logs/trading_bot.log'),
            
            # 거래 설정
            trading_symbol=os.getenv('TRADING_SYMBOL', 'BTCUSDT'),
            initial_capital=float(os.getenv('INITIAL_CAPITAL', '3000000')),
            max_position_size=float(os.getenv('MAX_POSITION_SIZE', '0.1')),
            stop_loss_percent=float(os.getenv('STOP_LOSS_PERCENT', '0.02')),
            take_profit_percent=float(os.getenv('TAKE_PROFIT_PERCENT', '0.04')),
            
            # 알림 설정
            telegram_bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
            telegram_chat_id=os.getenv('TELEGRAM_CHAT_ID'),
            
            # 개발 환경 설정
            debug_mode=os.getenv('DEBUG_MODE', 'true').lower() == 'true',
            backtest_mode=os.getenv('BACKTEST_MODE', 'false').lower() == 'true',
            
            # 50개 코인 설정
            selected_coins_file=os.getenv('SELECTED_COINS_FILE', './selected_coins.json'),
            max_coins=int(os.getenv('MAX_COINS', '50'))
        )
    
    def validate_required(self) -> bool:
        """필수 설정 검증"""
        required_fields = [
            self.binance_api_key,
            self.binance_secret_key,
            self.trading_symbol
        ]
        return all(field for field in required_fields)
    
    def print_config_summary(self):
        """설정 요약 출력"""
        print("="*50)
        print("🤖 트레이딩 봇 설정 요약")
        print("="*50)
        print(f"거래 심볼: {self.trading_symbol}")
        print(f"초기 자본: {self.initial_capital:,.0f} KRW")
        print(f"최대 포지션 크기: {self.max_position_size*100:.1f}%")
        print(f"손절 비율: {self.stop_loss_percent*100:.1f}%")
        print(f"익절 비율: {self.take_profit_percent*100:.1f}%")
        print(f"데버그 모드: {self.debug_mode}")
        print(f"백테스트 모드: {self.backtest_mode}")
        print(f"50개 코인 파일: {self.selected_coins_file}")
        print("="*50)

# 사용 예시
if __name__ == "__main__":
    config = Config.from_env()
    config.print_config_summary() 