from flask import Flask, request, jsonify
import os, json, re
from datetime import datetime

app = Flask(__name__)
FILE = "transactions.json"

def load_trans():
    if os.path.exists(FILE):
        try:
            with open(FILE,'r') as f: return json.load(f)
        except: return []
    return []

def save_trans(data):
    with open(FILE,'w') as f: json.dump(data[-200:], f)

@app.route('/sms/incoming', methods=['GET','POST'])
def sms_incoming():
    data = request.get_json(silent=True) or {}
    txt = str(data.get('message') or data.get('text') or request.form.get('message') or request.data.decode()[:500] if request.data else "test")
    
    all_t = load_trans()
    all_t.insert(0, {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "raw": txt[:400]})
    save_trans(all_t)
    print(f"[MPESA] {txt}")
    return jsonify({"status":"ok"}), 200

@app.route('/transactions')
def trans():
    all_t = load_trans()
    html = "<h1>VENTE TAVETA - Transactions</h1><a href='/'>Home</a> <a href='/transactions'>Refresh</a><hr>"
    if not all_t: html += "<p>Hakuna transaction bado. Tuma Test kwa SMS Forwarder!</p>"
    for t in all_t:
        html += f"<div><b>{t['time']}</b> - {t['raw']}</div><hr>"
    return html

@app.route('/')
def home():
    return "VENTE TAVETA LIVE - 0141761672"