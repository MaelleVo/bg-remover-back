import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from rembg.bg import load_model
from io import BytesIO
import uvicorn


load_dotenv()
frontend_urls = os.getenv("FRONTEND_URLS")
if not frontend_urls:
    raise ValueError("La variable FRONTEND_URLS n'est pas définie")

origins = [url.strip() for url in frontend_urls.split(",")]
print("Allowed origins:", origins)  


app = FastAPI()

# --- Middleware CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


print("Chargement du modèle U2NET...")
try:
    u2net_model = load_model("u2net") 
    print("Modèle chargé ✅")
except Exception as e:
    print(f"Erreur lors du chargement du modèle: {e}")

# --- Routes ---
@app.get("/health")
def health():
    return {"status": "ok", "frontend_urls": origins}

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    max_size = 10_000_000  # 10MB
    if file.spool_max_size > max_size:
        raise HTTPException(status_code=413, detail="Image trop grande")

    try:
        input_bytes = await file.read()
        output_bytes = remove(input_bytes, session=u2net_model)
        return StreamingResponse(BytesIO(output_bytes), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement de l'image : {str(e)}")

# --- Run ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000)) 
    uvicorn.run(app, host="0.0.0.0", port=port)
