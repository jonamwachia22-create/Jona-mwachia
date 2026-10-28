import os, re
from flask import Flask, render_template, request, jsonify, redirect, session, url_for
from datetime import datetime, timedelta
import africastalking

# === CONFIG ===
app = Flask(__name__)
app.secret_key = "vente-taveta-secret-2026"

# Africastalking
AT_USERNAME = os.environ.get("AT_USERNAME", "VENTETAVETA")
AT_API_KEY = os.environ.get("AT_API_KEY", "atsk_e5a6d59f4a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5")
try:
    africastalking.initialize(AT_USERNAME, AT_API_KEY)
    sms = africastalking.SMS
except:
    sms = None

TRANSACTIONS = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sms/incoming', methods=['GET','POST'])
def sms_incoming():
    data = request.get_json(silent=True) or {}
    raw_text = data.get('message') or data.get('text') or request.form.get('message') or str(request.data.decode() if request.data else "") or "Test"
    
    text = str(raw_text)
    TRANSACTIONS.insert(0, {"time": datetime.now().strftime("%H:%M:%S"), "raw": text[:400]})
    print(f"[MPESA] {text}")

    try:
        m = re.search(r'Ksh\s*([0-9,]+\.?[0-9]*)', text, re.I)
        amount = int(float(m.group(1).replace(',',''))) if m else 0
        
        p = re.search(r'(07\d{8}|2547\d{8}|01\d{8})', text)
        customer_phone = p.group(1) if p else ""
        if customer_phone.startswith('0'):
            customer_phone = '254' + customer_phone[1:]
        customer_phone_plus = '+' + customer_phone if customer_phone else ""

        bundle_map = {5:"10MB",10:"50MB",20:"1GB",35:"2GB",50:"5GB",100:"UNLIMITED 24HRS",500:"7 DAYS",1500:"30 DAYS"}
        bundle = bundle_map.get(amount, f"{amount} Bundle")

        if amount >= 5 and customer_phone_plus and sms:
            msg = f"VENTE TAVETA: Asante! Ume lipa {amount}. {bundle} yako iko tayari. Pochi: 0141761672. CEO Jona"
            sms.send(msg, [customer_phone_plus])
            print(f"[AUTO SENT] {amount} -> {bundle} kwa {customer_phone_plus}")
            TRANSACTIONS.insert(0, {"time": datetime.now().strftime("%H:%M:%S"), "raw": f"AUTO: {customer_phone_plus} => {bundle} ({amount})"})
    except Exception as e:
        print(f"AUTO ERROR: {e}")

    return jsonify({"status":"ok"}), 200

@app.route('/transactions')
def transactions_page():
    html = "<h1>VENTE TAVETA - Transactions</h1><a href='/'>Home</a><hr>"
    for t in TRANSACTIONS[:100]:
        html += f"<div><b>{t['time']}</b> - {t['raw']}</div><hr>"
    return html

if __name__ == '__main__':
    app.run(debug=True)