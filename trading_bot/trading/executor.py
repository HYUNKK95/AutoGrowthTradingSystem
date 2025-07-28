"""
거래 실행 모듈 - 고급 버전
"""

import logging
import time
import math
from typing import Dict, Any, Optional, List
from binance.client import Client
from binance.exceptions import BinanceAPIException
from binance.enums import *
from bot.config import Config
from dataclasses import dataclass
from enum import Enum

class OrderType(Enum):
    """주문 타입"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_MARKET = "STOP_MARKET"

@dataclass
class OrderResult:
    """주문 결과 데이터 클래스"""
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    status: str
    timestamp: int
    commission: float
    commission_asset: str

class OrderExecutor:
    """거래 실행 클래스 - 고급 버전"""
    
    def __init__(self, config: Config):
        """거래 실행기 초기화"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Binance 클라이언트
        self.client = Client(
            config.binance_api_key,
            config.binance_secret_key,
            testnet=config.binance_testnet
        )
        
        # 거래 상태
        self.current_position = 0.0
        self.last_order = None
        self.active_orders = []
        self.position_history = []
        
        # 고급 설정
        self.max_slippage = 0.001  # 0.1%
        self.min_order_size = 10.0  # USDT
        self.max_order_size = 1000.0  # USDT
        self.order_timeout = 30  # 초
        
        self.logger.info("OrderExecutor 고급 버전 초기화 완료")
    
    def get_account_info(self) -> Dict[str, Any]:
        """계정 정보 조회 - 고급 버전"""
        try:
            account = self.client.get_account()
            balances = {}
            
            for balance in account['balances']:
                if float(balance['free']) > 0 or float(balance['locked']) > 0:
                    balances[balance['asset']] = {
                        'free': float(balance['free']),
                        'locked': float(balance['locked']),
                        'total': float(balance['free']) + float(balance['locked'])
                    }
            
            # 계정 권한 확인
            permissions = account.get('permissions', [])
            can_trade = 'SPOT' in permissions
            
            return {
                'balances': balances,
                'permissions': permissions,
                'can_trade': can_trade,
                'maker_commission': account.get('makerCommission', 0),
                'taker_commission': account.get('takerCommission', 0)
            }
            
        except Exception as e:
            self.logger.error(f"계정 정보 조회 실패: {e}")
            return {}
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """현재 가격 조회 - 고급 버전"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            self.logger.error(f"현재 가격 조회 실패: {e}")
            return None
    
    def get_order_book(self, symbol: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """호가창 조회"""
        try:
            order_book = self.client.get_order_book(symbol=symbol, limit=limit)
            return {
                'bids': order_book['bids'],
                'asks': order_book['asks'],
                'last_update_id': order_book['lastUpdateId']
            }
        except Exception as e:
            self.logger.error(f"호가창 조회 실패: {e}")
            return None
    
    def calculate_optimal_quantity(self, signal_strength: float, current_price: float, balance: float) -> float:
        """최적 주문 수량 계산 - 고급 버전"""
        try:
            # 기본 포지션 크기
            base_position = self.config.max_position_size
            adjusted_position = base_position * abs(signal_strength)
            
            # 신호 강도에 따른 동적 조정
            if abs(signal_strength) > 0.8:
                adjusted_position *= 1.2  # 강한 신호는 20% 증가
            elif abs(signal_strength) < 0.3:
                adjusted_position *= 0.5  # 약한 신호는 50% 감소
            
            # 최소/최대 제한
            min_position = 0.01  # 1%
            max_position = 0.15  # 15%
            
            position_size = max(min_position, min(max_position, adjusted_position))
            
            # USDT 잔고 기반 수량 계산
            available_balance = balance * position_size
            quantity = available_balance / current_price
            
            # 최소 주문 크기 확인
            if available_balance < self.min_order_size:
                quantity = self.min_order_size / current_price
            
            # 최대 주문 크기 제한
            if available_balance > self.max_order_size:
                quantity = self.max_order_size / current_price
            
            return quantity
            
        except Exception as e:
            self.logger.error(f"최적 수량 계산 실패: {e}")
            return 0.0
    
    def calculate_slippage(self, order_book: Dict[str, Any], side: str, quantity: float) -> float:
        """슬리피지 계산"""
        try:
            if side == 'BUY':
                orders = order_book['asks']
            else:
                orders = order_book['bids']
            
            remaining_quantity = quantity
            total_cost = 0.0
            
            for price, qty in orders:
                price = float(price)
                qty = float(qty)
                
                if remaining_quantity <= 0:
                    break
                
                executed_qty = min(remaining_quantity, qty)
                total_cost += executed_qty * price
                remaining_quantity -= executed_qty
            
            if quantity > 0:
                avg_price = total_cost / quantity
                market_price = float(orders[0][0]) if orders else 0
                
                if market_price > 0:
                    slippage = abs(avg_price - market_price) / market_price
                    return min(slippage, self.max_slippage)
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"슬리피지 계산 실패: {e}")
            return 0.0
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Optional[OrderResult]:
        """시장가 주문 실행 - 고급 버전"""
        try:
            self.logger.info(f"시장가 주문: {side} {quantity} {symbol}")
            
            # 호가창 조회로 슬리피지 예상
            order_book = self.get_order_book(symbol)
            expected_slippage = 0.0
            if order_book:
                expected_slippage = self.calculate_slippage(order_book, side, quantity)
                self.logger.info(f"예상 슬리피지: {expected_slippage:.4f}")
            
            # 주문 실행
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            
            # 주문 결과 처리
            order_result = OrderResult(
                order_id=order['orderId'],
                symbol=order['symbol'],
                side=order['side'],
                quantity=float(order['executedQty']),
                price=float(order['cummulativeQuoteQty']) / float(order['executedQty']) if float(order['executedQty']) > 0 else 0,
                status=order['status'],
                timestamp=int(order['updateTime']),
                commission=float(order.get('commission', 0)),
                commission_asset=order.get('commissionAsset', '')
            )
            
            self.last_order = order_result
            self.active_orders.append(order_result)
            
            self.logger.info(f"주문 실행 완료: {order_result.order_id}, "
                           f"실행가: {order_result.price:.4f}, "
                           f"수량: {order_result.quantity:.4f}")
            
            return order_result
            
        except BinanceAPIException as e:
            self.logger.error(f"Binance API 오류: {e}")
            return None
        except Exception as e:
            self.logger.error(f"주문 실행 실패: {e}")
            return None
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> Optional[OrderResult]:
        """지정가 주문 실행"""
        try:
            self.logger.info(f"지정가 주문: {side} {quantity} {symbol} @ {price}")
            
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=quantity,
                price=str(price)
            )
            
            order_result = OrderResult(
                order_id=order['orderId'],
                symbol=order['symbol'],
                side=order['side'],
                quantity=float(order['executedQty']),
                price=float(order['price']),
                status=order['status'],
                timestamp=int(order['updateTime']),
                commission=float(order.get('commission', 0)),
                commission_asset=order.get('commissionAsset', '')
            )
            
            self.active_orders.append(order_result)
            
            self.logger.info(f"지정가 주문 생성: {order_result.order_id}")
            return order_result
            
        except Exception as e:
            self.logger.error(f"지정가 주문 실패: {e}")
            return None
    
    def place_stop_loss_order(self, symbol: str, side: str, quantity: float, stop_price: float) -> Optional[OrderResult]:
        """손절 주문 실행"""
        try:
            self.logger.info(f"손절 주문: {side} {quantity} {symbol} @ {stop_price}")
            
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_STOP_MARKET,
                quantity=quantity,
                stopPrice=str(stop_price)
            )
            
            order_result = OrderResult(
                order_id=order['orderId'],
                symbol=order['symbol'],
                side=order['side'],
                quantity=float(order['executedQty']),
                price=float(order.get('price', 0)),
                status=order['status'],
                timestamp=int(order['updateTime']),
                commission=float(order.get('commission', 0)),
                commission_asset=order.get('commissionAsset', '')
            )
            
            self.active_orders.append(order_result)
            
            self.logger.info(f"손절 주문 생성: {order_result.order_id}")
            return order_result
            
        except Exception as e:
            self.logger.error(f"손절 주문 실패: {e}")
            return None
    
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """주문 취소"""
        try:
            result = self.client.cancel_order(symbol=symbol, orderId=order_id)
            self.logger.info(f"주문 취소 완료: {order_id}")
            
            # 활성 주문 목록에서 제거
            self.active_orders = [order for order in self.active_orders if order.order_id != order_id]
            
            return True
            
        except Exception as e:
            self.logger.error(f"주문 취소 실패: {e}")
            return False
    
    def get_order_status(self, symbol: str, order_id: str) -> Optional[Dict[str, Any]]:
        """주문 상태 조회"""
        try:
            order = self.client.get_order(symbol=symbol, orderId=order_id)
            return {
                'order_id': order['orderId'],
                'status': order['status'],
                'executed_qty': float(order['executedQty']),
                'price': float(order['price']),
                'commission': float(order.get('commission', 0))
            }
        except Exception as e:
            self.logger.error(f"주문 상태 조회 실패: {e}")
            return None
    
    def execute_trade(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """거래 실행 - 고급 버전"""
        try:
            final_signal = signal.get('final_signal', 0.0)
            trade_decision = signal.get('trade_decision', 'HOLD')
            
            if trade_decision == 'HOLD':
                self.logger.info("거래 결정: HOLD")
                return None
            
            # 현재 가격 조회
            current_price = self.get_current_price(self.config.trading_symbol)
            if not current_price:
                return None
            
            # 계정 정보 조회
            account_info = self.get_account_info()
            if not account_info.get('can_trade', False):
                self.logger.error("거래 권한이 없습니다")
                return None
            
            # USDT 잔고 확인
            usdt_balance = account_info.get('balances', {}).get('USDT', {}).get('free', 0.0)
            if usdt_balance < self.min_order_size:
                self.logger.warning(f"USDT 잔고 부족: {usdt_balance}")
                return None
            
            # 최적 주문 수량 계산
            quantity = self.calculate_optimal_quantity(final_signal, current_price, usdt_balance)
            if quantity <= 0:
                self.logger.warning("유효하지 않은 주문 수량")
                return None
            
            # 거래 실행
            order_result = None
            if trade_decision == 'BUY':
                order_result = self.place_market_order(
                    self.config.trading_symbol,
                    'BUY',
                    quantity
                )
            elif trade_decision == 'SELL':
                order_result = self.place_market_order(
                    self.config.trading_symbol,
                    'SELL',
                    quantity
                )
            
            if order_result:
                # 포지션 업데이트
                if order_result.side == 'BUY':
                    self.current_position += order_result.quantity
                else:
                    self.current_position -= order_result.quantity
                
                # 거래 기록 저장
                trade_record = {
                    'order': order_result,
                    'signal': signal,
                    'execution_time': time.time(),
                    'position': self.current_position
                }
                
                self.position_history.append(trade_record)
                
                self.logger.info(f"거래 실행 성공: {trade_decision} {quantity}")
                return trade_record
            
            return None
            
        except Exception as e:
            self.logger.error(f"거래 실행 실패: {e}")
            return None
    
    def get_trading_summary(self) -> Dict[str, Any]:
        """거래 요약 정보"""
        try:
            total_trades = len(self.position_history)
            total_commission = sum(record['order'].commission for record in self.position_history)
            
            # 수익률 계산 (간단한 버전)
            total_pnl = 0.0
            if len(self.position_history) >= 2:
                for i in range(1, len(self.position_history)):
                    prev_record = self.position_history[i-1]
                    curr_record = self.position_history[i]
                    
                    if prev_record['order'].side != curr_record['order'].side:
                        if prev_record['order'].side == 'BUY':
                            pnl = (curr_record['order'].price - prev_record['order'].price) * prev_record['order'].quantity
                        else:
                            pnl = (prev_record['order'].price - curr_record['order'].price) * curr_record['order'].quantity
                        total_pnl += pnl
            
            return {
                'total_trades': total_trades,
                'total_commission': total_commission,
                'current_position': self.current_position,
                'total_pnl': total_pnl,
                'active_orders': len(self.active_orders)
            }
            
        except Exception as e:
            self.logger.error(f"거래 요약 계산 실패: {e}")
            return {} 