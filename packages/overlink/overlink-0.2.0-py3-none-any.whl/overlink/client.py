import requests
import numpy as np
import cv2
import os

class OvercloudClient:
    def __init__(self, server_url):
        self.server_url = server_url.rstrip('/')
        self.predict_url = f"{self.server_url}/predict"
        self.ping_url = f"{self.server_url}/ping"
    
    def ping(self):
        """Kiểm tra kết nối server"""
        try:
            response = requests.get(self.ping_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def process_image(self, image_path):
        """Xử lý ảnh thông qua cloud server"""
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                response = requests.post(
                    self.predict_url, 
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                img_array = np.frombuffer(response.content, np.uint8)
                return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            else:
                raise Exception(f"Server error: {response.status_code}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")