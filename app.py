from flask import Flask, request, render_template_string, jsonify
import africastalking
import os, re, json
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

# === AFRICASTALKING ===
AT_USERNAME = os.environ.get("AT_USERNAME", "sandbox")
AT_API_KEY = os.environ.get("AT_API_KEY", "atsk_xxx")
try:
    africastalking.initialize(AT_USERNAME, AT_API_KEY)
    sms = africastalking.SMS
except:
    sms = None

# === MPYA: BUNDLE MAP ===
BUNDLES = {5:"10MB", 10:"50MB", 20:"1GB", 35:"2GB", 50:"5GB", 100:"UNLIMITED 24H", 500:"7 DAYS", 1500:"30 DAYS"}

HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>VENTE TAVETA 24/7</title><style>body{font-family:sans-serif;text-align:center;padding:15px;background:#f5f5f5}.btn{background:green;color:white;padding:14px;border:none;width:100%;font-weight:bold;font-size:16px;border-radius:8px}.card{border:2px solid green;border-radius:10px;padding:15px;margin:10px 0;background:white}a{color:green;font-weight:bold;text-decoration:none}</style></head><body><h2 style="background:green;color:white;padding:12px;border-radius:8px;">VENTE - CEO JONA MWACHIA<br>TAVETA 24/7</h2><div class="card" style="background:#e8ffe8;border:3px solid green;"><h3 style="color:green;">💚 LIPA KWANZA NA POCHI</h3><p><b>Pochi:</b> 0141761672</p><p><a href="https://bit.ly/pb-pay" target="_blank">👉 BONYEZA HAPA KULIPA</a></p><p><a href="/transactions">👀 Angalia Malipo Live</a></p></div><div class="card"><h3>CHAGUA BUNDLE</h3><form method="post"><input name="phone" placeholder="0707XXXXXX" required style="padding:10px;width:90%;margin:8px;border:2px solid green;border-radius:5px;"><br><br><select name="product" style="padding:10px;width:95%;border:2px solid green;border-radius:5px;"><option value="10MB_5">10MB - 5 KSH</option><option value="50MB_10">50MB - 10 KSH</option><option value="1GB_20">1GB - 20 KSH</option><option value="2GB_35">2GB - 35 KSH</option><option value="5GB_50">5GB - 50 KSH</option><option value="UNLIMITED_1H_50">UNLIMITED 1H - 50</option><option value="UNLIMITED_1DAY_100">UNLIMITED 24H - 100</option><option value="UNLIMITED_7DAYS_500">7 DAYS - 500</option><option value="UNLIMITED_30DAYS_1500">30 DAYS - 1500</option></select><br><br><button class="btn">✅ TUMA BUNDLE</button></form></div><div class="card" style="font-size:12px;">CEO Jona - Nazareth - 0141761672<br><a href="/health">Health</a> | <a href="/ping">Ping</a> | <a href="/transactions">Transactions</a></div></body></html>"""

@app.route('/sms/incoming', methods=['GET','POST'])
def sms_incoming():
    data = request.get_json(silent=True) or {}
    raw = data.get('message') or data.get('text') or request.form.get('message') or ""
    if not raw and request.data:
        try: raw = request.data.decode()[:500]
        except: raw = str(request.data)[:500]
    if not raw: raw = "Test"
    all_t = load_trans()
    all_t.insert(0, {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "raw": str(raw)[:400]})
    save_trans(all_t)
    print(f"[MPESA] {raw}")

    # === MPYA: AUTO-REPLY KWA MTEJA ALIYELIPA POCHI ===
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
                reply = f"VENTE TAVETA: Asante! {bundle} yako (Ksh {amount}) imepokelewa Pochi 0141761672. Bundle inatumwa sasa. CEO Jona 0707681591"
                sms.send(reply, [phone_plus])
                print(f"[AUTO SENT] {phone_plus} -> {reply}")
        except Exception as e:
            print(f"[AUTO ERROR] {e}")

    return jsonify({"status":"ok"}), 200

@app.route('/transactions')
def trans_page():
    all_t = load_trans()
    html = "<h2>Pochi 0141761672 - LIVE</h2><a href='/'>Home</a> | <a href='/transactions'>Refresh</a><hr>"
    if not all_t:
        html += "<p>Hakuna bado. Tuma TEST kwenye SMS Forwarder!</p>"
    for t in all_t:
        html += f"<div style='border:1px solid green;margin:5px;padding:8px;background:#f0fff0;'><b>{t['time']}</b><br>{t['raw']}</div>"
    return html

@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        raw_phone = request.form['phone'].strip()
        product = request.form['product']
        clean = raw_phone.replace('+','').replace(' ','')
        if clean.startswith('0'): clean = clean[1:]
        if not clean.startswith('254'): clean = '254'+clean
        phone_plus = '+' + clean
        parts = product.split('_')
        amount = parts[-1]
        size = "_".join(parts[:-1])
        if sms:
            try: sms.send(f"VENTE TAVETA: {size} KES {amount} imetumwa. Pochi 0141761672. CEO Jona", [phone_plus])
            except: pass
        return f"<div style='text-align:center;padding:20px;'><h2 style='color:green;'>✅ {phone_plus}</h2><h3>{size} KES {amount}</h3><a href='/'>Rudi</a></div>"
    return render_template_string(HTML)

@app.route('/ping')
def ping():
    return "VENTE ALIVE - 0141761672", 200

@app.route('/health')
def health():
    return jsonify({"status":"healthy","pochi":"0141761672"}), 200

@app.route('/uptime')
def uptime():
    return jsonify({"alive":True}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)