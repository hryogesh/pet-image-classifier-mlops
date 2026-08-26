import os
import time
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, PlainTextResponse
import logging

from .utils import preprocess_image_bytes, load, predict


MODEL_PATH = os.environ.get('MODEL_PATH', '/app/models/model.pt')
MODEL_NAME = os.environ.get('MODEL_NAME', 'resnet18')

app = FastAPI()
logger = logging.getLogger('uvicorn.error')

# Basic in-memory metrics
REQUEST_COUNT = 0
TOTAL_LATENCY = 0.0
ERROR_COUNT = 0

# Prometheus metrics (optional)
try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

    PROM_AVAILABLE = True
    PROM_REQUESTS = Counter('inference_requests_total', 'Total inference requests')
    PROM_ERRORS = Counter('inference_errors_total', 'Total inference errors')
    PROM_LATENCY = Histogram('inference_latency_seconds', 'Inference request latency')
except Exception:
    PROM_AVAILABLE = False


@app.on_event('startup')
def startup():
    global MODEL
    MODEL = load(MODEL_PATH, model_name=MODEL_NAME)
    logger.info(f'Loaded {MODEL_NAME} model from {MODEL_PATH}')


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.post('/predict')
async def predict_endpoint(file: UploadFile = File(...)):
    global REQUEST_COUNT, TOTAL_LATENCY, ERROR_COUNT
    REQUEST_COUNT += 1
    start = time.time()
    content = await file.read()
    if PROM_AVAILABLE:
        PROM_REQUESTS.inc()
    try:
        img_t = preprocess_image_bytes(content)
        if PROM_AVAILABLE:
            with PROM_LATENCY.time():
                probs = predict(MODEL, img_t)
        else:
            probs = predict(MODEL, img_t)
        latency = time.time() - start
        TOTAL_LATENCY += latency
        logger.info(f'request={REQUEST_COUNT} latency={latency:.4f}s')
        return JSONResponse({'probs': probs, 'label': int(probs.index(max(probs))), 'latency': latency})
    except Exception as e:
        ERROR_COUNT += 1
        if PROM_AVAILABLE:
            PROM_ERRORS.inc()
        logger.exception('prediction failed')
        return JSONResponse({'error': str(e)}, status_code=500)


@app.get('/metrics')
def metrics_json():
    # lightweight JSON metrics for simple monitoring
    avg_latency = TOTAL_LATENCY / REQUEST_COUNT if REQUEST_COUNT else 0.0
    return {
        'requests_total': REQUEST_COUNT,
        'errors_total': ERROR_COUNT,
        'avg_latency_seconds': avg_latency,
    }


@app.get('/metrics_prometheus')
def metrics_prometheus():
    if PROM_AVAILABLE:
        data = generate_latest()
        return PlainTextResponse(data.decode('utf-8'), media_type=CONTENT_TYPE_LATEST)
    else:
        return PlainTextResponse('# Prometheus client not available', status_code=503)
