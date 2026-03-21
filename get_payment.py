import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Use your Paystack secret key here (not the public key)
PAYSTACK_SECRET_KEY = "sk_test_xxx"  # replace with your secret key

BASE_URL = "https://api.paystack.co"

def initialize_transaction(email: str, amount_kobo: int, callback_url: str):
    """
    Initialize a Paystack transaction.
    amount_kobo = amount in kobo (10000 = ₦100)
    """
    url = f"{BASE_URL}/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "amount": amount_kobo,
        "callback_url": callback_url
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def verify_transaction(reference: str):
    """
    Verify transaction status using reference.
    """
    url = f"{BASE_URL}/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

@app.route("/pay", methods=["POST"])
def pay():
    data = request.get_json()
    email = data.get("email")
    amount = int(data.get("amount", 10000))  # default ₦100
    callback_url = "https://yourdomain.com/callback"

    init = initialize_transaction(email, amount, callback_url)
    return jsonify(init)

@app.route("/verify/<reference>", methods=["GET"])
def verify(reference):
    result = verify_transaction(reference)
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
