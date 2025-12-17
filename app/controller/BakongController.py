from fastapi import APIRouter, Body
from pydantic import BaseModel
from app.service import BakongService
from fastapi import HTTPException,Header
import logging 

router = APIRouter(prefix="/bakong", tags=["bakong"])

class VerifyMD5Request(BaseModel):
    md5: str
    booking_id:int

@router.post("/generateQR")
async def generate_bakong_qr(amount: float = Body(...), currency: str = Body(...)):
    return BakongService.generateQR(amount,currency)

@router.post("/verifyMD5")
async def verify_md5_endpoint(
    request: VerifyMD5Request = Body(...),
    authorization: str | None = Header(None)  # Extract token from header
):
    # 1️⃣ Get token from header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ")[1]

    # 2️⃣ Call service and pass token
    result = await BakongService.verifyMD5(request.md5, request.booking_id, token)
    return {"success": True, "result": result}


@router.post("/payment_info")
async def payment_info(md5:str):
    return BakongService.payment_info(md5)
