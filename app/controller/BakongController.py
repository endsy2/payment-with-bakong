from fastapi import APIRouter, Query, Body
from pydantic import BaseModel
from app.service import BakongService
from fastapi import HTTPException, Header
import logging
from typing import Optional

router = APIRouter(prefix="/bakong", tags=["bakong"])

class VerifyMD5Request(BaseModel):
    md5: str
    booking_id: int

@router.get("/generateQR")
async def generate_bakong_qr(amount: float = Query(...), currency: str = Query(...), merchant_name: str = Query(...)):
    return BakongService.generateQR(amount, currency, merchant_name)

@router.post("/verifyMD5")
async def verify_md5_endpoint(
    request: VerifyMD5Request = Body(...),
    authorization: Optional[str] = Header(None)  # Extract token from header
):
    # 1️⃣ Get token from header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ")[1]

    # 2️⃣ Call service and pass token
    result = await BakongService.verifyMD5(request.md5, request.booking_id, token)
    return {"success": True, "result": result}


@router.post("/payment_info")
async def payment_info(md5: str):
    return BakongService.payment_info(md5)

@router.post("/renewToken")
async def renew_token():
    """
    Manually renew Bakong token
    """
    token = await BakongService.renew_bakong_token()
    return {"success": True, "message": "Token renewed successfully", "token": token}

@router.get("/checkToken")
async def check_token():
    """
    Check current Bakong token status
    """
    token = BakongService.get_bakong_token()
    if token:
        return {"success": True, "has_token": True, "token_preview": f"{token[:10]}..."}
    return {"success": False, "has_token": False, "message": "No token available"}
