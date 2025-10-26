
from fastapi import FastAPI
from controller import BakongController
import os
app = FastAPI()

app.include_router(BakongController.router)
