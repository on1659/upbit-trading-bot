"""
RSI 파라미터 최적화
최근 2개월 데이터로 RSI threshold 변경하면서 테스트
"""
import pyupbit
import pandas as pd
from strategies import Strategy1_MeanReversion
from backtest import Backtester
import config

print("=" * 80)
print("🔬 RSI 파라미터 최적화 (최근 6개월)")
print("=" * 80)
print()

results = []

# RSI 20~60까지 5씩 증가
for rsi_threshold in range(20, 65, 5):
    print(f"\n{'=' * 60}")
    print(f"🎯 RSI < {rsi_threshold} 테스트 중...")
    print('=' * 60)
    
    # 파라미터 설정
    params = config.STRATEGY_PARAMS.copy()
    params['rsi_oversold'] = rsi_threshold
    
    # 전략 생성
    strategy = Strategy1_MeanReversion(params)
    
    # 백테스터
    backtester = Backtester(strategy, initial_balance=1000000)
    
    # 백테스팅 실행
    result = backtester.run(
        ticker="KRW-BTC",
        start_date="20250817",  # 6개월 전
        end_date="20260217",
        interval="day"
    )
    
    if result:
        results.append({
            'rsi': rsi_threshold,
            'profit': result['total_return'],
            'ratio': result['return_ratio'],
            'trades': len([t for t in result['trades'] if t['type'] == 'buy']),
            'win_rate': result['win_rate']
        })

# 결과 정리
print("\n\n")
print("=" * 80)
print("📊 RSI 파라미터 최적화 결과")
print("=" * 80)
print()
print(f"{'RSI':<8} {'수익률':<12} {'수익':<15} {'거래':<8} {'승률':<8} {'평가'}")
print("-" * 80)

sorted_results = sorted(results, key=lambda x: x['ratio'], reverse=True)

for i, r in enumerate(sorted_results):
    emoji = "🏆" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else "  "))
    profit_sign = "+" if r['ratio'] > 0 else ""
    
    # 평가
    if r['trades'] == 0:
        eval_text = "거래 없음"
    elif r['trades'] < 3:
        eval_text = "거래 부족"
    elif r['trades'] > 15:
        eval_text = "과매매"
    else:
        eval_text = "적정"
    
    print(f"< {r['rsi']:<5} {emoji} {profit_sign}{r['ratio']:>7.2f}% {profit_sign}{r['profit']:>12,}원 {r['trades']:>5}회 {r['win_rate']:>6.1f}% {eval_text}")

print("\n")
print("💡 결론")
print("-" * 80)

best = sorted_results[0]
print(f"✅ 최적 RSI: {best['rsi']}")
print(f"   수익률: {best['ratio']:+.2f}%")
print(f"   거래 횟수: {best['trades']}회")
print(f"   승률: {best['win_rate']:.1f}%")

# 거래 빈도 분석
trade_counts = [r['trades'] for r in results]
print(f"\n📊 거래 빈도 분석:")
print(f"   최소: {min(trade_counts)}회 (RSI {[r['rsi'] for r in results if r['trades'] == min(trade_counts)][0]})")
print(f"   최대: {max(trade_counts)}회 (RSI {[r['rsi'] for r in results if r['trades'] == max(trade_counts)][0]})")
print(f"   평균: {sum(trade_counts)/len(trade_counts):.1f}회")
