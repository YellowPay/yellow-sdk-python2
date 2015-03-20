import requests
import hmac
import time
import hashlib
import os
import json

from exceptions import *

YELLOW_SERVER = "https://" + os.environ.get("YELLOW_SERVER", "api.yellowpay.co")

def create_invoice(api_key, api_secret, base_ccy, base_price, callback=None):
    """
    This function creates a yellow invoices based on the bellow parameters:

    :param str      api_key:        the API_KEY to use for authentication
    :param str      api_secret:     the API_SECRET to use for authentication
    :param str      base_ccy:       the currency code. ex. "USD"
    :param str      base_price:     the invoice price in the above currency. ex. "1.5"
    :param str      callback:       the URL we'll POST payment notifications to. (optional)

    """


    url = "{yellow_server}/v1/invoice/".format(yellow_server=YELLOW_SERVER)

    payload = {
        'base_ccy': base_ccy,
        'base_price': base_price
    }

    if callback:
        payload['callback'] = callback

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
    return handle_response(r)


def query_invoice(api_key, api_secret, invoice_id):
    """
    Use this function to query an invoice you created earlier using its ID 

    :param str      api_key:        the API_KEY to use for authentication
    :param str      api_secret:     the API_SECRET to use for authentication
    :param str      invoice_id:     the ID of the invoice you're querying
    """


    url = "{yellow_server}/v1/invoice/{invoice_id}".format(yellow_server=YELLOW_SERVER, invoice_id=invoice_id)

    nonce = int(time.time() * 1000)

    signature = get_signature(url, "", nonce, api_secret)


    headers = {'content-type': 'application/json',
                'API-Key': api_key,
                'API-Nonce' : nonce,
                'API-Sign' : signature}

    try:
      r = requests.get(url, headers=headers, verify=True)
    except Exception as req:
      raise YellowRequestError(req.args)
    return handle_response(r)

def verify_ipn(api_secret, host_url, request):
    """
    This is a helper function to verify that the request you just received really is from Yellow.

    :param str      api_secret:     the API_SECRET to use for verification
    :param str      host_url:       the callback URL you set when you created the invoice
    :param dict     request:        The request object returned from the invoice query

    :returns bool                   This function returns True if the signature matches (verified)
                                                  returns False if the signature DOESN'T match (not verified)
    """

    request_signature = request.META['HTTP_API_SIGN']
    request_nonce = request.META['HTTP_API_NONCE']
    request_body = request.body

    signature = get_signature(host_url, request_body, request_nonce, api_secret)

    return True if signature == request_signature else False

def get_signature(url, body, nonce, api_secret):
    """
    A tiny function used by our SDK to sign and verify requests.
    """
    message = str(nonce) + url + body
    h = hmac.new(api_secret,
                 message,
                 hashlib.sha256)
    signature = h.hexdigest()

    return signature


def handle_response(response):
    """
    A tiny function used by our SDK to handle the response we get from our API.
    """
    if response.ok:
        return response
    response_error = YellowApiError('{code}:{message}'.format(code=response.status_code, message=response.text))
    response_error.code = response.status_code
    response_error.message = response.text
    raise response_error
