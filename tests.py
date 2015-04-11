import unittest
import mock
import json
import responses
from decimal import Decimal
import platform

import yellow

DEFAULT_KEY = "APIKEY"
DEFAULT_SECRET = "APISECRET"

class CreateInvoiceTestCase(unittest.TestCase):

    @responses.activate
    def test_basic(self):
        create_response = { u'status': u'new',
                            u'received': u'0',
                            u'remaining': u'0.00042608',
                            u'server_time': u'2015-04-11T13:20:09.679Z',
                            u'url': u'https://cdn.yellowpay.co/invoice.html?invoiceId=LW6U5TALVCVJQVW9CSQGHV8VEH',
                            u'id': u'LW6U5TALVCVJQVW9CSQGHV8VEH',
                            u'invoice_ccy': u'BTC',
                            u'callback': None,
                            u'expiration': u'2015-04-11T13:30:09.468Z',
                            u'invoice_price': u'0.00042608',
                            u'address': u'161GX2wT9vNqTSgF9dXy9RRD3m4KJfYFKa',
                            u'order': None,
                            u'type': u'cart',
                            u'base_ccy': u'USD',
                            u'base_price': u'0.10000000'}
        responses.add(responses.POST, yellow.YELLOW_SERVER + "/v1/invoice/",
                      body=json.dumps(create_response), status=200,
                      content_type="application/json")
        
        with mock.patch("time.time", return_value=1428758911.002547):
            r = yellow.create_invoice(DEFAULT_KEY, DEFAULT_SECRET,
                                      base_ccy="USD",
                                      base_price="0.1",
                                      callback="https://example.com/ipn",
                                      type="cart",
                                      order="1234567")
        
        self.assertEqual(1, len(responses.calls))
        
        p = "{system} {release} - Python {python}".format(
                system=platform.system(),
                release=platform.release(),
                python=platform.python_version()
            )
        
        payload = json.loads(responses.calls[0].request.body)
        headers = responses.calls[0].request.headers
        self.assertEqual("application/json", headers['content-type'])
        self.assertEqual(DEFAULT_KEY, headers['API-Key'])
        self.assertEqual(1428758911002, headers['API-Nonce'])
        self.assertEqual("4a8407f15a918fef8ffb708402c918dbc9e0adf2d5d1a1b238cfc543b33eefef", headers['API-Sign'])
        self.assertEqual(p, headers['API-Platform'])
        self.assertEqual(yellow.VERSION, headers['API-Version'])
        self.assertEqual("USD", payload["base_ccy"])
        self.assertEqual("0.1", payload["base_price"])
        self.assertEqual("https://example.com/ipn", payload["callback"])
        self.assertEqual("cart", payload["type"])
        self.assertEqual("1234567", payload["order"])
        self.assertEqual(create_response, r.json())
        
    @responses.activate
    def test_error(self):
        """ Error from the servers should raise an exception"""
        create_response = { u'base_ccy': [u'This field is required.'],
                            u'base_price': [u'This field is required.'] }
        responses.add(responses.POST, yellow.YELLOW_SERVER + "/v1/invoice/",
                      body=json.dumps(create_response), status=400,
                      content_type="application/json")
        
        with self.assertRaises(yellow.YellowApiError):
            yellow.create_invoice(DEFAULT_KEY, DEFAULT_SECRET)


if __name__ == '__main__':
    unittest.main()