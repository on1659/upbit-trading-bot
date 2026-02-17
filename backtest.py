"""
백테스팅 시스템
"""
import pyupbit
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import config
from strategies import STRATEGIES, STRATEGY_CONFIGS


class Backtester:
    """
    백테스팅 클래스
    """
    
    def __init__(self, strategy, initial_balance=1000000):
        """
        초기화
        
        Args:
            strategy: 전략 객체
            initial_balance: 초기 자본금
        """
        self.strategy = strategy
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = None
        self.entry_price = 0
        self.trades = []
        
    def run(self, ticker, start_date, end_date, interval="day"):
        """
        백테스팅 실행
        
        Args:
            ticker: 티커
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)
            interval: 주기
            
        Returns:
            결과 딕셔너리
        """
        print(f"📊 백테스팅 시작")
        print(f"   티커: {ticker}")
        print(f"   기간: {start_date} ~ {end_date}")
        print(f"   초기 자본: {self.initial_balance:,.0f}원")
        print("-" * 50)
        
        # 데이터 가져오기
        df = pyupbit.get_ohlcv(
            ticker, 
            interval=interval,
            to=end_date
        )
        
        if df is None:
            print("❌ 데이터를 가져올 수 없습니다.")
            return None
        
        # 날짜 필터링
        df = df[start_date:end_date]
        
        # 컬럼명 소문자로
        df.columns = [col.lower() for col in df.columns]
        
        # 지표 계산
        df = self.strategy.calculate_indicators(df)
        
        # 백테스팅
        for i in range(len(df)):
            if i < 30:  # 최소 데이터 필요 (분봉은 짧게)
                continue
            
            current_df = df.iloc[:i+1]
            signal = self.strategy.generate_signal(current_df)
            current_price = df.iloc[i]['close']
            current_date = df.index[i]
            
            # 매수
            if signal == 'buy' and self.position is None:
                invest_amount = self.balance * config.INVEST_RATIO
                quantity = invest_amount / current_price
                
                self.position = quantity
                self.entry_price = current_price
                self.balance -= invest_amount
                
                self.trades.append({
                    'date': current_date,
                    'type': 'buy',
                    'price': current_price,
                    'quantity': quantity,
                    'balance': self.balance
                })
                
                print(f"📈 매수: {current_date.strftime('%Y-%m-%d')} {current_price:,.0f}원")
            
            # 매도
            elif signal == 'sell' and self.position is not None:
                sell_amount = self.position * current_price
                profit = sell_amount - (self.position * self.entry_price)
                profit_ratio = profit / (self.position * self.entry_price)
                
                self.balance += sell_amount
                
                self.trades.append({
                    'date': current_date,
                    'type': 'sell',
                    'price': current_price,
                    'quantity': self.position,
                    'balance': self.balance,
                    'profit': profit,
                    'profit_ratio': profit_ratio
                })
                
                print(f"📉 매도: {current_date.strftime('%Y-%m-%d')} {current_price:,.0f}원 (수익: {profit:,.0f}원, {profit_ratio*100:.2f}%)")
                
                self.position = None
                self.entry_price = 0
            
            # 손절/익절
            if self.position is not None:
                current_profit_ratio = (current_price - self.entry_price) / self.entry_price
                
                # 손절 (손절 설정이 있을 때만)
                if config.STOP_LOSS > 0 and current_profit_ratio <= -config.STOP_LOSS:
                    sell_amount = self.position * current_price
                    profit = sell_amount - (self.position * self.entry_price)
                    
                    self.balance += sell_amount
                    
                    self.trades.append({
                        'date': current_date,
                        'type': 'stop_loss',
                        'price': current_price,
                        'quantity': self.position,
                        'balance': self.balance,
                        'profit': profit,
                        'profit_ratio': current_profit_ratio
                    })
                    
                    print(f"🔻 손절: {current_date.strftime('%Y-%m-%d')} {current_price:,.0f}원 (손실: {profit:,.0f}원, {current_profit_ratio*100:.2f}%)")
                    
                    self.position = None
                    self.entry_price = 0
                
                # 익절
                elif current_profit_ratio >= config.TAKE_PROFIT:
                    sell_amount = self.position * current_price
                    profit = sell_amount - (self.position * self.entry_price)
                    
                    self.balance += sell_amount
                    
                    self.trades.append({
                        'date': current_date,
                        'type': 'take_profit',
                        'price': current_price,
                        'quantity': self.position,
                        'balance': self.balance,
                        'profit': profit,
                        'profit_ratio': current_profit_ratio
                    })
                    
                    print(f"🔺 익절: {current_date.strftime('%Y-%m-%d')} {current_price:,.0f}원 (수익: {profit:,.0f}원, {current_profit_ratio*100:.2f}%)")
                    
                    self.position = None
                    self.entry_price = 0
        
        # 마지막 포지션 정리
        if self.position is not None:
            final_price = df.iloc[-1]['close']
            sell_amount = self.position * final_price
            self.balance += sell_amount
        
        # 결과 계산
        final_balance = self.balance
        total_return = final_balance - self.initial_balance
        return_ratio = (final_balance / self.initial_balance - 1) * 100
        
        # 승률 계산
        sell_trades = [t for t in self.trades if t['type'] in ['sell', 'stop_loss', 'take_profit']]
        win_trades = [t for t in sell_trades if t.get('profit', 0) > 0]
        win_rate = len(win_trades) / len(sell_trades) * 100 if sell_trades else 0
        
        # 결과 출력
        print("\n" + "=" * 50)
        print("📊 백테스팅 결과")
        print("=" * 50)
        print(f"초기 자본: {self.initial_balance:,.0f}원")
        print(f"최종 자본: {final_balance:,.0f}원")
        print(f"총 수익: {total_return:,.0f}원 ({return_ratio:+.2f}%)")
        print(f"거래 횟수: {len(self.trades)}회")
        print(f"승률: {win_rate:.2f}% ({len(win_trades)}/{len(sell_trades)})")
        
        if sell_trades:
            avg_profit = sum(t.get('profit', 0) for t in sell_trades) / len(sell_trades)
            print(f"평균 수익: {avg_profit:,.0f}원")
        
        # Buy & Hold 전략과 비교
        buy_hold_return = (df.iloc[-1]['close'] / df.iloc[0]['close'] - 1) * 100
        print(f"\nBuy & Hold 수익률: {buy_hold_return:+.2f}%")
        print(f"전략 대비: {return_ratio - buy_hold_return:+.2f}%p")
        
        return {
            'initial_balance': self.initial_balance,
            'final_balance': final_balance,
            'total_return': total_return,
            'return_ratio': return_ratio,
            'trades': self.trades,
            'win_rate': win_rate,
            'buy_hold_return': buy_hold_return
        }


if __name__ == "__main__":
    # 전략 선택
    strategy_num = config.SELECTED_STRATEGY
    strategy_class = STRATEGIES[strategy_num]
    strategy = strategy_class(config.STRATEGY_PARAMS)
    strategy_config = STRATEGY_CONFIGS[strategy_num]
    
    print(f"🎯 전략: #{strategy_num} {strategy_config['name']}")
    print(f"   설명: {strategy_config['description']}")
    print(f"   손절: {config.STOP_LOSS*100:.1f}% / 익절: {config.TAKE_PROFIT*100:.1f}%")
    print(f"   시간봉: {config.INTERVAL}")
    print()
    
    # 백테스터 생성
    backtester = Backtester(strategy, initial_balance=1000000)
    
    # 백테스팅 실행
    result = backtester.run(
        ticker="KRW-BTC",
        start_date="20251101",
        end_date="20260217",
        interval=config.INTERVAL
    )
