"""
트레이딩 전략
"""
import pandas as pd
import ta


class Strategy:
    """
    기술적 지표 기반 매매 전략
    """
    
    def __init__(self, params=None):
        self.params = params or {}
        
    def calculate_indicators(self, df):
        """
        기술적 지표 계산
        
        Args:
            df: OHLCV 데이터프레임 (columns: open, high, low, close, volume)
            
        Returns:
            지표가 추가된 데이터프레임
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
        
        return df
    
    def generate_signal(self, df):
        """
        매매 신호 생성
        
        Args:
            df: 지표가 계산된 데이터프레임
            
        Returns:
            'buy', 'sell', 'hold'
        """
        if len(df) < 2:
            return 'hold'
        
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # RSI 과매도/과매수
        rsi_oversold = self.params.get('rsi_oversold', 28)  # 밸런스
        rsi_overbought = self.params.get('rsi_overbought', 70)
        
        # 매수 신호
        buy_signals = []
        
        # 1. RSI 과매도 구간
        if current['rsi'] < rsi_oversold:
            buy_signals.append('rsi_oversold')
        
        # 2. 가격이 20일선 아래 + MACD 상승
        if current['close'] < current['ma_20'] and current['macd'] > previous['macd']:
            buy_signals.append('price_below_ma20_macd_rising')
        
        # 3. 볼린저 밴드 하단 근처 (5% 이내)
        if current['close'] < current['bb_lower'] * 1.05:
            buy_signals.append('near_bb_lower')
        
        # 4. RSI 다이버전스 (가격 하락 but RSI 상승 → 반등 신호)
        if (current['close'] < previous['close'] and 
            current['rsi'] > previous['rsi'] and 
            current['rsi'] < rsi_oversold + 10):  # RSI 38 이하에서만
            buy_signals.append('rsi_divergence')
        
        # 매도 신호
        sell_signals = []
        
        # 1. RSI 과매수 구간
        if current['rsi'] > rsi_overbought:
            sell_signals.append('rsi_overbought')
        
        # 2. MACD 데드크로스
        if (current['macd'] < current['macd_signal'] and 
            previous['macd'] >= previous['macd_signal']):
            sell_signals.append('macd_dead_cross')
        
        # 3. 볼린저 밴드 상단 돌파
        if current['close'] > current['bb_upper']:
            sell_signals.append('bb_upper_break')
        
        # 신호 판단: 2개 이상 일치
        if len(buy_signals) >= 2:
            return 'buy'
        elif len(sell_signals) >= 2:
            return 'sell'
        else:
            return 'hold'


class SimpleRSIStrategy(Strategy):
    """
    단순 RSI 전략 (테스트용)
    """
    
    def generate_signal(self, df):
        if len(df) < 2:
            return 'hold'
        
        current = df.iloc[-1]
        
        rsi_oversold = self.params.get('rsi_oversold', 30)
        rsi_overbought = self.params.get('rsi_overbought', 70)
        
        if current['rsi'] < rsi_oversold:
            return 'buy'
        elif current['rsi'] > rsi_overbought:
            return 'sell'
        else:
            return 'hold'
