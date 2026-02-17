"""
포지션 보유 기간 분석
"""
from strategies import Strategy1_MeanReversion
from backtest import Backtester
import config
from datetime import datetime

print("=" * 80)
print("⏱️  포지션 보유 기간 분석 (RSI 30, 최근 3개월)")
print("=" * 80)
print()

# RSI 30 전략
params = config.STRATEGY_PARAMS.copy()
params['rsi_oversold'] = 30

strategy = Strategy1_MeanReversion(params)
backtester = Backtester(strategy, initial_balance=1000000)

# 백테스팅 실행
result = backtester.run(
    ticker="KRW-BTC",
    start_date="20251117",
    end_date="20260217",
    interval="day"
)

if result and result['trades']:
    trades = result['trades']
    
    # 매수/매도 페어 찾기
    holdings = []
    current_buy = None
    
    for trade in trades:
        if trade['type'] == 'buy':
            current_buy = trade
        elif trade['type'] in ['sell', 'stop_loss', 'take_profit'] and current_buy:
            buy_date = current_buy['date']
            sell_date = trade['date']
            days = (sell_date - buy_date).days
            profit = trade['profit']
            profit_ratio = trade['profit_ratio']
            
            holdings.append({
                'buy_date': buy_date,
                'sell_date': sell_date,
                'days': days,
                'profit': profit,
                'profit_ratio': profit_ratio,
                'type': trade['type']
            })
            
            current_buy = None
    
    # 현재 보유 중인 포지션
    if current_buy:
        buy_date = current_buy['date']
        sell_date = datetime.now()
        days = (sell_date - buy_date).days
        
        holdings.append({
            'buy_date': buy_date,
            'sell_date': '보유중',
            'days': days,
            'profit': 0,
            'profit_ratio': 0,
            'type': 'holding'
        })
    
    # 결과 출력
    print(f"총 {len(holdings)}건의 거래")
    print()
    print(f"{'#':<4} {'매수일':<12} {'매도일':<12} {'보유기간':<10} {'수익률':<12} {'유형'}")
    print("-" * 80)
    
    for i, h in enumerate(holdings, 1):
        buy_str = h['buy_date'].strftime('%Y-%m-%d')
        sell_str = h['sell_date'].strftime('%Y-%m-%d') if h['sell_date'] != '보유중' else '보유중      '
        days_str = f"{h['days']}일"
        profit_str = f"{h['profit_ratio']*100:+.2f}%" if h['type'] != 'holding' else "미실현"
        
        type_emoji = {
            'take_profit': '🔺 익절',
            'stop_loss': '🔻 손절',
            'sell': '📉 매도',
            'holding': '💎 보유중'
        }
        
        print(f"{i:<4} {buy_str:<12} {sell_str:<12} {days_str:<10} {profit_str:<12} {type_emoji.get(h['type'], '')}")
    
    # 통계
    print()
    print("=" * 80)
    print("📊 통계")
    print("=" * 80)
    
    completed = [h for h in holdings if h['type'] != 'holding']
    
    if completed:
        avg_days = sum(h['days'] for h in completed) / len(completed)
        max_holding = max(completed, key=lambda x: x['days'])
        min_holding = min(completed, key=lambda x: x['days'])
        
        print(f"평균 보유 기간: {avg_days:.1f}일")
        print(f"최장 보유: {max_holding['days']}일 ({max_holding['buy_date'].strftime('%Y-%m-%d')} ~ {max_holding['sell_date'].strftime('%Y-%m-%d')}, {max_holding['profit_ratio']*100:+.2f}%)")
        print(f"최단 보유: {min_holding['days']}일 ({min_holding['buy_date'].strftime('%Y-%m-%d')} ~ {min_holding['sell_date'].strftime('%Y-%m-%d')}, {min_holding['profit_ratio']*100:+.2f}%)")
        
        # 익절 vs 손절 평균 보유 기간
        profit_trades = [h for h in completed if h['profit'] > 0]
        loss_trades = [h for h in completed if h['profit'] < 0]
        
        if profit_trades:
            avg_profit_days = sum(h['days'] for h in profit_trades) / len(profit_trades)
            print(f"\n익절 평균 보유: {avg_profit_days:.1f}일 ({len(profit_trades)}건)")
        
        if loss_trades:
            avg_loss_days = sum(h['days'] for h in loss_trades) / len(loss_trades)
            print(f"손절 평균 보유: {avg_loss_days:.1f}일 ({len(loss_trades)}건)")
        
        # 보유 기간별 분포
        print()
        print("보유 기간별 분포:")
        ranges = [
            ("1일", 0, 1),
            ("2-3일", 2, 3),
            ("4-7일", 4, 7),
            ("8-14일", 8, 14),
            ("15일+", 15, 999)
        ]
        
        for label, min_d, max_d in ranges:
            count = len([h for h in completed if min_d <= h['days'] <= max_d])
            if count > 0:
                pct = count / len(completed) * 100
                print(f"  {label}: {count}건 ({pct:.1f}%)")

else:
    print("거래 데이터가 없습니다.")
