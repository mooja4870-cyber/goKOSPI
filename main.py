import sys
import os
import time
import argparse
import schedule
from collector import fetch_market_data, get_ticker_name, TICKERS
from engine import analyze_last_signal
from notifier import notify_signal, notify_system_status
from backtest import run_global_backtest

# 디스코드 웹훅 URL (우선 환경 변수에서 읽어옴)
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

def run_once() -> None:
    """
    모든 종목의 실시간 데이터를 수집해 당일 발생한 신규 신호를 진단하고 디스코드 알림을 송출합니다.
    """
    print("\n" + "="*50)
    print("        [goKOSPI 리밸런싱 스캐닝 시작]")
    print("="*50)
    
    # 최근 3개월간의 데이터를 바탕으로 당일 종가 변동성 계산
    market_data = fetch_market_data(period="3mo")
    if not market_data:
        print("[!] 수집된 마켓 데이터가 없습니다.")
        return
        
    signals_detected = 0
    for ticker, df in market_data.items():
        analysis = analyze_last_signal(df, ticker)
        
        # 신호가 포착되었고, 그것이 오늘 당일 새로 발생한(New) 신호인 경우
        if analysis["signal"] in ["OVERHEAT", "REBALANCED"] and analysis["is_new"]:
            name = get_ticker_name(ticker)
            success = notify_signal(DISCORD_WEBHOOK_URL, analysis, name)
            if success:
                print(f"[+] {name} ({ticker}) 신호 디스코드 전송 완료!")
            signals_detected += 1
            
    print(f"[*] 스캐닝 완료 (신규 알림 신호 포착: {signals_detected}건)")
    print("="*50 + "\n")

def start_scheduler() -> None:
    """
    스케줄러를 구동하여 장마감 후 배치 분석을 실행합니다.
    """
    print("[*] goKOSPI 백그라운드 스케줄러 가동 시작...")
    if DISCORD_WEBHOOK_URL:
        notify_system_status(DISCORD_WEBHOOK_URL, "goKOSPI 실시간 감시 스케줄러가 정상 시동되었습니다.")
    else:
        print("[!] DISCORD_WEBHOOK_URL 환경 변수가 잡히지 않아, 감지된 신호는 콘솔로만 표시됩니다.")
        
    # 매일 장마감 직후인 15시 45분에 당일 최종 리밸런싱 시그널 감시 실행
    schedule.every().day.at("15:45").do(run_once)
    
    # 장중 변동성 감지를 위해 월~금 10:00부터 15:00까지 매 정각마다 임시 스캔 추가
    # (한국 거래 시간 기준)
    schedule.every().hour.do(run_once)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

def main() -> None:
    parser = argparse.ArgumentParser(description="goKOSPI 리밸런싱 감지 엔진")
    parser.add_argument("mode", choices=["run", "backtest", "schedule"], 
                        help="실행 모드: run (1회 스캔), backtest (백테스트 시뮬레이션), schedule (백그라운드 스케줄러)")
    parser.add_argument("--zscore", type=float, default=2.5, help="과열 기준 Z-Score 임계값 (기본값: 2.5)")
    
    args = parser.parse_args()
    
    if args.mode == "run":
        run_once()
        
    elif args.mode == "backtest":
        # 백테스트는 더 넓은 시계열(과거 3년) 데이터를 수집하여 검증
        market_data = fetch_market_data(period="3y")
        run_global_backtest(market_data, threshold_z=args.zscore)
        
    elif args.mode == "schedule":
        # 즉시 1회 검증 실행 후 스케줄러 진입
        run_once()
        start_scheduler()

if __name__ == "__main__":
    main()
