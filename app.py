@app.route('/sms/incoming', methods=['GET','POST'])
def sms_incoming():
    data = request.get_json(silent=True) or {}
    raw_text = data.get('message') or request.form.get('message') or str(request.data.decode() if request.data else "") or ""
    
    text = str(raw_text)
    TRANSACTIONS.insert(0, {"time": datetime.now().strftime("%H:%M:%S"), "raw": text[:400]})
    print(f"[MPESA] {text}")

    # === AUTO DETECT AMOUNT ===
    try:
        # Tafuta Ksh
        m = re.search(r'Ksh\s*([0-9,]+\.?[0-9]*)', text, re.I)
        amount = int(float(m.group(1).replace(',',''))) if m else 0
        
        # Tafuta namba ya mteja
        p = re.search(r'(07\d{8}|2547\d{8}|01\d{8})', text)
        customer_phone = p.group(1) if p else ""
        if customer_phone.startswith('0'):
            customer_phone = '254' + customer_phone[1:]
        customer_phone_plus = '+' + customer_phone if customer_phone else ""

        # MAP YA BUNDLE KULINGANA NA PESA
        bundle_map = {
            5: "10MB",
            10: "50MB",
            20: "1GB",
            35: "2GB",
            50: "5GB au 1H UNLIMITED",
            100: "UNLIMITED 24HRS",
            500: "UNLIMITED 7 DAYS",
            1500: "UNLIMITED 30 DAYS"
        }
        
        bundle = bundle_map.get(amount, f"{amount} KSH Bundle")

        if amount >= 5 and customer_phone_plus and sms:
            msg = f"VENTE TAVETA: Asante! Ume lipa {amount}. {bundle} yako inatengenezwa. M-Pesa Pochi: 0141761672. CEO Jona - Nazareth"
            sms.send(msg, [customer_phone_plus])
            print(f"[AUTO SENT] {amount} -> {bundle} kwa {customer_phone_plus}")
            TRANSACTIONS.insert(0, {"time": datetime.now().strftime("%H:%M:%S"), "raw": f"AUTO: {customer_phone_plus} => {bundle} ({amount})"})
    except Exception as e:
        print(f"AUTO ERROR: {e}")

    return jsonify({"status":"ok"}), 200