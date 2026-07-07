import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, Any

def calculate_atr(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    최근 20일 이동평균 ATR(Average True Range)을 계산합니다.
    """
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    # PrevClose가 필요하므로 shift
    prev_close = close.shift(1)
    
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    
    # 세 변동 범위 중 최댓값 구함
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # 20일 단순 이동평균(SMA)으로 ATR 계산
    atr = tr.rolling(window=period).mean()
    return atr

def classify_signal_7stage(z_score: float) -> str:
    """
    Z-Score 값을 7단계 투자 신호로 분류합니다.
    
    단계 정의:
      STRONG_SELL    : Z >=  2.5  → 강력매도
      OVERHEAT       : Z >=  1.8  → 익절권장
      CAUTION        : Z >=  1.0  → 경계관망
      HOLD           : -1.0 < Z < 1.0 → 중립대기
      MILD_BUY       : Z <= -1.0  → 관심매집
      BUY            : Z <= -1.8  → 매수시그널
      STRONG_BUY     : Z <= -2.5  → 강력매수
    """
    if z_score >= 2.5:
        return 'STRONG_SELL'
    elif z_score >= 1.8:
        return 'OVERHEAT'
    elif z_score >= 1.0:
        return 'CAUTION'
    elif z_score <= -2.5:
        return 'STRONG_BUY'
    elif z_score <= -1.8:
        return 'BUY'
    elif z_score <= -1.0:
        return 'MILD_BUY'
    else:
        return 'HOLD'

def calculate_rebalancing_signals(df: pd.DataFrame, threshold_z: float = 2.5) -> pd.DataFrame:
    """
    주어진 가격 데이터를 바탕으로 누적 변동성 스코어 및 7단계 신호를 계산합니다.
    """
    df = df.copy()
    
    # 1. 일일 수익률 계산
    df['Return'] = df['Close'].pct_change()
    
    # 2. 3일 시간 가중 누적 수익률 스코어 (Sc)
    # Sc = R_t + R_{t-1} * 0.8 + R_{t-2} * 0.6
    df['Sc'] = df['Return'] + df['Return'].shift(1) * 0.8 + df['Return'].shift(2) * 0.6
    
    # 3. 20일 ATR 및 ATR 비율
    df['ATR_20'] = calculate_atr(df, period=20)
    df['ATR_Ratio'] = df['ATR_20'] / df['Close']
    
    # 4. 변동성 대비 최근 상승률 배율 (Z-Score)
    df['Z_Score'] = df['Sc'] / df['ATR_Ratio'].replace(0, np.nan)
    
    # 5. 7단계 신호 분류 (ATR 계산 대기 행은 HOLD 처리)
    df['Signal'] = 'HOLD'
    df['Peak_Close'] = df['Close']
    
    for i in range(len(df)):
        if i < 20:  # ATR 20일 계산 대기
            continue
        z = df.loc[df.index[i], 'Z_Score']
        if pd.isna(z):
            continue
        df.loc[df.index[i], 'Signal'] = classify_signal_7stage(z)
    
    return df

# 7단계 신호 → 화면 뱃지 레이블 & 색상 매핑
SIGNAL_META = {
    'STRONG_SELL': {'label': '🔴 강력매도',  'badge': 'strong-sell'},
    'OVERHEAT':    {'label': '🟠 익절권장',   'badge': 'overheat'},
    'CAUTION':     {'label': '🟡 경계관망',   'badge': 'caution'},
    'HOLD':        {'label': '⚪ 중립대기',   'badge': 'hold'},
    'MILD_BUY':    {'label': '🩵 관심매집',   'badge': 'mild-buy'},
    'BUY':         {'label': '🟢 매수시그널', 'badge': 'buy'},
    'STRONG_BUY':  {'label': '💚 강력매수',   'badge': 'strong-buy'},
}

def analyze_last_signal(df: pd.DataFrame, ticker: str, threshold_z: float = 2.5) -> Dict[str, Any]:
    """
    해당 종목의 가장 최근 날짜의 지표와 신호를 분석하여 딕셔너리로 반환합니다.
    """
    if len(df) < 22:
        return {
            "ticker": ticker,
            "status": "INSUFFICIENT_DATA",
            "signal": "HOLD",
            "message": "데이터 분석에 필요한 영업일(최소 22일)이 부족합니다."
        }
        
    df_analyzed = calculate_rebalancing_signals(df, threshold_z)
    last_row = df_analyzed.iloc[-1]
    prev_row = df_analyzed.iloc[-2]
    
    # 거래량 가중 분석 (수급 필터 대안)
    # 최근 5일 평균 거래량 대비 당일 거래량
    avg_vol = df['Volume'].rolling(window=20).mean().iloc[-1]
    curr_vol = last_row['Volume']
    vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 1.0
    
    signal = last_row['Signal']
    # 직전 상태에서 변경되었는지 파악
    is_new_signal = (signal != prev_row['Signal'])
    
    # 리밸런싱 완료 단계에서 최고가와 하락폭 계산
    drawdown = 0.0
    peak_close = last_row['Peak_Close']
    if peak_close > 0:
        drawdown = (peak_close - last_row['Close']) / peak_close
        
    return {
        "ticker": ticker,
        "date": df_analyzed.index[-1].strftime("%Y-%m-%d"),
        "close": float(last_row['Close']),
        "change_pct": float(last_row['Return'] * 100),
        "sc_pct": float(last_row['Sc'] * 100),
        "z_score": float(last_row['Z_Score']),
        "vol_ratio": float(vol_ratio),
        "signal": signal,
        "is_new": is_new_signal,
        "drawdown_pct": float(drawdown * 100),
        "peak_close": float(peak_close)
    }
