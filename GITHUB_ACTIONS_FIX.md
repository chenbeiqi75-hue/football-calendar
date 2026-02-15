# ⚡ GitHub Actions 部署修复说明

## 问题修复

之前的 `.github/workflows/deploy.yml` 包含以下问题：

❌ **问题 1**: 使用了不存在的 action `vercel/action@master`  
❌ **问题 2**: GitHub Secrets 未配置但被引用

## ✅ 解决方案

### 修复内容

1. **现在 `deploy.yml` 包含**：
   - ✅ 测试步骤（Python 语法检查）- 保持可用
   - ✅ 注释掉的 deploy job - 附带详细说明

2. **新增 `deploy-vercel-cli.yml.disabled`**：
   - 可选的 GitHub Actions 部署配置
   - 仅在 PR 上生成预览链接
   - 需要 GitHub Secrets 配置才能启用

3. **新增 `VERCEL_SECRETS.md`**：
   - 详细说明如何获取 Vercel token、project ID 等
   - 一步步指导如何配置 GitHub Secrets

---

## 🚀 现在该怎么做？

### 方案 1：使用官方推荐方式（⭐ 最简单）

**不需要任何额外配置！**

1. 推送代码到 GitHub
   ```bash
   git add .
   git commit -m "修复 GitHub Actions"
   git push origin main
   ```

2. 访问 [Vercel Dashboard](https://vercel.com/dashboard)

3. 点击 "Add New" → "Project"

4. 选择你的 GitHub 仓库，点击 "Deploy"

5. **完成！** 之后每次 push 都自动部署。

### 方案 2：可选 - 启用 GitHub Actions 预览部署

如需在 PR 上自动生成预览链接：

1. 参考 [VERCEL_SECRETS.md](VERCEL_SECRETS.md) 获取：
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`

2. 在 GitHub 中配置这 3 个 Secrets

3. 启用 workflow：
   ```bash
   mv .github/workflows/deploy-vercel-cli.yml.disabled \
      .github/workflows/deploy-vercel-cli.yml
   git add .github/workflows/
   git commit -m "启用 GitHub Actions Vercel 预览部署"
   git push origin main
   ```

4. 现在创建 PR 时会自动部署预览版本！

---

## 📊 三种部署方式对比

| 方式 | 难度 | 自动部署 | 需要 Token | 推荐指数 |
|------|------|--------|----------|--------|
| **方式 A**: Vercel GitHub 集成 | ⭐ 极简 | ✅ 是 | ❌ 否 | ⭐⭐⭐⭐⭐ |
| **方式 B**: GitHub Actions PR 预览 | ⭐⭐⭐ 一般 | ✅ PR 自动预览 | ✅ 是 | ⭐⭐⭐ |
| **方式 C**: Vercel CLI 手动 | ⭐⭐ 简单 | ❌ 否 | ✅ 是 | ⭐⭐ |

**新用户建议**：使用方式 A（包含在项目中的配置已完全可用）

---

## ✨ 现在的文件结构

```
.github/workflows/
├── deploy.yml                      # 包含测试 + 说明（可用）
└── deploy-vercel-cli.yml.disabled  # 可选的 PR 预览部署（需启用）

docs/
├── DEPLOYMENT.md                   # 完整部署指南
├── VERCEL_SECRETS.md              # Token 配置详解（新增）
├── QUICKSTART.md                  # 快速开始
└── README.md                       # 项目文档
```

---

## ❓ 常见问题

### Q: 我现在什么都不用做就能部署吗？

A: 是的！按以下步骤操作：
1. Push 代码到 GitHub
2. 在 Vercel Dashboard 连接你的 GitHub 仓库
3. 点击 Deploy
4. 搞定！

### Q: GitHub Actions 的错误消息消失了吗？

A: 是的！`deploy.yml` 现在是完全有效的配置。

### Q: 如何启用 GitHub Actions 部署？

A: 见上方"方案 2"，需要先配置 Secrets。详细步骤在 [VERCEL_SECRETS.md](VERCEL_SECRETS.md)。

### Q: 我想立即部署，不等 GitHub Actions 结果？

A: 使用 Vercel CLI（方式 C）或直接在 Vercel Dashboard 部署（方式 A）。

### Q: deploy.yml 中为什么要注释掉 deploy job？

A: 因为：
- 官方推荐使用 Vercel GitHub 集成（更简单、更安全、无需 token 泄露风险）
- GitHub Actions 用于测试（语法检查）
- 可选的 deploy-vercel-cli.yml 用于需要 PR 预览的场景

---

## 📞 遇到问题？

1. **GitHub Actions 报错？** 
   → 检查 [DEPLOYMENT.md](DEPLOYMENT.md) 故障排查段落

2. **需要配置 Vercel Secrets？**
   → 阅读 [VERCEL_SECRETS.md](VERCEL_SECRETS.md) 一步步操作

3. **想了解部署原理？**
   → 查看 [DEPLOYMENT.md](DEPLOYMENT.md) 完整指南

4. **本地测试？**
   → 运行 `make dev` 或 `docker-compose up`

---

**现在代码已就绪，可以开始部署了！** 🎉
