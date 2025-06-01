from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from ultralytics import YOLO
import tempfile
import os

app = FastAPI()
model = YOLO("yolov8n.pt")  # oder yolov8s.pt für genauere Ergebnisse

@app.post("/detect")
async def detect_image(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Die hochgeladene Datei ist kein Bild.")

    # Temporäre Datei speichern
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        image_path = tmp.name
        contents = await image.read()
        tmp.write(contents)

    try:
        results = model(image_path)

        labels = []
        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                label = result.names[cls]
                conf = float(box.conf[0])
                labels.append({
                    "label": label,
                    "confidence": round(conf, 2)
                })

        return JSONResponse(content={"results": labels})

    finally:
        os.remove(image_path)
