import requests
from typing import Dict, Any, List

def send_discord_webhook(webhook_url: str, payload: Dict[str, Any]) -> bool:
    """
    디스코드 웹훅 주소로 포맷팅된 JSON 데이터를 전송합니다.
    """
    if not webhook_url:
        print("[!] Discord Webhook URL이 설정되지 않아 알림 전송을 스킵하고 콘솔에만 출력합니다.")
        return False
        
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code in [200, 204]:
            return True
        else:
            print(f"[!] 디스코드 알림 전송 실패 (상태 코드: {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"[!] 디스코드 전송 예외 발생: {e}")
        return False

def make_signal_embed(analysis: Dict[str, Any], name: str) -> Dict[str, Any]:
    """
    분석 신호 데이터를 기반으로 디스코드에 전송할 Embed 오브젝트를 빌드합니다.
    """
    ticker = analysis["ticker"]
    close = analysis["close"]
    change = analysis["change_pct"]
    z_score = analysis["z_score"]
    vol_ratio = analysis["vol_ratio"]
    signal = analysis["signal"]
    
    # 한국 통화 서식
    price_str = f"{int(close):,}원" if close >= 100 else f"{close:.2f}달러/원"

    if signal == "OVERHEAT":
        title = f"🚨 [과열/리밸런싱 경보] {name} ({ticker})"
        description = f"**{name}** 종목이 단기 급등하여 **과열 임계치**에 도달했습니다. 향후 2~3일 내 리밸런싱 조정이 개시될 확률이 매우 높습니다."
        color = 16711680  # Red
        fields = [
            {"name": "현재가", "value": price_str, "inline": True},
            {"name": "당일 변동률", "value": f"{change:+.2f}%", "inline": True},
            {"name": "3일 가중 상승률", "value": f"{analysis['sc_pct']:+.2f}%", "inline": True},
            {"name": "변동성 대비 배율 (Z-Score)", "value": f"{z_score:.2f} (기준: 2.5)", "inline": True},
            {"name": "20일 평균 대비 거래량", "value": f"{vol_ratio * 100:.1f}%", "inline": True},
            {"name": "권장 가이드", "value": "💡 추격 매수 자제 및 보유 비중의 20~30% 분할 현금화 권장", "inline": False}
        ]
    elif signal == "REBALANCED":
        title = f"🟢 [리밸런싱 조정 완료] {name} ({ticker})"
        description = f"**{name}** 종목이 과열 발생 후 충분한 조정을 거쳐 **리밸런싱 완료 영역**에 도달했습니다. 재상승 추세 복귀 가능성이 큽니다."
        color = 65280  # Green
        drawdown = analysis["drawdown_pct"]
        fields = [
            {"name": "현재가", "value": price_str, "inline": True},
            {"name": "당일 변동률", "value": f"{change:+.2f}%", "inline": True},
            {"name": "고점 대비 조정폭", "value": f"-{drawdown:.2f}% (목표: -4.5%)", "inline": True},
            {"name": "리밸런싱 전 최고 종가", "value": f"{int(analysis['peak_close']):,}원", "inline": True},
            {"name": "20일 평균 대비 거래량", "value": f"{vol_ratio * 100:.1f}%", "inline": True},
            {"name": "권장 가이드", "value": "💡 확보했던 현금을 활용하여 저점 분할 재진입/추가 매수 추천", "inline": False}
        ]
    else:
        # 일반 현황 (디버그/콘솔용)
        title = f"ℹ️ [모니터링 정보] {name} ({ticker})"
        description = "현재 정상 변동 범위 내에서 움직이고 있습니다."
        color = 3447003  # Blue
        fields = []

    return {
        "title": title,
        "description": description,
        "color": color,
        "fields": fields,
        "footer": {
            "text": f"goKOSPI 리밸런싱 경보 시스템 • {analysis['date']}"
        }
    }

def notify_signal(webhook_url: str, analysis: Dict[str, Any], name: str) -> bool:
    """
    신호를 디스코드 웹훅으로 최종 포맷팅하여 발송합니다. (새로운 신호가 생성된 경우에만 권장)
    """
    # HOLD 상태면 알림을 보내지 않음
    if analysis["signal"] not in ["OVERHEAT", "REBALANCED"]:
        return False
        
    embed = make_signal_embed(analysis, name)
    payload = {
        "username": "goKOSPI 봇",
        "avatar_url": "https://i.imgur.com/2K1N2vU.png", # 가상 프로필 이미지
        "embeds": [embed]
    }
    
    print(f"[*] {name} ({analysis['ticker']}) - [{analysis['signal']}] 신호 발생! 알림 송출 시도...")
    return send_discord_webhook(webhook_url, payload)

def notify_system_status(webhook_url: str, message: str, is_error: bool = False) -> bool:
    """
    시스템 구동 정보 또는 에러 상태를 디코드로 알립니다.
    """
    color = 16776960 if is_error else 3447003 # Yellow(Error) or Blue(Info)
    title = "⚠️ [goKOSPI 시스템 오류]" if is_error else "📢 [goKOSPI 시스템 상태 알림]"
    
    embed = {
        "title": title,
        "description": message,
        "color": color,
        "footer": {
            "text": "goKOSPI 관리 엔진"
        }
    }
    payload = {
        "username": "goKOSPI 관리자",
        "embeds": [embed]
    }
    return send_discord_webhook(webhook_url, payload)
