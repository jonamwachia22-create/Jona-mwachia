from flask import Flask, request, render_template_string, jsonify
import africastalking
import os, re, json, requests
from datetime import datetime

app = Flask(__name__)

# === STORAGE YA KUDUMU - HAIPOTEI ===
FILE = "transactions.json"
def load_trans():
    if os.path.exists(FILE):
        try:
            with open(FILE,'r') as f: return json.load(f)
        except: return []
    return []
def save_trans(data):
    try:
        with open(FILE,'w') as f: json.dump(data[-200:], f)
    except: pass

# === AFRICASTALKING CONFIG - FIXED ===
AT_USERNAME = os.environ.get("AT_USERNAME", "sandbox")
AT_API_KEY = os.environ.get("AT_API_KEY", "atsk_xxx")

# Auto-detect LIVE vs SANDBOX URL
if AT_USERNAME == "sandbox":
    AT_SMS_URL = "sandbox"
    AT_DATA_URL = "https://api.sandbox.africastalking.com/version1/mobile/data/request"
    AT_AIRTIME_URL = "https://api.sandbox.africastalking.com/version1/airtime/send"
else:
    AT_SMS_URL = AT_USERNAME
    AT_DATA_URL = "https://api.africastalking.com/version1/mobile/data/request"
    AT_AIRTIME_URL = "https://api.africastalking.com/version1/airtime/send"

try:
    africastalking.initialize(AT_USERNAME, AT_API_KEY)
    sms = africastalking.SMS
    airtime = africastalking.Airtime
except Exception as e:
    print(f"[AT INIT ERROR] {e}")
    sms = None
    airtime = None

# === BUNDLE MAP - POCHI + AT ===
BUNDLES = {5:"10MB", 10:"50MB", 20:"1GB", 35:"2GB", 50:"5GB", 100:"UNLIMITED 24H", 500:"7 DAYS", 1500:"30 DAYS"}

# AT Mobile Data productNames - BADILISHA KWA ZAKO KWENYE AT DASHBOARD > MOBILE DATA > PRODUCTS
AT_DATA_PRODUCTS = {
    5: "Safaricom_10MB_5",
    10: "Safaricom_50MB_10",
    20: "Safaricom_Data_1GB_20",
    35: "Safaricom_Data_2GB_35",
    50: "Safaricom_Data_5GB_50",
    100: "Safaricom_Data_100",
    500: "Safaricom_Data_500",
    1500: "Safaricom_Data_1500"
}

def send_bundle_via_at(phone, amount):
    """Tuma bundle automatic via AT Mobile Data API"""
    try:
        product = AT_DATA_PRODUCTS.get(amount)
        if not product:
            print(f"[AT DATA] No product for amount {amount}")
            return False

        headers = {
            "apiKey": AT_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "username": AT_USERNAME,
            "productName": product,
            "recipients": [{"phoneNumber": phone}]
        }
        print(f"[AT DATA REQUEST] {AT_DATA_URL} -> {payload}")
        resp = requests.post(AT_DATA_URL, json=payload, headers=headers, timeout=20)
        print(f"[AT DATA RESPONSE] {resp.status_code} - {resp.text[:500]}")
        return resp.status_code in [200,201]
    except Exception as e:
        print(f"[AT DATA ERROR] {e}")
        return False

HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>VENTE TAVETA 24/7</title><style>body{font-family:sans-serif;text-align:center;padding:15px;background:#f5f5f5}.btn{background:green;color:white;padding:14px;border:none;width:100%;font-weight:bold;font-size:16px;border-radius:8px}.card{border:2px solid green;border-radius:10px;padding:15px;margin:10px 0;background:white}a{color:green;font-weight:bold;text-decoration:none}</style></head><body><h2 style="background:green;color:white;padding:12px;border-radius:8px;">VENTE - CEO JONA MWACHIA<br>TAVETA 24/7</h2><div class="card" style="background:#e8ffe8;border:3px solid green;"><h3 style="color:green;">💚 LIPA KWANZA NA POCHI</h3><p><b>Pochi:</b> 0141761672</p><p><a href="https://bit.ly/pb-pay" target="_blank">👉 BONYEZA HAPA KULIPA</a></p><p><a href="/transactions">👀 Angalia Malipo Live</a></p></div><div class="card"><h3>CHAGUA BUNDLE</h3><form method="post"><input name="phone" placeholder="0707XXXXXX" required style="padding:10px;width:90%;margin:8px;border:2px solid green;border-radius:5px;"><br><br><select name="product" style="padding:10px;width:95%;border:2px solid green;border-radius:5px;"><option value="10MB_5">10MB - 5 KSH</option><option value="50MB_10">50MB - 10 KSH</option><option value="1GB_20">1GB - 20 KSH</option><option value="2GB_35">2GB - 35 KSH</option><option value="5GB_50">5GB - 50 KSH</option><option value="UNLIMITED_1H_50">UNLIMITED 1H - 50</option><option value="UNLIMITED_1DAY_100">UNLIMITED 24H - 100</option><option value="UNLIMITED_7DAYS_500">7 DAYS - 500</option><option value="UNLIMITED_30DAYS_1500">30 DAYS - 1500</option></select><br><br><button class="btn">✅ TUMA BUNDLE</button></form></div><div class="card" style="font-size:12px;">CEO Jona - Nazareth - 0141761672<br>AT: """+AT_USERNAME+"""<br><a href="/health">Health</a> | <a href="/ping">Ping</a> | <a href="/transactions">Transactions</a></div></body></html>"""

@app.route('/sms/incoming', methods=['GET','POST'])
def sms_incoming():
    data = request.get_json(silent=True) or {}
    raw = data.get('message') or data.get('text') or request.form.get('message') or ""
    if not raw and request.data:
        try: raw = request.data.decode()[:800]
        except: raw = str(request.data)[:800]
    if not raw: raw = "Test"

    all_t = load_trans()
    all_t.insert(0, {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "raw": str(raw)[:800]})
    save_trans(all_t)
    print(f"[MPESA] {raw}")

    # === AUTO-DETECT MALIPO + AUTO-SEND BUNDLE ===
    if sms and raw and "Test" not in raw:
        try:
            amt_match = re.search(r'Ksh\s*([\d,]+\.\d+)', raw, re.IGNORECASE)
            phone_match = re.search(r'(254\d{9}|07\d{8}|01\d{8})', raw)
            if amt_match and phone_match:
                amount = int(float(amt_match.group(1).replace(',','')))
                raw_phone = phone_match.group(1)
                clean = raw_phone.replace(' ','')
                if clean.startswith('0'): clean = '254'+clean[1:]
                if not clean.startswith('254'): clean = '254'+clean
                phone_plus = '+' + clean
                bundle = BUNDLES.get(amount, f"Ksh {amount}")

                # 1. Tuma SMS ya shukrani
                reply = f"VENTE TAVETA: Asante! {bundle} yako (Ksh {amount}) imepokelewa Pochi 0141761672. Bundle inatumwa sasa. CEO Jona 0707681591"
                sms.send(reply, [phone_plus])
                print(f"[AUTO SMS] {phone_plus} -> {reply}")