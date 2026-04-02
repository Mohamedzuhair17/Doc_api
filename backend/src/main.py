"""
Vercel entrypoint compatibility shim.

Vercel's FastAPI preset imports `src.main:app` by default.
Keep this module minimal and forward to the real API app.
"""

from src.api.main import app
