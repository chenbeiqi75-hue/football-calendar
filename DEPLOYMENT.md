# 🚀 Vercel 部署指南

本指南将帮你快速部署足球赛程日历生成器到 Vercel。

## 前置条件

- ✅ GitHub 账户（用于部署）或 Vercel 账户
- ✅ 本项目代码已上传到 GitHub

## 方式 A：通过 GitHub 自动部署（推荐 ⭐）

### 为什么推荐这种方式？

- ✅ 最简单：无需配置 GitHub Secrets
- ✅ 最官方：Vercel 官方推荐
- ✅ 最安全：无需暴露 token 到 GitHub
- ✅ 最快：无需 GitHub Actions 编译步骤

### 步骤 1：准备代码

确保项目已上传到 GitHub：

```bash
git add .
git commit -m "完善 Vercel 部署配置"
git push origin main
```

### 步骤 2：连接 Vercel

1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 如果未登录，先使用 GitHub 账户登录
3. 点击 **"Add New"** → **"Project"**

### 步骤 3：选择仓库

1. 在 "Import Git Repository" 中找到你的 `football-calendar` 仓库
2. 如果未显示，点击 "Adjust GitHub App Permissions" 并授予对该仓库的权限
3. 点击 **"Import"**

### 步骤 4：配置项目

Vercel 会自动检测项目配置：

- **Framework Preset**: 选择 "Other"（不涉及 Next.js/Nuxt 等）
- **Build Command**: `pip install -r requirements.txt` （默认，无需改）
- **Output Directory**: 保持空白
- **Environment Variables**: 保持空白（暂无需环境变量）

点击 **"Deploy"** 开始部署。

### 步骤 5：等待部署完成

- 部署通常需要 1-2 分钟
- 查看 **"Deployments"** 标签监控进度
- 部署完成后会显示 ✅

### 步骤 6：获取部署 URL

部署完成后，Vercel 会显示类似以下的可用 URL：

```
https://football-calendar-YOUR-NAME.vercel.app
```

点击此链接即可访问你的应用！

### 步骤 7：配置自定义域名（可选）

1. 进入项目设置："Settings" → "Domains"
2. 点击 "Add" 添加自定义域名
3. 按照指示配置 DNS 记录

### 自动部署配置

完成以上步骤后，每当你推送代码到 GitHub：

```bash
git push origin main
```

Vercel 会自动：
1. ✅ 检测到新推送
2. ✅ 构建项目（安装依赖）
3. ✅ 部署到 Vercel 边缘节点
4. ✅ 生成预览 URL（PR 中显示）

---

## 方式 B（可选）：使用 GitHub Actions + Vercel CLI

此方式在 PR 上自动生成预览链接（仅用于测试，不影响生产部署）。

### 前置条件

1. 已完成方式 A 的初始设置
2. 在 Vercel 获取 token（见方式 C）

### 步骤 1：配置 GitHub Secrets

在 GitHub 仓库设置中添加以下 3 个 Secrets：

- `VERCEL_TOKEN` - 你的 Vercel token
- `VERCEL_ORG_ID` - 你的 Vercel 组织 ID  
- `VERCEL_PROJECT_ID` - 你的 Vercel 项目 ID

**如何获取这些值？** 见详细指南：[VERCEL_SECRETS.md](VERCEL_SECRETS.md)

### 步骤 2：启用可选的 Deploy Workflow

项目包含一个可选的 GitHub Actions workflow：

```
.github/workflows/deploy-vercel-cli.yml.disabled
```

如需启用自动 PR 预览部署：
1. 重命名文件：删除 `.disabled` 后缀
2. Push 到 GitHub
3. 之后每个 PR 都会自动部署预览版本

### 步骤 3：验证

创建测试 PR，应该看到 Vercel 预览链接被评论到 PR 中。

---

## 方式 C：使用 Vercel CLI

如果你更喜欢命令行操作，可以使用 Vercel CLI。

### 步骤 1：安装 Vercel CLI

```bash
npm install -g vercel
```

### 步骤 2：登录 Vercel

```bash
vercel login
```

按照提示使用 GitHub 账户登录。

### 步骤 3：部署项目

在项目根目录运行：

```bash
vercel
```

### 步骤 4：按提示配置

```
? Set up and deploy "~/football-calendar"? [Y/n] Y
? Which scope do you want to deploy to? <Your Account>
? Link to existing project? [y/N] N
? What's your project's name? football-calendar
? In which directory is your code located? ./
? Want to override the settings above? [y/N] N
```

### 步骤 5：引导完成

```
✨ Linked to your-account/football-calendar (created .vercel)
🔍 Inspect: <inspection-url>
✅ Production: <production-url>
```

访问 **Production URL** 即可！

### 后续部署

```bash
# 更新生产环境（需确认）
vercel --prod

# 仅生成预览（用于测试）
vercel
```

---

## 部署方式对比表

| 特性 | 方式 A（推荐）| 方式 B（可选）| 方式 C（CLI）|
|------|----------|----------|-----------|
| 安装复杂度 | ⭐ 最简单 | ⭐⭐ 一般 | ⭐⭐ 一般 |
| 自动部署 | ✅ 自动 | ✅ 自动（PR 预览）| ❌ 手动 |
| 需要 Token | ❌ 否 | ✅ 是 | ✅ 是 |
| 官方推荐 | ✅ 是 | - | ✅ 是 |
| 适用场景 | 大多数用户 | 需要 PR 预览 | 本地开发或自定义 |

---

## 部署后检查清单

部署完成后，请检查：

- [ ] 网站静态页面能正常加载
- [ ] 可以选择联赛和球队
- [ ] 能正常预览赛程
- [ ] 复制链接功能正常
- [ ] iOS 订阅链接能打开日历应用
- [ ] 日历 ICS 文件能正确下载/订阅

### 快速测试 API

在浏览器中打开：

```
https://your-domain.vercel.app/api/calendar?team_id=50000330&team_name=北京国安
```

应返回 ICS 日历内容。

### 测试健康检查

```
https://your-domain.vercel.app/health
```

应返回：
```json
{"status":"healthy","timestamp":"..."}
```

---

## 常见问题排查

### ❌ 部署失败 - "unable to run build command"

**原因**: 缺少 `requirements.txt` 或依赖版本不兼容

**解决**:
1. 确保 `requirements.txt` 存在且包含所有依赖
2. 验证版本号有效：
   ```bash
   pip install -r requirements.txt
   ```
3. 如果本地通过，重新推送到 GitHub 并在 Vercel 重新部署

### ❌ API 返回 500 错误

**原因**: `api/index.py` 导入 `main.py` 失败

**解决**:
1. 检查 `api/index.py` 内容
2. 确认根目录有 `main.py`
3. 查看 Vercel 日志获取详细错误：
   - "Deployments" → 点击部署 → "Logs" 标签
4. 删除 `.vercel` 目录，重新部署：
   ```bash
   rm -rf .vercel
   vercel --prod
   ```

### ❌ 静态页面返回 404

**原因**: `vercel.json` 中的 rewrite 规则配置错误

**解决**:
1. 确认 `vercel.json` 中包含：
   ```json
   {
     "rewrites": [
       { "source": "/(.*)", "destination": "/index.html" }
     ]
   }
   ```
2. 重新部署：`git push origin main`

### ❌ 爬虫无法获取赛程

**原因**: 懂球帝网站可能需要替换 User-Agent 或改用其他数据源

**解决**:
1. 检查 `main.py` 中的 User-Agent
2. 本地测试是否能正常爬取：
   ```bash
   uvicorn main:app --reload
   curl "http://localhost:8000/api/calendar?team_id=50000330"
   ```
3. 如果本地失败，可能是懂球帝改了资源定位，需更新 CSS 选择器

### ⚠️ 功能正常但很慢

**原因**: 网络请求超时或数据源响应慢

**解决**:
1. 增加 `REQUEST_TIMEOUT` 值在 `main.py` 中
2. 添加缓存机制（涉及更复杂的改动）
3. 切换数据源（如可用官方 API）

### ℹ️ GitHub Actions 相关问题

**Q: GitHub Actions 中有错误提示？**

A: 不用担心！当前配置已修复：
- ✅ `deploy.yml` 只包含测试步骤（无需配置）
- ℹ️ 可选的 `deploy-vercel-cli.yml.disabled` 用于 PR 预览（需 Secrets）
- 详情见 [GITHUB_ACTIONS_FIX.md](GITHUB_ACTIONS_FIX.md)

**Q: 如何启用 GitHub Actions 自动部署？**

A: 推荐使用 Vercel 官方 GitHub 集成（方式 A），无需 Action：
1. Push 代码到 GitHub
2. 在 Vercel Dashboard 连接仓库
3. 每次 push 都自动部署

若需 PR 预览功能：
1. 参考 [VERCEL_SECRETS.md](VERCEL_SECRETS.md) 配置 Secrets
2. 启用 `deploy-vercel-cli.yml.disabled` 文件

---

## 监测和日志

如果需要添加环境变量（如数据库、API Key 等）：

### 通过 Vercel Dashboard

1. 项目设置 → "Environment Variables"
2. 点击 "Add New"
3. 输入 `KEY` 和 `VALUE`
4. 选择应用环境（Production / Preview / Development）
5. 重新部署使变量生效

### 通过命令行

```bash
vercel env add DATABASE_URL
# 输入值，然后重新部署
vercel --prod
```

### 在代码中使用

```python
import os
db_url = os.getenv('DATABASE_URL')
```

---

## 监测和日志

### 查看日志

1. Vercel Dashboard → 项目 → "Deployments"
2. 点击最新部署
3. 点击 "Logs" 标签
4. 选择 Python 函数查看实时日志

### 查看函数调用统计

1. 项目主页 → "Analytics" 标签
2. 查看：
   - 请求数量
   - 性能数据
   - 错误统计

---

## 回滚和版本控制

### 快速回滚到上一个部署

1. Deployments 列表中找到上一个成功的部署
2. 点击三个点菜单 → "Promote to Production"

### 查看部署历史

所有部署历史都在 "Deployments" 标签中保存，可随时查看和切换。

---

## 优化建议

### 1. 添加缓存

在 `main.py` 中添加缓存，减少网络请求：

```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def get_cached_schedule(team_id, timestamp):
    # timestamp 每小时更新一次，作为缓存键
    return fetch_team_ics_internal(team_id, "...")
```

### 2. 增加超时和重试

已在代码中配置 `REQUEST_TIMEOUT = 10` 和 `MAX_RETRIES = 2`，可按需调整。

### 3. 添加速率限制（Rate Limiting）

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/calendar")
@limiter.limit("60/minute")
def get_calendar(...):
    ...
```

### 4. 监测和告警

设置 Vercel 告警：
- "Settings" → "Alerts"
- 添加函数执行时间、错误率等告警规则

---

## 下一步

- ✅ 部署完成后，可考虑添加 GitHub Actions CI/CD
- ✅ 添加单元测试和集成测试
- ✅ 改进 UI 和响应式设计
- ✅ 添加更多数据源和球队支持

---

**需要帮助？**

- 📖 [Vercel 官方文档](https://vercel.com/docs)
- 🐛 [提交 Issue](https://github.com/chenbeiqi/football-calendar/issues)
- 💬 [讨论区](https://github.com/chenbeiqi/football-calendar/discussions)

---

祝部署顺利！🎉
