import numpy as np
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

def run_nasa_engine(catches, attempts, weather=None):
    # BASIS-RECHNUNG (Wie bisher)
    prior_a = 2 
    prior_b = 38
    alpha = catches + prior_a
    beta = (attempts - catches) + prior_b
    
    samples = np.random.beta(alpha, beta, 10000)
    lower_bound = np.percentile(samples, 5)
    upper_bound = np.percentile(samples, 95)
    robust_samples = samples[(samples >= lower_bound) & (samples <= upper_bound)]
    
    nasa_score = np.mean(robust_samples)
    uncertainty = np.std(robust_samples)
    
    # KI-LOG (Hier lernt das Gehirn!)
    if weather:
        print(f"--- KI LERNT ---")
        print(f"Fang bei {weather.get('abs_pressure')} hPa")
        print(f"Trend 3h: {weather.get('pressure_trend_3h')} hPa")
        print(f"Mondphase: {weather.get('moon_phase')}")
        # In der echten KI-Stufe speichern wir dies später in einer Datenbank
    
    return {
        "score": round(nasa_score * 100, 2),
        "uncertainty": round(uncertainty * 100, 2)
    }

@app.route('/')
def home():
    return "NASA BRAIN: WEATHER-AWARE ENGINE ONLINE"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    c = data.get('catches', 0)
    a = data.get('attempts', 0)
    w = data.get('weather_context') # Das neue Wetter-Paket
    
    result = run_nasa_engine(c, a, weather=w)
    
    return jsonify({
      "status": "success",
      "nasa_score": f"{result['score']}%",
      "confidence_gap": f"{result['uncertainty']}%",
      "method": "Monte Carlo + Weather Fact Recording"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
