import torch
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class CNNModel(torch.nn.Module):
    def __init__(self):
        super(CNNModel, self).__init__()

        # Convolution 1 and Max pool 1
        self.cnn1 = torch.nn.Conv2d(in_channels=1, out_channels=32, kernel_size=5, stride=1, padding=1)
        self.batch1 = torch.nn.BatchNorm2d(32)
        self.drop1 = torch.nn.Dropout(0.2)
        self.relu1 = torch.nn.ReLU()
        self.maxpool1 = torch.nn.MaxPool2d(kernel_size=3, stride=1)

        # Convolution 2 and Max pool 2
        self.cnn2 = torch.nn.Conv2d(in_channels=32, out_channels=128, kernel_size=3, stride=1, padding=1)
        self.batch2 = torch.nn.BatchNorm2d(128)
        self.drop2 = torch.nn.Dropout(0.5)
        self.relu2 = torch.nn.ReLU()
        self.maxpool2 = torch.nn.MaxPool2d(kernel_size=2, stride=1)

        # Fully connected 1 (readout)
        self.flat = torch.nn.Flatten()
        self.fc1 = torch.nn.Linear(27 * 19 * 128, 256)
        self.fc2 = torch.nn.Linear(256, 64)
        self.fc3 = torch.nn.Linear(64, 3)

    def forward(self, x):
        # Convolution 1 and Max pool 1
        out = self.cnn1(x)
        out = self.batch1(out)
        out = self.drop1(out)
        out = self.relu1(out)
        out = self.maxpool1(out)

        # Convolution 2 and Max pool 2
        out = self.cnn2(out)
        out = self.batch2(out)
        out = self.drop2(out)
        out = self.relu2(out)
        out = self.maxpool2(out)

        # Resize
        out = out.view(out.size(0), -1)

        # Linear function (readout)
        out = self.flat(out)
        out = self.fc1(out)
        out = self.fc2(out)
        out = self.fc3(out)

        return out

# Initialize Firebase Admin SDK
cred = credentials.Certificate("Firebase-AdminSDK")
firebase_admin.initialize_app(cred, {"databaseURL": "URL-Firebase&Path"})

# Call a Model
model = CNNModel()
model.load_state_dict(torch.load("/app/static/CNN-Model-2-5.pth", map_location=torch.device('cpu')))
model.eval()

@app.get("/predict")
async def predict():
    try:
        combined_data = {}
        X_img = []

        # Get Data form Firebase
        firebase_data = db.reference("Path-Firebase").get()

        # Get Lastet Key and Value
        last_key = list(firebase_data.keys())[-1]
        last_value = firebase_data[last_key]

        for i, value in enumerate(last_value):
            key = str(i)
            combined_data[key] = value

        allFloatNumber = [number for sublist in combined_data.values() for number in sublist]

        df = pd.DataFrame(allFloatNumber)

        for key, value in df.items():
            frame2D = []
            for h in range(24):
                frame2D.append([])
                for w in range(32):
                    t = value.iloc[h * 32 + w]
                    frame2D[h].append(t)
            X_img.append(frame2D)

        for i, input_frame in enumerate(X_img):
            input_tensor = torch.FloatTensor(input_frame).unsqueeze(0).unsqueeze(0)
            input_tensor = input_tensor.to('cpu')

            with torch.no_grad():
                outputs = model(input_tensor)
                _, predicted = torch.max(outputs.data, 1)
            
        # Update Result to Firebase
        db.reference("Path-Firebase").update({last_key: predicted.item()})

        return JSONResponse(content={"success": True, "message": {"timestamp": last_key, "result": predicted.item()}})

    except Exception as e:
        return JSONResponse(content={"success": False, "message": f"Error: {e}"})

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
