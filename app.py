from flask import Flask, request, render_template_string, jsonify
import africastalking
import os
import re
from datetime import datetime

app = Flask(__name__)

# Africa's Talking
AT_USERNAME = os.environ.get("AT_USERNAME", "sandbox")
AT_API_KEY = os.environ.get("AT_API_KEY", "dummy")
try:
    africastalking.initialize(AT_USERNAME, AT_API_KEY)
    sms = africastalking.SMS
except:
    sms = None

# Hifadhi ya malipo - itaonekana kwenye /transactions
TRANSACTIONS = []

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
<h2 style="background:green;color:white;padding:12px;border-radius: