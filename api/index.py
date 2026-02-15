# Vercel 部署入口点
# 这个文件是 Vercel Python Runtime 的入口
# 它引用了根目录的 FastAPI app 并将其暴露为 ASGI 应用
# vercel.json 中的 rewrites 会将 /api/* 的请求转发到这个文件

import sys
import os

# 确保可以导入根目录的模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# ASGI 应用入口
__all__ = ['app']

