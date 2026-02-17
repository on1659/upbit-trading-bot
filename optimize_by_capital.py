"""
자본 규모별 최적 파라미터 찾기
각 금액대별로 여러 조합 테스트
"""
import itertools
from backtest_by_capital import BacktesterWithSlippage
from strategies import Strategy1_MeanReversion
import config

print("=" * 100)
print("🔬 자본 규모별 최적 파라미터 탐색")
print("=" * 100)
print()

# 테스트할 자본
capitals = [
    ("50만원", 500_000),
    ("100만원", 1_000_000),
    ("500만원", 5_000_000),
    ("1000만원", 10_000_000),
]

# 테스트할 파라미터 조합
test_params = {
    'rsi': [20, 25, 30, 35, 40],
    'invest_ratio': [0.05, 0.10, 0.15, 0.20],
    'stop_loss': [0.01, 0.015, 0.02],
    'take_profit': [0.05, 0.07, 0.10],
}

# 전체 조합 수
total_combinations = (
    len(test_params['rsi']) *
    len(test_params['invest_ratio']) *
    len(test_params['stop_loss']) *
    len(test_params['take_profit'])
)

print(f"📊 테스트 조합: {total_combinations}개")
print(f"   RSI: {test_params['rsi']}")
print(f"   투자비율: {[f'{r*100:.0f}%' for r in test_params['invest_ratio']]}")
print(f"   손절: {[f'{s*100:.1f}%' for s in test_params['stop_loss']]}")
print(f"   익절: {[f'{t*100:.0f}%' for t in test_params['take_profit']]}")
print()

all_results = {}

for cap_name, capital in capitals:
    print(f"\n{'=' * 100}")
    print(f"💰 {cap_name} ({capital:,}원) 최적화 중...")
    print('=' * 100)
    
    results = []
    count = 0
    
    for rsi, ratio, stop, take in itertools.product(
        test_params['rsi'],
        test_params['invest_ratio'],
        test_params['stop_loss'],
        test_params['take_profit']
    ):
        count += 1
        
        # 진행상황 표시 (10개마다)
        if count % 10 == 0:
            print(f"진행: {count}/{total_combinations} ({count/total_combinations*100:.0f}%)", end='\r')
        
        # 파라미터 설정
        params = config.STRATEGY_PARAMS.copy()
        params['rsi_oversold'] = rsi
        
        # 임시 config 오버라이드
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
        
        if result and result['return_ratio'] is not None:
            trades = len([t for t in result['trades'] if t['type'] == 'buy'])
            
            # 거래가 최소 3번 이상인 것만 (통계적 의미)
            if trades >= 3:
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
    
    print()  # 줄바꿈
    
    # 상위 10개 정렬
    results.sort(key=lambda x: x['return_ratio'], reverse=True)
    top10 = results[:10]
    
    all_results[cap_name] = top10
    
    # 결과 출력
    print(f"\n🏆 Top 10 설정 (수익률 순)")
    print("-" * 100)
    print(f"{'순위':<5} {'RSI':<6} {'투자비율':<10} {'손절':<8} {'익절':<8} {'수익률':<10} {'거래':<6} {'승률':<8} {'슬리피지'}")
    print("-" * 100)
    
    for i, r in enumerate(top10, 1):
        emoji = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else "  "))
        print(f"{emoji}{i:<4} {r['rsi']:<6} {r['ratio']*100:>6.0f}% {r['stop']*100:>6.1f}% {r['take']*100:>6.0f}% {r['return_ratio']:>+8.2f}% {r['trades']:>4}회 {r['win_rate']:>6.1f}% {r['slippage']:>8.3f}%")

# 종합 비교
print("\n\n")
print("=" * 100)
print("📊 자본별 최적 설정 비교")
print("=" * 100)
print()

print(f"{'자본':<12} {'RSI':<6} {'투자비율':<10} {'손절':<8} {'익절':<8} {'수익률':<10} {'거래':<6} {'승률'}")
print("-" * 100)

for cap_name in ["50만원", "100만원", "500만원", "1000만원"]:
    if cap_name in all_results and all_results[cap_name]:
        best = all_results[cap_name][0]
        print(f"{cap_name:<12} {best['rsi']:<6} {best['ratio']*100:>6.0f}% {best['stop']*100:>6.1f}% {best['take']*100:>6.0f}% {best['return_ratio']:>+8.2f}% {best['trades']:>4}회 {best['win_rate']:>6.1f}%")

print()
print("💡 결론")
print("-" * 100)

# 공통점 찾기
all_best = []
for cap_name in ["50만원", "100만원", "500만원", "1000만원"]:
    if cap_name in all_results and all_results[cap_name]:
        all_best.append(all_results[cap_name][0])

if all_best:
    avg_rsi = sum(r['rsi'] for r in all_best) / len(all_best)
    avg_ratio = sum(r['ratio'] for r in all_best) / len(all_best)
    avg_stop = sum(r['stop'] for r in all_best) / len(all_best)
    avg_take = sum(r['take'] for r in all_best) / len(all_best)
    
    print(f"평균 최적값:")
    print(f"  RSI: {avg_rsi:.0f}")
    print(f"  투자비율: {avg_ratio*100:.0f}%")
    print(f"  손절: {avg_stop*100:.1f}%")
    print(f"  익절: {avg_take*100:.0f}%")
    
    print()
    print("✅ 범용 추천 설정:")
    # 가장 안전한 쪽으로
    safe_rsi = min(r['rsi'] for r in all_best)
    safe_ratio = min(r['ratio'] for r in all_best)
    safe_stop = min(r['stop'] for r in all_best)
    safe_take = max(r['take'] for r in all_best)
    
    print(f"  RSI: {safe_rsi} (보수적)")
    print(f"  투자비율: {safe_ratio*100:.0f}% (안전)")
    print(f"  손절: {safe_stop*100:.1f}% (타이트)")
    print(f"  익절: {safe_take*100:.0f}% (여유)")
