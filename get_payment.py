import hashlib
import urllib.parse
from flask import Flask, request, redirect

app = Flask(__name__)

# Replace with your Ozow merchant details
MERCHANT_ID = "your-merchant-id"
APPLICATION_KEY = "your-app-key"
SECRET_KEY = "your-secret-key"
SITE_CODE = "your-site-code"
OZOW_URL = "https://pay.ozow.com/"

def generate_signature(params: dict, secret_key: str) -> str:
    """
    Generate Ozow signature using SHA512.
    Concatenate params in alphabetical order + secret key.
    """
    sorted_items = sorted(params.items())
    concat_str = "".join(str(v) for _, v in sorted_items) + secret_key
    return hashlib.sha512(concat_str.encode("utf-8")).hexdigest()

@app.route("/pay")
def pay():
    amount = "100.00"  # Example amount
    transaction_id = "TX12345"
    return_url = "https://yourdomain.com/return"
    cancel_url = "https://yourdomain.com/cancel"
    notify_url = "https://yourdomain.com/notify"

    params = {
        "SiteCode": SITE_CODE,
        "CountryCode": "ZA",
        "CurrencyCode": "ZAR",
        "Amount": amount,
        "TransactionReference": transaction_id,
        "BankReference": "EviiDrive Ride",
        "Customer": "customer@example.com",
        "CancelUrl": cancel_url,
        "ErrorUrl": cancel_url,
        "SuccessUrl": return_url,
        "NotifyUrl": notify_url,
        "IsTest": "true",  # set to "false" in production
    }

    signature = generate_signature(params, SECRET_KEY)
    params["HashCheck"] = signature

    # Redirect user to Ozow payment page
    query_string = urllib.parse.urlencode(params)
    return redirect(OZOW_URL + "?" + query_string)

@app.route("/notify", methods=["POST"])
def notify():
    # Ozow will POST payment result here
    data = request.form.to_dict()
    print("Ozow notification:", data)

    # Verify signature again before trusting
    signature = generate_signature({k: v for k, v in data.items() if k != "HashCheck"}, SECRET_KEY)
    if signature != data.get("HashCheck"):
        return "Invalid signature", 400

    # Handle payment status
    if data.get("Status") == "Complete":
        # Release funds in eviiDrive wallet
        print("Payment successful for:", data.get("TransactionReference"))
    else:
        print("Payment failed or cancelled")

    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
