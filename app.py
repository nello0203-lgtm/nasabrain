import numpy as np
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# NEU: Wir übergeben jetzt auch fish und water an die Engine
def run_nasa_engine(catches, attempts, weather=None, fish="Unbekannt", water="Unbekannt"):
    # 1. BASIS-RECHNUNG (Die Mondmathematik)
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
    
    # 2. KI-LOG (Hier sieht das Gehirn jetzt ALLES)
    if weather:
        print(f"\n--- 🧠 NEUER DATENSATZ FÜR KI ---")
        print(f"Ziel: {fish} am Gewässer: {water}")
        print(f"Erfolg: {catches} Fänge bei {attempts} Versuchen")
        print(f"Wetter: {weather.get('abs_pressure')} hPa | Trend 3h: {weather.get('pressure_trend_3h')} hPa")
        if 'lat' in weather and 'lng' in weather:
            print(f"Koordinaten: {weather.get('lat')}, {weather.get('lng')}")
        print(f"----------------------------------\n")
        # HIER kommt gleich die Datenbank hin!
    
    return {
        "score": round(nasa_score * 100, 2),
        "uncertainty": round(uncertainty * 100, 2)
    }

@app.route('/')
def home():
    return "NASA BRAIN: FULL-CONTEXT ENGINE ONLINE"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    
    # Den Rucksack komplett auspacken:
    c = data.get('catches', 0)
    a = data.get('attempts', 0)
    w = data.get('weather_context')
    fish_type = data.get('fish_type', 'Unbekannt')
    water_id = data.get('water_id', 'Unbekannt')
    
    # Alles an die Engine übergeben
    result = run_nasa_engine(c, a, weather=w, fish=fish_type, water=water_id)
    
    return jsonify({
      "status": "success",
      "nasa_score": f"{result['score']}%",
      "confidence_gap": f"{result['uncertainty']}%",
      "method": "Monte Carlo + Full Context Recording"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
