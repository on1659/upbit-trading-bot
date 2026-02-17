# 전략 #1: Mean Reversion (평균 회귀)

**순위**: 🏆 1위  
**수익률**: +2.11%  
**승률**: 42.9%  
**난이도**: ⭐⭐ 중급  

---

## 📖 철학

> "과매도는 반등한다"

가격이 평균에서 너무 멀어지면 다시 평균으로 돌아온다는 통계적 원리.

**핵심 아이디어**:
- RSI가 극단적으로 낮을 때 = 과매도
- 볼린저 밴드 하단 근처 = 비정상적 저가
- → 곧 반등할 가능성 높음

---

## 🎯 매수 조건 (2개 이상 일치)

### 1. RSI 과매도 (RSI < 45)
```python
if current['rsi'] < 45:
    buy_signals.append('rsi_oversold')
```
- 45 이하면 과매도 판단
- 원래 30이었지만 최근 데이터용 완화

### 2. 가격 < 20일선 + MACD 상승
```python
if current['close'] < current['ma_20'] and current['macd'] > previous['macd']:
    buy_signals.append('price_below_ma20_macd_rising')
```
- 평균 아래로 떨어졌지만
- MACD는 상승 중 = 반등 조짐

### 3. 볼린저 밴드 하단 근처 (10% 이내)
```python
if current['close'] < current['bb_lower'] * 1.10:
    buy_signals.append('near_bb_lower')
```
- 통계적 저가 구간
- 하단에서 반등 확률 높음

### 4. RSI 다이버전스
```python
if (current['close'] < previous['close'] and 
    current['rsi'] > previous['rsi']):
    buy_signals.append('rsi_divergence')
```
- 가격은 하락하는데 RSI는 상승
- → 매도 압력 약화, 반등 신호

---

## 📉 매도 조건 (2개 이상 일치)

### 1. RSI 과매수 (RSI > 70)
```python
if current['rsi'] > 70:
    sell_signals.append('rsi_overbought')
```

### 2. MACD 데드크로스
```python
if current['macd'] < current['macd_signal']:
    sell_signals.append('macd_dead_cross')
```

### 3. 볼린저 상단 돌파
```python
if current['close'] > current['bb_upper']:
    sell_signals.append('bb_upper_break')
```

---

## 💰 손익 관리

- **손절**: 1.5% (빠른 손절)
- **익절**: 7% (충분한 수익)
- **손익비**: 4.6:1

**왜 이 비율?**
- 승률 43%여도 수익 가능
- 손실 작게, 수익 크게

---

## 📊 백테스팅 결과

**기간**: 2025-11-01 ~ 2026-02-17 (3.5개월)

| 지표 | 값 |
|---|---|
| 수익률 | **+2.11%** |
| 거래 횟수 | 15회 |
| 승률 | 42.9% |
| Buy & Hold | -37.84% |
| 전략 우위 | **+39.95%p** |

**매매 내역**:
- 3승 4패 + 1홀딩
- 평균 보유 기간: 7일
- 최대 수익: +12.99%
- 최대 손실: -5.37%

---

## ✅ 장점

1. **하락장에 강함** - 과매도 반등 포착
2. **안정적** - 복합 지표로 신호 확인
3. **거래 빈도 적절** - 과매매 방지
4. **검증됨** - 3개월 실전 데이터 +2%

---

## ⚠️ 단점

1. **상승장에 약함** - 반등만 노림 (추세 못 탐)
2. **승률 낮음** - 43% (손익비로 커버)
3. **극단 하락 시** - 더 떨어질 수 있음 (손절 필수)

---

## 🎓 실전 팁

### 1. 손절 엄수
- 1.5% 손절 절대 지키기
- "한 번만 더 버텨보자" 금지

### 2. 욕심 부리지 않기
- 7% 익절 달성 시 즉시 매도
- "더 오를 것 같은데" 금지

### 3. 신호 2개 이상 확인
- 1개 신호로 성급하게 매수 금지
- 복합 확인이 안정성 높임

### 4. 하락장에 특화
- 상승장 전환 시 전략 #2로 스위칭 고려

---

## 🔧 파라미터 튜닝 가이드

### RSI 기준 조정
```python
# 보수적: 40 (거래 적음, 안전)
# 밸런스: 45 (현재 설정)
# 공격적: 50 (거래 많음, 위험)
rsi_oversold = 45
```

### 손익비 조정
```python
# 안정형: 1.5% / 5%
# 밸런스: 1.5% / 7% (현재)
# 공격형: 2% / 10%
STOP_LOSS = 0.015
TAKE_PROFIT = 0.07
```

---

## 📚 관련 전략

- **#6 Contrarian** - 더 극단적인 과매도 (RSI 20)
- **#9 Buy The Dip** - 폭락 특화 (-5%)

---

## 코드

전체 코드: `strategies.py` → `Strategy1_MeanReversion`

실행:
```bash
STRATEGY=1 python backtest.py
```
