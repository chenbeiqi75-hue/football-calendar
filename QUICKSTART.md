# ⚡ 快速开始指南

**5 分钟内让你的足球赛程日历运行起来！**

## 🎯 三种使用方式

### 方式 1：访问在线版本（无需部署）⭐⭐⭐

最快最简单！直接访问他人部署的在线版本：

```
https://football-calendar-demo.vercel.app
```

- ✅ 无需安装任何东西
- ✅ 立即可用
- ✅ 移动端友好

---

### 方式 2：本地运行开发版本（5 分钟）⭐⭐

#### 前置条件：安装 Python 3.8+

```bash
# 检查 Python 版本
python3 --version
```

#### 快速启动

```bash
# 1️⃣ 克隆项目
git clone <your-repo-url>
cd football-calendar

# 2️⃣ 安装依赖
pip install -r requirements.txt

# 或使用 Make（更简单）
make install

# 3️⃣ 启动服务
make dev

# 或手动启动两个终端：
# 终端 1：启动 API
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 终端 2：启动 Web 服务
python3 -m http.server 5500
```

#### 访问应用

打开浏览器访问：

```
http://localhost:5500
```

✅ 完成！你已经在本地运行应用了。

---

### 方式 3：部署到 Vercel（8 分钟）⭐⭐⭐

**得到一个可分享的在线链接！**

#### 前置条件

- GitHub 账户
- 项目代码已上传到 GitHub
- 本指南文件已包含所有部署配置

#### 一键部署步骤

##### 选项 A: GitHub + Vercel 自动连接（推荐 ✨）

1. **访问 Vercel Dashboard**
   ```
   https://vercel.com/dashboard
   ```

2. **点击 "Add New" → "Project"**

3. **导入你的 GitHub 仓库**
   - Vercel 会自动检测配置
   - 点击 "Deploy"

4. **等待完成（1-2 分钟）**
   ```
   ✅ Deployment complete!
   https://football-calendar-xxxxx.vercel.app
   ```

5. **分享链接！**
   ```
   你的应用已上线！
   https://your-domain.vercel.app
   ```

##### 选项 B: 使用 Vercel CLI

```bash
# 1. 安装 Vercel CLI
npm install -g vercel

# 2. 登录（使用 GitHub 账户）
vercel login

# 3. 部署
vercel --prod

# 4. 获得生产 URL
✅ https://football-calendar-xxxxx.vercel.app
```

---

## 📚 常用命令速查表

### 使用 Make（推荐）

```bash
make help           # 显示所有命令
make install        # 安装依赖
make dev            # 启动完整开发环境
make api            # 仅启动 API
make web            # 仅启动 Web
make test           # 运行 API 测试
make clean          # 清理缓存
make vercel-deploy  # 部署到 Vercel
```

### 使用 Docker

```bash
# 构建并运行容器
docker-compose up

# 仅构建
docker-compose build

# 后台运行
docker-compose up -d

# 停止容器
docker-compose down
```

### 直接使用 Python

```bash
# 安装依赖
pip install -r requirements.txt

# 启动 API（开发服务）
uvicorn main:app --reload

# 启动 API（生产服务）
uvicorn main:app --workers 4

# 启动 Web 服务
python3 -m http.server 5500
```

---

## 🔍 验证安装

### 1️⃣ 确认 API 正常

```bash
# 在浏览器或终端中访问
curl http://localhost:8000/health
```

应返回：
```json
{"status":"healthy","timestamp":"2026-02-15T..."}
```

### 2️⃣ 确认 Web 服务正常

在浏览器访问：
```
http://localhost:5500
```

应看到蓝色的"赛程日历生成器"界面。

### 3️⃣ 测试完整功能

1. 选择联赛：中超联赛
2. 选择球队：北京国安
3. 等待预览加载（显示近期比赛）
4. 点击"复制链接"按钮
5. 链接复制成功提示出现

---

## 📱 订阅日历

### iOS / macOS
1. 在应用中选择球队
2. 点击 "iOS/Mac 订阅"
3. 日历应用自动打开，点击"订阅"

### Android / Google Calendar
1. 点击 "复制链接"
2. 打开 Google Calendar
3. 点击 "+" → "由 URL 订阅"
4. 粘贴链接，点击确定

### Outlook
1. Copy 链接
2. Outlook → "日历" → "添加日历"
3. 从 URL 添加，粘贴链接

---

## 🆘 遇到问题？

### ❌ "ModuleNotFoundError: No module named 'fastapi'"

**解决方案：**
```bash
pip install -r requirements.txt
```

### ❌ "Port 8000 already in use"

**解决方案：**
```bash
# 方法 1: 改用其他端口
uvicorn main:app --port 9000

# 方法 2: 杀死占用端口的进程
lsof -i :8000  # 找到 PID
kill -9 <PID>
```

### ❌ "网络连接超时" 或 "无法获取赛程"

**原因：** 可能是网络问题或数据源不稳定

**解决方案：**
1. 检查网络连接
2. 重启应用：`Ctrl+C` 然后重新启动
3. 尝试不同的球队 ID
4. 本地测试：`curl http://localhost:8000/health`

### ❌ 部署到 Vercel 失败

**检查步骤：**
1. 确保所有文件都已 push 到 GitHub
2. 检查 `requirements.txt` 中所有版本号都有效
3. 查看 Vercel 部署日志获取详细错误
4. 删除 `.vercel` 文件夹，重新部署

更详细的故障排查见：[DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📖 下一步

- ✅ **[完整文档](README.md)** - 详细功能说明和 API 文档
- ✅ **[部署指南](DEPLOYMENT.md)** - Vercel/Docker/自托管详解
- ✅ **[GitHub Issues](https://github.com/chenbeiqi/football-calendar/issues)** - 报告 bug 或请求功能

---

## 💡 常见问题 FAQ

**Q: 这个项目是开源的吗？**
A: 是的！MIT 许可证，自由使用和修改。

**Q: 需要注册账户吗？**
A: 不需要！无需登录就能使用。

**Q: 数据来自哪里？**
A: 从懂球帝网站爬取公开的足球赛程信息。

**Q: 可以添加其他球队吗？**
A: 可以！编辑 `index.html` 中的 `db` 对象添加新球队。

**Q: 赛程多久更新一次？**
A: 每次订阅时实时获取最新数据，无缓存延迟。

**Q: 能在生产环境使用吗？**
A: 可以，但请尊重数据源的使用条款。

---

## 🎉 大功告成！

你现在已经拥有一个完整的足球赛程日历服务！

### 分享你的成果：

- **本地版本**：链接：`http://localhost:5500`
- **在线版本**：分享 Vercel URL 给朋友
- **GitHub**：给项目 ⭐ 支持一下

---

还有问题？查看完整文档或提交 Issue！🚀
