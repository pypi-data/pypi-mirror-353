import torch
from ultralytics import YOLO

def load_model(model_path):
    """Tải model lên GPU nếu có"""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = YOLO(model_path)
    model.to(device)
    print(f"✅ Model loaded on {device.upper()}!")
    return model