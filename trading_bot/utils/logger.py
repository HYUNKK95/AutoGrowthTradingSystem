"""
로깅 시스템
"""

import logging
import os
from datetime import datetime
from typing import Optional

def setup_logger(
    name: str = "trading_bot",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> logging.Logger:
    """로거 설정"""
    
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (지정된 경우)
    if log_file:
        # 로그 디렉토리 생성
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = "trading_bot") -> logging.Logger:
    """기존 로거 가져오기"""
    return logging.getLogger(name)

# 사용 예시
if __name__ == "__main__":
    # 로거 설정
    logger = setup_logger(
        name="test_logger",
        log_level="INFO",
        log_file="./logs/test.log"
    )
    
    # 로그 테스트
    logger.info("로깅 시스템 테스트 시작")
    logger.warning("경고 메시지 테스트")
    logger.error("오류 메시지 테스트")
    logger.info("로깅 시스템 테스트 완료") 