# Version History

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
