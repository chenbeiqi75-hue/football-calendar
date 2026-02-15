# 🔐 Vercel 部署 - Token 和 Secrets 配置指南

此文档详细说明如何获取 Vercel token、project ID 等配置。

## 📋 你需要的三样东西

如果使用**方式 A（推荐）**，无需以下配置。  
如果使用**方式 B 或方式 C**，需要以下 3 个值：

1. **VERCEL_TOKEN** - Vercel 个人 token
2. **VERCEL_ORG_ID** - Vercel 组织 ID
3. **VERCEL_PROJECT_ID** - Vercel 项目 ID

---

## 第 1 步：获取 VERCEL_TOKEN

### 方法：从 Vercel Dashboard

1. 访问 [Vercel Account Settings](https://vercel.com/account)
2. 左侧菜单 → **"Tokens"**
3. 点击 **"Create"** 创建新 token
4. 填写：
   - **Token name**: `GitHub-Actions` (可任意)
   - **Scope**: `Full Account` (推荐)
5. 点击 **"Create Token"**
6. **复制显示的 token**（只显示一次，之后无法查看）

⚠️ **安全提示**：Token 就像密码，不要分享或提交到 GitHub！

---

## 第 2 步：获取 VERCEL_ORG_ID

### 方法 1：从 Dashboard URL

1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 查看浏览器地址栏
3. URL 格式：`https://vercel.com/YOUR-TEAM-NAME/...`
4. `YOUR-TEAM-NAME` 就是你的 **organization ID**

**示例**：
- URL: `https://vercel.com/my-company`
- ORG_ID: `my-company`

### 方法 2：从项目设置

1. 进入任何项目 → **Settings** 标签
2. 左侧菜单 → **"General"**
3. 找到 **"Team"** 部分，即为 ORG_ID

---

## 第 3 步：获取 VERCEL_PROJECT_ID

### 方法 1：从 Vercel Dashboard（推荐）

1. 在 [Vercel Dashboard](https://vercel.com/dashboard) 中打开你的项目
2. 进入 **Settings** 标签
3. 左侧菜单 → **"General"**
4. 找到 **"Project ID"** 字段，全部复制

**示例**：
```
Project ID: prj_abc123xyz789
```

### 方法 2：从项目 .vercel/project.json（本地）

如果你已在本地运行过 `vercel` 命令，项目文件夹中会有：

```bash
cat .vercel/project.json | grep projectId
```

输出示例：
```json
{
  "projectId": "prj_abc123xyz789",
  "orgId": "team_abc123"
}
```

---

## 第 4 步：配置 GitHub Secrets

### 在 GitHub 中添加 Secrets

1. 打开你的 GitHub 仓库
2. 进入 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **"New repository secret"**
4. 添加以下 3 个 secret：

#### Secret 1: VERCEL_TOKEN
- **Name**: `VERCEL_TOKEN`
- **Value**: `<粘贴第1步复制的token>`

#### Secret 2: VERCEL_ORG_ID
- **Name**: `VERCEL_ORG_ID`
- **Value**: `<粘贴第2步获得的ORG_ID>`

#### Secret 3: VERCEL_PROJECT_ID
- **Name**: `VERCEL_PROJECT_ID`
- **Value**: `<粘贴第3步获得的PROJECT_ID，不包含"prj_"前缀>`

点击 **"Add secret"** 保存每一个。

### 验证配置

1. 进入 **Settings** → **Secrets and variables** → **Actions**
2. 应该看到 3 个已添加的 secrets：
   ```
   ✓ VERCEL_TOKEN
   ✓ VERCEL_ORG_ID
   ✓ VERCEL_PROJECT_ID
   ```

---

## 完整示例

假设你的 Vercel 配置如下：

```
Team URL: https://vercel.com/john-doe
Project Name: football-calendar
Project ID: prj_xyz789abc
Vercel Token: xxxx_yyyy_zzzz (隐藏显示)
```

则配置如下：

| GitHub Secret | 值 |
|---|---|
| VERCEL_TOKEN | `xxxx_yyyy_zzzz` |
| VERCEL_ORG_ID | `john-doe` |
| VERCEL_PROJECT_ID | `prj_xyz789abc` |

---

## 🚀 现在启用 GitHub Actions（可选）

如果你想要 GitHub Actions 在 PR 上自动部署预览版本：

1. 将 `.github/workflows/deploy-vercel-cli.yml.disabled` 重命名为 `.github/workflows/deploy-vercel-cli.yml`
2. Commit 并 push

```bash
mv .github/workflows/deploy-vercel-cli.yml.disabled .github/workflows/deploy-vercel-cli.yml
git add .github/workflows/
git commit -m "启用 GitHub Actions Vercel 部署"
git push origin main
```

之后，每次创建 PR 时都会自动部署预览版本。

---

## ⚠️ 常见问题

### Q: 为什么需要 Token？

A: GitHub Actions 需要 authenticate 到 Vercel，以获取权限部署项目。

### Q: Token 泄露了怎么办？

A: 立即进入 Vercel Dashboard → Tokens，删除泄露的 token。然后在 GitHub Secrets 中更新新 token。

### Q: 如何轮换 Token（定期更新）？

A: 建议每 3-6 个月：
1. Vercel Dashboard 创建新 token
2. GitHub Secrets 中更新新值
3. 删除旧 token

### Q: VERCEL_ORG_ID 可以是 email 吗？

A: 不行，必须是 team slug（如 `john-doe` 而不是 `john@example.com`）。

### Q: PROJECT_ID 需要包含 "prj_" 前缀吗？

A: 建议包含，但有些工具可能不需要。如遇到错误，尝试同时带和不带 "prj_" 前缀。

---

## 🔒 安全最佳实践

✅ **应该做**
- 定期轮换 token
- 使用 organization token 而非个人 token（如果有多个项目）
- 给 token 最小权限（仅限本项目或团队）
- 在 GitHub Secrets 中加密存储

❌ **不应该做**
- 将 token 提交到代码仓库
- 在 PR 评论或 issue 中分享 token
- 使用超级权限的 token（如 full account）
- 忘记更新泄露的 token

---

## 📚 更多资源

- [Vercel Token 文档](https://vercel.com/docs/concepts/projects/overview#project-id)
- [GitHub Secrets 文档](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Vercel GitHub 集成](https://vercel.com/docs/concepts/git/vercel-for-github)

---

准备好了？现在可以：
- 使用**方式 A**：直接在 Vercel Dashboard 连接 GitHub（推荐）
- 使用**方式 B**：启用 GitHub Actions 自动 PR 预览
- 使用**方式 C**：使用 Vercel CLI 手动部署

更多详情见 [DEPLOYMENT.md](DEPLOYMENT.md)
