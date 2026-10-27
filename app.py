from flask import Flask, request, render_template_string, jsonify
import requests, base64, datetime, os
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

CONSUMER_KEY = os.environ.get("MPESA_CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("MPESA_CONSUMER_SECRET")
SHORTCODE = os.environ.get("MPESA_SHORTCODE", "174379")
PASSKEY = os.environ.get("MPESA_PASSKEY")
CALLBACK_URL = "https://jona-mwachia.onrender.com/callback"

HTML = """
<h2>VENTE - CEO Jona Mwachia - LIVE</h2>
<h3 style="color:green;">NUNUA BUNDLE PAPO HAPO - TAVETA 24/7</h3>
<form method="post">
Namba:<br><input name="phone" placeholder="0141761672" required><br><br>
Bundle:<br>
<select name="product">
<option value="5_10MB">TEST 10MBs - 5 KSH</option>
<option value="10_50MB">TEST 50MBs - 10 KSH</option>
<option value="100_UNLIMITED_1DAY">UNLIMITED 24HRS - 100 KSH</option>
<option value="500_UNLIMITED_7DAYS">UNLIMITED 7DAYS - 500 KSH</option>
</select><br><br>
<button style="background:green;color:white;padding:15px;font-weight:bold;border:none;">LIPA NA M-PESA SASA</button>
</form>
"""

def get_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    return r.json()['access_token']

@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        phone = request.form['phone'].strip()
        if phone.startswith('0'): phone = '254' + phone[1:]
        if phone.startswith('+'): phone = phone[1:]
        amount, bundle = request.form['product'].split('_',1)
        
        try:
            token = get_token()
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode((SHORTCODE + PASSKEY + timestamp).encode()).decode()
            
            payload = {
                "BusinessShortCode": SHORTCODE,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone,
                "PartyB": SHORTCODE,
                "PhoneNumber": phone,
                "CallBackURL": CALLBACK_URL,
                "AccountReference": bundle,
                "TransactionDesc": f"VENTE {bundle}"
            }
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
            return f"<h3>STK Push imetumwa kwa {phone}! Weka PIN yako ufurahie {bundle}!</h3><p>{res.json()}</p><a href='/'>Rudi</a>"
        except Exception as e:
            return f"<h3>Error: {e}</h3><a href='/'>Rudi</a>"
    return render_template_string(HTML)

@app.route('/callback', methods=['POST'])
def callback():
    print(request.json)
    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"})

if __name__ == '__main__':
    app.run()