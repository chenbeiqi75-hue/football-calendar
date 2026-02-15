from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import hashlib
from urllib.parse import quote

app = FastAPI(title="Football Calendar API")

# 开启跨域，确保前端网页预览功能正常
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

def fetch_team_ics_internal(team_id: str, team_name: str):
    """
    内部爬虫逻辑：抓取赛程并生成标准的 ICS 文本
    """
    url = f"https://www.dongqiudi.com/team/{team_id}.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        matches = soup.find_all('div', class_='match-item')
    except Exception:
        return None

    # 初始化 ICS 文件头
    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//OpenSource//FootballCalendar//{team_name}//CN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{team_name}赛程",
        "X-WR-TIMEZONE:Asia/Shanghai",
        "BEGIN:VTIMEZONE",
        "TZID:Asia/Shanghai",
        "BEGIN:STANDARD",
        "TZOFFSETFROM:+0800",
        "TZOFFSETTO:+0800",
        "TZNAME:CST",
        "DTSTART:19700101T000000",
        "END:STANDARD",
        "END:VTIMEZONE"
    ]
    
    dt_stamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    
    # 保底逻辑：若无赛程，添加占位事件防止 iOS 报错
    if not matches:
        ics_content.extend([
            "BEGIN:VEVENT",
            f"UID:placeholder-{team_id}@football-cal",
            f"DTSTAMP:{dt_stamp}",
            f"DTSTART;TZID=Asia/Shanghai:{datetime.now().strftime('%Y%m%dT%H%M00')}",
            f"DTEND;TZID=Asia/Shanghai:{(datetime.now() + timedelta(hours=1)).strftime('%Y%m%dT%H%M00')}",
            "SUMMARY:【系统消息】赛程待更新",
            "DESCRIPTION:目前数据源中暂无该球队最新赛程数据。",
            "END:VEVENT"
        ])
    else:
        for match in matches:
            try:
                date_node = match.find('span', class_='date')
                team_a = match.find('p', class_='team-a').find('span').text.strip()
                team_b = match.find('p', class_='team-b').find('span').text.strip()
                if not date_node: continue
                
                date_str = date_node.text.strip()
                m_year = datetime.now().year
                start_dt = datetime.strptime(f"{m_year}-{date_str}", "%Y-%m-%d %H:%M")
                uid = hashlib.md5(f"{date_str}{team_a}{team_b}".encode()).hexdigest()
                
                ics_content.extend([
                    "BEGIN:VEVENT",
                    f"UID:match-{uid}@football-cal",
                    f"DTSTAMP:{dt_stamp}",
                    f"DTSTART;TZID=Asia/Shanghai:{start_dt.strftime('%Y%m%dT%H%M00')}",
                    f"DTEND;TZID=Asia/Shanghai:{(start_dt + timedelta(hours=2)).strftime('%Y%m%dT%H%M00')}",
                    f"SUMMARY:{team_a} vs {team_b}",
                    "END:VEVENT"
                ])
            except Exception:
                continue

    ics_content.append("END:VCALENDAR")
    # ✅ 必须使用 \r\n，且严禁删除换行符，否则 iOS 会提示数据无效
    return "\r\n".join(ics_content) + "\r\n"

@app.get("/api/calendar")
def get_calendar(team_id: str = None, team_name: str = "球队"):
    # 预防 422 错误：检查参数
    if not team_id:
        return Response(content="Missing team_id parameter", status_code=400)
        
    ics_data = fetch_team_ics_internal(team_id, team_name)
    if ics_data is None:
        return Response(content="Scraper Error", status_code=500)
    
    safe_filename = quote(f"{team_name}.ics")
    return Response(
        content=ics_data,
        media_type="text/calendar; charset=utf-8",
        headers={
            # ✅ 改为 inline，对 iOS 唤起订阅更友好
            "Content-Disposition": f'inline; filename="{safe_filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )