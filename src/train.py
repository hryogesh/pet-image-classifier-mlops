import argparse
import os
from pathlib import Path

import mlflow
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from model import build_model, save_model


def train(data_dir, save_dir, epochs=3, batch_size=16, lr=1e-3, img_size=224, device=None):
    device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
    train_dir = os.path.join(data_dir, 'train')
    val_dir = os.path.join(data_dir, 'val')

    train_tf = transforms.Compose([
        transforms.RandomResizedCrop(img_size),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
    ])
    val_tf = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
    ])

    train_ds = datasets.ImageFolder(train_dir, transform=train_tf)
    val_ds = datasets.ImageFolder(val_dir, transform=val_tf)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)

    model = build_model(num_classes=2)
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    mlflow.set_experiment('catsdogs')
    with mlflow.start_run():
        mlflow.log_param('epochs', epochs)
        mlflow.log_param('batch_size', batch_size)
        mlflow.log_param('lr', lr)

        best_val = 0.0
        for epoch in range(epochs):
            model.train()
            running = 0.0
            total = 0
            for xb, yb in train_loader:
                xb = xb.to(device)
                yb = yb.to(device)
                optimizer.zero_grad()
                out = model(xb)
                loss = criterion(out, yb)
                loss.backward()
                optimizer.step()
                running += loss.item() * xb.size(0)
                total += xb.size(0)
            train_loss = running / total

            model.eval()
            correct = 0
            total = 0
            val_loss = 0.0
            with torch.no_grad():
                for xb, yb in val_loader:
                    xb = xb.to(device)
                    yb = yb.to(device)
                    out = model(xb)
                    loss = criterion(out, yb)
                    val_loss += loss.item() * xb.size(0)
                    preds = out.argmax(dim=1)
                    correct += (preds == yb).sum().item()
                    total += xb.size(0)
            val_loss = val_loss / total if total else 0.0
            val_acc = correct / total if total else 0.0

            mlflow.log_metric('train_loss', train_loss, step=epoch)
            mlflow.log_metric('val_loss', val_loss, step=epoch)
            mlflow.log_metric('val_acc', val_acc, step=epoch)
            print(f'Epoch {epoch+1}/{epochs} train_loss={train_loss:.4f} val_loss={val_loss:.4f} val_acc={val_acc:.4f}')

            if val_acc > best_val:
                best_val = val_acc
                Path(save_dir).mkdir(parents=True, exist_ok=True)
                out_path = os.path.join(save_dir, 'model.pt')
                save_model(model, out_path)
                mlflow.log_artifact(out_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', required=True)
    parser.add_argument('--save_dir', required=True)
    parser.add_argument('--epochs', type=int, default=3)
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--img_size', type=int, default=224)
    args = parser.parse_args()
    train(args.data_dir, args.save_dir, epochs=args.epochs, batch_size=args.batch_size, lr=args.lr, img_size=args.img_size)
