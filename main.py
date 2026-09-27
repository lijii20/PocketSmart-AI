from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app.routes import auth, planners, history
from app.models import db_models

BASE=Path(__file__).resolve().parent.parent
Base.metadata.create_all(bind=engine)
app=FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static",StaticFiles(directory=str(BASE/"static")),name="static")
templates=Jinja2Templates(directory=str(BASE/"templates"))
app.include_router(auth.router); app.include_router(planners.router); app.include_router(history.router)

@app.get("/",response_class=HTMLResponse)
async def index(request:Request): return templates.TemplateResponse("index.html",{"request":request})
@app.get("/login",response_class=HTMLResponse)
async def login_page(request:Request): return templates.TemplateResponse("login.html",{"request":request})
@app.get("/register",response_class=HTMLResponse)
async def register_page(request:Request): return templates.TemplateResponse("register.html",{"request":request})
@app.get("/dashboard",response_class=HTMLResponse)
async def dashboard(request:Request): return templates.TemplateResponse("dashboard.html",{"request":request})
@app.get("/planner/{planner}",response_class=HTMLResponse)
async def planner_page(request:Request,planner:str):
    if planner not in {"home","party","jewelry"}: return HTMLResponse("Planner not found",404)
    return templates.TemplateResponse(f"{planner}.html",{"request":request})
@app.get("/history",response_class=HTMLResponse)
async def history_page(request:Request): return templates.TemplateResponse("history.html",{"request":request})
@app.get("/health")
def health(): return {"status":"ok","gemini_configured":bool(settings.gemini_api_key),"model":settings.gemini_model}
