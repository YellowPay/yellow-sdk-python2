import unittest
import mock
import json
import responses
from decimal import Decimal
import platform
import os
import re
import yellow

# we need predictable key/secret pair to get a predictable signature for mocking
DEFAULT_KEY = "KEY" 
DEFAULT_SECRET = "SECRET"
API_KEY = os.environ.get('TEST_API_KEY')
API_SECRET = os.environ.get('TEST_API_SECRET')
TEST_INVOICE_ID = "YBN4YC9FNMCPYMQZY3F8X55W9Y"
CALLBACK = "https://example.com/ipn"
BASE_CCY = "USD"
BASE_PRICE = "0.1"
STYLE = "cart"
ORDER = "1234567"

class CreateInvoiceTestCase(unittest.TestCase):
    
    def create_invoice(self, api_key=API_KEY, api_secret=API_SECRET, base_ccy=BASE_CCY, 
                       base_price=BASE_PRICE, callback=CALLBACK, style=STYLE, order=ORDER):
                       
        return yellow.create_invoice(api_key, api_secret, base_ccy=base_ccy, 
                                     base_price=base_price, callback=callback, 
                                     style=style, order=order)
                                     

    
    def test_basic(self):
        data = self.create_invoice()
        
        self.assertEqual(data['status'], 'loading')
        self.assertEqual(data['received'], '0')
        self.assertEqual(data['invoice_ccy'], 'BTC')
        self.assertEqual(data['callback'], CALLBACK)
        self.assertEqual(data['order'], '1234567')
        self.assertEqual(data['style'], 'cart')
        self.assertEqual(data['base_ccy'], 'USD')
        self.assertEqual(data['base_price'], '0.10000000')
        self.assertEqual(data['remaining'], data['invoice_price'])
        
        self.assertTrue(data['expiration'] > data['server_time'])
        self.assertTrue(len(data['id']) == 26)
        for c in data['id']:
            self.assertTrue(c in 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789')
        
        string_to_remove = re.search('invoice.(.*).html', data['url']).group(1)
        stripped_url = data['url'].replace(string_to_remove, '')
        self.assertTrue(stripped_url == '//cdn.yellowpay.co/invoice..html?invoiceId={invoice_id}'.format(invoice_id=data['id']))
          
            
    def test_authentication_error(self):
        with self.assertRaises(yellow.YellowApiError):
            self.create_invoice(api_key="xxx", api_secret="xxx")
        
    def test_nonce_error(self):
        with self.assertRaises(yellow.YellowApiError):
            with mock.patch("time.time", return_value=111111):
                self.create_invoice()
        
    def test_minimum_price_error(self):
        with self.assertRaises(yellow.YellowApiError):
            self.create_invoice(base_price="0.01")
        
        
    def test_base_ccy_error(self):
        with self.assertRaises(yellow.YellowApiError):
            self.create_invoice(base_ccy="xxx")
        
        
    def test_callback_error(self):
        with self.assertRaises(yellow.YellowApiError):
            self.create_invoice(callback="xxx")
            
    @responses.activate
    def test_basic_mock(self):
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
        self.assertEqual('1428758911002', headers['API-Nonce'])
        self.assertEqual("7ae79d20d18281e0b305a646880343b122cd742f7e62d56ab3415581ee0409d4", headers['API-Sign'])
        self.assertEqual(p, headers['API-Platform'])
        self.assertEqual(yellow.VERSION, headers['API-Plugin'])
        self.assertEqual("USD", payload["base_ccy"])
        self.assertEqual("0.1", payload["base_price"])
        self.assertEqual("https://example.com/ipn", payload["callback"])
        self.assertEqual("cart", payload["type"])
        self.assertEqual("1234567", payload["order"])
        self.assertEqual(create_response, r)
        
    @responses.activate
    def test_error_mock(self):
        """ Error from the servers should raise an exception"""
        create_response = { u'base_ccy': [u'This field is required.'],
                            u'base_price': [u'This field is required.'] }
        responses.add(responses.POST, yellow.YELLOW_SERVER + "/v1/invoice/",
                      body=json.dumps(create_response), status=400,
                      content_type="application/json")
        
        with self.assertRaises(yellow.YellowApiError):
            yellow.create_invoice(DEFAULT_KEY, DEFAULT_SECRET)


class QueryInvoiceTestCase(unittest.TestCase):
    
    def test_basic(self):
        expected_invoice = {u'status': u'expired', u'received': u'0', u'remaining': u'0.00044228', u'url': u'//cdn.yellowpay.co/invoice.9796a76b.html?invoiceId=YBN4YC9FNMCPYMQZY3F8X55W9Y', u'style': u'cart', u'id': u'YBN4YC9FNMCPYMQZY3F8X55W9Y', u'invoice_ccy': u'BTC', u'callback': u'https://www.example.com/ipn', u'expiration': u'2015-06-03T18:37:04.433Z', u'invoice_price': u'0.00044228', u'address': u'1DGgddiCk9pY6oBwL1GQFSnKAc5ZHubh88', u'order': None, u'base_ccy': u'USD', u'base_price': u'0.10000000'}
        r = yellow.query_invoice(API_KEY, API_SECRET, TEST_INVOICE_ID)
        del r['server_time']
        self.assertEqual(expected_invoice, r)
        
    def test_authentication_error(self):
        with self.assertRaises(yellow.YellowApiError):
            yellow.query_invoice("xxx", "xxx", TEST_INVOICE_ID)
        
        
    def test_invalid_id(self):
        with self.assertRaises(yellow.YellowApiError):
            yellow.query_invoice(API_KEY, API_SECRET, "xxx")


if __name__ == '__main__':
    unittest.main()
