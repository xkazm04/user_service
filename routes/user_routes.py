from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.models import User
from auth import verify_gateway_request
from pydantic import BaseModel

# Create Pydantic models for request validation
class UserRegistration(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    credits: int = 100
    plan: str = "free"

router = APIRouter(tags=["User"])

@router.post("/register", dependencies=[Depends(verify_gateway_request)])
def register_user(user_data: UserRegistration, db: Session = Depends(get_db)):
    clerk_user_id = user_data.id 
    email = user_data.email

    existing_user = db.query(User).filter(User.id == clerk_user_id).first()
    if existing_user:
        return {"message": "User already registered."}
    
    user = User(
        id=clerk_user_id,
        email=email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        credits=user_data.credits,  
        plan=user_data.plan  
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully.", "user": user}

@router.post("/credits", dependencies=[Depends(verify_gateway_request)])
def charge_credits(user_id: str, amount: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if user.credits < amount:
        raise HTTPException(status_code=400, detail="Insufficient credits.")

    # Deduct credits
    user.credits -= amount
    db.commit()

    return {"message": "Credits charged successfully.", "remaining_credits": user.credits}

@router.get("/profile/{user_id}", dependencies=[Depends(verify_gateway_request)])
def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {}
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "plan": user.plan,
        "credits": user.credits,
    }
   
def get_current_user(db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == "user_2s5HTRiNgteULVxz0Lx0FKHPr23").first()