from flask import Flask, request, render_template_string, jsonify
import africastalking
import os

app = Flask(__name__)

# Africa's Talking
AT_USERNAME = os.environ.get("AT_USERNAME", "sandbox")
AT_API_KEY = os.environ.get("AT_API_KEY", "dummy")

try:
    africastalking.initialize(AT_USERNAME, AT_API_KEY)
    sms = africastalking.SMS
except:
    sms = None

HTML = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>VENTE TAVETA 24/7 - CEO JONA</title>
<style>
body{font-family:sans-serif;text-align:center;padding:15px;background:#f5f5f5}
.btn{background:green;color:white;padding:14px;border:none;width:100%;font-weight:bold;font-size:16px;border-radius:8px;cursor:pointer}
.card{border:2px solid green;border-radius:10px;padding:15px;margin:10px 0;background:white}
a{color:green;font-weight:bold;text-decoration:none}
</style>
</head>
<body>
<h2 style="background:green;color:white;padding:12px;border-radius:8px;">VENTE - CEO JONA MWACHIA<br>TAVETA 24/7</h2>

<div class="card" style="background:#e8ffe8;border:3px solid green;">
<h3 style="color:green;">💚 LIPA KWANZA NA POCHI</h3>
<p><b>Pochi Till:</b> 0141761672</p>
<p style="font-size:18px;"><a href="https://bit.ly/pb-pay" target="_blank">👉 BONYEZA HAPA KULIPA - bit.ly/pb-pay</a></p>
<p><small>M-Pesa > Lipa na M-Pesa > Pochi la Biashara > 0707681591</small></p>
<p style="color:red;"><b>LIPA NDIO UPATE BUNDLE!</b></p>
</div>

<div class="card">
<h3>CHAGUA BUNDLE BAADA YA KULIPA</h3>
<form method="post">
Namba yako (ya kupokea bundle):<br>
<input name="phone" placeholder="0707681591" required style="padding:10px;width:90%;margin:8px;border:2px solid green;border-radius:5px;"><br><br>
Chagua Bundle Uliolipia:<br>
<select name="product" style="padding:10px;width:95%;border:2px solid green;border-radius:5px;">
<option value="10MB_5">10MB - 5 KSH</option>
<option value="50MB_10">50MB - 10 KSH</option>
<option value="1GB_20">1GB - 20 KSH</option>
<option value="2GB_35">2GB - 35 KSH</option>
<option value="5GB_50">5GB - 50 KSH</option>
<option value="UNLIMITED_1H_50">UNLIMITED 1 HOUR - 50 KSH</option>
<option value="UNLIMITED_1DAY_100">UNLIMITED 24HRS - 100 KSH</option>
<option value="UNLIMITED_7DAYS_500">UNLIMITED 7 DAYS - 500 KSH</option>
<option value="UNLIMITED_30DAYS_1500">UNLIMITED 30 DAYS - 1500 KSH</option>
</select><br><br>
<button class="btn">✅ TUMA BUNDLE SASA</button>
</form>
</div>
<div class="card" style="font-size:12px;">
<b>VENTE TAVETA 24/7</b> - Haraka | Uaminifu | Unlimited<br>
CEO Jona Mwachia - Nazareth Offline ✅<br>
<a href="/health">Health</a> | <a href="/ping">Ping</a> | <a href="/uptime">Uptime</a>
</div>
</body>
</html>
"""

@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        raw_phone = request.form['phone'].strip()
        product = request.form['product']
        
        clean = raw_phone.replace('+','').replace(' ','')
        if clean.startswith('0'):
            clean = clean[1:]
        if not clean.startswith('254'):
            clean = '254' + clean
        phone_plus = '+' + clean
        
        parts = product.split('_')
        amount = parts[-1]
        size = "_".join(parts[:-1])
        
        try:
            if sms:
                sms.send(f"VENTE TAVETA: {size} kwa KES {amount} imetumwa. Confirmation kutoka Pochi 0707681591. CEO Jona", [phone_plus])
            return f"""
            <div style="text-align:center;padding:20px;">
            <h2 style="color:green;">✅ Poa {phone_plus}!</h2>
            <h3>{size} ya KES {amount}</h3>
            <p>Umelipa na Pochi 0707681591? Tutakutumia bundle ndani ya dakika 2!</p>
            <p><b>Piga 0707681591 kwa haraka!</b></p>
            <a href="/">Rudi Nyumbani</a>
            </div>
            """
        except Exception as e:
            return f"<h3 style='text-align:center;color:green;'>✅ {size} ya KES {amount} kwa {phone_plus} - Imetumwa! Piga 0707681591. Error ya SMS: {e}</h3><a href='/'>Rudi</a>"
    
    return render_template_string(HTML)

# HEALTH CHECKS - KWA BOT UPTIME
@app.route('/ping')
def ping():
    return "VENTE TAVETA 24/7 IS ALIVE - CEO JONA MWACHIA - POCHI 0707681591", 200

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "VENTE TAVETA 24/7",
        "ceo": "Jona Mwachia",
        "location": "Nazareth - Taveta",
        "pochila": "0707681591",
        "uptime": "24/7",
        "version": "1.0",
        "ping": "/ping",
        "uptime_url": "/uptime"
    }), 200

@app.route('/uptime')
def uptime():
    return jsonify({
        "status": "live",
        "service": "VENTE",
        "ceo": "Jona Mwachia",
        "location": "Nazareth Taveta",
        "alive": True
    }), 200

@app.route('/ussd', methods=['POST'])
def ussd():
    text = request.values.get("text", "")
    if text == "":
        res = "CON VENTE TAVETA - POCHI 0707681591\n1. 10MB @5\n2. 1GB @20\n3. UNLIMITED 24H @100\n4. Lipa Pochi"
    elif text == "4":
        res = "END Lipa: M-Pesa > Pochi > 0707681591 au bit.ly/pb-pay"
    else:
        res = "END Umetuma. Lipa kwa Pochi 0707681591 kisha subiri bundle. CEO Jona"
    return res

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)