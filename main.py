from fastapi import FastAPI, Query, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import hashlib
from urllib.parse import quote
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Football Calendar API",
    version="1.1.0",
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
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "600"))

_schedule_cache: Dict[str, Dict] = {}

ERROR_MESSAGES = {
    "TIMEOUT": "抓取懂球帝赛程超时，请稍后重试。",
    "DNS_RESOLUTION_FAILED": "服务器无法解析懂球帝域名，当前网络环境不可达。",
    "NETWORK_ERROR": "抓取懂球帝赛程时发生网络错误。",
    "UNEXPECTED_ERROR": "抓取赛程时发生未预期错误。",
    "UPSTREAM_UNAVAILABLE": "懂球帝暂时不可用或返回异常页面。",
}


def _ics_escape(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(",", "\\,")
        .replace(";", "\\;")
    )


def _infer_match_datetime(raw_date: str, now: datetime) -> Optional[datetime]:
    """
    把懂球帝常见的 MM-DD HH:MM 转成 datetime，带跨年修正。
    """
    try:
        parsed = datetime.strptime(raw_date, "%m-%d %H:%M")
    except ValueError:
        return None

    year = now.year
    # 跨赛季修正：当前月很小而比赛月很大，判定为上一年；反之为下一年。
    if now.month <= 2 and parsed.month >= 10:
        year -= 1
    elif now.month >= 10 and parsed.month <= 2:
        year += 1
    return datetime(year, parsed.month, parsed.day, parsed.hour, parsed.minute)


def _extract_matches_from_html(soup: BeautifulSoup, now: datetime) -> List[Dict]:
    """
    优先解析 DOM 结构；若页面样式更新，可继续向后兼容扩展。
    """
    raw_matches: List[Dict] = []
    candidate_items = soup.select("div.match-item, li.match-item")

    for item in candidate_items:
        date_node = item.select_one("span.date")
        team_a_node = item.select_one("p.team-a span")
        team_b_node = item.select_one("p.team-b span")
        if not (date_node and team_a_node and team_b_node):
            continue
        raw_date = date_node.get_text(strip=True)
        start_dt = _infer_match_datetime(raw_date, now)
        if not start_dt:
            continue

        team_a = team_a_node.get_text(strip=True)
        team_b = team_b_node.get_text(strip=True)
        raw_matches.append(
            {
                "start_dt": start_dt,
                "team_a": team_a,
                "team_b": team_b,
                "summary": f"{team_a} vs {team_b}",
            }
        )

    raw_matches.sort(key=lambda x: x["start_dt"])
    return raw_matches


def fetch_team_schedule(team_id: str, team_name: str) -> Dict[str, Any]:
    """
    从懂球帝抓取球队赛程（结构化结果）。
    """
    cache_key = f"{team_id}:{team_name}"
    cache_hit = _schedule_cache.get(cache_key)
    now = datetime.now()
    if cache_hit and cache_hit["expires_at"] > now:
        return {"ok": True, "matches": cache_hit["matches"]}

    url = f"https://www.dongqiudi.com/team/{team_id}.html"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    matches: List[Dict] = []
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"[{team_name}] 正在抓取赛程 (尝试 {attempt + 1}/{MAX_RETRIES})")
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            response.encoding = "utf-8"

            soup = BeautifulSoup(response.text, "html.parser")
            matches = _extract_matches_from_html(soup, now)
            logger.info(f"[{team_name}] 抓取完成，解析到 {len(matches)} 场比赛")
            break
        except requests.exceptions.Timeout:
            logger.warning(f"[{team_name}] 网络超时 (尝试 {attempt + 1}/{MAX_RETRIES})")
            if attempt == MAX_RETRIES - 1:
                logger.error(f"[{team_name}] 最终失败：网络超时")
                return {
                    "ok": False,
                    "error_code": "TIMEOUT",
                    "error_message": ERROR_MESSAGES["TIMEOUT"],
                }
        except requests.exceptions.RequestException as exc:
            logger.warning(f"[{team_name}] 网络错误: {exc} (尝试 {attempt + 1}/{MAX_RETRIES})")
            if attempt == MAX_RETRIES - 1:
                logger.error(f"[{team_name}] 最终失败：网络错误")
                error_code = "DNS_RESOLUTION_FAILED" if "Failed to resolve" in str(exc) else "NETWORK_ERROR"
                return {
                    "ok": False,
                    "error_code": error_code,
                    "error_message": ERROR_MESSAGES[error_code],
                }
        except Exception as exc:
            logger.error(f"[{team_name}] 未预期错误: {exc}", exc_info=True)
            return {
                "ok": False,
                "error_code": "UNEXPECTED_ERROR",
                "error_message": ERROR_MESSAGES["UNEXPECTED_ERROR"],
            }

    _schedule_cache[cache_key] = {
        "matches": matches,
        "expires_at": datetime.now() + timedelta(seconds=CACHE_TTL_SECONDS),
    }
    return {"ok": True, "matches": matches}


def fetch_team_ics_internal(team_id: str, team_name: str) -> Tuple[Optional[str], Optional[Dict[str, str]]]:
    """
    从懂球帝网站抓取球队赛程，生成 ICS 日历格式
    
    Args:
        team_id: 球队在懂球帝的 ID
        team_name: 球队名称
    
    Returns:
        ICS 格式的日历内容，或 None（失败时）
    """
    schedule_result = fetch_team_schedule(team_id, team_name)
    if not schedule_result["ok"]:
        return None, {
            "error_code": schedule_result["error_code"],
            "error_message": schedule_result["error_message"],
        }
    matches = schedule_result["matches"]

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
    
    dt_stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    
    # 保底逻辑：若无赛程，添加占位事件防止 iOS 报错
    if len(matches) == 0:
        logger.warning(f"[{team_name}] 暂无赛程数据，添加占位事件")
        ics_content.extend([
            "BEGIN:VEVENT",
            f"UID:placeholder-{team_id}@football-cal",
            f"DTSTAMP:{dt_stamp}",
            f"DTSTART;TZID=Asia/Shanghai:{datetime.now().strftime('%Y%m%dT%H%M00')}",
            f"DTEND;TZID=Asia/Shanghai:{(datetime.now() + timedelta(hours=1)).strftime('%Y%m%dT%H%M00')}",
            "SUMMARY:【系统消息】赛程待更新",
            f"DESCRIPTION:{_ics_escape('目前数据源中暂无该球队最新赛程数据。')}",
            "END:VEVENT"
        ])
    else:
        for match in matches:
            start_dt = match["start_dt"]
            uid_seed = f"{start_dt.isoformat()}-{match['team_a']}-{match['team_b']}"
            uid = hashlib.md5(uid_seed.encode("utf-8")).hexdigest()

            ics_content.extend([
                "BEGIN:VEVENT",
                f"UID:match-{uid}@football-cal",
                f"DTSTAMP:{dt_stamp}",
                f"DTSTART;TZID=Asia/Shanghai:{start_dt.strftime('%Y%m%dT%H%M00')}",
                f"DTEND;TZID=Asia/Shanghai:{(start_dt + timedelta(hours=2)).strftime('%Y%m%dT%H%M00')}",
                f"SUMMARY:{_ics_escape(match['summary'])}",
                f"DESCRIPTION:{_ics_escape(f'数据源: 懂球帝 | 球队: {team_name}')}",
                "STATUS:CONFIRMED",
                "END:VEVENT",
            ])

        logger.info(f"[{team_name}] 成功添加 {len(matches)} 场比赛到日历")

    ics_content.append("END:VCALENDAR")
    return "\r\n".join(ics_content) + "\r\n", None


def build_fallback_ics(team_id: str, team_name: str, reason: str) -> str:
    """
    抓取失败时返回一个合法 ICS，避免 Google/Outlook 因 500 无法添加订阅。
    """
    now = datetime.now()
    dt_stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//OpenSource//FootballCalendar//{team_name}//CN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{team_name}赛程",
        "X-WR-TIMEZONE:Asia/Shanghai",
        "X-WR-CALDESC:抓取失败时自动降级，稍后会继续同步",
        "BEGIN:VTIMEZONE",
        "TZID:Asia/Shanghai",
        "BEGIN:STANDARD",
        "TZOFFSETFROM:+0800",
        "TZOFFSETTO:+0800",
        "TZNAME:CST",
        "DTSTART:19700101T000000",
        "END:STANDARD",
        "END:VTIMEZONE",
        "BEGIN:VEVENT",
        f"UID:fallback-{team_id}@football-cal",
        f"DTSTAMP:{dt_stamp}",
        f"DTSTART;TZID=Asia/Shanghai:{now.strftime('%Y%m%dT%H%M00')}",
        f"DTEND;TZID=Asia/Shanghai:{(now + timedelta(hours=1)).strftime('%Y%m%dT%H%M00')}",
        "SUMMARY:【系统消息】赛程同步中",
        f"DESCRIPTION:{_ics_escape(f'当前抓取失败原因: {reason}。系统将继续自动重试。')}",
        "STATUS:CONFIRMED",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return "\r\n".join(ics_content) + "\r\n"

@app.get("/api/calendar")
def get_calendar(
    team_id: Optional[str] = None,
    team_name: str = "球队",
    download: int = Query(default=0, ge=0, le=1),
    allow_fallback: int = Query(default=1, ge=0, le=1),
):
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
        return JSONResponse(
            status_code=400,
            content={
                "error": "BAD_REQUEST",
                "message": "Missing team_id parameter",
            },
        )
    
    logger.info(f"请求日历: team_id={team_id}, team_name={team_name}")
    
    ics_data, error = fetch_team_ics_internal(team_id, team_name)
    if ics_data is None:
        logger.error(f"生成日历失败: team_id={team_id}")
        if allow_fallback == 1:
            reason = error.get("error_message", ERROR_MESSAGES["UPSTREAM_UNAVAILABLE"])
            ics_data = build_fallback_ics(team_id, team_name, reason)
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "FETCH_FAILED",
                    "error_code": error.get("error_code", "UPSTREAM_UNAVAILABLE"),
                    "message": error.get("error_message", ERROR_MESSAGES["UPSTREAM_UNAVAILABLE"]),
                },
            )
    
    safe_filename = quote(f"{team_name}.ics")
    logger.info(f"成功生成日历: {safe_filename}")
    
    disposition = "attachment" if download == 1 else "inline"
    return Response(
        content=ics_data,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'{disposition}; filename="{safe_filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@app.get("/api/preview")
def get_preview(
    team_id: Optional[str] = None,
    team_name: str = "球队",
    limit: int = Query(default=5, ge=1, le=20),
):
    if not team_id:
        return JSONResponse(
            status_code=400,
            content={
                "error": "BAD_REQUEST",
                "message": "Missing team_id parameter",
            },
        )

    schedule_result = fetch_team_schedule(team_id, team_name)
    if not schedule_result["ok"]:
        return JSONResponse(
            status_code=500,
            content={
                "error": "FETCH_FAILED",
                "error_code": schedule_result["error_code"],
                "message": schedule_result["error_message"],
            },
        )
    matches = schedule_result["matches"]

    preview = []
    for item in matches[:limit]:
        preview.append(
            {
                "summary": item["summary"],
                "date": item["start_dt"].strftime("%m-%d %H:%M"),
                "start_iso": item["start_dt"].isoformat(),
            }
        )
    return {"team_id": team_id, "team_name": team_name, "matches": preview}


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


@app.get("/api/health")
def api_health_check():
    """
    Vercel 下用于前端与运维探活的健康检查端点
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
