from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from bakong_khqr import KHQR
import os

from pip._internal.cli import status_codes

load_dotenv()  # Load environment variables from .env

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

def verifyMD5(md5: str):
    try:
        khqr = KHQR(os.getenv("token"))
        check_payment = khqr.check_payment(md5)
        return JSONResponse({"check_payment": check_payment}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def payment_info(md5: str):
    try:
        khqr = KHQR(os.getenv("token"))
        payment_info_data = khqr.get_payment(md5)
        return JSONResponse({"payment_info": payment_info_data}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))