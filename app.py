import threading
import time
from flask import Flask, render_template, jsonify
from collector import fetch_market_data, get_ticker_name
from engine import analyze_last_signal

app = Flask(__name__)

# 분석 결과 캐시용 메모리
signal_cache = []
cache_lock = threading.Lock()
is_loading = True

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
                    import math
                    z = analysis.get("z_score", 0.0)
                    if math.isnan(z):
                        analysis["z_score"] = 0.0
                        
                    temp_cache.append(analysis)
                
                # Z-Score 기준으로 내림차순 정렬
                temp_cache = sorted(temp_cache, key=lambda x: abs(x.get("z_score", 0)), reverse=True)
                
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

@app.route("/api/backtest_summary")
def get_backtest_summary():
    # 과거 백테스팅 대표 종목 성과 요약 데이터 정적 리턴 (백테스트 실행 시간이 10초 이상이므로)
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
    # 백그라운드 캐시 갱신 스레드 기동
    cache_thread = threading.Thread(target=update_signal_cache_worker, daemon=True)
    cache_thread.start()
    
    print("[*] goKOSPI 프리미엄 대시보드 웹 서버 기동 중... (Port: 9000)")
    # 포트 9000으로 플라스크 웹 서버 실행
    app.run(host="0.0.0.0", port=9000, debug=False)
