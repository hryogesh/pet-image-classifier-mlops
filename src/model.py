import torch
import torch.nn as nn
from torchvision import models


class BaselineCNN(nn.Module):
    def __init__(self, num_classes=2):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.classifier = nn.Linear(32, num_classes)

    def forward(self, inputs):
        return self.classifier(self.features(inputs).flatten(1))


def build_model(num_classes=2, model_name='resnet18'):
    if model_name == 'baseline_cnn':
        return BaselineCNN(num_classes=num_classes)
    if model_name != 'resnet18':
        raise ValueError(f'Unsupported model: {model_name}')
    model = models.resnet18(weights=None)
    in_feat = model.fc.in_features
    model.fc = nn.Linear(in_feat, num_classes)
    return model


def save_model(model, path):
    torch.save(model.state_dict(), path)


def load_model(path, device='cpu', model_name='resnet18'):
    model = build_model(model_name=model_name)
    model.load_state_dict(torch.load(path, map_location=device))
    model.to(device)
    model.eval()
    return model
