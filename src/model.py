import torch
import torch.nn as nn
from torchvision import models


def build_model(num_classes=2):
    model = models.resnet18(pretrained=False)
    in_feat = model.fc.in_features
    model.fc = nn.Linear(in_feat, num_classes)
    return model


def save_model(model, path):
    torch.save(model.state_dict(), path)


def load_model(path, device='cpu'):
    model = build_model()
    model.load_state_dict(torch.load(path, map_location=device))
    model.to(device)
    model.eval()
    return model
