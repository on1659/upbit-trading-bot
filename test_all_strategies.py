"""
전략 일괄 테스트
"""
import os
import subprocess
import json

print("=" * 60)
print("📊 전략 일괄 백테스팅 (2025-11-01 ~ 2026-02-17)")
print("=" * 60)
print()

results = []

for strategy_num in range(1, 11):
    print(f"\n{'=' * 60}")
    print(f"전략 #{strategy_num} 테스트 중...")
    print('=' * 60)
    
    # 환경변수로 전략 번호 전달
    env = os.environ.copy()
    env['STRATEGY'] = str(strategy_num)
    
    # 백테스팅 실행
    result = subprocess.run(
        ['python', 'backtest.py'],
        cwd='/Users/radar/Work/upbit-trading-bot',
        env=env,
        capture_output=True,
        text=True
    )
    
    # 출력 파싱
    output = result.stdout
    
    # 결과 추출
    name = ""
    profit = 0
    trades = 0
    win_rate = 0
    
    for line in output.split('\n'):
        if '전략:' in line:
            name = line.split('#')[1].split('\n')[0].strip()
        elif '총 수익:' in line:
            parts = line.split('총 수익: ')[1].split('원')
            profit_str = parts[0].replace(',', '')
            profit = int(profit_str)
            ratio = float(parts[1].split('(')[1].split('%')[0])
        elif '거래 횟수:' in line:
            trades = int(line.split('거래 횟수: ')[1].split('회')[0])
        elif '승률:' in line:
            win_rate_str = line.split('승률: ')[1].split('%')[0]
            win_rate = float(win_rate_str)
    
    results.append({
        'num': strategy_num,
        'name': name,
        'profit': profit,
        'ratio': ratio,
        'trades': trades,
        'win_rate': win_rate
    })
    
    print(output)

# 결과 요약
print("\n\n")
print("=" * 80)
print("📊 전략 성과 랭킹")
print("=" * 80)
print()
print(f"{'#':<3} {'전략명':<25} {'수익률':<10} {'수익':<15} {'거래':<8} {'승률'}")
print("-" * 80)

# 수익률 순 정렬
sorted_results = sorted(results, key=lambda x: x['ratio'], reverse=True)

for r in sorted_results:
    emoji = "🏆" if r['num'] == sorted_results[0]['num'] else "  "
    profit_color = "+" if r['ratio'] > 0 else ""
    print(f"{r['num']:<3} {r['name']:<25} {emoji} {profit_color}{r['ratio']:>6.2f}% {profit_color}{r['profit']:>10,}원 {r['trades']:>5}회 {r['win_rate']:>6.1f}%")

print("\n")
