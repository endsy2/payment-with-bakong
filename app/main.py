from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controller import BakongController
import logging
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging here
logging.basicConfig(
    level=logging.DEBUG,  # Show all DEBUG messages
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Include your router
app.include_router(BakongController.router)
