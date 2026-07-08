import threading
import time
import math
from flask import Flask, render_template, jsonify, request
import FinanceDataReader as fdr
import yfinance as yf
from collector import fetch_market_data, get_ticker_name, CATEGORY_TICKERS
from engine import analyze_last_signal

app = Flask(__name__)

# 분석 결과 캐시용 메모리 (6대 카테고리별 분할 저장)
signal_cache = {
    "KOSPI": [],
    "KOSDAQ": [],
    "DOW": [],
    "SP500": [],
    "COMMODITY": [],
    "CRYPTO": []
}
cache_lock = threading.Lock()
is_loading = True

# KRX 전 종목 리스트 캐시 (국내 주식 및 ETF 검색용 메모리 로딩)
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
    백그라운드에서 주기적으로 6대 자산군 전 종목의 시세를 병렬 수집 및 분석하여 캐시를 갱신합니다.
    """
    global signal_cache, is_loading
    while True:
        try:
            print("[*] 백그라운드 6대 자산군 캐시 갱신 시작...")
            temp_cache_all = {}
            
            for category in signal_cache.keys():
                market_data = fetch_market_data(category, period="3mo")
                category_cache = []
                
                if market_data:
                    for ticker, df in market_data.items():
                        analysis = analyze_last_signal(df, ticker)
                        analysis["name"] = get_ticker_name(category, ticker)
                        
                        # NaN 값 안전 정제
                        z = analysis.get("z_score", 0.0)
                        if math.isnan(z):
                            analysis["z_score"] = 0.0
                            
                        # drawdown_pct NaN 값 정제
                        dd = analysis.get("drawdown_pct", 0.0)
                        if math.isnan(dd):
                            analysis["drawdown_pct"] = 0.0
                            
                        category_cache.append(analysis)
                    
                    # 원래 정의된 순서대로 정렬 고정
                    order_list = list(CATEGORY_TICKERS[category].keys())
                    tickers_order = {ticker: idx for idx, ticker in enumerate(order_list)}
                    category_cache = sorted(category_cache, key=lambda x: tickers_order.get(x["ticker"], 999))
                    
                temp_cache_all[category] = category_cache
            
            # 한 번에 락 잡고 교체
            with cache_lock:
                for category, cached_list in temp_cache_all.items():
                    signal_cache[category] = cached_list
                is_loading = False
                
            print("[*] 백그라운드 6대 자산군 캐시 갱신 완료!")
        except Exception as e:
            print(f"[!] 캐시 갱신 도중 예외 발생: {e}")
            
        # 30분 주기로 캐시 갱신
        time.sleep(1800)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/signals")
def get_signals():
    global signal_cache, is_loading
    category = request.args.get("category", "KOSPI").upper()
    if category not in signal_cache:
        category = "KOSPI"
        
    with cache_lock:
        return jsonify({
            "loading": is_loading,
            "data": signal_cache[category],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })

@app.route("/api/search_ticker")
def search_ticker():
    """
    코스피/코스닥/ETF 전 종목명 검색 API (한글 검색) + 미국 지수 구성주 및 가상자산도 검색 범위에 융합
    """
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])
    
    results = []
    # 1. 미국 주식, 원자재, 크립토 등 정의된 수동 사전을 먼저 매칭
    for cat, tickers_dict in CATEGORY_TICKERS.items():
        if cat in ["KOSPI", "KOSDAQ"]:
            continue
        for ticker, name in tickers_dict.items():
            if query.lower() in name.lower() or query.lower() in ticker.lower():
                results.append({
                    "name": f"[{cat}] {name}",
                    "ticker": ticker
                })
                
    # 2. 국내 KRX/ETF 리스트 검색 병합
    krx_matches = [
        {"name": s["name"], "ticker": s["ticker"]} 
        for s in krx_stocks if query.lower() in s["name"].lower()
    ]
    results.extend(krx_matches)
    
    # 중복 제거 및 최대 20개까지만 리턴
    seen = set()
    unique_results = []
    for r in results:
        if r["ticker"] not in seen:
            seen.add(r["ticker"])
            unique_results.append(r)
            
    return jsonify(unique_results[:20])

@app.route("/api/inspect_ticker")
def inspect_ticker():
    """
    특정 종목에 대해 실시간 Z-Score 신호 분석 결과 제공 API (주식, 원자재, 암호화폐 전천후 진단)
    """
    ticker = request.args.get("ticker", "").strip()
    if not ticker:
        return jsonify({"success": False, "error": "티커 파라미터가 누락되었습니다."})
        
    try:
        # 야후 파이낸스에서 실시간 3개월 시세 다운로드
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(period="3mo", timeout=4)
        
        if df is None or df.empty:
            return jsonify({"success": False, "error": f"{ticker}의 시세 데이터를 야후 파이낸스에서 찾을 수 없습니다."})
            
        df_cleaned = df.dropna(subset=["Close"])
        if df_cleaned.empty:
            return jsonify({"success": False, "error": f"{ticker}의 종가 데이터가 비어있습니다."})
            
        # Z-Score 신호 계산
        analysis = analyze_last_signal(df_cleaned, ticker)
        
        # 1. 6대 카테고리 정의에서 한글명 탐색
        name = ticker
        found = False
        for cat, tickers_dict in CATEGORY_TICKERS.items():
            if ticker in tickers_dict:
                name = tickers_dict[ticker]
                found = True
                break
                
        # 2. 전종목 사전에서 한글명 탐색
        if not found:
            match = next((s for s in krx_stocks if s["ticker"] == ticker), None)
            if match:
                name = match["name"]
                
        analysis["name"] = name
        
        # NaN 값 안전 정제
        z = analysis.get("z_score", 0.0)
        if math.isnan(z):
            analysis["z_score"] = 0.0
            
        dd = analysis.get("drawdown_pct", 0.0)
        if math.isnan(dd):
            analysis["drawdown_pct"] = 0.0
            
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
    init_krx_stocks()
    
    # 백그라운드 캐시 갱신 스레드 기동
    cache_thread = threading.Thread(target=update_signal_cache_worker, daemon=True)
    cache_thread.start()
    
    print("[*] goKOSPI 프리미엄 대시보드 웹 서버 기동 중... (Port: 9000)")
    app.run(host="0.0.0.0", port=9000, debug=False)
