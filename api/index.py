from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from calendar import fetch_team_ics
from urllib.parse import quote

app = FastAPI(title="Football Calendar API")

# 开启跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/api/calendar")
def get_calendar(team_id: str, team_name: str = "球队"):
    ics_data = fetch_team_ics(team_id, team_name)
    if ics_data is None:
        return Response(content="Service Error", status_code=500)
    
    safe_filename = quote(f"{team_name}.ics")
    return Response(
        content=ics_data,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )