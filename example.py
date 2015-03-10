import json
import yellow




api_key = "Eo2VE5PrHcJVvqK9uIdU"
api_secret = "73jnZflRHpGRIqFxzwf_JtynRNmZXoQM4PaxTtsy"

payload = {
            'base_ccy': "USD",
            'base_price': "0.05",
            'callback': "https://example.com/invoice-callback/",
            'redirect': "https://example.com/success/"
          }

data = yellow.create_invoice(api_key, api_secret, payload)
print json.dumps(data, sort_keys=True, indent=4)
#yellow.query_invoice()
