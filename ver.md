# Version History

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
