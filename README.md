Yellow Python SDK
=====================
This is the Yellow Python SDK. This simple SDK contains couple of python functions that makes it easy to integrate with the Yellow API. To get started just:
```
pip install yellow-sdk-python
```

Examples
---------
```
import json
import yellow


# You can get your api key/secret from your merchant dashboard.

api_key = "YOUR_API_KEY"            # store it in environment variable for better security
api_secret = "YOUR_API_SECRET"      # store it in environment variable for better security
base_ccy = "USD"                    # Required: A 3-letter currency code
base_price = "0.05"                 # Required: The invoice price in the above currency
callback = "https://example.com"    # Optional: URL for Yellow to POST to as a callback

created_invoice = yellow.create_invoice(api_key, api_secret, base_ccy=base_ccy, base_price=base_price, callback=callback)

# Print the result beautifully!
print json.dumps(created_invoice.json(), sort_keys=True, indent=4)
```
You should see something similar to the following in your terminal:
```
{
    "address": "155xsayoDXxRFP9rxDoecmpVUo7y5xKtc7", # Invoice Address
    "base_ccy": "USD",
    "base_price": "0.05",
    "callback": "https://example.com",
    "expiration": "2015-03-10T18:17:51.248Z", # Each invoice expires after 10 minutes of creation
    "id": "6dd264975861fddbfe4404ed995f1ca4", # Invoice ID (to query the invoice later if you need to!)
    "invoice_ccy": "BTC",
    "invoice_price": "0.00017070",
    "received": "0",
    "redirect": null,
    "remaining": "0.00017070",
    "server_time": "2015-03-10T18:07:51.454Z",
    "status": "new", # Status of the invoice. Other values are "authorizing" for unconfirmed transactions, and "paid" for confirmed transactions
    "url": "https://cdn.yellowpay.co/invoice.5f0d082e.html?invoiceId=6dd264975861fddbfe4404ed995f1ca4" # Direct URL for the invoice. You can use it to embed the invoice widget in an iframe on your website.
}

```
To query an invoice that you created, just pass in the `invoice_id` to the `query_invoice` function:
```
invoice_id = "..." # invoice ID you received when you created the invoice.
invoice = yellow.query_invoice(api_key, api_secret, invoice_id)
print json.dumps(invoice.json(), sort_keys=True, indent=4)
```
You should see exactly the same returned data you got from `create_invoice` above!

Verifying Yellow POST requests
---------------------------
To verify that the request you just receive really is from us, we created a helper function that checks the signature of the request. This method will return true if the signature matches (verified), or false if it doesn't match (not verified).
```
is_verified = yellow.verify_ipn(api_secret, host_url, request_signature, request_nonce, request_body)
```
Since this method only works in the context of a web app, check the [full demo code](https://github.com/YellowPay/yellowdemo) for more info on how to use it.