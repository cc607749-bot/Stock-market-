from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
API_KEY = "QUxMIFPVVlgqFTRSBBUkUgQkVMT(" # Apni complete API key yahan dalein
BASE_URL = "https://stock.indianapi.in"

# Jin stocks ko aap track karna chahte hain unki list
TRACKED_STOCKS = [
    "Tata Power", "Reliance", "L&T", "KPI Green", 
    "Suzlon", "BHEL", "Infosys", "Adani Green"
]

def check_company_deals(stock_name):
    """
    Har company ki recent news ya announcements fetch karke keywords match karta hai.
    """
    headers = {
        "x-api-key": API_KEY,
        "Accept": "application/json"
    }
    
    # 1. Pehle Recent Announcements ya News check karte hain
    url = f"{BASE_URL}/stock?name={stock_name}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            # Extract basic details
            current_price = data.get("currentPrice", "N/A")
            percent_change = data.get("percentChange", 0)
            
            # Keywords jisse deals/orders ka pata chale
            keywords = ["order", "deal", "project", "contract", "awarded", "secures", "mou"]
            found_deals = []
            
            # Recent News list ko check karna
            recent_news = data.get("recentNews", [])
            for news in recent_news:
                title = news.get("title", "").lower()
                description = news.get("description", "").lower()
                
                # Agar koi keyword match hota hai
                if any(kw in title or any(kw in description for kw in keywords) for kw in keywords):
                    found_deals.append({
                        "title": news.get("title"),
                        "url": news.get("url", "#"),
                        "date": news.get("date", "Recent")
                    })
            
            # Agar koi deal ya project mili, toh company select hogi
            if found_deals:
                return {
                    "companyName": stock_name,
                    "currentPrice": current_price,
                    "percentChange": percent_change,
                    "deals": found_deals
                }
    except Exception as e:
        print(f"Error fetching {stock_name}: {e}")
        
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scan-deals')
def scan_deals():
    selected_companies = []
    
    # Sabhi tracked stocks ko loop karke filter karna
    for stock in TRACKED_STOCKS:
        result = check_company_deals(stock)
        if result:
            selected_companies.append(result)
            
    return jsonify(selected_companies)

if __name__ == '__main__':
    app.run(debug=True, port=5000)