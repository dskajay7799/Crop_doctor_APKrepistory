from pathlib import Path

import httpx
import numpy as np
import tensorflow as tf
from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image
from io import BytesIO

app = FastAPI(title="Crop Doctor API")

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------
BASE_DIR = Path(r"C:\CropDoctor")

MODEL_PATH = (
    BASE_DIR
    / "ai"
    / "model"
    / "crop_doctor_mobilenetv3.keras"
)

LABELS_PATH = (
    BASE_DIR
    / "ai"
    / "scripts"
    / "labels.txt"
)

IMAGE_SIZE = (224, 224)

# ---------------------------------------------------------
# Load model and labels once when backend starts
# ---------------------------------------------------------
print("Loading Crop Doctor AI model...")

try:
    model = tf.keras.models.load_model(MODEL_PATH)

    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        labels = [
            line.strip()
            for line in f
            if line.strip()
        ]

    print("AI model loaded successfully.")
    print("Number of labels:", len(labels))

except Exception as e:
    model = None
    labels = []
    print("ERROR loading AI model:", e)


# ---------------------------------------------------------
# Home
# ---------------------------------------------------------
@app.get("/")
def home():
    return {
        "message": "Crop Doctor API is running!",
        "status": "online",
    }


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Crop Doctor API",
        "model_loaded": model is not None,
        "number_of_classes": len(labels),
    }


# ---------------------------------------------------------
# Online AI prediction
# ---------------------------------------------------------
@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    if model is None:
        raise HTTPException(
            status_code=500,
            detail="AI model is not loaded.",
        )

    try:
        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Empty image file.",
            )

        # Read image
        image = Image.open(
            BytesIO(contents)
        ).convert("RGB")

        # Resize exactly like the mobile model
        image = image.resize(
            IMAGE_SIZE
        )

        # Convert to float32
        image_array = np.array(
            image,
            dtype=np.float32,
        )

        # Add batch dimension
        image_array = np.expand_dims(
            image_array,
            axis=0,
        )

        # Model already contains MobileNetV3
        # preprocessing in the Keras graph.
        prediction = model.predict(
            image_array,
            verbose=0,
        )[0]

        predicted_index = int(
            np.argmax(prediction)
        )

        confidence = float(
            prediction[predicted_index]
        ) * 100.0

        disease = labels[predicted_index]

        return {
            "status": "success",
            "disease": disease,
            "confidence": confidence,
            "source": "online",
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {e}",
        )


# ---------------------------------------------------------
# Weather
# ---------------------------------------------------------
@app.get("/weather")
async def weather(
    latitude: float,
    longitude: float,
):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current":
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "wind_speed_10m",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            params=params,
            timeout=15.0,
        )

        response.raise_for_status()

        return response.json()