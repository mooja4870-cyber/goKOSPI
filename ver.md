# Version History

## v2.2.0

Date: 2026-07-08

### 변경 내용

* 6대 자산군별로 동일하게 고정 노출되던 하드코딩 백테스트 데이터를 **탭 연동 동적 데이터로 개편** (버그 수정)
* `/api/backtest_summary` API에 `category` 파라미터를 추가하여 6대 자산군별 백테스트 통계 데이터(신호 승률, 적중률, 검증 횟수) 반환 (`app.py`)
* 대시보드 백테스트 위젯 내부에 **"🏆 리밸런싱 최적화 상위 종목" 리스트 영역 신설** 및 동적 바인딩 렌더러 연동 (`templates/index.html`)
* 탭 전환 시 지수 분위기와 함께 백테스트 통계 지표와 최적화 종목이 비동기로 유연하게 재로드되도록 처리

### 수정 파일

* app.py
* templates/index.html
* ver.md

### 비고

* 다중 자산 통합 리밸런싱 플랫폼 백테스트 검증 데이터 연동 버그 클리어 완료

## v2.1.0

Date: 2026-07-08

### 변경 내용

* 사용자의 지시에 따라 **"시안 2. 파스텔 버블검 글래스모피즘 (Bubblegum Glassmorphism)" 테마 전격 적용**
* 핑크-라벤더 퍼플의 몽환적이고 부드러운 그라데이션 고정 배경 적용
* 밝은 배경에서 가독성을 확보하기 위해 주요 글자색을 다크 그레이(#1a202c, #4a5568) 계열로 리타칭
* 모든 카드 컴포넌트에 Frosted-Glass 효과(`backdrop-filter: blur(20px)`) 및 투명도 높은 화이트 테두리 적용
* Z-Score 7단계 뱃지 디자인을 파스텔 톤(부드러운 레드/오렌지/옐로우/그레이/블루/그린)으로 교환
* 검색창 입력 필드 및 정렬 셀렉트 박스, 툴팁 도움말도 화사하고 깨끗한 글래스 스타일로 전격 개편

### 수정 파일

* templates/index.html
* ver.md

### 비고

* 파스텔 버블검 글래스모피즘 테마(v2.1.0) 최종 배포 완료

## v2.0.0

Date: 2026-07-08

### 변경 내용

* 2030 젊은 세대의 취향을 저격하는 **"사이버펑크 네온 핑크 (Cyberpunk Neon Pink)" 테마로 전면 리디자인** 단행
* 둥글고 트렌디한 구글 영문/한글 폰트 `Plus Jakarta Sans` 도입 적용
* 바디 배경에 몽환적인 핑크-블루 네온 오로라 광원 효과 백드롭 적용
* 모든 대형 카드와 UI 컴포넌트에 은은한 형광 핑크 글로우 테두리 및 그림자 효과 부여
* Z-Score 리밸런싱 7단계 뱃지를 선명한 형광 야광 텍스트 및 밝은 테두리(텍스트 쉐도우 글로우)로 변경
* 지수 동기화 상태바 및 의사결정 카드 세부 컬러도 네온 핑크/사이언 톤으로 고대조 리터칭 완료

### 수정 파일

* templates/index.html
* ver.md

### 비고

* 메이저 리디자인(v2.0.0) 배포 완료

## v1.9.0

Date: 2026-07-08

### 변경 내용

* 글로벌 멀티 자산 리밸런싱 포탈 진화를 위한 **6대 자산군 탭 인터페이스 적용** (`templates/index.html`)
* 6대 탭: 🇰🇷 코스피 / 🇰🇷 코스닥 / 🇺🇸 다우지수 / 🇺🇸 S&P 500 / 🪙 금·은 / ₿ 가상자산
* 5-스레드 병렬 다운로더(`ThreadPoolExecutor`) 도입으로 190개 대량 종목 수집 속도를 15초 내외로 단축 (`collector.py`)
* 백엔드 API `/api/signals?category=...` 세그먼트 캐싱 라우트 구현 (`app.py`)
* 자산군 특성별 시장 분위기(Market Mood) Z-Score 해석 가이드 다변화 주입

### 수정 파일

* collector.py
* app.py
* templates/index.html
* ver.md

### 비고

* 글로벌 멀티 탭 투자 나침반 플랫폼 리뉴얼 릴리즈 완료

## v1.8.1

Date: 2026-07-08

### 변경 내용

* 조정완료 및 매수 진입 시 하락폭(Drawdown)이 일관되게 `0.0%`로 노출되던 계산 버그 수정
* 고가 기준점(`Peak_Close`)을 기존 당일 종가에서 최근 20영업일 기준 최고 종가(`rolling.max()`)로 변경하여 정확한 낙폭 계산 구현

### 수정 파일

* engine.py
* ver.md

### 비고

* 종목별 실질 고점 대비 낙폭 퍼센트 계산 동기화 완료

## v1.8.0

Date: 2026-07-07

### 변경 내용

* 리밸런싱 신호를 기존 4단계(HOLD/OVERHEAT/OVERHEATED_HOLD/REBALANCED)에서 **Z-Score 기반 7단계 체계**로 전면 재설계
* 7단계: 💚 강력매수 / 🟢 매수시그널 / 🩵 관심매집 / ⚪ 중립대기 / 🟡 경계관망 / 🟠 익절권장 / 🔴 강력매도
* 각 단계별 전용 컬러 뱃지(badge CSS 7종) 및 이모지 아이콘 렌더링 적용
* 스캐너 테이블 리밸런싱 신호 헤더 마우스 도움말(툴팁)도 7단계 설명으로 업데이트

### 수정 파일

* engine.py
* templates/index.html
* ver.md

### 비고

* 상태 머신 기반 복잡도를 제거하고 Z-Score 구간 직접 분기 방식으로 단순화 및 직관성 극대화

## v1.7.0

Date: 2026-07-07

### 변경 내용

* 국내 상장 ETF(KODEX, TIGER, SOL 등 900여 개 종목) 실시간 Z-Score 신호 검색 및 진단 연동
* `finance-datareader`를 활용하여 ETF 전 목록(`ETF/KR`)을 백엔드 시동 시점 메모리에 자동 합산하도록 개편
* 검색 리스트에서 구분하기 쉽도록 ETF 상품은 이름 머리에 `[ETF]` 접두어 자동 렌더링 지원

### 수정 파일

* app.py
* ver.md

### 비고

* 주식뿐만 아니라 지수형/테마형 ETF 리밸런싱 대응력 확보 완료

## v1.6.0

Date: 2026-07-07

### 변경 내용

* 관심 종목 검색 범위를 KOSPI 50대 대형주 한정에서 **코스피/코스닥 전 종목(2,500개 이상)으로 전격 확장**
* `finance-datareader` 라이브러리를 추가 탑재하여 실시간 KRX 전 종목 데이터 연동 아키텍처 구축
* 실시간 전 종목 자동완성 검색 API(`/api/search_ticker`) 및 실시간 개별 종목 시세 연산 진단 API(`/api/inspect_ticker`) 신설 및 적용

### 수정 파일

* app.py
* templates/index.html
* requirements.txt
* ver.md

### 비고

* 코스피/코스닥 전 종목에 대한 실시간 Z-Score 진단 서비스 가동 완료

## v1.5.0

Date: 2026-07-07

### 변경 내용

* 관심 종목 실시간 개별 신호 검색기(Quick Inspector) 추가 (`templates/index.html` 기능 추가)
* 한글 초중성 가나다 자모음 정렬(`localeCompare`) 기반 자동완성 드롭 리스트 구현
* 관심종목 클릭 시 Z-Score, 실시간 가격 대비 변동성, 세부 1줄 행동 가이드를 동적으로 카드 렌더링하는 진단 모듈 완성

### 수정 파일

* templates/index.html
* ver.md

### 비고

* 검색형 신호 판독 위젯 연동 성공

## v1.4.2

Date: 2026-07-07

### 변경 내용

* Z-Score 및 리밸런싱 신호 테이블 헤더에 마우스 호버 도움말(툴팁) 연동 (`templates/index.html` 구현)
* 중등 눈높이에 맞춘 초간단 해설 카드 말풍선 구현 (CSS 가상선택자 및 pre-wrap 처리 적용)

### 수정 파일

* templates/index.html
* ver.md

### 비고

* 직관적인 용어 설명 툴팁 기법 적용 완료

## v1.4.1

Date: 2026-07-07

### 변경 내용

* 백엔드 API `/api/signals` 정렬 기준을 시총 순서로 고정하도록 원천 수정 (`app.py` 핫패치)
* 프론트엔드 최초 로딩 시 시총 순으로 보기(삼성전자, SK하이닉스 탑 순위)가 정확히 작동하지 않던 버그 해결

### 수정 파일

* app.py
* ver.md

### 비고

* 시총 기본 정렬 동기화 완료

## v1.4.0

Date: 2026-07-07

### 변경 내용

* 전체보기 우량주 스캐너 리스트에 실시간 다중 정렬 기능 탑재 (`templates/index.html` 기능 추가)
* 시총 순으로 보기, 상승률 순으로 보기, 과열도(Z-Score) 순으로 보기 옵션 3종 동적 정렬 지원

### 수정 파일

* templates/index.html
* ver.md

### 비고

* 프론트엔드 실시간 정렬 제어 지원 릴리즈 완료

## v1.3.0

Date: 2026-07-07

### 변경 내용

* 대시보드 UI/UX 전면 직관성 극대화 리뉴얼 (`templates/index.html` 재설계)
* 최상단 3단 의사결정 나침반 카드 연동 (1. 시장 상태 해설 / 2. 🚨 즉시 매도 권장 및 과열주 노출 / 3. 🟢 저점 분할 매수 적기 종목 목록 노출)
* 50대 우량주 정보에서 매수/매도 대기 추천 상태를 필터링 바인딩하여 직관적인 조치 가이드 텍스트 자동 출력

### 수정 파일

* templates/index.html
* ver.md

### 비고

* 대시보드 로컬호스트 직관성 보강 릴리즈 완료

## v1.2.3

Date: 2026-07-07

### 변경 내용

* 브라우저 Unsafe Port 차단(ERR_UNSAFE_PORT) 회피 조치 (대시보드 기동 포트를 6666에서 9000으로 안전 포트 변경)

### 수정 파일

* app.py
* ver.md

### 비고

* 로컬호스트 포트 9000 정상 구동 완료

## v1.2.2

Date: 2026-07-07

### 변경 내용

* yfinance 일괄 다운로드 데드락(수집 블로킹) 현상 완전 해결 (개별 Ticker 순차 수집 및 3초 타임아웃 세이프가드 필터 구현)

### 수정 파일

* collector.py
* ver.md

### 비고

* 대시보드 로컬호스트 정상 로드 및 캐시 갱신 완료 (v1.2.2 최종 패치)

## v1.2.0

Date: 2026-07-07

### 변경 내용

* 포트 6666 웹 대시보드 인터페이스 구현 및 탑재 (Flask 웹 서버 적용)
* 프리미엄 다크 모드 및 글래스모피즘이 적용된 실시간 시그널/백테스트 웹 화면 구축 (`templates/index.html` 구현)
* 백그라운드 데이터 수집 캐싱 아키텍처 도입 (웹 로딩 속도 최적화)

### 수정 파일

* app.py (신규)
* templates/index.html (신규)
* requirements.txt
* ver.md

### 비고

* 로컬호스트 포트 6666 구동 검증 완료

## v1.1.0

Date: 2026-07-07

### 변경 내용

* 가상 서버 배포 자동화 및 백그라운드 구동 환경 추가 (VM 배포 쉘 스크립트 및 systemd 서비스 템플릿 구현)
* 환경 변수 구성용 `.env.example` 템플릿 신규 지원
* 로컬호스트 실행 검증 완료 (`main.py schedule` 로컬 가동 테스트)

### 수정 파일

* gokospi.service (신규)
* deploy.sh (신규)
* .env.example (신규)
* ver.md

### 비고

* 16단계 전체 자동 구축 완료 및 가상 서버 배포 준비 완료

## v1.0.5

Date: 2026-07-07

### 변경 내용

* VS Code 내 파이썬 인터프리터 경로 수동 설정 무력화 현상 해결 (`.vscode/settings.json` 내 `"python.defaultInterpreterPath"` 키를 완전히 제거하여 VS Code 자체 시스템 자동 감지(Auto-detect) 알고리즘을 타도록 조치)

### 수정 파일

* .vscode/settings.json
* ver.md

### 비고

* 인터프리터 자동 탐지 가이드 적용

## v1.0.4

Date: 2026-07-07

### 변경 내용

* 가상환경 내 심볼릭 링크 해석 보안 제한에 따른 인터프리터 오류 해결 (`.vscode/settings.json` 내 인터프리터를 홈브루 시스템 파이썬 `/opt/homebrew/bin/python3`으로 지정하고 가상환경 패키지 폴더를 `extraPaths`에 수동 맵핑)

### 수정 파일

* .vscode/settings.json
* ver.md

### 비고

* 시스템 파이썬 + 가상환경 extraPaths 연동으로 인터프리터 경고 최종 차단 완료

## v1.0.3

Date: 2026-07-07

### 변경 내용

* VS Code 멀티 워크스페이스 구조에서의 경로 해석 오류 해결 (`.vscode/settings.json` 내 인터프리터 경로를 완전 절대 경로인 `/Users/l/project/goKOSPI/venv/bin/python`으로 고정)

### 수정 파일

* .vscode/settings.json
* ver.md

### 비고

* 절대 경로 적용을 통한 인터프리터 해소 완료

## v1.0.2

Date: 2026-07-07

### 변경 내용

* VS Code 설정 변수 `${workspaceFolder}` 미인식 오류 해결 (`.vscode/settings.json` 내 인터프리터 경로를 상대 경로인 `./venv/bin/python`으로 변경)

### 수정 파일

* .vscode/settings.json
* ver.md

### 비고

* VS Code 환경 변수 미해석 문제 조치 완료

## v1.0.1

Date: 2026-07-07

### 변경 내용

* VS Code Python 인터프리터 경로 오류 해결 (`.vscode/settings.json` 내 인터프리터를 가상환경 경로로 변경)

### 수정 파일

* .vscode/settings.json
* ver.md

### 비고

* VS Code 환경 에러 조치 완료

## v1.0.0

Date: 2026-07-07

### 변경 내용

* goKOSPI 리밸런싱 패턴 추적 시스템 전체 구현 완료 (DAY 5 ~ DAY 16)
* 50대 우량 종목 및 코스피 지수 데이터 수집기 구현 (Python `yfinance` 연동)
* ATR 및 가중 누적 변동성 기반 과열/조정 신호 엔진 탑재
* 디스코드 웹훅 연동 실시간 경보 메시지 송출 모듈 구축
* 과거 3개년 시뮬레이션용 로컬 백테스터 완성 및 검증

### 수정 파일

* requirements.txt
* collector.py
* engine.py
* notifier.py
* backtest.py
* main.py
* ver.md

### 비고

* 백테스트 검증 및 디스코드 연동 테스트 완료 (v1.0.0 최종 릴리즈)

## v0.1.0

Date: 2026-07-07

### 변경 내용

* goKOSPI 프로젝트 16일 로드맵 기반 기획 설계
* DAY 1~4 단계별 기획 산출물 마크다운 문서 생성

### 수정 파일

* ver.md
* docs/01-day1-문제후보도출.md
* docs/02-day2-문제확정-비전수립.md
* docs/02-problem.md
* docs/02-vision.md
* docs/03-day3-시나리오-성공기준.md
* docs/03-scenario.md
* docs/03-success.md
* docs/04-day4-기능목록-PRD.md
* docs/04-features.md
* docs/04-prd.md

### 비고

* 기획 단계 완료
