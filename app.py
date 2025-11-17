from flask import Flask, request, jsonify
from pytrends.request import TrendReq
from datetime import datetime
import time, random

app = Flask(__name__)
from flask_cors import CORS
CORS(app)

# In-memory cache: { keyword: { data, last_update } }
cache = {}
UPDATE_INTERVAL = 43200  # 12 hours (seconds)


def fetch_real_trend(keyword):
    """Fetch from Google Trends once every 12 hours."""
    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload([keyword], cat=0, timeframe="today 3-m", geo="", gprop="")
        data = pytrends.interest_over_time()
        if data.empty:
            return None
        values = data[keyword].tolist()
        growth = values[-1] - values[0] if len(values) > 1 else 0
        direction = "rising" if growth > 0 else "falling" if growth < 0 else "stable"
        return {
            "keyword": keyword,
            "trend_direction": direction,
            "growth_rate": growth,
            "search_volume": int(values[-1]),
            "timestamp": datetime.utcnow().isoformat(),
            "source": "live"
        }
    except Exception:
        return None


def simulate_trend(last):
    """Apply gentle random drift to cached data."""
    drift = random.randint(-3, 3)
    new_volume = max(0, last["search_volume"] + drift)
    growth = drift
    direction = "rising" if growth > 0 else "falling" if growth < 0 else "stable"
    return {
        "keyword": last["keyword"],
        "trend_direction": direction,
        "growth_rate": growth,
        "search_volume": new_volume,
        "timestamp": datetime.utcnow().isoformat(),
        "source": "simulated"
    }


@app.route("/")
def home():
    return jsonify({
        "message": "Smart Trend Fetcher is running (12-hour live updates + simulation)",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/trends", methods=["GET"])
def get_trend():
    keyword = request.args.get("keyword", "").strip().lower()
    if not keyword:
        return jsonify({"error": "Missing keyword"}), 400

    entry = cache.get(keyword)
    now = time.time()

    # If new keyword or cache older than 12h → fetch fresh
    if not entry or (now - entry["last_update"]) > UPDATE_INTERVAL:
        data = fetch_real_trend(keyword)
        if data:
            cache[keyword] = {"data": data, "last_update": now}
            return jsonify(data)
        elif entry:
            sim = simulate_trend(entry["data"])
            cache[keyword] = {"data": sim, "last_update": now}
            return jsonify(sim)
        else:
            return jsonify({"error": "No data available and fetch failed"}), 500

    # Use simulated drift between real updates
    sim = simulate_trend(entry["data"])
    cache[keyword] = {"data": sim, "last_update": entry["last_update"]}
    return jsonify(sim)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
