import requests
import json
import hmac
import time
import hashlib

from yellow.exceptions import *

YELLOW_SERVER = "https://" + os.environ.get("YELLOW_SERVER", "api.yellowpay.co")

def create_invoice(api_key, api_secret, base_ccy, base_price, callback=None):
    """
    :param str      api_key:        the API_KEY to use for authentication
    :param str      api_secret:     the API_SECRET to use for authentication
    :param str      base_ccy:       the currency code. ex. "USD"
    :param str      base_price:     the invoice price in the above currency. ex. "1.5"
    :param str      callback:       the URL we'll POST payment notifications to. (optional)

    """

    url = "{yellow_server}/api/invoice/".format(yellow_server=YELLOW_SERVER)

    payload = {
        'base_ccy': base_ccy,
        'base_price': base_price
    }

    #payload['callback'] = callback if callback else pass

    if callback payload['callback'] = callback

    body = json.dumps(payload)

    nonce = int(time.time() * 1000)

    signature = get_signature(url, body, nonce, api_secret)

    headers = {'content-type': 'application/json',
                'API-Key': api_key,
                'API-Nonce' : nonce,
                'API-Sign' : signature}

    try:
      r = requests.post(url, data=body, headers=headers, verify=True)
    except Exception as req:
      raise YellowRequestError(req.args)
    handle_response(r)


def query_invoice(api_key, api_secret, invoice_id):
    """
    :param str      api_key:        the API_KEY to use for authentication
    :param str      api_secret:     the API_SECRET to use for authentication
    :param str      invoice_id:     the ID of the invoice you're querying
    """


    url = "{yellow_server}/api/invoice/{invoice_id}".format(yellow_server=YELLOW_SERVER, invoice_id=invoice_id)

    nonce = int(time.time() * 1000)

    signature = get_signature(url, "", nonce, api_secret)


    headers = {'content-type': 'application/json',
                'API-Key': api_key,
                'API-Nonce' : nonce,
                'API-Sign' : signature}

    r = requests.get(url, headers=headers, verify=True)

    try:
      r = requests.get(url, headers=headers, verify=True)
    except Exception as req:
      raise YellowRequestError(req.args)
    handle_response(r)

def get_signature(url, body, nonce, api_secret):
    ''' To secure communication between merchant server and Yellow server we
        use a form of HMAC authentication.
        (http://en.wikipedia.org/wiki/Hash-based_message_authentication_code)

        When submitting a request to Yellow 3 additional header elements are
        needed:
        API-Key: your public API key, you can get this from your merchant
                 dashboard
        API-Nonce: an ever-increasing number that is different for each request
                   (e.g., current UNIX time in milliseconds)
        API-Sign: an HMAC hash signed with your API secret and converted to
                  hexadecimal. The message to be hahed and signed is the
                  concatenation of the nonce, fully-qualified request URL,
                  and any request parameters.

        This allows us to authenticate the request as coming from you,
        prevents anyone else from modifying or replaying your request, and
        ensures your secret key is never exposed (even in a Heartbleed-type
        scenario where the SSL layer itself is compromised).
        '''

    # Concatenate the components of the request to be hashed. They should
    # always be concatenated in this order: Nonce, fully-qualified URL
    # (e.g. https://yellowpay.co/api/invoice/), body
    message = str(nonce) + url + body

    # Hash and sign the message with your API secret
    h = hmac.new(api_secret,
                 message,
                 hashlib.sha256)

    # Convert the signature to hexadecimal
    signature = h.hexdigest()

    return signature


def handle_response(response):
    if response.ok:
        return response.json()
    response_error = YellowApiError('{code}:{message}'.format(code=response.status_code, message=response.text))
    response_error.code = response.status_code
    response_error.message = response.message
    raise response_error
