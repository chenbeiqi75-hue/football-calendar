.PHONY: help install dev test docs clean

help:
	@echo "足球赛程日历生成器 - 开发命令"
	@echo ""
	@echo "常用命令:"
	@echo "  make install       - 安装项目依赖"
	@echo "  make dev           - 启动本地开发服务 (API + 静态服务)"
	@echo "  make api           - 仅启动 API 服务 (端口 8000)"
	@echo "  make web           - 仅启动 Web 服务 (端口 5500)"
	@echo "  make test          - 测试 API 端点"
	@echo "  make clean         - 清理缓存文件"
	@echo ""
	@echo "部署命令:"
	@echo "  make vercel-login  - 登录 Vercel"
	@echo "  make vercel-deploy - 部署到 Vercel"
	@echo ""

install:
	@echo "📦 安装依赖..."
	python3 -m pip install -r requirements.txt
	@echo "✅ 依赖安装完成"

dev:
	@echo "🚀 启动开发环境 (API + Web)..."
	@echo ""
	@echo "API 服务: http://localhost:8000"
	@echo "Web 页面: http://localhost:5500"
	@echo ""
	@echo "按 Ctrl+C 停止服务"
	@echo ""
	(uvicorn main:app --reload --host 0.0.0.0 --port 8000) & \
	sleep 2 && \
	cd . && python3 -m http.server 5500

api:
	@echo "🔧 启动 API 服务 (端口 8000)..."
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

web:
	@echo "🌐 启动 Web 服务 (端口 5500)..."
	python3 -m http.server 5500

test:
	@echo "🧪 测试 API..."
	@echo ""
	@echo "1️⃣ 测试健康检查:"
	@curl -s http://localhost:8000/health | python3 -m json.tool
	@echo ""
	@echo "2️⃣ 测试日历接口 (北京国安):"
	@curl -s "http://localhost:8000/api/calendar?team_id=50000330&team_name=北京国安" | grep -E "^(BEGIN|VERSION|PRODID|SUMMARY)" | head -10
	@echo ""
	@echo "3️⃣ 测试日历接口 (曼城):"
	@curl -s "http://localhost:8000/api/calendar?team_id=50000529&team_name=曼城" | grep -E "SUMMARY" | head -5
	@echo ""
	@echo "✅ 测试完成"

clean:
	@echo "🧹 清理缓存文件..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .vercel dist build *.egg-info 2>/dev/null || true
	@echo "✅ 清理完成"

vercel-login:
	@echo "🔑 登录 Vercel..."
	npm install -g vercel 2>/dev/null || echo "需要 npm 支持"
	vercel login

vercel-deploy:
	@echo "🚀 部署到 Vercel..."
	vercel --prod

vercel-deploy-preview:
	@echo "👀 部署预览版本到 Vercel..."
	vercel

lint:
	@echo "🔍 检查代码..."
	python3 -m pip install pylint 2>/dev/null || true
	pylint main.py --errors-only || true

format:
	@echo "✨ 格式化代码..."
	python3 -m pip install black 2>/dev/null || true
	black main.py api/index.py || true

requirements:
	@echo "📋 生成依赖列表..."
	pip freeze > requirements-full.txt
	@cat requirements.txt
