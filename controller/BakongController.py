from fastapi import APIRouter, Body
from pydantic import BaseModel
from service import BakongService

router = APIRouter(prefix="/bakong", tags=["bakong"])


@router.post("/generateQR")
async def generate_bakong_qr(amount: float = Body(...), currency: str = Body(...)):
    return BakongService.generateQR(amount,currency)

@router.post("/verifyMD5")
async def verifyMD5(md5:str):
    return BakongService.verifyMD5(md5)

@router.post("/payment_info")
async def payment_info(md5:str):
    return BakongService.payment_info(md5)
