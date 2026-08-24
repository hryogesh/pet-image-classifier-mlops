import os
import time
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import logging

from .utils import preprocess_image_bytes, load, predict


MODEL_PATH = os.environ.get('MODEL_PATH', '/app/models/model.pt')

app = FastAPI()
logger = logging.getLogger('uvicorn.error')

REQUEST_COUNT = 0


@app.on_event('startup')
def startup():
    global MODEL
    MODEL = load(MODEL_PATH)
    logger.info(f'Loaded model from {MODEL_PATH}')


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.post('/predict')
async def predict_endpoint(file: UploadFile = File(...)):
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    start = time.time()
    content = await file.read()
    try:
        img_t = preprocess_image_bytes(content)
        probs = predict(MODEL, img_t)
        latency = time.time() - start
        logger.info(f'request={REQUEST_COUNT} latency={latency:.4f}s')
        return JSONResponse({'probs': probs, 'label': int(probs.index(max(probs))), 'latency': latency})
    except Exception as e:
        logger.exception('prediction failed')
        return JSONResponse({'error': str(e)}, status_code=500)
