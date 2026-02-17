"""
설정 파일
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API 키
UPBIT_ACCESS_KEY = os.getenv('UPBIT_ACCESS_KEY', '')
UPBIT_SECRET_KEY = os.getenv('UPBIT_SECRET_KEY', '')

# 매매 설정
TRADING_MODE = os.getenv('TRADING_MODE', 'test')  # test or real
INVEST_RATIO = float(os.getenv('INVEST_RATIO', '0.1'))  # 투자 비율

# 코인 설정
TARGET_COIN = os.getenv('TARGET_COIN', 'KRW-BTC')

# 전략 파라미터
STRATEGY_PARAMS = {
    'rsi_period': 14,
    'rsi_oversold': 30,
    'rsi_overbought': 70,
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
}

# 리스크 관리
STOP_LOSS = 0.015  # 1.5% 손절 (최적)
TAKE_PROFIT = 0.07  # 7% 익절 (밸런스)

# 텔레그램 알림
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
