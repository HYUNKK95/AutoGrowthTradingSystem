#!/usr/bin/env python3
"""
트레이딩 봇 메인 실행 파일
실시간 봇만 담당하며, 과거데이터 수집은 별도 스크립트로 분리됩니다.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from bot.config import Config
from utils.logger import setup_logger
from config.coins_config import CoinsConfig
from data.database import Database

def main():
    """메인 실행 함수"""
    try:
        # 1. 환경 변수 로드
        load_dotenv()
        
        # 2. 설정 로드
        config = Config.from_env()
        
        # 3. 로거 설정
        logger = setup_logger(
            name="trading_bot",
            log_level=config.log_level,
            log_file=config.log_file
        )
        logger.info("트레이딩 봇 시작")
        
        # 4. 설정 검증
        if not config.validate_required():
            logger.error("필수 설정이 누락되었습니다.")
            config.print_config_summary()
            sys.exit(1)
        
        logger.info(f"설정 로드 완료: {config.trading_symbol}")
        
        # 5. 50개 코인 설정 로드
        coins_config = CoinsConfig(config.selected_coins_file)
        logger.info(f"50개 코인 설정 로드 완료: {coins_config.get_total_coins()}개")
        
        # 6. 데이터베이스 초기화
        database = Database(config.database_path)
        logger.info("데이터베이스 초기화 완료")
        
        # 7. 설정 요약 출력
        config.print_config_summary()
        coins_config.print_coins_summary()
        
        # 8. Phase 1 완료 상태 출력
        logger.info("Phase 1 완료: 데이터 수집 시스템 준비 완료!")
        logger.info("다음 단계: Phase 2 - 통합 봇 개발")
        
        # 9. 데이터베이스 정보 출력
        db_info = database.get_database_info()
        logger.info(f"데이터베이스 상태: {db_info}")
        
        # 10. Phase 1 완료 메시지
        logger.info("Phase 1 모든 기능이 정상적으로 작동합니다!")
        logger.info("Phase 2에서 통합 봇 개발을 시작하세요")
        
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
    except Exception as e:
        logger.error(f"오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 