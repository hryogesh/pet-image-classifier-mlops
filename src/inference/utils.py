import io
import time
from PIL import Image
import torch
import torchvision.transforms as transforms
from src.model import load_model


IMG_SIZE = 224


def preprocess_image_bytes(content: bytes):
    img = Image.open(io.BytesIO(content)).convert('RGB')
    tf = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
    ])
    return tf(img).unsqueeze(0)


def predict(model, img_tensor, device='cpu'):
    model.to(device)
    model.eval()
    with torch.no_grad():
        out = model(img_tensor.to(device))
        probs = torch.softmax(out, dim=1).cpu().numpy().tolist()[0]
    return probs


def load(path, device='cpu'):
    return load_model(path, device=device)
