from fastapi import FastAPI
from app.controller import BakongController
import logging
import os

app = FastAPI()

# Configure logging here
logging.basicConfig(
    level=logging.DEBUG,  # Show all DEBUG messages
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Include your router
app.include_router(BakongController.router)
