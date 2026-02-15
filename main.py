from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import hashlib
from urllib.parse import quote

app = FastAPI()

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def fetch_team_ics(team_id: str, team_name: str):
    url = f"https://www.dongqiudi.com/team/{team_id}.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        matches = soup.find_all('div', class_='match-item')
    except Exception as e:
        print(f"抓取失败: {e}")
        return None

    # 初始化 ICS 文件头 (严格遵守 RFC 5545 规范)
    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//OpenSource//FootballCalendar//{team_name}//CN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{team_name}赛程",
        f"X-WR-CALDESC:{team_name}最新赛程及比分同步工具",
        "X-WR-TIMEZONE:Asia/Shanghai",
        "X-PUBLISHED-TTL:PT12H",
        "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
        "BEGIN:VTIMEZONE",
        "TZID:Asia/Shanghai",
        "X-LIC-LOCATION:Asia/Shanghai",
        "BEGIN:STANDARD",
        "TZOFFSETFROM:+0800",
        "TZOFFSETTO:+0800",
        "TZNAME:CST",
        "DTSTART:19700101T000000",
        "END:STANDARD",
        "END:VTIMEZONE"
    ]
    
    current_year = datetime.now().year
    current_month = datetime.now().month
    dt_stamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    
    if matches:
        for match in matches:
            try:
                date_node = match.find('span', class_='date')
                round_node = match.find('span', class_='round')
                team_a_node = match.find('p', class_='team-a')
                team_b_node = match.find('p', class_='team-b')
                
                if not (date_node and team_a_node and team_b_node): continue
                    
                date_str = date_node.text.strip() # 示例: "02-16 04:00"
                if len(date_str) < 11: continue
                    
                # 跨年逻辑推算
                m_month = int(date_str.split('-')[0])
                m_year = current_year
                if current_month > 10 and m_month < 6: m_year = current_year + 1
                elif current_month < 3 and m_month > 6: m_year = current_year - 1
                    
                round_name = round_node.text.strip() if round_node else "比赛"
                home_team = team_a_node.find('span', class_='teama-name').text.strip()
                away_team = team_b_node.find('span', class_='teamb-name').text.strip()
                
                start_dt = datetime.strptime(f"{m_year}-{date_str}", "%Y-%m-%d %H:%M")
                end_dt = start_dt + timedelta(hours=2)
                
                # 唯一标识符，防止重复
                uid_hash = hashlib.md5(f"{m_year}-{date_str}-{home_team}-{away_team}".encode('utf-8')).hexdigest()
                
                ics_content.extend([
                    "BEGIN:VEVENT",
                    f"UID:match-{uid_hash}@football-cal",
                    f"DTSTAMP:{dt_stamp}",
                    f"DTSTART;TZID=Asia/Shanghai:{start_dt.strftime('%Y%m%dT%H%M00')}",
                    f"DTEND;TZID=Asia/Shanghai:{end_dt.strftime('%Y%m%dT%H%M00')}",
                    f"SUMMARY:{home_team} vs {away_team} ({round_name})",
                    f"DESCRIPTION:赛事类型: {round_name}\\n数据同步时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    "END:VEVENT"
                ])
            except:
                continue
            
    ics_content.append("END:VCALENDAR")
    
    # ✅ 必须使用 \r\n 换行，否则苹果日历会报错
    return "\r\n".join(ics_content) + "\r\n"

@app.get("/")
def home():
    return {"status": "running", "project": "Football Calendar Generator"}

@app.get("/api/calendar")
def get_calendar(team_id: str, team_name: str = "球队"):
    ics_data = fetch_team_ics(team_id, team_name)
    
    if ics_data is None:
        return Response(content="Service Error", status_code=500)
    
    # 编码文件名，防止 Safari 解析错误
    safe_filename = quote(f"{team_name}.ics")
    
    return Response(
        content=ics_data, 
        media_type="text/calendar; charset=utf-8",
        headers={
            # inline 触发跳转订阅，不弹出下载框
            "Content-Disposition": f'inline; filename="{safe_filename}"',
            # 彻底禁用缓存，确保每次都是最新赛程
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )