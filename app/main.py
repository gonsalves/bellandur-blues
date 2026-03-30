from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import init_db
from app.routers import articles, feed, audio
from app.config import BASE_DIR

app = FastAPI(title="Bellandur Blues", version="0.1.0")

app.include_router(articles.router)
app.include_router(feed.router)
app.include_router(audio.router)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def index():
    return FileResponse(str(BASE_DIR / "app" / "static" / "index.html"))


def start():
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
