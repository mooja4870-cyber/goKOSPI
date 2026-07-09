import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# 6대 자산군 카테고리별 티커와 이름 매핑 정보
CATEGORY_TICKERS = {
    "KOSPI": {
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
    },
    "KOSDAQ": {
        "^KQ11": "코스닥 지수",
        "196170.KQ": "알테오젠",
        "247540.KQ": "에코프로비엠",
        "086520.KQ": "에코프로",
        "028300.KQ": "HLB",
        "141080.KQ": "리가켐바이오",
        "348370.KQ": "엔켐",
        "214150.KQ": "클래시스",
        "000250.KQ": "삼천당제약",
        "145020.KQ": "휴젤",
        "058470.KQ": "리노공업",
        "403870.KQ": "HPSP",
        "277810.KQ": "레인보우로보틱스",
        "357780.KQ": "솔브레인",
        "257720.KQ": "실리콘투",
        "237690.KQ": "에스티팜",
        "214450.KQ": "파마리서치",
        "005290.KQ": "동진쎄미켐",
        "041510.KQ": "에스엠",
        "035900.KQ": "JYP Ent.",
        "122870.KQ": "와이지엔터테인먼트",
        "096530.KQ": "씨젠",
        "278280.KQ": "천보",
        "068760.KQ": "셀트리온제약",
        "310210.KQ": "보로노이",
        "078600.KQ": "대주전자재료",
        "298380.KQ": "에이비엘바이오",
        "065350.KQ": "신성델타테크",
        "328130.KQ": "루닛",
        "015750.KQ": "성우하이텍",
        "036930.KQ": "주성엔지니어링",
        "039030.KQ": "이오테크닉스",
        "131970.KQ": "두산테스나",
        "240810.KQ": "원익IPS",
        "064760.KQ": "티씨케이",
        "166090.KQ": "하나머티리얼즈",
        "319660.KQ": "피에스케이",
        "440110.KQ": "파두",
        "067160.KQ": "SOOP",
        "053800.KQ": "안랩",
        "204270.KQ": "제이앤티씨",
        "225570.KQ": "넥슨게임즈",
        "950160.KQ": "코오롱티슈진",
        "034230.KQ": "파라다이스",
        "393890.KQ": "더블유씨피",
        "036530.KQ": "솔브레인홀딩스"
    },
    "DOW": {
        "^DJI": "다우존스 산업지수",
        "AAPL": "애플",
        "MSFT": "마이크로소프트",
        "AMZN": "아마존",
        "NVDA": "엔비디아",
        "JPM": "JP모건 체이스",
        "V": "비자",
        "UNH": "유나이티드헬스",
        "HD": "홈디포",
        "PG": "프록터 앤 갬블",
        "DIS": "디즈니",
        "CAT": "캐터필러",
        "JNJ": "존슨 앤 존슨",
        "CRM": "세일즈포스",
        "AXP": "아메리칸 익스프레스",
        "MRK": "머크",
        "WMT": "월마트",
        "GS": "골드만삭스",
        "TRV": "트래블러스",
        "IBM": "IBM",
        "MCD": "맥도날드",
        "HON": "하니웰",
        "AMGN": "암젠",
        "VZ": "버라이즌",
        "CVX": "셰브론",
        "CSCO": "시스코",
        "NKE": "나이키",
        "SHW": "셔윈 윌리엄스",
        "DOW": "다우 케미칼",
        "KO": "코카콜라",
        "INTC": "인텔"
    },
    "SP500": {
        "^GSPC": "S&P 500 지수",
        "META": "메타",
        "GOOGL": "알파벳A",
        "TSLA": "테슬라",
        "LLY": "일라이 릴리",
        "AVGO": "브로드컴",
        "COST": "코스트코",
        "NFLX": "넷플릭스",
        "ABBV": "애브비",
        "AMD": "AMD",
        "ORCL": "오라클",
        "BAC": "뱅크 오브 아메리카",
        "PEP": "펩시코",
        "PM": "필립 모리스",
        "TMO": "써모 피셔",
        "LIN": "린데",
        "ADBE": "어도비",
        "ACN": "액센츄어",
        "WFC": "웰스 파고",
        "TXN": "텍사스 인스트루먼트",
        "FDX": "페덱스",
        "GE": "제너럴 일렉트릭",
        "QCOM": "퀄컴",
        "INTU": "인튜이트",
        "SBUX": "스타벅스",
        "MS": "모건 스탠리",
        "MDLZ": "몬델리즈",
        "ISRG": "인튜이티브 서지컬",
        "BKNG": "부킹 홀딩스",
        "AMAT": "어플라이드 머티어리얼즈",
        "NOW": "서비스나우",
        "PLTR": "팔란티어",
        "AAPL": "애플",
        "MSFT": "마이크로소프트",
        "AMZN": "아마존",
        "NVDA": "엔비디아",
        "JPM": "JP모건 체이스",
        "V": "비자",
        "UNH": "유나이티드헬스",
        "HD": "홈디포",
        "PG": "프록터 앤 갬블",
        "JNJ": "존슨 앤 존슨",
        "MRK": "머크",
        "WMT": "월마트",
        "KO": "코카콜라",
        "CVX": "셰브론",
        "CSCO": "시스코"
    },
    "COMMODITY": {
        "GC=F": "국제 금 선물 지수",
        "SI=F": "국제 은 선물",
        "132030.KS": "KODEX 골드선물(H)",
        "144600.KS": "KODEX 은선물(H)",
        "GLD": "SPDR Gold Shares ETF",
        "SLV": "iShares Silver Trust ETF"
    },
    "CRYPTO": {
        "BTC-USD": "비트코인 지수",
        "ETH-USD": "이더리움",
        "SOL-USD": "솔라나",
        "XRP-USD": "리플",
        "DOGE-USD": "도지코인",
        "ADA-USD": "에이다"
    }
}

def fetch_single_ticker(ticker: str, period: str) -> Optional[pd.DataFrame]:
    """
    야후 파이낸스에서 단일 티커의 데이터를 수집하는 헬퍼 함수
    """
    try:
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(period=period, timeout=4)
        if df is not None and not df.empty:
            df_cleaned = df.dropna(subset=["Close"])
            if not df_cleaned.empty:
                return df_cleaned
    except Exception as e:
        print(f"[!] {ticker} 수집 실패: {e}")
    return None

def fetch_market_data(category: str, period: str = "3mo") -> Dict[str, pd.DataFrame]:
    """
    선택된 카테고리의 모든 티커 데이터를 ThreadPoolExecutor 병렬 처리를 통해 고속 수집합니다.
    """
    tickers_dict = CATEGORY_TICKERS.get(category, {})
    if not tickers_dict:
        print(f"[!] 알 수 없는 카테고리: {category}")
        return {}

    tickers_list = list(tickers_dict.keys())
    print(f"[*] [{category}] {len(tickers_list)}개 종목 시세 데이터 병렬 수집 시작 (기간: {period})...")
    
    market_data = {}
    
    # 15개의 스레드로 스레드풀을 구성하여 고속 병렬 개별 호출
    with ThreadPoolExecutor(max_workers=15) as executor:
        future_to_ticker = {
            executor.submit(fetch_single_ticker, ticker, period): ticker 
            for ticker in tickers_list
        }
        
        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                data = future.result()
                if data is not None:
                    market_data[ticker] = data
            except Exception as exc:
                print(f"[!] {ticker} 작업 실패: {exc}")
                
    print(f"[*] [{category}] 데이터 수집 완료 (성공: {len(market_data)}/{len(tickers_list)} 종목)")
    return market_data

def get_ticker_name(arg1: str, arg2: str = None) -> str:
    """
    지정된 카테고리 안에서 티커에 상응하는 종목명을 반환하거나, 티커만 주어지면 전체 카테고리에서 찾습니다.
    """
    if arg2 is None:
        ticker = arg1
        for cat_dict in CATEGORY_TICKERS.values():
            if ticker in cat_dict:
                return cat_dict[ticker]
        return ticker
    category, ticker = arg1, arg2
    return CATEGORY_TICKERS.get(category, {}).get(ticker, ticker)
