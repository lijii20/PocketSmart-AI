import json, os
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import RecommendationHistory, User
from app.models.schemas import HomeRequest, PartyRequest, JewelryRequest
from app.services.auth import decode_token
from app.services.gemini_service import gemini_service
from app.services.fallback import home_fallback, party_fallback, jewelry_fallback
from app.config import settings
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router=APIRouter(prefix="/api/planners", tags=["planners"])
bearer=HTTPBearer(auto_error=False)

def current_user(creds:HTTPAuthorizationCredentials=Depends(bearer), db:Session=Depends(get_db)):
    if not creds: raise HTTPException(401,"Login required")
    payload=decode_token(creds.credentials)
    user=db.query(User).filter(User.id==int(payload["sub"])).first()
    if not user: raise HTTPException(401,"User not found")
    return user

def save(db,user,planner,data,result):
    db.add(RecommendationHistory(user_id=user.id,planner=planner,request_json=json.dumps(data),response_json=json.dumps(result)))
    db.commit()

def response_or_fallback(planner,data,user,db,image_bytes=None,mime_type=None):
    result=gemini_service.generate(planner,data,image_bytes,mime_type)
    if result is None:
        result={"source":"fallback","warning":"Gemini was unavailable; showing deterministic starter recommendations."}
        result.update({"home":home_fallback(data)} if planner=="home" else {"party":party_fallback(data)} if planner=="party" else {"jewelry":jewelry_fallback(data)})
    else: result["source"]="gemini"
    save(db,user,planner,data,result)
    return result

@router.post("/home")
def home(payload:HomeRequest,user=Depends(current_user),db:Session=Depends(get_db)):
    return response_or_fallback("home",payload.model_dump(),user,db)

@router.post("/party")
def party(payload:PartyRequest,user=Depends(current_user),db:Session=Depends(get_db)):
    return response_or_fallback("party",payload.model_dump(),user,db)

@router.post("/jewelry")
async def jewelry(
    budget: float = Form(...),
    occasion: str = Form(...),
    style: str = Form(...),
    outfit_description: str = Form("Not provided"),
    outfit: UploadFile | None = File(default=None),
    user=Depends(current_user),
    db: Session = Depends(get_db),
):
    payload=JewelryRequest(budget=budget, occasion=occasion, style=style, outfit_description=outfit_description)
    image_bytes=None; mime=None
    if outfit and outfit.filename:
        if outfit.content_type not in {"image/jpeg","image/png","image/webp"}:
            raise HTTPException(400,"Upload JPG, PNG, or WEBP image")
        image_bytes=await outfit.read()
        if len(image_bytes)>settings.max_upload_mb*1024*1024: raise HTTPException(413,"Image is too large")
        mime=outfit.content_type
    return response_or_fallback("jewelry",payload.model_dump(),user,db,image_bytes,mime)

@router.post("/generate-home")
def generate_home_alias(payload:HomeRequest,user=Depends(current_user),db:Session=Depends(get_db)):
    return home(payload,user,db)

@router.post("/generate-party")
def generate_party_alias(payload:PartyRequest,user=Depends(current_user),db:Session=Depends(get_db)):
    return party(payload,user,db)

@router.post("/generate-jewelry")
async def generate_jewelry_alias(
    budget: float = Form(...), occasion: str = Form(...), style: str = Form(...),
    outfit_description: str = Form("Not provided"), outfit: UploadFile | None = File(default=None),
    user=Depends(current_user), db: Session = Depends(get_db)):
    return await jewelry(budget, occasion, style, outfit_description, outfit, user, db)
