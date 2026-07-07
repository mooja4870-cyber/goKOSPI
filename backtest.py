import pandas as pd
import numpy as np
from typing import Dict, List, Any
from collector import TICKERS, fetch_market_data, get_ticker_name
from engine import calculate_rebalancing_signals

def run_backtest_for_ticker(ticker: str, df: pd.DataFrame, threshold_z: float = 2.5) -> Dict[str, Any]:
    """
    단일 종목에 대해 과거 데이터를 바탕으로 리밸런싱 전략의 승률과 수익률을 계산합니다.
    """
    if len(df) < 50:
        return {"success": False, "reason": "데이터가 부족합니다."}
        
    # 지표 및 신호 시뮬레이션 계산
    df_signals = calculate_rebalancing_signals(df, threshold_z)
    
    overheat_signals = df_signals[df_signals['Signal'] == 'OVERHEAT']
    rebalanced_signals = df_signals[df_signals['Signal'] == 'REBALANCED']
    
    # 1. 과열 신호 검증 (5일 이내 하락 조정 발생률)
    overheat_hits = 0
    overheat_total = 0
    for idx in overheat_signals.index:
        pos = df_signals.index.get_loc(idx)
        if pos + 5 < len(df_signals):
            signal_close = df_signals.loc[idx, 'Close']
            # t+1 ~ t+5 영업일의 최저가 확인
            forward_prices = df_signals['Close'].iloc[pos+1 : pos+6]
            min_forward = forward_prices.min()
            
            # 신호 시점 종가 대비 하락(조정)했으면 성공
            if min_forward < signal_close:
                overheat_hits += 1
            overheat_total += 1
            
    # 2. 리밸런싱 완료 신호 검증 (5일 이내 반등 발생률)
    rebalance_hits = 0
    rebalance_total = 0
    for idx in rebalanced_signals.index:
        pos = df_signals.index.get_loc(idx)
        if pos + 5 < len(df_signals):
            signal_close = df_signals.loc[idx, 'Close']
            # t+1 ~ t+5 영업일의 최고가 확인
            forward_prices = df_signals['Close'].iloc[pos+1 : pos+6]
            max_forward = forward_prices.max()
            
            # 신호 시점 종가 대비 상승했으면 성공
            if max_forward > signal_close:
                rebalance_hits += 1
            rebalance_total += 1
            
    # 3. 모의 매매 수익률 시뮬레이션
    # 초기 상태: 100% 종목 보유 (시작 자산 = 1.0)
    position = 1.0  # 1.0이면 주식 보유, 0.0이면 현금 보유
    cash = 0.0
    asset = 1.0
    
    # 단순 홀딩(Buy & Hold) 수익률
    bh_return = (df_signals['Close'].iloc[-1] - df_signals['Close'].iloc[0]) / df_signals['Close'].iloc[0]
    
    start_close = df_signals['Close'].iloc[0]
    shares = 1.0 / start_close
    
    for i in range(1, len(df_signals)):
        close_price = df_signals['Close'].iloc[i]
        signal = df_signals['Signal'].iloc[i]
        
        # 과열 감지 시 매도 (현금화)
        if signal == 'OVERHEAT' and position > 0:
            cash = shares * close_price
            shares = 0.0
            position = 0.0
            
        # 조정 완료 감지 시 매수 (주식화)
        elif signal == 'REBALANCED' and position == 0:
            shares = cash / close_price
            cash = 0.0
            position = 1.0
            
    # 최종 평가 금액 계산
    final_close = df_signals['Close'].iloc[-1]
    final_asset = (shares * final_close) + cash
    strategy_return = final_asset - 1.0
    
    overheat_win_rate = (overheat_hits / overheat_total) if overheat_total > 0 else 1.0
    rebalance_win_rate = (rebalance_hits / rebalance_total) if rebalance_total > 0 else 1.0
    
    total_signals = overheat_total + rebalance_total
    overall_win_rate = ((overheat_hits + rebalance_hits) / total_signals) if total_signals > 0 else 1.0
    
    return {
        "success": True,
        "ticker": ticker,
        "name": get_ticker_name(ticker),
        "total_signals": total_signals,
        "overheat_signals": overheat_total,
        "rebalance_signals": rebalance_total,
        "overheat_win_rate": overheat_win_rate,
        "rebalance_win_rate": rebalance_win_rate,
        "overall_win_rate": overall_win_rate,
        "buy_and_hold_return": bh_return * 100,
        "strategy_return": strategy_return * 100,
        "outperformance": (strategy_return - bh_return) * 100
    }

def run_global_backtest(market_data: Dict[str, pd.DataFrame], threshold_z: float = 2.5) -> None:
    """
    수집된 전체 종목 데이터를 대상으로 백테스트를 일괄 실행하여 요약 보고서를 출력합니다.
    """
    print("\n" + "="*80)
    print("                      [goKOSPI 백테스트 통합 시뮬레이션]")
    print("="*80)
    
    results = []
    for ticker, df in market_data.items():
        res = run_backtest_for_ticker(ticker, df, threshold_z)
        if res.get("success"):
            results.append(res)
            
    if not results:
        print("[!] 백테스트를 실행할 수 있는 유효한 데이터가 없습니다.")
        return
        
    # 결과 정렬 (초과 수익률 기준 내림차순)
    results = sorted(results, key=lambda x: x["outperformance"], reverse=True)
    
    print(f"{'종목명 (코드)':<18} | {'신호수':<5} | {'전체승률':<8} | {'과열승률':<8} | {'조정승률':<8} | {'단순보유':<9} | {'전략수익':<9} | {'초과수익':<9}")
    print("-"*100)
    
    total_signals = 0
    win_rates = []
    strategy_returns = []
    bh_returns = []
    outperformances = []
    
    for r in results:
        # 주요 15개 종목만 표에 상세히 노출하고 나머지는 하단에 요약
        name_ticker = f"{r['name']}({r['ticker'][:6]})"
        print(f"{name_ticker:<18} | {r['total_signals']:<5} | {r['overall_win_rate']*100:6.1f}% | {r['overheat_win_rate']*100:6.1f}% | {r['rebalance_win_rate']*100:6.1f}% | {r['buy_and_hold_return']:+7.1f}% | {r['strategy_return']:+7.1f}% | {r['outperformance']:+7.1f}%")
        
        total_signals += r['total_signals']
        win_rates.append(r['overall_win_rate'])
        strategy_returns.append(r['strategy_return'])
        bh_returns.append(r['buy_and_hold_return'])
        outperformances.append(r['outperformance'])
        
    print("-"*100)
    print(f"[*] 분석 대상 종목 수: {len(results)}개")
    print(f"[*] 검증된 총 신호 횟수: {total_signals}회")
    print(f"[*] 평균 신호 승률 (Hit Rate): {np.mean(win_rates)*100:.2f}%")
    print(f"[*] 평균 단순 보유 수익률: {np.mean(bh_returns):+.2f}%")
    print(f"[*] 평균 리밸런싱 전략 수익률: {np.mean(strategy_returns):+.2f}%")
    print(f"[*] 평균 초과 수익률 (Alpha): {np.mean(outperformances):+.2f}%")
    print("="*80 + "\n")
