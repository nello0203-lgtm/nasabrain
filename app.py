import numpy as np
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Die NASA-Simulation (Monte Carlo)
def run_simulation(catches, attempts):
    # Wir starten mit einem 'Expert Prior' (Basis-Glaube)
    # entspr. ca. 1 Fang auf 20 Versuche
    alpha = catches + 1
    beta = (attempts - catches) + 19
    
    # Der Kern: 10.000 Stichproben ziehen
    samples = np.random.beta(alpha, beta, 10000)
    return round(np.mean(samples) * 100, 2)

@app.route('/')
def home():
    return "NASA BRAIN IS ONLINE"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    c = data.get('catches', 0)
    a = data.get('attempts', 0)
    score = run_simulation(c, a)
    return jsonify({"nasa_score": f"{score}%", "status": "success"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
