#!/bin/bash

# goKOSPI Oracle Cloud VM 배포 자동화 스크립트
# 본 스크립트는 가상 서버(VM) 내부의 프로젝트 루트 폴더에서 실행됩니다.

echo "=================================================="
echo "         goKOSPI VM 자동 배포 및 시동 시작"
echo "=================================================="

# 1. 최신 소스 코드 가져오기
echo "[*] GitHub 최신 소스 동기화..."
git pull origin main

# 2. 파이썬 가상환경 설정
if [ ! -d "venv" ]; then
    echo "[*] 파이썬 가상환경(venv) 생성 중..."
    python3 -m venv venv
fi

echo "[*] 종속성 라이브러리 설치/업데이트..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 3. 환경 변수 파일(.env) 존재 여부 체크
if [ ! -f ".env" ]; then
    echo "[!] .env 파일이 존재하지 않습니다. .env.example 복사본을 생성합니다."
    cp .env.example .env
    echo "[!] 배포 완료 후 반드시 .env 파일을 편집하여 DISCORD_WEBHOOK_URL을 입력하십시오."
fi

# 4. Systemd 서비스 파일 셋업
echo "[*] Systemd 서비스 설정 구성 중..."
CURRENT_DIR=$(pwd)
CURRENT_USER=$(whoami)

# gokospi.service 템플릿 내의 플레이스홀더 치환
sed -e "s|__DIR__|${CURRENT_DIR}|g" \
    -e "s|__USER__|${CURRENT_USER}|g" \
    gokospi.service > tmp_gokospi.service

# 서비스를 systemd 경로로 이동 (sudo 권한 필요)
echo "[*] Systemd 서비스 등록 시도 (비밀번호를 물어볼 수 있습니다)..."
sudo mv tmp_gokospi.service /etc/systemd/system/gokospi.service
sudo chown root:root /etc/systemd/system/gokospi.service
sudo chmod 644 /etc/systemd/system/gokospi.service

# 서비스 데몬 재로드 및 재시작
echo "[*] Systemd 서비스 등록 완료. 백그라운드 구동 시작..."
sudo systemctl daemon-reload
sudo systemctl enable gokospi.service
sudo systemctl restart gokospi.service

echo "=================================================="
echo "  goKOSPI 배포 완료! (상태 확인: sudo systemctl status gokospi)"
echo "=================================================="
