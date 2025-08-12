import asyncio
import os
import pickle
import shutil

import numpy as np
from fastapi import (
    FastAPI,
    File,
    Query,
    Request,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from tensorflow.keras.models import load_model
from werkzeug.utils import secure_filename

# --- (No change to directory setup) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
TOKENIZERS_DIR = os.path.join(MODELS_DIR, "tokenizers")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(TOKENIZERS_DIR, exist_ok=True)


def discover_datasets(data_directory):
    """Finds all .txt files in the data directory and creates a dictionary."""
    datasets = {}
    for filename in os.listdir(data_directory):
        if filename.endswith(".txt"):
            key_name = os.path.splitext(filename)[0]
            datasets[key_name] = os.path.join(data_directory, filename)
    return datasets


DATASETS = discover_datasets(DATA_DIR)

app = FastAPI()

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount(
    "/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static"
)


class PredictRequest(BaseModel):
    dataset: str
    text: str


@app.get("/get_datasets")
async def get_datasets():
    return JSONResponse(content=list(DATASETS.keys()))


@app.post("/upload_dataset")
async def upload_dataset(file: UploadFile = File(...)):
    if file.content_type != "text/plain":
        return JSONResponse(
            status_code=400,
            content={"message": "Invalid file type. Please upload a .txt file."},
        )

    filename = secure_filename(file.filename)
    save_path = os.path.join(DATA_DIR, filename)

    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        global DATASETS
        DATASETS = discover_datasets(DATA_DIR)

    except Exception as e:
        return JSONResponse(
            status_code=500, content={"message": f"Could not save file: {e}"}
        )
    finally:
        file.file.close()

    return JSONResponse(
        status_code=200,
        content={
            "message": f"File '{filename}' uploaded successfully.",
            "new_dataset_key": os.path.splitext(filename)[0],
        },
    )


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            if data["action"] == "train":
                dataset = data["dataset"]
                if dataset == "custom":
                    text = data["custom_text"]
                else:
                    with open(DATASETS[dataset], "r", encoding="utf-8") as f:
                        text = f.read()

                await websocket.send_json(
                    {"status": "training", "log": "Starting training..."}
                )

                from model import train_model_on_text

                model, tokenizer, max_sequence_len, history = await train_model_on_text(
                    text
                )

                model_path = os.path.join(MODELS_DIR, f"{dataset}_model.keras")
                tokenizer_path = os.path.join(
                    TOKENIZERS_DIR, f"{dataset}_tokenizer.pkl"
                )

                model.save(model_path)

                with open(tokenizer_path, "wb") as f:
                    pickle.dump(
                        {"tokenizer": tokenizer, "max_len": max_sequence_len}, f
                    )

                for i, loss in enumerate(history.history["loss"]):
                    await websocket.send_json(
                        {
                            "status": "training",
                            "log": f"Epoch {i+1}/{len(history.history['loss'])} - loss: {loss:.4f}",
                        }
                    )
                    await asyncio.sleep(0.1)

                await websocket.send_json(
                    {
                        "status": "trained",
                        "dataset": dataset,
                        "log": "Model training complete.",
                    }
                )

    except WebSocketDisconnect:
        print("Client disconnected")


@app.post("/predict")
async def predict(request: PredictRequest):
    dataset_name = request.dataset
    text = request.text.strip().lower()

    if not text:
        return {"predictions": []}

    dataset_path = DATASETS.get(dataset_name)
    if not dataset_path or not os.path.exists(dataset_path):
        return {"predictions": []}

    with open(dataset_path, "r", encoding="utf-8") as f:
        all_lines = [line.strip().lower() for line in f.readlines()]

    matches = [line for line in all_lines if line.startswith(text)]
    contains_matches = [
        line for line in all_lines if text in line and line not in matches
    ]
    full_matches = list(dict.fromkeys(matches + contains_matches))

    return {"predictions": full_matches[:10]}


@app.get("/check_model_status")
async def check_model_status(dataset: str):
    model_path = os.path.join(MODELS_DIR, f"{dataset}_model.keras")
    tokenizer_path = os.path.join(TOKENIZERS_DIR, f"{dataset}_tokenizer.pkl")
    is_trained = os.path.exists(model_path) and os.path.exists(tokenizer_path)
    return {"is_trained": is_trained}


@app.get("/get_dataset_preview")
async def get_dataset_preview(
    dataset: str,
    max_lines: int = Query(500, gt=0, le=5000),
):
    """
    Provides a preview of a dataset file.
    - dataset: The key of the dataset to preview.
    - max_lines: The maximum number of lines to return.
      Defaults to 500. Has a server-side limit of 5000 to prevent abuse.
    """
    if dataset in DATASETS:
        try:
            with open(DATASETS[dataset], "r", encoding="utf-8") as f:
                lines = f.readlines()[:max_lines]
                content = "".join(lines)
            return {"preview": content}
        except FileNotFoundError:
            return {"preview": f"Error: {dataset}.txt not found."}
        except Exception as e:
            return {"preview": f"An error occurred: {e}"}

    return {"preview": ""}
