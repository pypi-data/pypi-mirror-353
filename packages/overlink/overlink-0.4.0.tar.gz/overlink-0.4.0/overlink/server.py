import threading
import time
from flask import Flask, request, send_file
from pyngrok import ngrok
from .utils import load_model
import cv2
import numpy as np
import io

class OvercloudServer:
    def __init__(self, authtoken, model_path="aov_herodetector_v5.pt", port=3001):
        self.authtoken = authtoken
        self.model_path = model_path
        self.port = port
        self.model = None
        self.ngrok_tunnel = None
        self.app = Flask(__name__)
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.route('/ping', methods=['GET'])
        def ping():
            return {"status": "ok"}, 200
        
        @self.app.route('/predict', methods=['POST'])
        def predict():
            if 'image' not in request.files:
                return {"error": "No image provided"}, 400
            
            try:
                file = request.files['image']
                img_bytes = file.read()
                nparr = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                results = self.model(img)
                annotated_img = results[0].plot()
                
                _, img_encoded = cv2.imencode('.jpg', annotated_img)
                return send_file(
                    io.BytesIO(img_encoded.tobytes()),
                    mimetype='image/jpeg'
                )
            except Exception as e:
                return {"error": str(e)}, 500
    
    def start(self):
        """Khởi động server và ngrok tunnel"""
        print("🌐 Initializing Overlink Server...")
        
        # Load model
        self.model = load_model(self.model_path)
        print("✅ Model loaded successfully!")
        
        # Start Flask in background thread
        flask_thread = threading.Thread(
            target=self.app.run, 
            kwargs={'host': '0.0.0.0', 'port': self.port},
            daemon=True
        )
        flask_thread.start()
        
        # Setup ngrok tunnel
        ngrok.set_auth_token(self.authtoken)
        try:
            self.ngrok_tunnel = ngrok.connect(self.port, bind_tls=True)
            public_url = self.ngrok_tunnel.public_url

            print("\n" + "="*70)
            print(f"🔥 Public URL: {public_url}/predict")
            print("="*70)
            print("\nCopy this URL for OvercloudClient")

            return public_url
        except Exception as e:
            err_msg = str(e)
            if ("authentication failed" in err_msg and "simultaneous ngrok agent" in err_msg) or \
               ("ERR_NGROK_108" in err_msg):
                print("\n🚨 [Overlink Ngrok Warning]")
                print("⚠️ KHÔNG thể tạo tunnel do vượt quá giới hạn session Ngrok Free. Bạn chỉ được phép 1 endpoint/ngrok ở chế độ miễn phí.")
                print("→ Xem và xoá các endpoint/ngrok cũ tại: https://dashboard.ngrok.com/endpoint")
                print("→ Hoặc thử tắt các tiến trình ngrok cũ trên máy bằng lệnh: !pkill -f ngrok")
                print(f"Thông tin lỗi: {err_msg}")
            else:
                print(f"[Overlink Ngrok Error] {err_msg}")
            raise
    
    def keep_alive(self):
        """Giữ server hoạt động"""
        try:
            while True:
                time.sleep(10)
                print(f"⏱ Server is running | URL: {self.ngrok_tunnel.public_url}/ping")
        except KeyboardInterrupt:
            print("🚫 Stopping server...")
            ngrok.disconnect(self.ngrok_tunnel.public_url)