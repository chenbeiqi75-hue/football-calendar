# Re-export the FastAPI ASGI app from project root so Vercel's Python runtime can serve it.
# Requests to /api/* are rewritten to this file by `vercel.json`.
from main import app
