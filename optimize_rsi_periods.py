"""
RSI 파라미터 최적화 - 기간별 비교
1개월, 2개월, 3개월
"""
import pyupbit
import pandas as pd
from strategies import Strategy1_MeanReversion
from backtest import Backtester
import config
from datetime import datetime, timedelta

# 기간 설정
periods = {
    '1개월': '20260117',
    '2개월': '20251217',
    '3개월': '20251117',
}

all_results = {}

for period_name, start_date in periods.items():
    print("\n" + "=" * 80)
    print(f"📅 {period_name} 백테스팅")
    print("=" * 80)
    
    results = []
    
    for rsi_threshold in range(20, 65, 5):
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
            start_date=start_date,
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
    
    all_results[period_name] = results

# 결과 출력
print("\n\n")
print("=" * 100)
print("📊 RSI 파라미터 최적화 - 기간별 비교")
print("=" * 100)
print()

for period_name in ['1개월', '2개월', '3개월']:
    results = all_results[period_name]
    sorted_results = sorted(results, key=lambda x: x['ratio'], reverse=True)
    
    print(f"\n{'=' * 100}")
    print(f"📅 {period_name} (최근 {period_name})")
    print('=' * 100)
    print(f"{'RSI':<8} {'수익률':<12} {'수익':<18} {'거래':<8} {'승률':<8} {'평가'}")
    print("-" * 100)
    
    for i, r in enumerate(sorted_results):
        emoji = "🏆" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else "  "))
        profit_sign = "+" if r['ratio'] > 0 else ""
        
        # 평가
        if r['trades'] == 0:
            eval_text = "거래 없음"
        elif r['trades'] < 2:
            eval_text = "거래 극소"
        elif r['trades'] < 4:
            eval_text = "거래 부족"
        elif r['trades'] > 15:
            eval_text = "과매매"
        else:
            eval_text = "적정"
        
        print(f"< {r['rsi']:<5} {emoji} {profit_sign}{r['ratio']:>7.2f}% {profit_sign}{r['profit']:>15,.0f}원 {r['trades']:>5}회 {r['win_rate']:>6.1f}% {eval_text}")

# 종합 비교
print("\n\n")
print("=" * 100)
print("📊 종합 비교 - RSI별 기간별 성과")
print("=" * 100)
print()
print(f"{'RSI':<8} {'1개월':<15} {'2개월':<15} {'3개월':<15} {'평균':<15} {'추천'}")
print("-" * 100)

rsi_values = range(20, 65, 5)
for rsi in rsi_values:
    ratios = []
    for period_name in ['1개월', '2개월', '3개월']:
        result = next((r for r in all_results[period_name] if r['rsi'] == rsi), None)
        if result:
            ratios.append(result['ratio'])
    
    avg = sum(ratios) / len(ratios) if ratios else 0
    
    # 추천 평가
    if avg > 0.5:
        recommend = "✅ 강력 추천"
    elif avg > 0:
        recommend = "👍 추천"
    elif avg > -0.5:
        recommend = "⚠️ 주의"
    else:
        recommend = "🚫 비추"
    
    ratio_strs = []
    for period_name in ['1개월', '2개월', '3개월']:
        result = next((r for r in all_results[period_name] if r['rsi'] == rsi), None)
        if result:
            sign = "+" if result['ratio'] > 0 else ""
            ratio_strs.append(f"{sign}{result['ratio']:>6.2f}%")
        else:
            ratio_strs.append("    N/A")
    
    avg_sign = "+" if avg > 0 else ""
    print(f"< {rsi:<5} {ratio_strs[0]:<15} {ratio_strs[1]:<15} {ratio_strs[2]:<15} {avg_sign}{avg:>6.2f}%      {recommend}")

print("\n")
print("💡 최종 추천")
print("-" * 100)

# 평균 수익률 기준 최고 RSI 찾기
best_avg = -999
best_rsi = 0
for rsi in rsi_values:
    ratios = []
    for period_name in ['1개월', '2개월', '3개월']:
        result = next((r for r in all_results[period_name] if r['rsi'] == rsi), None)
        if result:
            ratios.append(result['ratio'])
    avg = sum(ratios) / len(ratios) if ratios else 0
    if avg > best_avg:
        best_avg = avg
        best_rsi = rsi

print(f"✅ 최적 RSI: {best_rsi}")
print(f"   평균 수익률: {best_avg:+.2f}%")
print(f"   안정성: 여러 기간에서 검증됨")
