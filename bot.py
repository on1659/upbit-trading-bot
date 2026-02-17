"""
업비트 자동매매 봇
"""
import time
import pyupbit
import pandas as pd
from datetime import datetime
import config
from strategy import Strategy, SimpleRSIStrategy


class TradingBot:
    def __init__(self, access_key=None, secret_key=None):
        """
        초기화
        
        Args:
            access_key: 업비트 Access Key
            secret_key: 업비트 Secret Key
        """
        self.access_key = access_key or config.UPBIT_ACCESS_KEY
        self.secret_key = secret_key or config.UPBIT_SECRET_KEY
        
        # API 연결
        if self.access_key and self.secret_key:
            self.upbit = pyupbit.Upbit(self.access_key, self.secret_key)
            print("✅ 업비트 API 연결 성공")
        else:
            self.upbit = None
            print("⚠️ API 키가 없습니다. 읽기 전용 모드로 실행됩니다.")
        
        # 전략 설정
        self.strategy = Strategy(config.STRATEGY_PARAMS)
        # self.strategy = SimpleRSIStrategy(config.STRATEGY_PARAMS)  # 단순 전략
        
        # 매매 상태
        self.position = None  # 'long', 'short', None
        self.entry_price = 0
        self.entry_time = None
        
    def get_balance(self, ticker="KRW"):
        """
        잔고 조회
        
        Args:
            ticker: 티커 (기본값: KRW)
            
        Returns:
            잔고
        """
        if not self.upbit:
            return 0
        
        balance = self.upbit.get_balance(ticker)
        return balance if balance else 0
    
    def get_current_price(self, ticker):
        """
        현재가 조회
        
        Args:
            ticker: 티커
            
        Returns:
            현재가
        """
        return pyupbit.get_current_price(ticker)
    
    def get_ohlcv(self, ticker, interval="minute60", count=200):
        """
        OHLCV 데이터 조회
        
        Args:
            ticker: 티커
            interval: 주기 (minute1, minute3, minute5, minute10, minute15, minute30, minute60, minute240, day, week, month)
            count: 개수
            
        Returns:
            DataFrame
        """
        df = pyupbit.get_ohlcv(ticker, interval=interval, count=count)
        
        if df is None or len(df) == 0:
            return None
        
        # 컬럼명 소문자로 변경
        df.columns = [col.lower() for col in df.columns]
        
        return df
    
    def buy(self, ticker, amount=None, ratio=None):
        """
        매수
        
        Args:
            ticker: 티커
            amount: 매수 금액 (원)
            ratio: KRW 잔고 대비 비율 (0~1)
            
        Returns:
            주문 결과
        """
        if not self.upbit:
            print("⚠️ API 키가 없어 매수할 수 없습니다.")
            return None
        
        if config.TRADING_MODE == 'test':
            print("🧪 [테스트 모드] 실제 매수는 실행되지 않습니다.")
            return None
        
        # 매수 금액 계산
        if ratio:
            krw_balance = self.get_balance("KRW")
            amount = krw_balance * ratio
        
        if not amount or amount <= 5000:
            print("⚠️ 매수 금액이 최소 금액(5000원)보다 적습니다.")
            return None
        
        # 매수 실행
        try:
            result = self.upbit.buy_market_order(ticker, amount)
            print(f"✅ 매수 주문: {ticker}, {amount:,.0f}원")
            print(f"   주문 UUID: {result['uuid']}")
            
            self.position = 'long'
            self.entry_price = self.get_current_price(ticker)
            self.entry_time = datetime.now()
            
            return result
        except Exception as e:
            print(f"❌ 매수 실패: {e}")
            return None
    
    def sell(self, ticker, amount=None):
        """
        매도
        
        Args:
            ticker: 티커
            amount: 매도 수량 (None이면 전량 매도)
            
        Returns:
            주문 결과
        """
        if not self.upbit:
            print("⚠️ API 키가 없어 매도할 수 없습니다.")
            return None
        
        if config.TRADING_MODE == 'test':
            print("🧪 [테스트 모드] 실제 매도는 실행되지 않습니다.")
            return None
        
        # 보유 수량 확인
        coin_ticker = ticker.split('-')[1]
        coin_balance = self.get_balance(coin_ticker)
        
        if coin_balance <= 0:
            print("⚠️ 보유 수량이 없습니다.")
            return None
        
        # 매도 수량 결정
        sell_amount = amount if amount else coin_balance
        
        # 매도 실행
        try:
            result = self.upbit.sell_market_order(ticker, sell_amount)
            print(f"✅ 매도 주문: {ticker}, {sell_amount}개")
            print(f"   주문 UUID: {result['uuid']}")
            
            self.position = None
            self.entry_price = 0
            self.entry_time = None
            
            return result
        except Exception as e:
            print(f"❌ 매도 실패: {e}")
            return None
    
    def check_stop_loss(self, ticker):
        """
        손절 체크
        
        Args:
            ticker: 티커
            
        Returns:
            손절 여부
        """
        if self.position != 'long' or self.entry_price == 0:
            return False
        
        current_price = self.get_current_price(ticker)
        loss_ratio = (current_price - self.entry_price) / self.entry_price
        
        if loss_ratio <= -config.STOP_LOSS:
            print(f"⚠️ 손절 발동! 손실률: {loss_ratio*100:.2f}%")
            return True
        
        return False
    
    def check_take_profit(self, ticker):
        """
        익절 체크
        
        Args:
            ticker: 티커
            
        Returns:
            익절 여부
        """
        if self.position != 'long' or self.entry_price == 0:
            return False
        
        current_price = self.get_current_price(ticker)
        profit_ratio = (current_price - self.entry_price) / self.entry_price
        
        if profit_ratio >= config.TAKE_PROFIT:
            print(f"✅ 익절 발동! 수익률: {profit_ratio*100:.2f}%")
            return True
        
        return False
    
    def run(self, ticker=None, interval="minute60", sleep_sec=60):
        """
        봇 실행
        
        Args:
            ticker: 티커
            interval: 캔들 주기
            sleep_sec: 대기 시간 (초)
        """
        ticker = ticker or config.TARGET_COIN
        
        print(f"🤖 자동매매 봇 시작")
        print(f"   티커: {ticker}")
        print(f"   주기: {interval}")
        print(f"   모드: {config.TRADING_MODE}")
        print("-" * 50)
        
        while True:
            try:
                # OHLCV 데이터 가져오기
                df = self.get_ohlcv(ticker, interval=interval)
                
                if df is None:
                    print("⚠️ 데이터를 가져올 수 없습니다.")
                    time.sleep(sleep_sec)
                    continue
                
                # 지표 계산
                df = self.strategy.calculate_indicators(df)
                
                # 신호 생성
                signal = self.strategy.generate_signal(df)
                
                # 현재 상태 출력
                current = df.iloc[-1]
                current_price = self.get_current_price(ticker)
                
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
                print(f"현재가: {current_price:,.0f}원")
                print(f"RSI: {current['rsi']:.2f}")
                print(f"MACD: {current['macd']:.2f}")
                print(f"신호: {signal}")
                
                # 손절/익절 체크
                if self.position == 'long':
                    if self.check_stop_loss(ticker):
                        self.sell(ticker)
                    elif self.check_take_profit(ticker):
                        self.sell(ticker)
                
                # 매매 실행
                if signal == 'buy' and self.position is None:
                    self.buy(ticker, ratio=config.INVEST_RATIO)
                elif signal == 'sell' and self.position == 'long':
                    self.sell(ticker)
                
                # 대기
                time.sleep(sleep_sec)
                
            except KeyboardInterrupt:
                print("\n\n⛔ 봇 종료")
                break
            except Exception as e:
                print(f"❌ 에러 발생: {e}")
                time.sleep(sleep_sec)


if __name__ == "__main__":
    bot = TradingBot()
    
    # 잔고 확인
    krw = bot.get_balance("KRW")
    print(f"💰 KRW 잔고: {krw:,.0f}원")
    
    # 봇 실행
    bot.run()
