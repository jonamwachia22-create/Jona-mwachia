```python
from flask import Flask, request, render_template_string
import africastalking
import os

app = Flask(__name__)

AT_USERNAME = os.environ.get("AT_USERNAME")
AT_API_KEY = os.environ.get("AT_API_KEY")

africastalking.initialize(AT_USERNAME, AT_API_KEY)
airtime = africastalking.Airtime
sms = africastalking.SMS
payment = africastalking.Payment

HTML = """
<h2>VENTE - CEO Jona Mwachia</h2>
<h3 style="color:green;">NUNUA BUNDLE PAPO HAPO - TAVETA 24/7</h3>
<form method="post">
 Namba ya M-Pesa:<br>
 <input name="phone" placeholder="0141761672" required><br><br>
 
 Chagua Bundle:<br>
 <select name="product">
   <option value="10MB_5">TEST 10MBs - 5 KSH</option>
   <option value="50MB_10">TEST 50MBs - 10 KSH</option>
   <option value="1GB_20">1GB - 20 KSH</option>
   <option value="2GB_35">2GB - 35 KSH</option>
   <option value="5GB_50">5GB - 50 KSH</option>
   <option value="UNLIMITED_1H_50">UNLIMITED 1 HOUR - 50 KSH</option>
   <option value="UNLIMITED_1DAY_100">UNLIMITED 24HRS - 100 KSH</option>
   <option value="UNLIMITED_7DAYS_500">UNLIMITED 7 DAYS - 500 KSH</option>
   <option value="UNLIMITED_30DAYS_1500">UNLIMITED 30 DAYS - 1500 KSH</option>
 </select><br><br>
 
 <button style="background:green;color:white;padding:12px;font-weight:bold;">LIPA NA M-PESA SASA - UNLIMITED!</button>
</form>
<p><small>TAVETA 24/7 - Haraka | Uaminifu | Unlimited Speed</small></p>
"""

@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        phone = request.form['phone'].strip()
        product = request.form['product']
        
        if phone.startswith('0'):
            phone = '+254' + phone[1:]
        if not phone.startswith('+254'):
            phone = '+254' + phone
        
        # Chukua amount - mwisho baada ya _
        parts = product.split('_')
        amount = parts[-1]
        size = "_".join(parts[:-1])

        try:
            checkout = payment.checkout(
                productName=size,
                phoneNumber=phone,
                currencyCode="KES",
                amount=amount
            )
            
            sms.send(f"VENTE TAVETA: {size} kwa KES {amount} imetumwa. Weka PIN. Unlimited itaanza! CEO Jona Mwachia", [phone])
            
            return f"<h3>Poa! {size} ya KES {amount} imetumwa kwa {phone}. Lipa ufurahie Unlimited Taveta 24/7!</h3><a href='/'>Rudi</a>"
        except Exception as e:
            return f"<h3>Error: {e}</h3><a href='/'>Rudi</a>"
    
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run()
```