import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional

# KOSPI 50 주요 종목 티커 정의 (2026년 기준 주요 대형주 및 지수)
TICKERS = {
    "^KS11": "코스피 지수",
    "005930.KS": "삼성전자",
    "000660.KS": "SK하이닉스",
    "373220.KS": "LG에너지솔루션",
    "207940.KS": "삼성바이오로직스",
    "005380.KS": "현대차",
    "000270.KS": "기아",
    "068270.KS": "셀트리온",
    "105560.KS": "KB금융",
    "055550.KS": "신한지주",
    "005490.KS": "POSCO홀딩스",
    "035420.KS": "NAVER",
    "028260.KS": "삼성물산",
    "012330.KS": "현대모비스",
    "051910.KS": "LG화학",
    "006400.KS": "삼성SDI",
    "138040.KS": "메리츠금융지주",
    "086790.KS": "하나금융지주",
    "035720.KS": "카카오",
    "032830.KS": "삼성생명",
    "003670.KS": "포스코퓨처엠",
    "329180.KS": "HD현대중공업",
    "000810.KS": "삼성화재",
    "066570.KS": "LG전자",
    "042660.KS": "한화오션",
    "450080.KS": "에코프로머티",
    "009540.KS": "HD한국조선해양",
    "033780.KS": "KT&G",
    "316140.KS": "우리금융지주",
    "018260.KS": "삼성에스디에스",
    "096770.KS": "SK이노베이션",
    "010130.KS": "고려아연",
    "024110.KS": "기업은행",
    "011200.KS": "HMM",
    "010950.KS": "S-Oil",
    "259960.KS": "크래프톤",
    "034020.KS": "두산에너빌리티",
    "015760.KS": "한국전력",
    "047050.KS": "포스코인터내셔널",
    "003490.KS": "대한항공",
    "012450.KS": "한화에어로스페이스",
    "090430.KS": "아모레퍼시픽",
    "017670.KS": "SK텔레콤",
    "030200.KS": "KT",
    "010140.KS": "삼성중공업",
    "001570.KS": "금양",
    "273200.KS": "HD현대일렉트릭",
    "161390.KS": "한국타이어앤테크놀로지",
    "323410.KS": "카카오뱅크",
    "377300.KS": "카카오페이"
}

def fetch_market_data(period: str = "3mo") -> Dict[str, pd.DataFrame]:
    """
    정의된 모든 티커에 대해 야후 파이낸스로부터 지정된 기간의 일봉 데이터를 수집합니다.
    """
    tickers_list = list(TICKERS.keys())
    print(f"[*] {len(tickers_list)}개 종목 시세 데이터 수집 시작 (기간: {period})...")
    
    # yfinance를 사용하여 데이터를 일괄 다운로드 (병렬 다운로드 자동 활성화)
    try:
        data = yf.download(tickers_list, period=period, group_by="ticker", progress=False)
    except Exception as e:
        print(f"[!] 데이터 수집 실패: {e}")
        return {}

    market_data = {}
    for ticker in tickers_list:
        try:
            if ticker in data.columns.levels[0]:
                ticker_df = data[ticker].dropna(subset=["Close"])
                if not ticker_df.empty:
                    market_data[ticker] = ticker_df
        except Exception as e:
            print(f"[!] {ticker} 데이터 파싱 에러: {e}")
            
    print(f"[*] 데이터 수집 완료 (성공: {len(market_data)}/{len(tickers_list)} 종목)")
    return market_data

def get_ticker_name(ticker: str) -> str:
    return TICKERS.get(ticker, ticker)
