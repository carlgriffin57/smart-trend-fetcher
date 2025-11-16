# Smart Trend Fetcher

A lightweight Flask API that delivers believable, dynamic trend data without tripping Google Trends rate limits.  
It fetches real data every 12 hours and simulates gradual movement between live updates.

---

## 🌍 Live Endpoint
Deployed example on Render:
> https://smart-trend-fetcher.onrender.com/

---

## 🔹 Endpoints

### `/`
**Purpose:** Health check  
**Example:**  
https://smart-trend-fetcher.onrender.com/

---

### `/trends?keyword=ai`
**Purpose:** Fetch cached or simulated trend data  
**Example:**  
https://smart-trend-fetcher.onrender.com/trends?keyword=ai%20automation  

**Response Example:**
```json
{
  "keyword": "ai automation",
  "trend_direction": "rising",
  "growth_rate": 2,
  "search_volume": 58,
  "timestamp": "2025-11-16T22:50:00Z",
  "source": "simulated"
}
