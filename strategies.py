"""
트레이딩 전략 프리셋
"""
import pandas as pd
import ta


class BaseStrategy:
    """
    기본 전략 클래스
    """
    
    def __init__(self, params=None):
        self.params = params or {}
        self.name = "Base Strategy"
        
    def calculate_indicators(self, df):
        """
        기술적 지표 계산
        """
        # RSI
        rsi_period = self.params.get('rsi_period', 14)
        df['rsi'] = ta.momentum.RSIIndicator(
            close=df['close'], 
            window=rsi_period
        ).rsi()
        
        # MACD
        macd_fast = self.params.get('macd_fast', 12)
        macd_slow = self.params.get('macd_slow', 26)
        macd_signal = self.params.get('macd_signal', 9)
        
        macd = ta.trend.MACD(
            close=df['close'],
            window_fast=macd_fast,
            window_slow=macd_slow,
            window_sign=macd_signal
        )
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        
        # 볼린저 밴드
        bollinger = ta.volatility.BollingerBands(
            close=df['close'],
            window=20,
            window_dev=2
        )
        df['bb_upper'] = bollinger.bollinger_hband()
        df['bb_middle'] = bollinger.bollinger_mavg()
        df['bb_lower'] = bollinger.bollinger_lband()
        
        # 이동평균선
        df['ma_5'] = df['close'].rolling(window=5).mean()
        df['ma_20'] = df['close'].rolling(window=20).mean()
        df['ma_60'] = df['close'].rolling(window=60).mean()
        df['ma_120'] = df['close'].rolling(window=120).mean()
        
        return df
    
    def generate_signal(self, df):
        """
        매매 신호 생성 (자식 클래스에서 구현)
        """
        return 'hold'


class Strategy1_MeanReversion(BaseStrategy):
    """
    전략 #1: 역추세 반등형 (Mean Reversion)
    
    특징:
    - RSI 과매도 구간에서 반등 포착
    - 볼린저 밴드 하단 근처 매수
    - 손절 1.5%, 익절 7%
    
    성과: +1.67% (3개월, Buy & Hold -37.84%)
    """
    
    def __init__(self, params=None):
        super().__init__(params)
        self.name = "Strategy #1: Mean Reversion"
        
    def generate_signal(self, df):
        if len(df) < 2:
            return 'hold'
        
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        rsi_oversold = self.params.get('rsi_oversold', 45)
        rsi_overbought = self.params.get('rsi_overbought', 70)
        
        # 매수 신호
        buy_signals = []
        
        # 1. RSI 과매도
        if current['rsi'] < rsi_oversold:
            buy_signals.append('rsi_oversold')
        
        # 2. 가격 < 20일선 + MACD 상승
        if current['close'] < current['ma_20'] and current['macd'] > previous['macd']:
            buy_signals.append('price_below_ma20_macd_rising')
        
        # 3. 볼린저 하단 근처
        if current['close'] < current['bb_lower'] * 1.10:
            buy_signals.append('near_bb_lower')
        
        # 4. RSI 다이버전스
        if (current['close'] < previous['close'] and 
            current['rsi'] > previous['rsi'] and 
            current['rsi'] < rsi_oversold + 15):
            buy_signals.append('rsi_divergence')
        
        # 매도 신호
        sell_signals = []
        
        if current['rsi'] > rsi_overbought:
            sell_signals.append('rsi_overbought')
        
        if (current['macd'] < current['macd_signal'] and 
            previous['macd'] >= previous['macd_signal']):
            sell_signals.append('macd_dead_cross')
        
        if current['close'] > current['bb_upper']:
            sell_signals.append('bb_upper_break')
        
        # 2개 이상 일치
        if len(buy_signals) >= 2:
            return 'buy'
        elif len(sell_signals) >= 2:
            return 'sell'
        else:
            return 'hold'


class Strategy2_TrendFollowing(BaseStrategy):
    """
    전략 #2: 추세 추종형 (Trend Following)
    
    특징:
    - 골든크로스 매수 (5일선 > 20일선)
    - 상승 추세 올라타기
    - 추세 전환 시 빠른 매도
    - 손절 2%, 익절 10%
    
    철학:
    - "추세는 친구" (Trend is your friend)
    - 반등이 아닌 추세에 올라타기
    - 큰 수익 노림, 작은 손실 수용
    """
    
    def __init__(self, params=None):
        super().__init__(params)
        self.name = "Strategy #2: Trend Following"
        
    def generate_signal(self, df):
        if len(df) < 3:
            return 'hold'
        
        current = df.iloc[-1]
        previous = df.iloc[-2]
        prev2 = df.iloc[-3]
        
        # 매수 신호
        buy_signals = []
        
        # 1. 골든크로스 (5일선이 20일선 돌파)
        if (current['ma_5'] > current['ma_20'] and 
            previous['ma_5'] <= previous['ma_20']):
            buy_signals.append('golden_cross')
        
        # 2. 상승 추세 확인 (20일선 > 60일선)
        if current['ma_20'] > current['ma_60']:
            buy_signals.append('uptrend')
        
        # 3. MACD 골든크로스
        if (current['macd'] > current['macd_signal'] and 
            previous['macd'] <= previous['macd_signal']):
            buy_signals.append('macd_golden')
        
        # 4. 가격이 20일선 위에서 지지
        if (current['close'] > current['ma_20'] and 
            previous['close'] <= previous['ma_20']):
            buy_signals.append('ma20_support')
        
        # 5. 거래량 증가 (전일 대비 1.3배)
        if current['volume'] > previous['volume'] * 1.3:
            buy_signals.append('volume_surge')
        
        # 매도 신호
        sell_signals = []
        
        # 1. 데드크로스 (5일선이 20일선 하향 돌파)
        if (current['ma_5'] < current['ma_20'] and 
            previous['ma_5'] >= previous['ma_20']):
            sell_signals.append('dead_cross')
        
        # 2. MACD 데드크로스
        if (current['macd'] < current['macd_signal'] and 
            previous['macd'] >= previous['macd_signal']):
            sell_signals.append('macd_dead')
        
        # 3. 20일선 이탈 (지지 붕괴)
        if (current['close'] < current['ma_20'] and 
            previous['close'] >= previous['ma_20']):
            sell_signals.append('ma20_breakdown')
        
        # 매수: 2개 이상 (골든크로스 or MA20 지지 중 1개 필수)
        if ('golden_cross' in buy_signals or 'ma20_support' in buy_signals) and len(buy_signals) >= 2:
            return 'buy'
        # 상승 추세 강할 때
        elif len(buy_signals) >= 3:
            return 'buy'
        # 매도: 데드크로스 or MA20 이탈
        elif 'dead_cross' in sell_signals or 'ma20_breakdown' in sell_signals:
            return 'sell'
        else:
            return 'hold'


class Strategy3_Scalping(BaseStrategy):
    """
    전략 #3: 스캘핑 (Scalping)
    
    특징:
    - 단기 변동성 활용
    - 빠른 진입/청산
    - 손절 0.5%, 익절 1.5%
    - 1시간봉 이하 권장
    
    ⚠️ 주의: 수수료 부담 큼, 실전 검증 필요
    """
    
    def __init__(self, params=None):
        super().__init__(params)
        self.name = "Strategy #3: Scalping"
        
    def generate_signal(self, df):
        if len(df) < 2:
            return 'hold'
        
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # 매수: 볼린저 하단 터치 + RSI 과매도
        if (current['close'] <= current['bb_lower'] and 
            current['rsi'] < 35):
            return 'buy'
        
        # 매도: 볼린저 중간선 도달 or RSI 중립
        if (current['close'] >= current['bb_middle'] or 
            current['rsi'] > 55):
            return 'sell'
        
        return 'hold'


class Strategy4_MACDOnly(BaseStrategy):
    """
    전략 #4: MACD 순수주의 (MACD Only)
    
    특징:
    - MACD만 믿는다
    - 다른 지표 무시
    - 골든/데드크로스만 따름
    - 손절 2%, 익절 8%
    """
    
    def __init__(self, params=None):
        super().__init__(params)
        self.name = "Strategy #4: MACD Only"
        
    def generate_signal(self, df):
        if len(df) < 2:
            return 'hold'
        
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # 골든크로스
        if (current['macd'] > current['macd_signal'] and 
            previous['macd'] <= previous['macd_signal']):
            return 'buy'
        
        # 데드크로스
        if (current['macd'] < current['macd_signal'] and 
            previous['macd'] >= previous['macd_signal']):
            return 'sell'
        
        return 'hold'


class Strategy5_Momentum(BaseStrategy):
    """
    전략 #5: 모멘텀 폭탄 (Momentum Bomb)
    
    특징:
    - 거래량 폭발 + 가격 상승 = 매수
    - "돈 냄새나는 곳으로 달려간다"
    - 손절 3%, 익절 15%
    """
    
    def __init__(self, params=None):
        super().__init__(params)
        self.name = "Strategy #5: Momentum Bomb"
        
    def generate_signal(self, df):
        if len(df) < 3:
            return 'hold'
        
        current = df.iloc[-1]
        previous = df.iloc[-2]
        prev2 = df.iloc[-3]
        
        # 평균 거래량 계산
        avg_volume = df['volume'].tail(20).mean()
        
        # 매수: 거래량 2배 + 가격 상승 + RSI 상승
        if (current['volume'] > avg_volume * 2 and
            current['close'] > previous['close'] and
            current['rsi'] > previous['rsi']):
            return 'buy'
        
        # 매도: 거래량 급감 or RSI 과매수
        if (current['volume'] < avg_volume * 0.5 or
            current['rsi'] > 75):
            return 'sell'
        
        return 'hold'


class Strategy6_Contrarian(BaseStrategy):
    """
    전략 #6: 역발상 (Contrarian)
    
    특징:
    - "공포는 기회다"
    - RSI 극단 과매도 (20 이하)만 매수
    - 볼린저 하단 -10% 이탈 매수
    - 손절 1%, 익절 20%
    """
    
    def __init__(self, params=None):
        super().__init__(params)
        self.name = "Strategy #6: Contrarian"
        
    def generate_signal(self, df):
        if len(df) < 2:
            return 'hold'
        
        current = df.iloc[-1]
        
        # 매수: 극단적 공포
        if (current['rsi'] < 20 or
            current['close'] < current['bb_lower'] * 0.90):
            return 'buy'
        
        # 매도: 정상 회복
        if current['rsi'] > 50:
            return 'sell'
        
        return 'hold'


class Strategy7_Random(BaseStrategy):
    """
    전략 #7: 랜덤 원숭이 (Random Monkey) 🐵
    
    특징:
    - 원숭이가 다트 던지기
    - 10% 확률로 매수
    - 10% 확률로 매도
    - 손절 2%, 익절 5%
    
    목적: 통제군 (다른 전략과 비교)
    """
    
    def __init__(self, params=None):
        super().__init__(params)
        self.name = "Strategy #7: Random Monkey 🐵"
        
    def generate_signal(self, df):
        import random
        
        rand = random.random()
        
        if rand < 0.1:  # 10% 확률
            return 'buy'
        elif rand < 0.2:  # 10% 확률
            return 'sell'
        else:
            return 'hold'


class Strategy8_AlwaysBuy(BaseStrategy):
    """
    전략 #8: 무조건 사 (Always Buy)
    
    특징:
    - 조건 없이 항상 매수 시도
    - "시간이 해결해줄 거야"
    - 손절 없음, 익절 50%
    
    ⚠️ 절대 실전 금지
    """
    
    def __init__(self, params=None):
        super().__init__(params)
        self.name = "Strategy #8: Always Buy"
        
    def generate_signal(self, df):
        # 항상 매수
        return 'buy'


class Strategy9_BuyTheDip(BaseStrategy):
    """
    전략 #9: 폭락 사냥꾼 (Buy The Dip)
    
    특징:
    - 하루 -5% 이상 폭락만 매수
    - "피 흘릴 때 사라"
    - 손절 3%, 익절 12%
    """
    
    def __init__(self, params=None):
        super().__init__(params)
        self.name = "Strategy #9: Buy The Dip"
        
    def generate_signal(self, df):
        if len(df) < 2:
            return 'hold'
        
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # 하루 변동률
        change = (current['close'] / previous['close'] - 1) * 100
        
        # 매수: -5% 이상 폭락
        if change < -5:
            return 'buy'
        
        # 매도: +5% 이상 반등
        if change > 5:
            return 'sell'
        
        return 'hold'


class Strategy10_MoonShot(BaseStrategy):
    """
    전략 #10: 로켓 탑승 (Moon Shot) 🚀
    
    특징:
    - 급등 중인 것만 올라탄다
    - 하루 +3% 이상 상승 + 거래량 폭발
    - "이미 오른 건 더 오른다"
    - 손절 5%, 익절 25%
    
    위험도: ⚠️⚠️⚠️ 극고위험
    """
    
    def __init__(self, params=None):
        super().__init__(params)
        self.name = "Strategy #10: Moon Shot 🚀"
        
    def generate_signal(self, df):
        if len(df) < 3:
            return 'hold'
        
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # 평균 거래량
        avg_volume = df['volume'].tail(20).mean()
        
        # 하루 변동률
        change = (current['close'] / previous['close'] - 1) * 100
        
        # 매수: 급등 + 거래량 폭발
        if (change > 3 and 
            current['volume'] > avg_volume * 1.5 and
            current['rsi'] > 60):
            return 'buy'
        
        # 매도: 하락 전환
        if (change < -2 or current['rsi'] < 50):
            return 'sell'
        
        return 'hold'


# 전략 레지스트리
STRATEGIES = {
    1: Strategy1_MeanReversion,
    2: Strategy2_TrendFollowing,
    3: Strategy3_Scalping,
    4: Strategy4_MACDOnly,
    5: Strategy5_Momentum,
    6: Strategy6_Contrarian,
    7: Strategy7_Random,
    8: Strategy8_AlwaysBuy,
    9: Strategy9_BuyTheDip,
    10: Strategy10_MoonShot,
}

# 전략별 권장 설정
STRATEGY_CONFIGS = {
    1: {
        'name': 'Mean Reversion',
        'stop_loss': 0.015,
        'take_profit': 0.07,
        'interval': 'day',
        'description': '역추세 반등형 - RSI 과매도 반등 포착'
    },
    2: {
        'name': 'Trend Following',
        'stop_loss': 0.02,
        'take_profit': 0.10,
        'interval': 'day',
        'description': '추세 추종형 - 골든크로스 올라타기'
    },
    3: {
        'name': 'Scalping',
        'stop_loss': 0.005,
        'take_profit': 0.015,
        'interval': 'minute60',
        'description': '스캘핑 - 단기 변동성 활용'
    },
    4: {
        'name': 'MACD Only',
        'stop_loss': 0.02,
        'take_profit': 0.08,
        'interval': 'day',
        'description': 'MACD 순수주의 - MACD만 믿는다'
    },
    5: {
        'name': 'Momentum Bomb',
        'stop_loss': 0.03,
        'take_profit': 0.15,
        'interval': 'day',
        'description': '모멘텀 폭탄 - 거래량 폭발 포착'
    },
    6: {
        'name': 'Contrarian',
        'stop_loss': 0.01,
        'take_profit': 0.20,
        'interval': 'day',
        'description': '역발상 - 공포는 기회다'
    },
    7: {
        'name': 'Random Monkey 🐵',
        'stop_loss': 0.02,
        'take_profit': 0.05,
        'interval': 'day',
        'description': '랜덤 원숭이 - 통제군'
    },
    8: {
        'name': 'Always Buy',
        'stop_loss': 0,  # 손절 없음
        'take_profit': 0.50,
        'interval': 'day',
        'description': '무조건 사 - 절대 실전 금지'
    },
    9: {
        'name': 'Buy The Dip',
        'stop_loss': 0.03,
        'take_profit': 0.12,
        'interval': 'day',
        'description': '폭락 사냥꾼 - 피 흘릴 때 사라'
    },
    10: {
        'name': 'Moon Shot 🚀',
        'stop_loss': 0.05,
        'take_profit': 0.25,
        'interval': 'day',
        'description': '로켓 탑승 - 급등 올라타기 (극고위험)'
    }
}
