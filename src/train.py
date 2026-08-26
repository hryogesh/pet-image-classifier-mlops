import argparse
import os
from pathlib import Path

import mlflow
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report

from src.model import build_model, save_model, load_model


def train(data_dir, save_dir, epochs=3, batch_size=16, lr=1e-3, img_size=224,
          model_name='resnet18', device=None):
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

    def ensure_min_samples(root_dir, min_per_class=1):
        exts = ('.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif', '.tiff', '.webp')
        for split in ['train', 'val', 'test']:
            split_dir = os.path.join(root_dir, split)
            if not os.path.isdir(split_dir):
                continue
            for cls in os.listdir(split_dir):
                cls_dir = os.path.join(split_dir, cls)
                if not os.path.isdir(cls_dir):
                    continue
                files = [f for f in os.listdir(cls_dir) if f.lower().endswith(exts)]
                if len(files) >= min_per_class:
                    continue
                # try to copy one from train for this class
                src_dir = os.path.join(root_dir, 'train', cls)
                if os.path.isdir(src_dir):
                    src_files = [f for f in os.listdir(src_dir) if f.lower().endswith(exts)]
                    if src_files:
                        src = os.path.join(src_dir, src_files[0])
                        dst = os.path.join(cls_dir, src_files[0])
                        try:
                            ensure_dir(cls_dir)
                            from shutil import copy2
                            copy2(src, dst)
                            continue
                        except Exception:
                            pass
                # if we couldn't populate, remove empty dir so ImageFolder ignores it
                try:
                    os.rmdir(cls_dir)
                except Exception:
                    pass

    # Make sure splits/classes have at least one valid file to avoid ImageFolder errors
    ensure_min_samples(data_dir)

    try:
        train_ds = datasets.ImageFolder(train_dir, transform=train_tf)
    except Exception as e:
        raise RuntimeError(f'Failed to load training dataset from {train_dir}: {e}')
    try:
        val_ds = datasets.ImageFolder(val_dir, transform=val_tf)
    except Exception:
        # fallback to using training dataset if validation isn't available
        val_ds = train_ds

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)

    model = build_model(num_classes=2, model_name=model_name)
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    mlflow.set_experiment('catsdogs')
    with mlflow.start_run():
        mlflow.log_param('epochs', epochs)
        mlflow.log_param('batch_size', batch_size)
        mlflow.log_param('lr', lr)

        mlflow.log_param('model_name', model_name)
        best_val = -1.0
        train_losses = []
        val_losses = []
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
            train_loss = running / total if total else 0.0
            train_losses.append(train_loss)

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
            val_losses.append(val_loss)

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

        # Plot and log loss curves
        try:
            Path(save_dir).mkdir(parents=True, exist_ok=True)
            loss_fig = os.path.join(save_dir, 'loss_curve.png')
            plt.figure()
            plt.plot(range(1, len(train_losses) + 1), train_losses, label='train_loss')
            plt.plot(range(1, len(val_losses) + 1), val_losses, label='val_loss')
            plt.xlabel('epoch')
            plt.ylabel('loss')
            plt.legend()
            plt.title('Loss curve')
            plt.savefig(loss_fig)
            plt.close()
            mlflow.log_artifact(loss_fig)
        except Exception:
            pass

        # Evaluate and log confusion matrix on test set if present
        test_dir = os.path.join(data_dir, 'test')
        if os.path.exists(test_dir):
            test_ds = datasets.ImageFolder(test_dir, transform=val_tf)
            test_loader = DataLoader(test_ds, batch_size=batch_size)

            # load best model
            best_model_path = os.path.join(save_dir, 'model.pt')
            if os.path.exists(best_model_path):
                best = load_model(best_model_path, device=device, model_name=model_name)
            else:
                best = model

            y_true = []
            y_pred = []
            with torch.no_grad():
                for xb, yb in test_loader:
                    xb = xb.to(device)
                    out = best(xb)
                    preds = out.argmax(dim=1).cpu().numpy()
                    y_pred.extend(preds.tolist())
                    y_true.extend(yb.numpy().tolist())

            if y_true:
                cm = confusion_matrix(y_true, y_pred)
                try:
                    cm_fig = os.path.join(save_dir, 'confusion_matrix.png')
                    plt.figure()
                    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
                    plt.title('Confusion matrix')
                    plt.colorbar()
                    tick_marks = list(range(len(test_ds.classes)))
                    plt.xticks(tick_marks, test_ds.classes, rotation=45)
                    plt.yticks(tick_marks, test_ds.classes)
                    plt.ylabel('True label')
                    plt.xlabel('Predicted label')
                    plt.tight_layout()
                    plt.savefig(cm_fig)
                    plt.close()
                    mlflow.log_artifact(cm_fig)
                except Exception:
                    pass

                # classification report
                try:
                    report = classification_report(y_true, y_pred, target_names=test_ds.classes)
                    rpt_file = os.path.join(save_dir, 'classification_report.txt')
                    with open(rpt_file, 'w') as fh:
                        fh.write(report)
                    mlflow.log_artifact(rpt_file)
                except Exception:
                    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', required=True)
    parser.add_argument('--save_dir', required=True)
    parser.add_argument('--epochs', type=int, default=3)
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--img_size', type=int, default=224)
    parser.add_argument('--model_name', choices=['resnet18', 'baseline_cnn'], default='resnet18')
    args = parser.parse_args()
    train(args.data_dir, args.save_dir, epochs=args.epochs, batch_size=args.batch_size,
          lr=args.lr, img_size=args.img_size, model_name=args.model_name)
