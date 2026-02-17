"""
업비트 자동매매 봇 v2.0
- 10개 전략 선택 가능
- 실시간 매매
- 손절/익절 자동화
"""
import time
import pyupbit
import pandas as pd
from datetime import datetime
import config
from strategies import STRATEGIES, STRATEGY_CONFIGS


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
        strategy_num = config.SELECTED_STRATEGY
        strategy_class = STRATEGIES.get(strategy_num)
        
        if not strategy_class:
            print(f"❌ 전략 #{strategy_num}을 찾을 수 없습니다. 전략 #1로 대체합니다.")
            strategy_num = 1
            strategy_class = STRATEGIES[1]
        
        self.strategy = strategy_class(config.STRATEGY_PARAMS)
        self.strategy_config = STRATEGY_CONFIGS[strategy_num]
        
        print(f"🎯 전략: #{strategy_num} {self.strategy_config['name']}")
        print(f"   {self.strategy_config['description']}")
        print(f"   손절: {config.STOP_LOSS*100:.1f}% / 익절: {config.TAKE_PROFIT*100:.1f}%")
        
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
    
    def send_telegram(self, message):
        """
        텔레그램 알림 (선택사항)
        """
        if not config.TELEGRAM_TOKEN or not config.TELEGRAM_CHAT_ID:
            return
        
        try:
            import requests
            url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage"
            data = {
                "chat_id": config.TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }
            requests.post(url, data=data, timeout=5)
        except:
            pass  # 알림 실패해도 봇은 계속
    
    def run(self, ticker=None, interval=None, sleep_sec=60):
        """
        봇 실행
        
        Args:
            ticker: 티커
            interval: 캔들 주기
            sleep_sec: 대기 시간 (초)
        """
        ticker = ticker or config.TARGET_COIN
        interval = interval or config.INTERVAL
        
        print()
        print("=" * 60)
        print(f"🤖 자동매매 봇 시작")
        print("=" * 60)
        print(f"   티커: {ticker}")
        print(f"   주기: {interval}")
        print(f"   모드: {config.TRADING_MODE}")
        print(f"   전략: #{config.SELECTED_STRATEGY} {self.strategy_config['name']}")
        print("=" * 60)
        
        # 시작 알림
        start_msg = f"""
🤖 <b>업비트 봇 시작</b>

전략: #{config.SELECTED_STRATEGY} {self.strategy_config['name']}
티커: {ticker}
모드: {config.TRADING_MODE}
손절: {config.STOP_LOSS*100:.1f}% / 익절: {config.TAKE_PROFIT*100:.1f}%
"""
        self.send_telegram(start_msg.strip())
        
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
                
                # 포지션 정보
                pos_info = ""
                if self.position == 'long':
                    profit_ratio = (current_price - self.entry_price) / self.entry_price * 100
                    holding_time = (datetime.now() - self.entry_time).total_seconds() / 3600
                    pos_info = f" | 포지션: +{profit_ratio:.2f}% ({holding_time:.1f}h)"
                
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
                print(f"현재가: {current_price:,.0f}원 | RSI: {current['rsi']:.1f} | 신호: {signal}{pos_info}")
                
                # 손절/익절 체크
                if self.position == 'long':
                    if self.check_stop_loss(ticker):
                        result = self.sell(ticker)
                        if result or config.TRADING_MODE == 'test':
                            profit_ratio = (current_price - self.entry_price) / self.entry_price * 100
                            msg = f"""
🔻 <b>손절</b>

티커: {ticker}
진입가: {self.entry_price:,.0f}원
현재가: {current_price:,.0f}원
손실: {profit_ratio:.2f}%
"""
                            self.send_telegram(msg.strip())
                    elif self.check_take_profit(ticker):
                        result = self.sell(ticker)
                        if result or config.TRADING_MODE == 'test':
                            profit_ratio = (current_price - self.entry_price) / self.entry_price * 100
                            msg = f"""
🔺 <b>익절</b>

티커: {ticker}
진입가: {self.entry_price:,.0f}원
현재가: {current_price:,.0f}원
수익: {profit_ratio:.2f}%
"""
                            self.send_telegram(msg.strip())
                
                # 매매 실행
                if signal == 'buy' and self.position is None:
                    result = self.buy(ticker, ratio=config.INVEST_RATIO)
                    if result or config.TRADING_MODE == 'test':
                        msg = f"""
📈 <b>매수</b>

티커: {ticker}
가격: {current_price:,.0f}원
RSI: {current['rsi']:.1f}
전략: {self.strategy_config['name']}
"""
                        self.send_telegram(msg.strip())
                elif signal == 'sell' and self.position == 'long':
                    result = self.sell(ticker)
                    if result or config.TRADING_MODE == 'test':
                        profit_ratio = (current_price - self.entry_price) / self.entry_price * 100
                        msg = f"""
📉 <b>매도</b>

티커: {ticker}
진입가: {self.entry_price:,.0f}원
현재가: {current_price:,.0f}원
수익: {profit_ratio:+.2f}%
"""
                        self.send_telegram(msg.strip())
                
                # 대기
                time.sleep(sleep_sec)
                
            except KeyboardInterrupt:
                print("\n\n⛔ 봇 종료")
                break
            except Exception as e:
                print(f"❌ 에러 발생: {e}")
                time.sleep(sleep_sec)


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("🤖 업비트 자동매매 봇 v2.0")
    print("=" * 60)
    
    bot = TradingBot()
    
    # 잔고 확인
    if bot.upbit:
        krw = bot.get_balance("KRW")
        btc = bot.get_balance("BTC")
        print(f"\n💰 잔고")
        print(f"   KRW: {krw:,.0f}원")
        if btc > 0:
            print(f"   BTC: {btc:.8f}")
    
    # 경고
    if config.TRADING_MODE == 'real':
        print()
        print("⚠️" * 20)
        print("실전 모드입니다! 실제 돈이 거래됩니다!")
        print("⚠️" * 20)
        print()
        response = input("계속하시겠습니까? (yes/no): ")
        if response.lower() != 'yes':
            print("봇을 종료합니다.")
            exit()
    
    # 봇 실행
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n\n⛔ 봇 종료")
        bot.send_telegram("⛔ 봇이 수동으로 종료되었습니다.")
