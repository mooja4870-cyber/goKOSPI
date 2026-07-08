import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta

def compute_features(df):
    """
    10개 이상의 기술적 지표(Feature)를 계산하여 데이터프레임에 추가합니다.
    """
    df = df.copy()
    
    # 1. 이동평균선 (MA5, MA20, MA60)
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()
    
    # 2. 이격도 (Disparity)
    df['Disp5'] = df['Close'] / df['MA5']
    df['Disp20'] = df['Close'] / df['MA20']
    
    # 3. 거래량 지표
    df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
    df['Vol_Ratio'] = df['Volume'] / df['Vol_MA20'].replace(0, np.nan)
    
    # 4. 일일 수익률 및 변동성
    df['Daily_Return'] = df['Close'].pct_change()
    df['Volatility'] = df['Daily_Return'].rolling(window=20).std()
    
    # 5. Z-Score (과열/침체 지표)
    std20 = df['Close'].rolling(window=20).std()
    df['Z_Score'] = (df['Close'] - df['MA20']) / std20.replace(0, np.nan)
    
    # 6. 볼린저 밴드 (Upper, Lower, Width)
    df['BB_Upper'] = df['MA20'] + 2 * std20
    df['BB_Lower'] = df['MA20'] - 2 * std20
    df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['MA20']
    
    # 7. 모멘텀 (Momentum) 10일
    df['Momentum'] = df['Close'] - df['Close'].shift(10)
    
    # 8. RSI (Relative Strength Index) 14일
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, np.nan)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 결측치 처리 (최초 N일간의 데이터는 지표 계산이 안되므로 삭제)
    df = df.dropna()
    return df

def run_prediction(ticker, horizon_days=5):
    """
    주어진 종목에 대해 회귀 분석을 수행하고 예측 결과를 반환합니다.
    - horizon_days: 예측 목표 시점 (기본값 5영업일 = 1주일)
    """
    # 1. 데이터 로드 (최소 2년)
    ticker_obj = yf.Ticker(ticker)
    df = ticker_obj.history(period="2y")
    
    if len(df) < 100:
        return {"success": False, "error": "데이터가 부족하여 예측할 수 없습니다."}
    
    df = compute_features(df)
    
    # 입력 Feature 목록 (10개 이상)
    features = [
        'MA5', 'MA20', 'MA60', 'Disp5', 'Disp20', 
        'Vol_Ratio', 'Volatility', 'Z_Score', 
        'BB_Width', 'Momentum', 'RSI'
    ]
    
    # 2. 미래 가격 예측 모델링 (Target: N일 뒤 종가)
    # df['Target']은 현재 행의 시점으로부터 horizon_days 이후의 종가
    df['Target'] = df['Close'].shift(-horizon_days)
    
    # 모델 학습을 위해 Target이 존재하는 데이터만 사용
    train_df = df.dropna(subset=['Target']).copy()
    
    if len(train_df) < 50:
        return {"success": False, "error": "학습 데이터가 부족합니다."}
        
    # --- Rolling Window 기반 동적 리밸런싱 (최근 120 영업일) ---
    if len(train_df) > 120:
        X_train = train_df[features].iloc[-120:]
        y_train = train_df['Target'].iloc[-120:]
    else:
        X_train = train_df[features]
        y_train = train_df['Target']
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # ElasticNet Regression 사용 (L1+L2 정규화 기반 동적 가중치 할당)
    model = ElasticNet(alpha=0.1, l1_ratio=0.5)
    model.fit(X_train_scaled, y_train)
    
    # --- A. 현재 시점에서 미래 가격 예측 ---
    # 가장 마지막 행 (오늘 데이터)
    current_row = df.iloc[-1:]
    current_date = current_row.index[0]
    current_price = current_row['Close'].values[0]
    
    X_current = current_row[features]
    X_current_scaled = scaler.transform(X_current)
    predicted_future_price = model.predict(X_current_scaled)[0]
    
    future_date = current_date + timedelta(days=int(horizon_days * 1.4)) # 대략적 영업일 환산 (주말 포함)
    
    # --- B. 과거 예측의 다중 백테스트 (오늘을 예측했던 과거 시점들 평가) ---
    backtest_list = []
    for h in [1, 3, 7, 15, 30, 90]:
        if len(df) > h + 50:
            df_h = df.copy()
            df_h['Target_h'] = df_h['Close'].shift(-h)
            train_df_h = df_h.dropna(subset=['Target_h']).copy()
            if len(train_df_h) < 50:
                continue
                
            if len(train_df_h) > 120:
                X_train_h = train_df_h[features].iloc[-120:]
                y_train_h = train_df_h['Target_h'].iloc[-120:]
            else:
                X_train_h = train_df_h[features]
                y_train_h = train_df_h['Target_h']
                
            scaler_h = StandardScaler()
            X_train_scaled_h = scaler_h.fit_transform(X_train_h)
            model_h = ElasticNet(alpha=0.1, l1_ratio=0.5)
            model_h.fit(X_train_scaled_h, y_train_h)
            
            past_idx = -1 - h
            past_row = df_h.iloc[[past_idx]]
            past_date = past_row.index[0]
            past_price = past_row['Close'].values[0]
            
            X_past_h = past_row[features]
            X_past_scaled_h = scaler_h.transform(X_past_h)
            past_predicted_price = model_h.predict(X_past_scaled_h)[0]
            
            actual_today_price = current_price
            error_pct = abs(actual_today_price - past_predicted_price) / actual_today_price * 100
            accuracy = max(0, 100 - error_pct)
            
            backtest_list.append({
                "days_ago": h,
                "past_date": past_date.strftime('%Y-%m-%d'),
                "past_price": float(past_price),
                "predicted_today_price": float(past_predicted_price),
                "actual_today_price": float(actual_today_price),
                "accuracy": float(accuracy)
            })
    
    return {
        "success": True,
        "ticker": ticker,
        "current_date": current_date.strftime('%Y-%m-%d'),
        "current_price": float(current_price),
        "future_date": future_date.strftime('%Y-%m-%d'),
        "horizon_days": horizon_days,
        "predicted_future_price": float(predicted_future_price),
        "expected_return_pct": float((predicted_future_price - current_price) / current_price * 100),
        "backtest_list": backtest_list,
        "features_used": features
    }

if __name__ == "__main__":
    # Test
    res = run_prediction("005930.KS")
    import json
    print(json.dumps(res, indent=2, ensure_ascii=False))
