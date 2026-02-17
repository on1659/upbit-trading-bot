"""
자본 규모별 빠른 최적화 (핵심 조합만)
"""
from backtest_by_capital import BacktesterWithSlippage
from strategies import Strategy1_MeanReversion
import config

print("=" * 80)
print("🔬 자본 규모별 최적 파라미터 탐색 (빠른 버전)")
print("=" * 80)
print()

# 테스트할 자본
capitals = [
    ("50만원", 500_000),
    ("100만원", 1_000_000),
    ("500만원", 5_000_000),
    ("1000만원", 10_000_000),
]

# 핵심 조합만 테스트 (10개)
test_combinations = [
    # (RSI, 투자비율, 손절, 익절)
    (20, 0.10, 0.015, 0.07),  # 극단 보수
    (25, 0.10, 0.015, 0.07),  # 보수
    (30, 0.10, 0.015, 0.07),  # 밸런스 (현재)
    (35, 0.10, 0.015, 0.07),  # 중도
    (40, 0.10, 0.015, 0.07),  # 공격
    
    (30, 0.05, 0.015, 0.07),  # 투자비율 낮음
    (30, 0.15, 0.015, 0.07),  # 투자비율 높음
    
    (30, 0.10, 0.010, 0.07),  # 손절 타이트
    (30, 0.10, 0.020, 0.07),  # 손절 여유
    
    (30, 0.10, 0.015, 0.10),  # 익절 높음
]

print(f"📊 테스트 조합: {len(test_combinations)}개")
print()

all_results = {}

for cap_name, capital in capitals:
    print(f"\n{'=' * 80}")
    print(f"💰 {cap_name} ({capital:,}원)")
    print('=' * 80)
    
    results = []
    
    for i, (rsi, ratio, stop, take) in enumerate(test_combinations, 1):
        print(f"[{i}/{len(test_combinations)}] RSI={rsi} 비율={ratio*100:.0f}% 손절={stop*100:.1f}% 익절={take*100:.0f}%", end=' ')
        
        # 파라미터 설정
        params = config.STRATEGY_PARAMS.copy()
        params['rsi_oversold'] = rsi
        
        # 임시 config
        original_ratio = config.INVEST_RATIO
        original_stop = config.STOP_LOSS
        original_take = config.TAKE_PROFIT
        
        config.INVEST_RATIO = ratio
        config.STOP_LOSS = stop
        config.TAKE_PROFIT = take
        
        # 백테스팅
        strategy = Strategy1_MeanReversion(params)
        backtester = BacktesterWithSlippage(strategy, initial_balance=capital)
        
        result = backtester.run(
            ticker="KRW-BTC",
            start_date="20251117",
            end_date="20260217",
            interval="day"
        )
        
        # 복원
        config.INVEST_RATIO = original_ratio
        config.STOP_LOSS = original_stop
        config.TAKE_PROFIT = original_take
        
        if result:
            trades = len([t for t in result['trades'] if t['type'] == 'buy'])
            print(f"→ {result['return_ratio']:+.2f}% ({trades}회)")
            
            results.append({
                'rsi': rsi,
                'ratio': ratio,
                'stop': stop,
                'take': take,
                'profit': result['total_return'],
                'return_ratio': result['return_ratio'],
                'trades': trades,
                'win_rate': result['win_rate'],
                'slippage': result['avg_slippage']
            })
        else:
            print("→ 실패")
    
    # 정렬
    results.sort(key=lambda x: x['return_ratio'], reverse=True)
    all_results[cap_name] = results
    
    # Top 3
    print(f"\n🏆 Top 3:")
    for i, r in enumerate(results[:3], 1):
        emoji = "🥇" if i == 1 else ("🥈" if i == 2 else "🥉")
        print(f"{emoji} RSI={r['rsi']} 비율={r['ratio']*100:.0f}% 손절={r['stop']*100:.1f}% 익절={r['take']*100:.0f}% → {r['return_ratio']:+.2f}% ({r['trades']}회, 승률 {r['win_rate']:.0f}%)")

# 종합
print("\n\n")
print("=" * 80)
print("📊 자본별 최적 설정")
print("=" * 80)
print()

print(f"{'자본':<12} {'RSI':<6} {'투자비율':<10} {'손절':<8} {'익절':<8} {'수익률':<10} {'거래'}")
print("-" * 80)

summary = []
for cap_name in ["50만원", "100만원", "500만원", "1000만원"]:
    if cap_name in all_results and all_results[cap_name]:
        best = all_results[cap_name][0]
        print(f"{cap_name:<12} {best['rsi']:<6} {best['ratio']*100:>6.0f}% {best['stop']*100:>6.1f}% {best['take']*100:>6.0f}% {best['return_ratio']:>+8.2f}% {best['trades']:>4}회")
        summary.append(best)

print()
print("💡 결론")
print("-" * 80)

if summary:
    # 가장 많이 나온 값 찾기
    from collections import Counter
    
    rsi_common = Counter(r['rsi'] for r in summary).most_common(1)[0][0]
    ratio_common = Counter(r['ratio'] for r in summary).most_common(1)[0][0]
    stop_common = Counter(r['stop'] for r in summary).most_common(1)[0][0]
    take_common = Counter(r['take'] for r in summary).most_common(1)[0][0]
    
    print("✅ 모든 금액대에 적합한 범용 설정:")
    print(f"   RSI: {rsi_common}")
    print(f"   투자비율: {ratio_common*100:.0f}%")
    print(f"   손절: {stop_common*100:.1f}%")
    print(f"   익절: {take_common*100:.0f}%")
    
    avg_return = sum(r['return_ratio'] for r in summary) / len(summary)
    print(f"\n   예상 수익률: {avg_return:+.2f}% (평균)")
