"""
최적화 결과 시각화
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터
labels = ['RSI', '투자비율\n(%)', '손절\n(%)', '익절\n(%)', '수익률\n(%)']
delta_br = [20, 20, 1.0, 10, 4.38]
repeat_10 = [30, 10, 1.5, 7, 1.85]

# 정규화를 위한 최대값
max_values = [40, 20, 2.0, 10, 5]

# 정규화
delta_br_norm = [d/m for d, m in zip(delta_br, max_values)]
repeat_10_norm = [r/m for r, m in zip(repeat_10, max_values)]

# 그래프 생성
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('📊 파라미터 최적화 비교 (델타-브래빅 vs 10회 반복)', fontsize=16, fontweight='bold')

# 1. 레이더 차트
ax1 = plt.subplot(221, projection='polar')
angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
delta_br_norm += delta_br_norm[:1]
repeat_10_norm += repeat_10_norm[:1]
angles += angles[:1]

ax1.plot(angles, delta_br_norm, 'o-', linewidth=2, label='델타-브래빅 (1회)', color='#FF6B6B')
ax1.fill(angles, delta_br_norm, alpha=0.25, color='#FF6B6B')
ax1.plot(angles, repeat_10_norm, 'o-', linewidth=2, label='10회 반복 평균', color='#4ECDC4')
ax1.fill(angles, repeat_10_norm, alpha=0.25, color='#4ECDC4')
ax1.set_xticks(angles[:-1])
ax1.set_xticklabels(labels)
ax1.set_ylim(0, 1)
ax1.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
ax1.set_title('정규화 비교 (레이더)', pad=20)
ax1.grid(True)

# 2. 막대 그래프 (파라미터)
ax2 = axes[0, 1]
x = np.arange(4)
width = 0.35
params_delta = [20, 20, 1.0, 10]
params_repeat = [30, 10, 1.5, 7]
param_labels = ['RSI', '투자비율', '손절', '익절']

bars1 = ax2.bar(x - width/2, params_delta, width, label='델타-브래빅', color='#FF6B6B', alpha=0.8)
bars2 = ax2.bar(x + width/2, params_repeat, width, label='10회 반복', color='#4ECDC4', alpha=0.8)

ax2.set_ylabel('값')
ax2.set_title('파라미터 비교')
ax2.set_xticks(x)
ax2.set_xticklabels(param_labels)
ax2.legend()
ax2.grid(axis='y', alpha=0.3)

# 값 표시
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=9)

# 3. 수익률 비교
ax3 = axes[1, 0]
methods = ['델타-브래빅\n(1회)', '10회 반복\n평균']
profits = [4.38, 1.85]
colors = ['#FF6B6B', '#4ECDC4']

bars = ax3.bar(methods, profits, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax3.set_ylabel('수익률 (%)')
ax3.set_title('수익률 비교')
ax3.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax3.grid(axis='y', alpha=0.3)

# 값 표시
for bar, profit in zip(bars, profits):
    ax3.text(bar.get_x() + bar.get_width()/2., profit,
            f'+{profit:.2f}%',
            ha='center', va='bottom' if profit > 0 else 'top',
            fontsize=12, fontweight='bold')

# 4. 리스크:리워드 비율
ax4 = axes[1, 1]
risk_reward_delta = 10 / 1.0  # 익절/손절
risk_reward_repeat = 7 / 1.5

bars = ax4.bar(methods, [risk_reward_delta, risk_reward_repeat], 
               color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax4.set_ylabel('리스크:리워드 비율')
ax4.set_title('리스크:리워드 비율 (익절/손절)')
ax4.grid(axis='y', alpha=0.3)

# 값 표시
for bar, rr in zip(bars, [risk_reward_delta, risk_reward_repeat]):
    ax4.text(bar.get_x() + bar.get_width()/2., rr,
            f'1:{rr:.1f}',
            ha='center', va='bottom',
            fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('/Users/radar/Work/upbit-trading-bot/optimization_comparison.png', dpi=150, bbox_inches='tight')
print("✅ 그래프 저장: optimization_comparison.png")

# 자본별 최적 파라미터 비교 그래프
fig2, axes2 = plt.subplots(2, 2, figsize=(14, 10))
fig2.suptitle('💰 자본금별 최적 파라미터 (10회 반복 마지막 결과)', fontsize=16, fontweight='bold')

capitals = ['50만원', '500만원', '1000만원']
rsi_values = [20, 30, 30]
ratio_values = [10, 15, 10]
profit_values = [2.01, 2.13, 1.42]
trades = [3, 6, 6]

# RSI
ax1 = axes2[0, 0]
bars = ax1.bar(capitals, rsi_values, color='#95E1D3', edgecolor='black', linewidth=1.5)
ax1.set_ylabel('RSI 임계값')
ax1.set_title('최적 RSI 값')
ax1.grid(axis='y', alpha=0.3)
for bar, val in zip(bars, rsi_values):
    ax1.text(bar.get_x() + bar.get_width()/2., val, f'{val}',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

# 투자비율
ax2 = axes2[0, 1]
bars = ax2.bar(capitals, ratio_values, color='#F38181', edgecolor='black', linewidth=1.5)
ax2.set_ylabel('투자비율 (%)')
ax2.set_title('최적 투자비율')
ax2.grid(axis='y', alpha=0.3)
for bar, val in zip(bars, ratio_values):
    ax2.text(bar.get_x() + bar.get_width()/2., val, f'{val}%',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

# 수익률
ax3 = axes2[1, 0]
bars = ax3.bar(capitals, profit_values, color='#FFEAA7', edgecolor='black', linewidth=1.5)
ax3.set_ylabel('수익률 (%)')
ax3.set_title('백테스트 수익률')
ax3.grid(axis='y', alpha=0.3)
for bar, val in zip(bars, profit_values):
    ax3.text(bar.get_x() + bar.get_width()/2., val, f'+{val:.2f}%',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

# 거래횟수
ax4 = axes2[1, 1]
bars = ax4.bar(capitals, trades, color='#A29BFE', edgecolor='black', linewidth=1.5)
ax4.set_ylabel('거래 횟수')
ax4.set_title('총 거래 횟수')
ax4.grid(axis='y', alpha=0.3)
for bar, val in zip(bars, trades):
    ax4.text(bar.get_x() + bar.get_width()/2., val, f'{val}회',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('/Users/radar/Work/upbit-trading-bot/capital_comparison.png', dpi=150, bbox_inches='tight')
print("✅ 그래프 저장: capital_comparison.png")

print("\n📈 2개 그래프 생성 완료!")
