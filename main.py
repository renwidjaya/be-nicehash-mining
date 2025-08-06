from fastapi import FastAPI, Query
import os
import time
import hmac
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ORG_ID = os.getenv("ORG_ID")
TO_ADDRESS = os.getenv("TO_ADDRESS") 

def get_nonce():
    return str(int(time.time() * 1000))

def sign_request(nonce, path, method, body=""):
    message = f"{API_KEY}{nonce}{nonce}{ORG_ID}{method}{path}{body}"
    return hmac.new(API_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()

@app.get("/")
def root():
    return {"message": "🚀 BTC Mining API aktif"}

@app.get("/mining-status")
def mining_status():
    path = "/main/api/v2/accounting/account2/BTC"
    nonce = get_nonce()
    sig = sign_request(nonce, path, "GET")


    headers = {
        "X-Time": nonce,
        "X-Nonce": nonce,
        "X-Auth": f"{API_KEY}:{sig}",
        "X-Organization-Id": ORG_ID,
        "Content-Type": "application/json"
    }
    
    print("🔐 Nonce:", nonce)
    print("🔐 Signature:", sig)
    print("🔐 Header:", headers)

    res = requests.get("https://api2.nicehash.com" + path, headers=headers)
    return res.json()

@app.post("/withdraw")
def withdraw(amount_btc: float = Query(..., gt=0.0005)):
    """
    Melakukan withdraw BTC ke alamat Indodax.
    Minimal withdraw: 0.0005 BTC
    """
    path = "/main/api/v2/accounting/withdrawal"
    nonce = get_nonce()
    body = {
        "currency": "BTC",
        "amount": f"{amount_btc:.8f}",
        "wallet": TO_ADDRESS
    }

    import json
    body_str = json.dumps(body)
    sig = sign_request(nonce, path, "POST", body_str)

    headers = {
        "X-Time": nonce,
        "X-Nonce": nonce,
        "X-Auth": f"{API_KEY}:{sig}",
        "X-Organization-Id": ORG_ID,
        "Content-Type": "application/json"
    }

    res = requests.post("https://api2.nicehash.com" + path, headers=headers, json=body)
    return res.json()