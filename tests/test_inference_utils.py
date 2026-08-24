import io
from PIL import Image
from src.inference.utils import preprocess_image_bytes


def test_preprocess_shape():
    img = Image.new('RGB', (500, 400), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    b = buf.getvalue()
    t = preprocess_image_bytes(b)
    assert t.shape[1:] == (3, 224, 224)
