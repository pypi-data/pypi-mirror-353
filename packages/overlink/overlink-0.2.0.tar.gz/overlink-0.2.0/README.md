# Overlink - Cloud GPU Bridge

[![PyPI version](https://img.shields.io/pypi/v/overlink.svg)](https://pypi.org/project/overlink/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/)
[![Documentation Status](https://readthedocs.org/projects/overlink/badge/?version=latest)](https://overlink.readthedocs.io/en/latest/?badge=latest)

**Overlink** is a Python framework that connects your local application to cloud GPU resources (Google Colab, Kaggle, etc.) through ngrok tunnels. With Overlink, you can easily leverage powerful cloud GPUs without complicated setup.

## 🌟 Key Features

- 🚀 **Automatic ngrok tunnel setup** - No manual configuration needed
- ⚡ **Leverage cloud GPUs** - Handle intensive AI/ML tasks seamlessly
- 🔄 **Simple API** - Easy integration into existing projects
- 🔒 **Secure HTTPS connection** - Safeguard your data
- 📊 **Connection monitoring** - Track server status in real time
- 🧩 **YOLO model support** - Built-in Ultralytics YOLOv5/v8 integration

## 📦 Installation

Install Overlink via pip:

```bash
pip install overlink
```

System requirements:

- Python 3.6+
- Dependencies are automatically installed with the package

## 🚀 Quick Start

### 1. Setup server on Google Colab

```python
!pip install -q overlink
from overlink import OvercloudServer
import getpass

# Enter your ngrok authtoken (get it at: https://dashboard.ngrok.com/get-started/your-authtoken)
ngrok_token = getpass.getpass("🔑 Enter your ngrok authtoken: ")

# Initialize the server
server = OvercloudServer(
    authtoken=ngrok_token,
    model_path="/content/yolov8n.pt",  # Path to your model
    port=5000  # Optional port (default: 3001)
)

# Start the server and get the public URL
public_url = server.start()

# Keep the server running
server.keep_alive()
```

### 2. Use client on your local machine

```python
from overlink import OvercloudClient
import cv2

# Initialize the client with the server URL
client = OvercloudClient("https://your-ngrok-url")

# Check connection
if client.ping():
    print("✅ Successfully connected to cloud GPU!")

    # Process image via cloud
    result = client.process_image("input.jpg")

    # Display and save the result
    cv2.imshow("Result", result)
    cv2.waitKey(0)
    cv2.imwrite("output.jpg", result)
else:
    print("❌ Cannot connect to server")
```

## 📚 Detailed Guide

### Server configuration

| Parameter     | Default      | Description                                |
| ------------- | ------------ | ------------------------------------------ |
| `authtoken`   | **Required** | Ngrok authtoken (get from ngrok dashboard) |
| `model_path`  | `None`       | Path to YOLO model (.pt file)              |
| `port`        | `3001`       | Local port for Flask server                |
| `flask_debug` | `False`      | Enable Flask debug mode                    |

**Advanced Example:**

```python
server = OvercloudServer(
    authtoken="2w1Z93Yc23gB6Jl6jncvYfEkQC4_KpA55x6yTnakDb81HXJo",
    model_path="/content/custom_model.pt",
    port=5000
)

# Custom image processing endpoint
@server.app.route('/custom-process', methods=['POST'])
def custom_process():
    # Add your custom processing code here
    pass

public_url = server.start()
```

### Using the client

#### Main methods

1. **`ping()`** - Check server connectivity
   - Returns `True` if the server is up, `False` otherwise
2. **`process_image(image_path)`** - Process an image via the server
   - `image_path`: Path to the image file to process
   - Returns the processed image as a numpy array (OpenCV format)

#### Example: Batch processing

```python
import os
from tqdm import tqdm

input_dir = "input_images"
output_dir = "processed_images"

os.makedirs(output_dir, exist_ok=True)

for filename in tqdm(os.listdir(input_dir)):
    if filename.endswith(('.jpg', '.png', '.jpeg')):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, f"processed_{filename}")

        try:
            result = client.process_image(input_path)
            cv2.imwrite(output_path, result)
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
```

## 🧪 Performance Test

| Input Image | Processing Time (Colab T4 GPU) | Processing Time (Local CPU) |
| ----------- | ------------------------------ | --------------------------- |
| 640x480     | 120ms                          | 850ms                       |
| 1280x720    | 250ms                          | 2200ms                      |
| 1920x1080   | 450ms                          | 4800ms                      |

_Test results with YOLOv8n using the same hardware_

## 🔧 Common Troubleshooting

1. **Ngrok connection error**

   - Make sure your authtoken is correct
   - Check the server's internet connection

2. **Timeout while processing image**

   - Increase timeout on the client:
     ```python
     # In client.py, update timeout=60
     response = requests.post(..., timeout=60)
     ```
   - Reduce the input image size

3. **Failed to load model**

   - Check the model path on the server
   - Ensure the model is compatible with the Ultralytics version

4. **GPU out of memory**
   - Reduce batch size
   - Use a smaller model
   - Upgrade your Colab GPU (Pro/Premium)

## 🌐 System Architecture

```mermaid
graph LR
    A[Local PC] -->|Send image| B[OvercloudClient]
    B -->|HTTPS Request| C[ngrok Tunnel]
    C --> D[Cloud Server]
    D -->|GPU Processing| E[YOLO Model]
    E -->|Result| D
    D -->|Response| C
    C -->|Processed image| B
    B --> A
```

## 💡 Example Applications

### 1. GUI Client (using Tkinter)

```python
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
from overlink import OvercloudClient

class OverlinkGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Overlink Client")
        self.geometry("1200x600")

        # Build user interface
        self.create_widgets()

        # Initialize client
        self.client = None

    def create_widgets(self):
        # URL input section
        url_frame = tk.Frame(self)
        url_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(url_frame, text="Server URL:").pack(side=tk.LEFT)
        self.url_entry = tk.Entry(url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.connect_btn = tk.Button(
            url_frame,
            text="Connect",
            command=self.connect_server
        )
        self.connect_btn.pack(side=tk.LEFT)

        # Image display sections
        img_frame = tk.Frame(self)
        img_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Original image
        self.orig_frame = tk.LabelFrame(img_frame, text="Original Image")
        self.orig_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.orig_label = tk.Label(self.orig_frame)
        self.orig_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Processed result image
        self.result_frame = tk.LabelFrame(img_frame, text="Result")
        self.result_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.result_label = tk.Label(self.result_frame)
        self.result_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Action buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=10)

        self.select_btn = tk.Button(
            btn_frame,
            text="Choose Image",
            command=self.select_image,
            state=tk.DISABLED
        )
        self.select_btn.pack(side=tk.LEFT, padx=20)

        self.save_btn = tk.Button(
            btn_frame,
            text="Save Result",
            command=self.save_result,
            state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=20)

        # Status bar
        self.status_var = tk.StringVar(value="Not connected")
        status_bar = tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def connect_server(self):
        server_url = self.url_entry.get().strip()
        if not server_url:
            self.status_var.set("❌ Please enter the server URL")
            return

        try:
            self.client = OvercloudClient(server_url)
            if self.client.ping():
                self.status_var.set(f"✅ Connected to: {server_url}")
                self.select_btn.config(state=tk.NORMAL)
            else:
                self.status_var.set(f"❌ Cannot connect to server")
        except Exception as e:
            self.status_var.set(f"Connection error: {str(e)}")

    def select_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            # Display original image
            self.display_image(file_path, self.orig_label)

            # Process the image
            self.process_image(file_path)

    def process_image(self, file_path):
        try:
            result = self.client.process_image(file_path)

            # Convert for display
            result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            self.result_image = Image.fromarray(result_rgb)
            self.display_result(self.result_image)

            self.status_var.set("✅ Successfully processed!")
            self.save_btn.config(state=tk.NORMAL)
        except Exception as e:
            self.status_var.set(f"❌ Processing error: {str(e)}")

    def display_image(self, path, label):
        img = Image.open(path)
        img.thumbnail((500, 500))
        photo = ImageTk.PhotoImage(img)
        label.config(image=photo)
        label.image = photo

    def display_result(self, img):
        img.thumbnail((500, 500))
        photo = ImageTk.PhotoImage(img)
        self.result_label.config(image=photo)
        self.result_label.image = photo

    def save_result(self):
        if hasattr(self, 'result_image'):
            file_path = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            if file_path:
                self.result_image.save(file_path)
                self.status_var.set(f"✅ Saved at: {file_path}")

if __name__ == "__main__":
    app = OverlinkGUI()
    app.mainloop()
```

### 2. Integrate into image processing pipeline

```python
from overlink import OvercloudClient
import cv2
import time

class ImageProcessor:
    def __init__(self, use_cloud=False, cloud_url=None):
        self.use_cloud = use_cloud
        if use_cloud:
            self.client = OvercloudClient(cloud_url)
            assert self.client.ping(), "Cannot connect to cloud server"

    def process(self, image):
        if self.use_cloud:
            # Save a temp image to send to server
            temp_path = "temp_input.jpg"
            cv2.imwrite(temp_path, image)
            return self.client.process_image(temp_path)
        else:
            # Local processing
            return self.local_processing(image)

    def local_processing(self, image):
        # Your CPU local processing code here
        # ...
        return processed_image

# Usage
processor = ImageProcessor(
    use_cloud=True,
    cloud_url="https://your-ngrok-url"
)

cap = cv2.VideoCapture(0)  # Webcam

while True:
    ret, frame = cap.read()
    if not ret:
        break

    start = time.time()
    result = processor.process(frame)
    fps = 1 / (time.time() - start)

    cv2.putText(result, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Real-time Processing", result)

    if cv2.waitKey(1) == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
```

## 🤝 Contributions

Overlink is an open source project and welcomes all contributions! Get involved by:

1. **Reporting bugs**: Open an issue on GitHub
2. **Suggesting features**: Share your new ideas
3. **Contributing code**: Submit a pull request
4. **Improving documentation**: Help make the docs clearer

Detailed contribution guide:

```bash
# 1. Fork the repository
# 2. Clone your fork
git clone https://github.com/username/overlink.git

# 3. Create a new branch
git checkout -b feature/new-feature

# 4. Make changes
# 5. Commit and push
git push origin feature/new-feature

# 6. Open a pull request
```

## 📜 License

This project is distributed under the MIT License. See the [LICENSE](https://github.com/KhanhRomVN/overlink/blob/main/LICENSE) file for more details.

## 📞 Contact

- Author: KhanhRomVN
- Email: khanhromvn@gmail.com
- GitHub: [https://github.com/KhanhRomVN](https://github.com/KhanhRomVN)
- Project: [https://github.com/KhanhRomVN/overlink](https://github.com/KhanhRomVN/overlink)

## 🙏 Credits

Overlink relies on these awesome open source projects:

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) - Object detection framework
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Pyngrok](https://pyngrok.readthedocs.io/) - Python wrapper for ngrok
- [OpenCV](https://opencv.org/) - Image processing

---

**Overlink** – The simple bridge between your local application and the power of cloud GPUs!
