from strategies import Strategy1_MeanReversion
from backtest import Backtester
import config

print("=" * 60)
print("📅 최근 1개월 RSI 최적화")
print("=" * 60)

results = []
for rsi in [20, 25, 30, 35, 40, 45, 50]:
    params = config.STRATEGY_PARAMS.copy()
    params['rsi_oversold'] = rsi
    strategy = Strategy1_MeanReversion(params)
    backtester = Backtester(strategy, initial_balance=1000000)
    
    result = backtester.run("KRW-BTC", "20260117", "20260217", "day")
    
    if result:
        print(f"RSI {rsi}: {result['return_ratio']:+.2f}% ({len([t for t in result['trades'] if t['type']=='buy'])}회)")
        results.append((rsi, result['return_ratio']))

print("\n최고: RSI", max(results, key=lambda x: x[1]))
