from flask import Flask, request, jsonify
import torch
import numpy as np
from joblib import load
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load model and scaler
class Autoencoder(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = torch.nn.Sequential(
            torch.nn.Linear(6, 4),
            torch.nn.ReLU(),
            torch.nn.Linear(4, 2)
        )
        self.decoder = torch.nn.Sequential(
            torch.nn.Linear(2, 4),
            torch.nn.ReLU(),
            torch.nn.Linear(4, 6)
        )

    def forward(self, x):
        return self.decoder(self.encoder(x))

model = Autoencoder()
model.load_state_dict(torch.load("model/autoencoder.pth"))
model.eval()
scaler = load("model/scaler.save")

anomaly_scores = []

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    vector = np.array([
        data["avgKeystrokeInterval"],
        data["mouseVelocity"],
        data["clickFrequency"],
        data["scrollPattern"],
        data["navigationFlow"],
        data["sessionDuration"]
    ]).reshape(1, -1)

    scaled = scaler.transform(vector)
    tensor = torch.tensor(scaled, dtype=torch.float32)

    with torch.no_grad():
        output = model(tensor)
        loss = torch.mean((tensor - output) ** 2).item()

    anomaly_scores.append(loss)
    if len(anomaly_scores) > 10:
        anomaly_scores.pop(0)

    mean = np.mean(anomaly_scores)
    std = np.std(anomaly_scores)
    hijack = loss > (mean + 2 * std)

    return jsonify({
        "anomaly_score": loss,
        "risk_score": round(loss * 100, 2),
        "confidence": max(20, round(100 - loss * 100, 2)),
        "hijack_detected": hijack
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)
