import io
from PIL import Image
import torch
from src.inference.utils import preprocess_image_bytes
from src.model import build_model


def test_preprocess_shape():
    img = Image.new('RGB', (500, 400), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    b = buf.getvalue()
    t = preprocess_image_bytes(b)
    assert t.shape[1:] == (3, 224, 224)


def test_supported_models_return_two_class_logits():
    for model_name in ('baseline_cnn', 'resnet18'):
        model = build_model(model_name=model_name)
        output = model(torch.zeros(1, 3, 224, 224))
        assert output.shape == (1, 2)
