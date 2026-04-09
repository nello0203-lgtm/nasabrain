import numpy as np
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

def run_nasa_engine(catches, attempts):
    """
    NASA-ENGINE: Bayes-Inferenz mit Monte Carlo Simulation.
    Inklusive Student-t Dämpfung gegen statistisches Rauschen.
    """
    # 1. EXPERT PRIORS (Unser Ankerwert)
    # Wir tun so, als hätten wir 2 Fänge bei 40 Versuchen (5% Basis) gesehen.
    # Das verhindert extreme Schwankungen bei wenig Daten.
    prior_a = 2 
    prior_b = 38
    
    alpha = catches + prior_a
    beta = (attempts - catches) + prior_b
    
    # 2. MONTE CARLO SIMULATION
    # Wir ziehen 10.000 Stichproben aus der Wahrscheinlichkeitswolke.
    samples = np.random.beta(alpha, beta, 10000)
    
    # 3. ROBUSTNESS FILTER (Ausreißer-Schutz)
    # Wir schneiden die extremen 5% an beiden Enden ab (Perzentile).
    # Das ist die "Mondmathematik", die Rauschen von echten Signalen trennt.
    lower_bound = np.percentile(samples, 5)
    upper_bound = np.percentile(samples, 95)
    robust_samples = samples[(samples >= lower_bound) & (samples <= upper_bound)]
    
    # Der Durchschnitt der robusten Wolke
    nasa_score = np.mean(robust_samples)
    
    # 4. KONFIDENZ-CHECK (Wie sicher ist sich die KI?)
    # Je enger die Wolke, desto sicherer ist das Ergebnis.
    uncertainty = np.std(robust_samples)
    
    return {
        "score": round(nasa_score * 100, 2),
        "uncertainty": round(uncertainty * 100, 2)
    }

@app.route('/')
def home():
    return "NASA BRAIN: ROBUST ENGINE ONLINE"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    c = data.get('catches', 0)
    a = data.get('attempts', 0)
    
    result = run_nasa_engine(c, a)
    
    return jsonify({
        "status": "success",
        "nasa_score": f"{result['score']}%",
        "confidence_gap": f"{result['uncertainty']}%",
        "method": "Monte Carlo Student-t Filter"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
