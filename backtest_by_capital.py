"""
초기 자본 규모별 백테스팅
슬리피지(체결가 차이) 포함
"""
import pyupbit
import pandas as pd
from strategies import Strategy1_MeanReversion
import config

class BacktesterWithSlippage:
    """
    슬리피지를 고려한 백테스터
    """
    
    def __init__(self, strategy, initial_balance=1000000):
        self.strategy = strategy
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = None
        self.entry_price = 0
        self.trades = []
        
    def calculate_slippage(self, amount):
        """
        거래 금액에 따른 슬리피지 계산
        
        100만원 이하: 0.05%
        500만원: 0.15%
        1000만원: 0.3%
        """
        if amount < 1_000_000:
            return 0.0005  # 0.05%
        elif amount < 5_000_000:
            # 100만~500만: 선형 보간
            ratio = (amount - 1_000_000) / 4_000_000
            return 0.0005 + (0.001 * ratio)  # 0.05% ~ 0.15%
        elif amount < 10_000_000:
            # 500만~1000만: 선형 보간
            ratio = (amount - 5_000_000) / 5_000_000
            return 0.0015 + (0.0015 * ratio)  # 0.15% ~ 0.3%
        else:
            # 1000만 이상
            excess = (amount - 10_000_000) / 10_000_000
            return 0.003 + (excess * 0.001)  # 0.3% + α
    
    def run(self, ticker, start_date, end_date, interval="day"):
        # 데이터 가져오기
        df = pyupbit.get_ohlcv(ticker, interval=interval, to=end_date)
        if df is None:
            return None
        
        df = df[start_date:end_date]
        df.columns = [col.lower() for col in df.columns]
        df = self.strategy.calculate_indicators(df)
        
        # 백테스팅
        for i in range(len(df)):
            if i < 30:
                continue
            
            current_df = df.iloc[:i+1]
            signal = self.strategy.generate_signal(current_df)
            current_price = df.iloc[i]['close']
            current_date = df.index[i]
            
            # 매수
            if signal == 'buy' and self.position is None:
                invest_amount = self.balance * config.INVEST_RATIO
                
                # 슬리피지 적용
                slippage = self.calculate_slippage(invest_amount)
                actual_price = current_price * (1 + slippage)
                
                quantity = invest_amount / actual_price
                
                self.position = quantity
                self.entry_price = actual_price
                self.balance -= invest_amount
                
                self.trades.append({
                    'date': current_date,
                    'type': 'buy',
                    'price': current_price,
                    'actual_price': actual_price,
                    'slippage': slippage,
                    'quantity': quantity,
                    'balance': self.balance
                })
            
            # 손절/익절
            if self.position is not None:
                current_profit_ratio = (current_price - self.entry_price) / self.entry_price
                
                # 손절
                if config.STOP_LOSS > 0 and current_profit_ratio <= -config.STOP_LOSS:
                    sell_amount = self.position * current_price
                    
                    # 슬리피지 적용 (매도는 반대)
                    slippage = self.calculate_slippage(sell_amount)
                    actual_price = current_price * (1 - slippage)
                    
                    profit = self.position * (actual_price - self.entry_price)
                    
                    self.balance += self.position * actual_price
                    
                    self.trades.append({
                        'date': current_date,
                        'type': 'stop_loss',
                        'price': current_price,
                        'actual_price': actual_price,
                        'slippage': slippage,
                        'quantity': self.position,
                        'balance': self.balance,
                        'profit': profit,
                        'profit_ratio': profit / (self.position * self.entry_price)
                    })
                    
                    self.position = None
                    self.entry_price = 0
                
                # 익절
                elif current_profit_ratio >= config.TAKE_PROFIT:
                    sell_amount = self.position * current_price
                    
                    # 슬리피지 적용
                    slippage = self.calculate_slippage(sell_amount)
                    actual_price = current_price * (1 - slippage)
                    
                    profit = self.position * (actual_price - self.entry_price)
                    
                    self.balance += self.position * actual_price
                    
                    self.trades.append({
                        'date': current_date,
                        'type': 'take_profit',
                        'price': current_price,
                        'actual_price': actual_price,
                        'slippage': slippage,
                        'quantity': self.position,
                        'balance': self.balance,
                        'profit': profit,
                        'profit_ratio': profit / (self.position * self.entry_price)
                    })
                    
                    self.position = None
                    self.entry_price = 0
        
        # 최종 자산
        final_balance = self.balance
        if self.position:
            final_balance += self.position * df.iloc[-1]['close']
        
        # 통계
        total_return = final_balance - self.initial_balance
        return_ratio = (total_return / self.initial_balance) * 100
        
        completed_trades = [t for t in self.trades if t['type'] in ['stop_loss', 'take_profit']]
        wins = [t for t in completed_trades if t.get('profit', 0) > 0]
        win_rate = (len(wins) / len(completed_trades) * 100) if completed_trades else 0
        
        # 평균 슬리피지
        avg_slippage = sum(t['slippage'] for t in self.trades) / len(self.trades) if self.trades else 0
        
        return {
            'initial_balance': self.initial_balance,
            'final_balance': final_balance,
            'total_return': total_return,
            'return_ratio': return_ratio,
            'trades': self.trades,
            'win_rate': win_rate,
            'avg_slippage': avg_slippage * 100  # %로 표시
        }


# 테스트
print("=" * 80)
print("💰 초기 자본 규모별 백테스팅 (슬리피지 포함)")
print("=" * 80)
print()

capitals = [
    ("50만원", 500_000),
    ("100만원", 1_000_000),
    ("500만원", 5_000_000),
    ("1000만원", 10_000_000),
]

# RSI 30 전략
params = config.STRATEGY_PARAMS.copy()
params['rsi_oversold'] = 30

results = []

for name, capital in capitals:
    print(f"\n{'=' * 60}")
    print(f"💰 초기 자본: {name} ({capital:,}원)")
    print('=' * 60)
    
    strategy = Strategy1_MeanReversion(params)
    backtester = BacktesterWithSlippage(strategy, initial_balance=capital)
    
    result = backtester.run(
        ticker="KRW-BTC",
        start_date="20251117",
        end_date="20260217",
        interval="day"
    )
    
    if result:
        print(f"최종 자산: {result['final_balance']:,.0f}원")
        print(f"수익: {result['total_return']:+,.0f}원 ({result['return_ratio']:+.2f}%)")
        print(f"거래 횟수: {len([t for t in result['trades'] if t['type'] == 'buy'])}회")
        print(f"승률: {result['win_rate']:.1f}%")
        print(f"평균 슬리피지: {result['avg_slippage']:.3f}%")
        
        results.append({
            'name': name,
            'capital': capital,
            'final': result['final_balance'],
            'profit': result['total_return'],
            'ratio': result['return_ratio'],
            'trades': len([t for t in result['trades'] if t['type'] == 'buy']),
            'win_rate': result['win_rate'],
            'slippage': result['avg_slippage']
        })

# 비교표
print("\n\n")
print("=" * 100)
print("📊 자본 규모별 비교")
print("=" * 100)
print()
print(f"{'자본':<12} {'최종자산':<18} {'수익':<18} {'수익률':<12} {'거래':<8} {'승률':<8} {'슬리피지'}")
print("-" * 100)

for r in results:
    print(f"{r['name']:<12} {r['final']:>15,}원 {r['profit']:>+15,}원 {r['ratio']:>+8.2f}% {r['trades']:>5}회 {r['win_rate']:>6.1f}% {r['slippage']:>8.3f}%")

print()
print("💡 결론")
print("-" * 100)

# 절대 수익 비교
print(f"절대 수익:")
for r in results:
    print(f"  {r['name']}: {r['profit']:+,}원")

print()
print(f"수익률 (슬리피지 영향):")
for r in results:
    print(f"  {r['name']}: {r['ratio']:+.2f}%")
