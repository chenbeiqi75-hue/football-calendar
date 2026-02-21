# Football Calendar

一个基于 FastAPI + 静态前端的足球赛程日历生成器。  
支持通过懂球帝抓取球队赛程，生成可订阅的 ICS 日历，并可一键导入到 iOS/Mac、Google Calendar、Outlook。

## 功能

- 按联赛、球队选择并生成赛程订阅链接
- 通过懂球帝抓取球队赛程
- 输出 ICS 日历（支持共享订阅）
- 支持：
  - `webcal://`（iOS / macOS 日历）
  - Google Calendar 导入
  - Outlook 导入
  - 直接下载 `.ics`
- 前端显示近期赛程预览
- 抓取失败时返回明确错误信息（超时、DNS 失败、网络错误等）

## 技术栈

- 后端：FastAPI
- 抓取：requests + BeautifulSoup4
- 前端：Vue 3（CDN）+ Tailwind（CDN）
- 部署：Vercel（Python Serverless Function + 静态页面）

## 项目结构

```text
.
├── api/
│   └── index.py          # Vercel Python Function 入口
├── index.html            # 前端页面
├── main.py               # FastAPI 主服务
├── requirements.txt      # Python 依赖
└── vercel.json           # Vercel 路由与函数配置
```

## 本地运行

### 1) 安装依赖

```bash
pip install -r requirements.txt
```

### 2) 启动后端

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3) 打开前端

- 推荐：通过 HTTP 服务访问（而不是直接双击 `file://`）
- 若直接打开 `index.html`，前端会默认请求 `http://localhost:8000`

## API

### `GET /api/health`

健康检查。

返回示例：

```json
{
  "status": "healthy",
  "timestamp": "2026-02-21T12:34:56.000000"
}
```

### `GET /api/preview`

获取球队赛程预览（JSON）。

查询参数：

- `team_id` (必填)：懂球帝球队 ID
- `team_name` (可选)：球队名称，默认 `球队`
- `limit` (可选)：返回条数，默认 `5`，范围 `1-20`

成功返回示例：

```json
{
  "team_id": "50000516",
  "team_name": "利物浦",
  "matches": [
    {
      "summary": "利物浦 vs 曼联",
      "date": "03-12 20:00",
      "start_iso": "2026-03-12T20:00:00"
    }
  ]
}
```

失败返回示例：

```json
{
  "error": "FETCH_FAILED",
  "error_code": "DNS_RESOLUTION_FAILED",
  "message": "服务器无法解析懂球帝域名，当前网络环境不可达。"
}
```

### `GET /api/calendar`

生成 ICS 日历。

查询参数：

- `team_id` (必填)：懂球帝球队 ID
- `team_name` (可选)：球队名称，默认 `球队`
- `download` (可选)：`1` 时下载附件；默认 `0`（inline）

示例：

```text
/api/calendar?team_id=50000516&team_name=利物浦
/api/calendar?team_id=50000516&team_name=利物浦&download=1
```

## Vercel 部署

### 1) 推送代码到 GitHub

确保包含以下关键文件：

- `api/index.py`
- `main.py`
- `index.html`
- `requirements.txt`
- `vercel.json`

### 2) 在 Vercel 导入项目

- Framework Preset：Other
- Root Directory：仓库根目录
- Build/Install 由 Vercel Python Runtime 自动处理

### 3) 路由说明

`vercel.json` 已配置：

- `/api/*` 转发到 `api/index.py`
- 其他路径转发到 `index.html`

## 常见问题

### 1) 前端提示 `Failed to fetch` / 无法连接接口

先访问：

- 线上：`https://你的域名/api/health`
- 本地：`http://localhost:8000/api/health`

若健康检查不通，说明是 API 部署或网络问题，不是赛程数据问题。

### 2) 页面显示 `file:///api/health`

这是 `file://` 打开页面导致的。  
请改为：

- 启动本地后端后访问 `http://localhost:8000`（或用静态服务器启动前端）
- 或直接用 Vercel 域名访问

### 3) Vercel 报错 `Function Runtimes must have a valid version`

这是旧 `runtime` 字段写法导致。  
当前配置已移除不兼容 runtime 写法，保留函数配置即可。

### 4) 抓不到赛程

可能原因：

- 懂球帝临时不可达
- 目标环境 DNS/网络限制
- 目标页面结构变更

可先看 `/api/preview` 返回的 `error_code` 和 `message`。

## 环境变量（可选）

在 `.env` 或部署平台中设置：

- `REQUEST_TIMEOUT`：请求超时秒数（默认 `10`）
- `MAX_RETRIES`：重试次数（默认 `2`）
- `CACHE_TTL_SECONDS`：赛程缓存秒数（默认 `600`）

## License

MIT
