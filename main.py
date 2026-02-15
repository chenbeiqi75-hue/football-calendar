from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import hashlib
from urllib.parse import quote
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Football Calendar API",
    version="1.0.0",
    description="足球赛程日历生成器 - 自动同步改期、延期"
)

# 开启跨域，确保前端预览功能正常
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# 网络请求超时配置
REQUEST_TIMEOUT = 10
MAX_RETRIES = 2

def fetch_team_ics_internal(team_id: str, team_name: str):
    """
    从懂球帝网站抓取球队赛程，生成 ICS 日历格式
    
    Args:
        team_id: 球队在懂球帝的 ID
        team_name: 球队名称
    
    Returns:
        ICS 格式的日历内容，或 None（失败时）
    """
    url = f"https://www.dongqiudi.com/team/{team_id}.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    matches = []
    
    # 带重试的网络请求
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"[{team_name}] 正在抓取赛程 (尝试 {attempt + 1}/{MAX_RETRIES})")
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            matches = soup.find_all('div', class_='match-item')
            logger.info(f"[{team_name}] 成功抓取，找到 {len(matches)} 场比赛")
            break
            
        except requests.exceptions.Timeout:
            logger.warning(f"[{team_name}] 网络超时 (尝试 {attempt + 1}/{MAX_RETRIES})")
            if attempt == MAX_RETRIES - 1:
                logger.error(f"[{team_name}] 最终失败：网络超时")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"[{team_name}] 网络错误: {str(e)} (尝试 {attempt + 1}/{MAX_RETRIES})")
            if attempt == MAX_RETRIES - 1:
                logger.error(f"[{team_name}] 最终失败：网络错误")
                return None
                
        except Exception as e:
            logger.error(f"[{team_name}] 未预期的错误: {str(e)}")
            return None

    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//OpenSource//FootballCalendar//{team_name}//CN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{team_name}赛程",
        "X-WR-TIMEZONE:Asia/Shanghai",
        "X-WR-CALDESC:自动同步改期、延期",
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
        logger.warning(f"[{team_name}] 暂无赛程数据，添加占位事件")
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
        # 解析比赛信息
        event_count = 0
        for match in matches:
            try:
                date_node = match.find('span', class_='date')
                team_a_elem = match.find('p', class_='team-a')
                team_b_elem = match.find('p', class_='team-b')
                
                # 验证数据完整性
                if not all([date_node, team_a_elem, team_b_elem]):
                    continue
                    
                team_a = team_a_elem.find('span').text.strip()
                team_b = team_b_elem.find('span').text.strip()
                date_str = date_node.text.strip()
                
                # 针对 2026 赛季的时间逻辑
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
                    "STATUS:CONFIRMED",
                    "END:VEVENT"
                ])
                event_count += 1
                
            except Exception as e:
                logger.warning(f"[{team_name}] 解析比赛失败: {str(e)}")
                continue
        
        logger.info(f"[{team_name}] 成功添加 {event_count} 场比赛到日历")

    ics_content.append("END:VCALENDAR")
    return "\r\n".join(ics_content) + "\r\n"

@app.get("/api/calendar")
def get_calendar(team_id: str = None, team_name: str = "球队"):
    """
    生成并返回球队赛程的 ICS 日历文件
    
    查询参数:
        team_id (str): 必需，球队在懂球帝的 ID
        team_name (str): 可选，球队名称（用于文件名和日历标题）
    
    返回:
        ICS 格式的日历文件或错误提示
    """
    if not team_id:
        logger.warning("缺少必要参数: team_id")
        return Response(content="Missing team_id parameter", status_code=400)
    
    logger.info(f"请求日历: team_id={team_id}, team_name={team_name}")
    
    ics_data = fetch_team_ics_internal(team_id, team_name)
    if ics_data is None:
        logger.error(f"生成日历失败: team_id={team_id}")
        return Response(
            content="Failed to fetch schedule data. Please check team_id and try again.",
            status_code=500
        )
    
    safe_filename = quote(f"{team_name}.ics")
    logger.info(f"成功生成日历: {safe_filename}")
    
    return Response(
        content=ics_data,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'inline; filename="{safe_filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@app.get("/")
def root():
    """
    根路径重定向到 index.html（Vercel 会处理）
    """
    return {"message": "Football Calendar API - Use /api/calendar endpoint"}


@app.get("/health")
def health_check():
    """
    健康检查端点
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    全局异常处理器
    """
    logger.error(f"未捕获的异常: {str(exc)}", exc_info=True)
    return Response(
        content="Internal server error",
        status_code=500
    )