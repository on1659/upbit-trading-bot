"""
설정 파일
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ========================================
# 전략 선택
# ========================================
# 1: Mean Reversion (역추세 반등형) - 추천! ⭐
# 2: Trend Following (추세 추종형)
# 3: Scalping (스캘핑)
# 4: MACD Only (MACD 순수주의)
# 5: Momentum Bomb (모멘텀 폭탄)
# 6: Contrarian (역발상)
# 7: Random Monkey (랜덤 원숭이 - 통제군)
# 8: Always Buy (무조건 사 - 절대 실전 금지)
# 9: Buy The Dip (폭락 사냥꾼)
# 10: Moon Shot (로켓 탑승 - 극고위험)
SELECTED_STRATEGY = int(os.getenv('STRATEGY', '1'))

# ========================================
# API 키
# ========================================
UPBIT_ACCESS_KEY = os.getenv('UPBIT_ACCESS_KEY', '')
UPBIT_SECRET_KEY = os.getenv('UPBIT_SECRET_KEY', '')

# ========================================
# 매매 설정
# ========================================
TRADING_MODE = os.getenv('TRADING_MODE', 'test')  # test or real
INVEST_RATIO = float(os.getenv('INVEST_RATIO', '0.1'))  # 투자 비율
TARGET_COIN = os.getenv('TARGET_COIN', 'KRW-BTC')

# ========================================
# 전략 파라미터
# ========================================
STRATEGY_PARAMS = {
    'rsi_period': 14,
    'rsi_oversold': 30,
    'rsi_overbought': 70,
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
}

# ========================================
# 전략별 손익 설정
# ========================================
STRATEGY_SETTINGS = {
    1: {'stop_loss': 0.015, 'take_profit': 0.07, 'interval': 'day'},
    2: {'stop_loss': 0.02, 'take_profit': 0.10, 'interval': 'day'},
    3: {'stop_loss': 0.005, 'take_profit': 0.015, 'interval': 'minute60'},
    4: {'stop_loss': 0.02, 'take_profit': 0.08, 'interval': 'day'},
    5: {'stop_loss': 0.03, 'take_profit': 0.15, 'interval': 'day'},
    6: {'stop_loss': 0.01, 'take_profit': 0.20, 'interval': 'day'},
    7: {'stop_loss': 0.02, 'take_profit': 0.05, 'interval': 'day'},
    8: {'stop_loss': 0, 'take_profit': 0.50, 'interval': 'day'},
    9: {'stop_loss': 0.03, 'take_profit': 0.12, 'interval': 'day'},
    10: {'stop_loss': 0.05, 'take_profit': 0.25, 'interval': 'day'},
}

# 현재 선택된 전략의 설정 적용
STOP_LOSS = STRATEGY_SETTINGS[SELECTED_STRATEGY]['stop_loss']
TAKE_PROFIT = STRATEGY_SETTINGS[SELECTED_STRATEGY]['take_profit']
INTERVAL = STRATEGY_SETTINGS[SELECTED_STRATEGY]['interval']

# ========================================
# 텔레그램 알림
# ========================================
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
