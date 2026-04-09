import numpy as np
from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

# Der Name unserer "Aktenordner"-Datei
HISTORY_FILE = "ai_history.json"

def save_to_memory(catches, attempts, weather, fish, water):
    """Speichert den Rucksack dauerhaft in der Datenbank ab."""
    if not weather:
        return # Ohne Wetter lernen wir nichts
        
    entry = {
        "timestamp": datetime.now().isoformat(),
        "fish_type": fish,
        "water_id": water,
        "catches": catches,
        "attempts": attempts,
        "weather": weather
    }
    
    # 1. Aktenordner öffnen (falls er schon existiert)
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except Exception as e:
            print(f"Fehler beim Lesen der Akte: {e}")
            
    # 2. Neue Postkarte abheften
    history.append(entry)
    
    # 3. Aktenordner wieder schließen und speichern
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)
        
    print(f"\n--- 💾 KI HAT GESPEICHERT ---")
    print(f"Eintrag Nr. {len(history)} erfolgreich abgeheftet!")
    print(f"Zielfisch: {fish} | Gewässer: {water}")
    print(f"-----------------------------\n")

def run_nasa_engine(catches, attempts, weather=None, fish="Unbekannt", water="Unbekannt"):
    # 1. BASIS-RECHNUNG
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
    
    # 2. ERINNERUNG SPEICHERN
    save_to_memory(catches, attempts, weather, fish, water)
    
    return {
        "score": round(nasa_score * 100, 2),
        "uncertainty": round(uncertainty * 100, 2)
    }

@app.route('/')
def home():
    # Wir zeigen direkt an, wie viele Einträge die KI schon gelernt hat
    count = 0
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            count = len(json.load(f))
    return f"NASA BRAIN ONLINE. Ich habe bereits {count} Angel-Erlebnisse studiert."

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    
    c = data.get('catches', 0)
    a = data.get('attempts', 0)
    w = data.get('weather_context')
    fish_type = data.get('fish_type', 'Unbekannt')
    water_id = data.get('water_id', 'Unbekannt')
    
    result = run_nasa_engine(c, a, weather=w, fish=fish_type, water=water_id)
    
    return jsonify({
      "status": "success",
      "nasa_score": f"{result['score']}%",
      "confidence_gap": f"{result['uncertainty']}%",
      "method": "Monte Carlo + Database Storage"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
