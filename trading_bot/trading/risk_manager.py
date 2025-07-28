"""
리스크 관리 모듈
"""

import logging
from typing import Dict, Any, Optional
from bot.config import Config

class RiskManager:
    """리스크 관리 클래스"""
    
    def __init__(self, config: Config):
        """리스크 관리자 초기화"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 리스크 상태
        self.daily_loss = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        
        self.logger.info("RiskManager 초기화 완료")
    
    def check_daily_loss_limit(self) -> bool:
        """일일 손실 한도 확인"""
        daily_loss_percent = abs(self.daily_loss) / self.config.initial_capital
        
        if daily_loss_percent > 0.05:  # 5% 일일 손실 한도
            self.logger.warning(f"일일 손실 한도 초과: {daily_loss_percent:.2%}")
            return False
        
        return True
    
    def check_position_size(self, signal_strength: float) -> bool:
        """포지션 크기 확인"""
        proposed_position = self.config.max_position_size * abs(signal_strength)
        
        if proposed_position > self.config.max_position_size:
            self.logger.warning(f"포지션 크기 초과: {proposed_position:.2%}")
            return False
        
        return True
    
    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """손절가 계산"""
        if side == 'BUY':
            return entry_price * (1 - self.config.stop_loss_percent)
        else:
            return entry_price * (1 + self.config.stop_loss_percent)
    
    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """익절가 계산"""
        if side == 'BUY':
            return entry_price * (1 + self.config.take_profit_percent)
        else:
            return entry_price * (1 - self.config.take_profit_percent)
    
    def check_risk(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """리스크 체크"""
        try:
            final_signal = signal.get('final_signal', 0.0)
            trade_decision = signal.get('trade_decision', 'HOLD')
            
            risk_check = {
                'can_trade': True,
                'reasons': [],
                'stop_loss': None,
                'take_profit': None
            }
            
            # 일일 손실 한도 확인
            if not self.check_daily_loss_limit():
                risk_check['can_trade'] = False
                risk_check['reasons'].append('일일 손실 한도 초과')
            
            # 포지션 크기 확인
            if not self.check_position_size(final_signal):
                risk_check['can_trade'] = False
                risk_check['reasons'].append('포지션 크기 초과')
            
            # 거래 결정이 있는 경우 손절/익절 계산
            if trade_decision != 'HOLD':
                # 현재 가격은 실제 거래 시점에 조회
                # 여기서는 예시로 50000 사용
                current_price = 50000  # 실제로는 API에서 조회
                
                if trade_decision == 'BUY':
                    risk_check['stop_loss'] = self.calculate_stop_loss(current_price, 'BUY')
                    risk_check['take_profit'] = self.calculate_take_profit(current_price, 'BUY')
                elif trade_decision == 'SELL':
                    risk_check['stop_loss'] = self.calculate_stop_loss(current_price, 'SELL')
                    risk_check['take_profit'] = self.calculate_take_profit(current_price, 'SELL')
            
            self.logger.info(f"리스크 체크: {risk_check['can_trade']}, 이유: {risk_check['reasons']}")
            return risk_check
            
        except Exception as e:
            self.logger.error(f"리스크 체크 실패: {e}")
            return {
                'can_trade': False,
                'reasons': ['리스크 체크 오류'],
                'stop_loss': None,
                'take_profit': None
            }
    
    def update_trade_result(self, trade_result: Dict[str, Any]):
        """거래 결과 업데이트"""
        try:
            pnl = trade_result.get('pnl', 0.0)
            self.daily_loss += pnl
            self.total_trades += 1
            
            if pnl > 0:
                self.winning_trades += 1
            
            win_rate = self.winning_trades / self.total_trades if self.total_trades > 0 else 0
            
            self.logger.info(f"거래 결과 업데이트: PnL={pnl:.2f}, 승률={win_rate:.2%}")
            
        except Exception as e:
            self.logger.error(f"거래 결과 업데이트 실패: {e}")
    
    def get_risk_status(self) -> Dict[str, Any]:
        """리스크 상태 조회"""
        return {
            'daily_loss': self.daily_loss,
            'daily_loss_percent': abs(self.daily_loss) / self.config.initial_capital,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': self.winning_trades / self.total_trades if self.total_trades > 0 else 0
        } 