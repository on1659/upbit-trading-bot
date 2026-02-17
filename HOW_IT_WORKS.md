# ⚡ 빠른 테스트의 비밀

## 🤔 질문: "어떻게 10개 전략을 3분만에 테스트했나?"

**답**: 백테스팅 (Backtesting)

---

## 📖 백테스팅이란?

**정의**: 과거 데이터로 전략을 시뮬레이션하는 것

**실제 매매 vs 백테스팅**:

| 구분 | 실제 매매 | 백테스팅 |
|---|---|---|
| 시간 | 3개월 기다림 | **3분** |
| 돈 | 진짜 돈 | 가상 돈 |
| 리스크 | 손실 가능 | 리스크 없음 |
| 데이터 | 미래 (예측) | 과거 (확정) |

---

## 🚀 빠른 이유

### 1. 과거 데이터 사용
```python
# pyupbit API로 과거 데이터 즉시 다운로드
df = pyupbit.get_ohlcv('KRW-BTC', interval='day', to='20260217')
# → 2년치 데이터를 1초만에!
```

- 2024-01-01 ~ 2026-02-17 (2년)
- 일봉: 약 750개 데이터
- 다운로드: **1초**

### 2. 컴퓨터가 순식간에 계산
```python
for i in range(len(df)):  # 750번 반복
    signal = strategy.generate_signal(df)
    # RSI, MACD, 볼린저 계산
    # 매수/매도 판단
    # 손익 계산
# → 1개 전략 백테스트: 약 0.2초
```

- 750일 시뮬레이션 = 0.2초
- 10개 전략 = 2초
- 출력 시간 포함 = **3분**

### 3. 실시간 대기 없음
실제 매매:
```
2025-11-01 → 매수 신호 기다림 → 3일 후 매수
→ 7일 후 익절 → 다시 매수 신호 기다림 → ...
(총 3.5개월 소요)
```

백테스팅:
```python
for day in days:  # 루프 한 번에!
    check_signal()
    execute_trade()
# (0.2초 소요)
```

---

## 🎯 백테스팅 vs 실전

### ✅ 백테스팅 장점
1. **빠름** - 몇 년치를 몇 초에
2. **안전** - 진짜 돈 안 씀
3. **반복** - 파라미터 튜닝 가능
4. **비교** - 여러 전략 동시 테스트

### ⚠️ 백테스팅 한계
1. **과거 ≠ 미래** - 과거 성과가 미래 보장 안 함
2. **슬리피지** - 백테스팅: 정확한 가격 / 실전: 약간 다름
3. **수수료** - 백테스팅에 포함은 하지만 실전엔 변수 많음
4. **심리** - 백테스팅: 감정 없음 / 실전: 공포/욕심

---

## 🔬 우리가 한 과정

### 1단계: 데이터 수집 (1초)
```python
df = pyupbit.get_ohlcv('KRW-BTC', interval='day')
# 2025-11-01 ~ 2026-02-17
# 105일 데이터
```

### 2단계: 지표 계산 (0.1초)
```python
df['rsi'] = RSIIndicator(...).rsi()
df['macd'] = MACD(...).macd()
df['bb_lower'] = BollingerBands(...).bollinger_lband()
# RSI, MACD, 볼린저, 이동평균 계산
```

### 3단계: 시뮬레이션 (0.1초)
```python
for i in range(len(df)):
    signal = strategy.generate_signal(df.iloc[:i+1])
    
    if signal == 'buy' and no_position:
        buy(current_price)
    
    if position:
        if profit >= 7%:
            sell(current_price)  # 익절
        elif loss >= 1.5%:
            sell(current_price)  # 손절
```

### 4단계: 결과 출력
```
수익률: +2.11%
거래 횟수: 15회
승률: 42.9%
```

**총 소요 시간: 0.3초 per 전략**

---

## 💡 실제 코드 예시

### 가상 시뮬레이션
```python
class Backtester:
    def __init__(self, strategy, initial_balance=1000000):
        self.balance = initial_balance  # 가상 100만원
        self.position = None
        
    def run(self, ticker, start_date, end_date):
        # 1. 과거 데이터 가져오기
        df = pyupbit.get_ohlcv(ticker, to=end_date)
        df = df[start_date:end_date]
        
        # 2. 지표 계산
        df = self.strategy.calculate_indicators(df)
        
        # 3. 시뮬레이션
        for i in range(len(df)):
            current_price = df.iloc[i]['close']
            signal = self.strategy.generate_signal(df.iloc[:i+1])
            
            # 매수
            if signal == 'buy' and self.position is None:
                self.position = self.balance * 0.1 / current_price
                self.balance -= self.balance * 0.1
                print(f"📈 매수: {current_price:,.0f}원")
            
            # 손절/익절
            if self.position:
                profit_ratio = (current_price - entry_price) / entry_price
                
                if profit_ratio >= 0.07:  # 익절 7%
                    self.balance += self.position * current_price
                    print(f"🔺 익절: +{profit_ratio*100:.2f}%")
                    self.position = None
                
                elif profit_ratio <= -0.015:  # 손절 1.5%
                    self.balance += self.position * current_price
                    print(f"🔻 손절: {profit_ratio*100:.2f}%")
                    self.position = None
```

---

## 🎓 핵심 정리

### Q: 왜 이렇게 빨랐나?
**A**: 과거 데이터로 시뮬레이션했기 때문 (실제 매매 안 함)

### Q: 백테스팅 결과 믿어도 되나?
**A**: 참고용. 실전에선 슬리피지/수수료/심리 변수 있음

### Q: 실전과 차이는?
**A**: 
- 백테스팅: 과거 정답 보고 계산 (빠름, 정확)
- 실전: 미래 예측하며 매매 (느림, 불확실)

### Q: 다음 단계는?
**A**: 
1. 백테스팅으로 전략 검증 ✅ (완료)
2. 소액 실전 테스트 (10만원)
3. 1개월 검증
4. 자금 증액

---

## 📊 비유

**백테스팅** = 녹화 영상 돌려보기 (빠름)
- 과거 3개월치 녹화본을 빨리감기로 3분에 시청

**실전 매매** = 라이브 방송 (느림)
- 3개월 동안 실시간으로 지켜봐야 함

---

## 🚀 기술 스택

우리가 사용한 도구들:

1. **pyupbit** - 업비트 API 라이브러리 (과거 데이터 다운로드)
2. **pandas** - 데이터 처리 (표 계산)
3. **ta** - 기술적 지표 계산 (RSI, MACD, 볼린저)
4. **Python** - 빠른 계산 (초당 수천 번 시뮬레이션)

```bash
# 설치
pip install pyupbit pandas ta

# 실행 (0.3초)
python backtest.py
```

---

## 💪 이제 알았죠?

**백테스팅 = 타임머신**
- 과거로 돌아가서 전략 시험
- 돈 안 쓰고 빠르게 검증
- 실전 전에 필수!

**하지만 기억하세요**:
> "과거 성과가 미래 수익을 보장하지 않습니다"

그래도 아무것도 안 하는 것보단 훨씬 낫죠! 🎯
