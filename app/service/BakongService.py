from dotenv import load_dotenv
from fastapi import HTTPException,Header
from fastapi.responses import JSONResponse
from bakong_khqr import KHQR
import os
import httpx
from fastapi import Request
from pydantic import BaseModel
import logging
from pip._internal.cli import status_codes
from datetime import datetime

load_dotenv()  # Load environment variables from .env



BASE_URL = "http://127.0.0.1:3000"  # FastAPI base URL for internal calls

async def call_insert_payment(payment_data: dict,token:str):
    """
    Send payment data to Node.js backend using the token from header
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("http://127.0.0.1:3000/payment/insertPayment",
                                         json=payment_data, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=500, detail=f"Node.js request failed: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
async def verifyMD5(md5: str, booking_id: int,token:str):
    try:
        if not md5:
            raise HTTPException(status_code=400, detail="md5 is required")

        # 1️⃣ Check KHQR payment status
        khqr = KHQR(os.getenv("token"))
        check_payment = khqr.check_payment(md5)
        logging.info("KHQR status: %s", check_payment)

        if check_payment != "PAID":
            return {"status": check_payment}

        logging.info("Payment is PAID")

        # 2️⃣ Get payment info (async-safe)
        payment_info_result = payment_info(md5)
        if callable(getattr(payment_info_result, "__await__", None)):
            payment_info_result = await payment_info_result

        # 3️⃣ If payment_info still returns JSONResponse, extract dict
        if hasattr(payment_info_result, "body"):
            import json
            payment_info_dict = json.loads(payment_info_result.body.decode())
        else:
            payment_info_dict = payment_info_result  # assume it's already dict

        payment_info_data = payment_info_dict.get("payment_info", {})
        if not payment_info_data:
            raise HTTPException(status_code=500, detail="payment_info is empty")

        # 4️⃣ Logging for debug
        logging.debug("booking_id: %s", booking_id)
        logging.debug("amount: %s", payment_info_data.get("amount"))
        logging.debug("transaction hash: %s", payment_info_data.get("hash"))
        logging.debug("createdDateMs: %s", datetime.utcfromtimestamp(payment_info_data.get("createdDateMs") / 1000).isoformat())

        # 5️⃣ Prepare payment data for DB / Node.js endpoint
        payment_data = {
            "bookingId": booking_id,
            "amount": payment_info_data.get("amount"),
            "method": "KHQR",
            "transaction_id": payment_info_data.get("hash"),
            "status": "PAID",
            "paidAt":datetime.utcfromtimestamp(payment_info_data.get("createdDateMs") / 1000).isoformat(),
        }

        # 6️⃣ Call the endpoint to insert payment
        result = await call_insert_payment(payment_data,token)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logging.exception("verifyMD5 error")
        raise HTTPException(status_code=500, detail=str(e))

    
def payment_info(md5: str):
    try:
        khqr = KHQR(os.getenv("token"))
        payment_info_data = khqr.get_payment(md5)
        return JSONResponse({"payment_info": payment_info_data}, status_code=200)
        


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def generateQR(amount: float,currency: str):
    try:
        # Create an instance of KHQR with Bakong Developer Token
        khqr = KHQR(os.getenv("token"))

        # Generate QR code data for a transaction
        qr = khqr.create_qr(
            bank_account='chin_kongming@aclb',  # Your Bakong profile user_name@bank
            merchant_name='CHIN KONG MING',
            merchant_city='Phnom Penh',
            amount=amount,  # Use passed parameter
            currency=currency,  # USD or KHR
            store_label='MShop',
            phone_number='85581362035',
            bill_number='TRX01234567',
            terminal_label='Cashier-01',
            static=False  # Static or Dynamic QR code
        )
        md5 = khqr.generate_md5(qr)

        return JSONResponse({"qr": qr, "md5": md5}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

async def get_token_from_header(authorization: str | None = Header(None)):
    """
    Extract Bearer token from request header
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    token = authorization.split(" ")[1]
    return token



