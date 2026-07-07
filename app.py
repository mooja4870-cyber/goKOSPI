import threading
import time
import math
from flask import Flask, render_template, jsonify, request
import FinanceDataReader as fdr
import yfinance as yf
from collector import fetch_market_data, get_ticker_name
from engine import analyze_last_signal

app = Flask(__name__)

# 분석 결과 캐시용 메모리
signal_cache = []
cache_lock = threading.Lock()
is_loading = True

# KRX 전 종목 리스트 캐시 (메모리 로딩)
krx_stocks = []

def init_krx_stocks():
    """
    FinanceDataReader를 통해 코스피/코스닥 전 종목 및 국내 상장 ETF 메타데이터를 가져와 로딩합니다.
    """
    global krx_stocks
    try:
        print("[*] KRX 전 종목 메타데이터 로딩 시작 (finance-datareader)...")
        df = fdr.StockListing('KRX')
        temp_stocks = []
        for _, row in df.iterrows():
            code = row.get('Code')
            name = row.get('Name')
            market = row.get('Market', '')
            
            if not code or not name:
                continue
                
            # 야후 파이낸스용 티커 접미사 분기 매핑 (.KS / .KQ)
            if 'KOSPI' in market:
                ticker = f"{code}.KS"
            elif 'KOSDAQ' in market:
                ticker = f"{code}.KQ"
            else:
                ticker = f"{code}.KS"  # 기본값 KS
                
            temp_stocks.append({
                "name": name,
                "ticker": ticker
            })

        print("[*] 국내 상장 ETF 메타데이터 로딩 시작 (finance-datareader)...")
        try:
            df_etf = fdr.StockListing('ETF/KR')
            for _, row in df_etf.iterrows():
                code = row.get('Symbol')
                if not code:
                    code = row.get('Code')
                name = row.get('Name')
                if not code or not name:
                    continue
                
                # ETF는 야후 파이낸스에서 .KS 접미사 사용
                ticker = f"{code}.KS"
                temp_stocks.append({
                    "name": f"[ETF] {name}",
                    "ticker": ticker
                })
        except Exception as etf_err:
            print(f"[!] ETF 메타데이터 로딩 실패: {etf_err}")

        # 중복 방지 (티커 기준)
        seen = set()
        unique_stocks = []
        for s in temp_stocks:
            if s["ticker"] not in seen:
                seen.add(s["ticker"])
                unique_stocks.append(s)

        # 가나다 순 기본 정렬
        krx_stocks = sorted(unique_stocks, key=lambda x: x["name"])
        print(f"[*] KRX 전 종목 및 ETF 로딩 완료 (총 {len(krx_stocks)}개 종목 로드됨)")
    except Exception as e:
        print(f"[!] KRX/ETF 종목 로딩 실패: {e}")

def update_signal_cache_worker():
    """
    백그라운드에서 주기적으로 50대 종목 시세를 수집 및 분석하여 캐시를 동기화합니다.
    """
    global signal_cache, is_loading
    while True:
        try:
            print("[*] 백그라운드 캐시 갱신 시작...")
            # 데이터 수집 (최근 3개월)
            market_data = fetch_market_data(period="3mo")
            
            temp_cache = []
            if market_data:
                for ticker, df in market_data.items():
                    analysis = analyze_last_signal(df, ticker)
                    analysis["name"] = get_ticker_name(ticker)
                    
                    # NaN 값 안전 정제 (JSON 직렬화 및 프론트엔드 오류 방지)
                    z = analysis.get("z_score", 0.0)
                    if math.isnan(z):
                        analysis["z_score"] = 0.0
                        
                    temp_cache.append(analysis)
                
                # 원래 TICKERS 정의 순서(시가총액 50대 종목 순위)대로 캐시 정렬
                from collector import TICKERS
                tickers_order = {ticker: idx for idx, ticker in enumerate(list(TICKERS.keys()) + ["^KS11"])}
                temp_cache = sorted(temp_cache, key=lambda x: tickers_order.get(x["ticker"], 999))
                
                with cache_lock:
                    signal_cache = temp_cache
                    is_loading = False
            print(f"[*] 백그라운드 캐시 갱신 완료 (총 {len(signal_cache)}개 종목)")
        except Exception as e:
            print(f"[!] 캐시 갱신 도중 예외 발생: {e}")
            
        # 30분 주기로 캐시 갱신 (서버 부하 및 야후 파이낸스 차단 우려 완화)
        time.sleep(1800)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/signals")
def get_signals():
    global signal_cache, is_loading
    with cache_lock:
        return jsonify({
            "loading": is_loading,
            "data": signal_cache,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })

@app.route("/api/search_ticker")
def search_ticker():
    """
    코스피/코스닥 전 종목명 검색 API
    """
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])
    
    # 키워드가 들어간 종목들 검색 (최대 20개까지만 리턴하여 속도 및 사용성 극대화)
    results = [s for s in krx_stocks if query.lower() in s["name"].lower()]
    return jsonify(results[:20])

@app.route("/api/inspect_ticker")
def inspect_ticker():
    """
    특정 종목에 대해 실시간 다운로드 및 Z-Score 신호 분석 결과 제공 API
    """
    ticker = request.args.get("ticker", "").strip()
    if not ticker:
        return jsonify({"success": False, "error": "티커 파라미터가 누락되었습니다."})
        
    try:
        # 야후 파이낸스에서 실시간 3개월 시세 다운로드 (타임아웃 4초)
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(period="3mo", timeout=4)
        
        if df is None or df.empty:
            return jsonify({"success": False, "error": f"{ticker}의 시세 데이터를 야후 파이낸스에서 찾을 수 없습니다."})
            
        df_cleaned = df.dropna(subset=["Close"])
        if df_cleaned.empty:
            return jsonify({"success": False, "error": f"{ticker}의 종가 데이터가 비어있습니다."})
            
        # 실시간 분석
        analysis = analyze_last_signal(df_cleaned, ticker)
        
        # 종목명 역조회
        name = ticker
        match = next((s for s in krx_stocks if s["ticker"] == ticker), None)
        if match:
            name = match["name"]
        analysis["name"] = name
        
        # NaN 값 정제
        z = analysis.get("z_score", 0.0)
        if math.isnan(z):
            analysis["z_score"] = 0.0
            
        analysis["success"] = True
        return jsonify(analysis)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/backtest_summary")
def get_backtest_summary():
    return jsonify({
        "success": True,
        "total_signals": 860,
        "hit_rate": 72.12,
        "overheat_hit_rate": 74.3,
        "rebalance_hit_rate": 70.2,
        "avg_hold_return": 165.67,
        "avg_strategy_return": 116.42,
        "top_performers": [
            {"name": "신한지주", "ticker": "055550.KS", "win_rate": 77.8, "bh_return": 271.7, "st_return": 410.5, "alpha": 138.8},
            {"name": "삼성중공업", "ticker": "010140.KS", "win_rate": 91.7, "bh_return": 214.1, "st_return": 311.9, "alpha": 97.8},
            {"name": "대한항공", "ticker": "003490.KS", "win_rate": 75.0, "bh_return": 26.7, "st_return": 93.5, "alpha": 66.8},
            {"name": "메리츠금융", "ticker": "138040.KS", "win_rate": 85.7, "bh_return": 186.6, "st_return": 244.7, "alpha": 58.1}
        ]
    })

if __name__ == "__main__":
    # KRX 종목 사전 로드
    init_krx_stocks()
    
    # 백그라운드 캐시 갱신 스레드 기동
    cache_thread = threading.Thread(target=update_signal_cache_worker, daemon=True)
    cache_thread.start()
    
    print("[*] goKOSPI 프리미엄 대시보드 웹 서버 기동 중... (Port: 9000)")
    app.run(host="0.0.0.0", port=9000, debug=False)
