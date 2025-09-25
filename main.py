import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from io import BytesIO

# Charge les variables depuis .env
load_dotenv()

frontend_urls = os.getenv("FRONTEND_URLS")
if not frontend_urls:
    raise ValueError("La variable FRONTEND_URLS n'est pas définie")

origins = [url.strip() for url in frontend_urls.split(",")]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    input_bytes = await file.read()
    output_bytes = remove(input_bytes)
    return StreamingResponse(BytesIO(output_bytes), media_type="image/png")
