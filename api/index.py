from fastapi import FastAPI
from main import app as main_app

# 将 main.py 中的 app 引入并挂载到子应用
app = FastAPI(title="Football Calendar API")

# 挂载 main_app 到根路径
app.mount("/", main_app)