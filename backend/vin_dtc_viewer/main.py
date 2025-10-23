from fastapi import FastAPI, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from vin_dtc_viewer import upload_handler
from vin_dtc_viewer.api import router as api_router

app = FastAPI()

# CORS настройка – разрешаваме заявки от всички източници
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Включваме стандартните API маршрути (/vehicles и т.н.)
app.include_router(api_router)

@app.post("/upload/combined/")
async def upload_combined(
    modules_file: UploadFile = File(...),
    dtc_file: Optional[UploadFile] = File(None),
    label: str = Form(""),
    comment: str = Form("")
):
    """
    modules_file: .uuw или .txt (съдържа VIN и модули)
    dtc_file:     .txt (съдържа DTC грешки) – по избор
    label:        потребителско име/описание на автомобила
    comment:      допълнителен коментар
    """
    # Парсваме конфигурационния файл
    contents1 = await modules_file.read()
    vin = upload_handler.process_modules_only_upload(
        contents1.decode(errors="ignore"),
        label,
        comment
    )
    # Ако има DTC файл – добавяме грешките
    if dtc_file:
        contents2 = await dtc_file.read()
        upload_handler.add_dtc_errors(
            vin,
            contents2.decode(errors="ignore")
        )
    return {"status": "ok", "vin": vin}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "vin_dtc_viewer.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
