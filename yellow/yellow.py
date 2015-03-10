import requests
import json
import hmac
import time
import hashlib


PROD_ENDPOINT = "https://api.yellowpay.co"
STAGE_ENDPOINT = "https://api-stage.yellowpay.co"


def create_invoice(api_key, api_secret, payload, production=True):
    """
    :param str      api_key:        the API_KEY to use for authentication
    :param str      api_secret:     the API_SECRET to use for authentication
    :param dict     payload:        the data object to be passed in the request
                                        required keys: base_ccy, base_price
                                        optional keys: callback, redirect
    :param bool     production:     to use our production endpoint, pass True.
                                    to use our staging endpoint, pass False.
                                    if you don't pass it at all, we'll use
                                    our production endpoint by default.
    """

    assert(api_key), "Please pass in your api_key."
    assert(api_secret), "Please pass in your api_secret."

    assert(type(payload) is dict), "payload should be a dictionary"

    assert(payload['base_ccy']), "base_ccy key is required for the payload dict"
    assert(payload['base_price']), "base_price key is required for the payload dict"

    endpoint = PROD_ENDPOINT if production else STAGE_ENDPOINT

    url = "{endpoint}/api/invoice/".format(endpoint=endpoint)

    body = json.dumps(payload)

    nonce = int(time.time() * 1000)

    signature = get_signature(url, body, nonce, api_secret)


    headers = {'content-type': 'application/json',
                'API-Key': api_key,
                'API-Nonce' : nonce,
                'API-Sign' : signature}

    r = requests.post(url,
                      data=body,
                      headers=headers,
                      verify=True)

    if 200 == r.status_code:
        return r.json()
    else:
        return r.text

def query_invoice(api_key, api_secret, invoice_id, production=True):
    """
    :param str      api_key:        the API_KEY to use for authentication.
    :param str      api_secret:     the API_SECRET to use for authentication.
    :param str      invoice_id:     the ID of the invoice you want to query.
    :param bool     production:     to use our production endpoint, pass True.
                                    to use our staging endpoint, pass False.
                                    if you don't pass it at all, we'll use
                                    our production endpoint by default.
    """

    assert(api_key), "Please pass in your api_key."
    assert(api_secret), "Please pass in your api_secret."
    assert(invoice_id), "Please pass in the ID of the invoice you want to query."


    endpoint = PROD_ENDPOINT if production else STAGE_ENDPOINT

    url = "{endpoint}/api/invoice/{invoice_id}".format(endpoint=endpoint, invoice_id=invoice_id)

    nonce = int(time.time() * 1000)

    signature = get_signature(url, "", nonce, api_secret)


    headers = {'content-type': 'application/json',
                'API-Key': api_key,
                'API-Nonce' : nonce,
                'API-Sign' : signature}

    r = requests.get(url, headers=headers, verify=True)

    if 200 == r.status_code:
        return r.json()
    else:
        return r.text

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
