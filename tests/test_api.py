import json
import unittest
from unittest.mock import MagicMock, patch
import linepay
from linepay.exceptions import LinePayApiError


class TestLinePayApi(unittest.TestCase):

    def test_constructor(self):
        print("testing constructor.")
        with self.assertRaises(ValueError):
            channel_id = "hoge"
            channel_secret = None
            api = linepay.LinePayApi(channel_id, channel_secret, is_sandbox=True)

    def test_constructor_with_sandbox(self):
        print("testing constructor with sandbox.")
        channel_id = "hoge"
        channel_secret = "fuga"
        api = linepay.LinePayApi(channel_id, channel_secret, is_sandbox=True)
        # assert
        self.assertEqual(api.headers.get("Content-Type"), "application/json")
        self.assertEqual(api.headers.get("X-LINE-ChannelId"), channel_id)
        self.assertEqual(api.channel_id, channel_id)
        self.assertEqual(api.channel_secret, channel_secret)
        self.assertEqual(api.api_endpoint, linepay.LinePayApi.SANDBOX_API_ENDPOINT)

    def test_constructor_with_production(self):
        print("testing constructor with production.")
        channel_id = "hoge"
        channel_secret = "fuga"
        api = linepay.LinePayApi(channel_id, channel_secret, is_sandbox=False)
        # assert
        self.assertEqual(api.headers.get("Content-Type"), "application/json")
        self.assertEqual(api.headers.get("X-LINE-ChannelId"), channel_id)
        self.assertEqual(api.channel_id, channel_id)
        self.assertEqual(api.channel_secret, channel_secret)
        self.assertEqual(api.api_endpoint, linepay.LinePayApi.DEFAULT_API_ENDPOINT)
    
    def test_constructor_with_default_endpoint(self):
        print("testing constructor with production.")
        channel_id = "hoge"
        channel_secret = "fuga"
        api = linepay.LinePayApi(channel_id, channel_secret)
        # assert
        self.assertEqual(api.headers.get("Content-Type"), "application/json")
        self.assertEqual(api.headers.get("X-LINE-ChannelId"), channel_id)
        self.assertEqual(api.channel_id, channel_id)
        self.assertEqual(api.channel_secret, channel_secret)
        self.assertEqual(api.api_endpoint, linepay.LinePayApi.DEFAULT_API_ENDPOINT)

    def test_sign(self):
        print("testing sign.")
        channel_id = "hoge"
        channel_secret = "fuga"
        api = linepay.LinePayApi(channel_id, channel_secret, is_sandbox=True)
        body_str = '{"amount": 1, "currency": "JPY", "orderId": "5383b36e-fe10-4767-b11b-81eefd1752fa", "packages": [{"id": "package-999", "amount": 1, "name": "Sample package", "products": [{"id": "product-001", "name": "Sample product", "quantity": 1, "price": 1}]}], "redirectUrls": {"confirmUrl": "https://example.com/pay/confirm", "cancelUrl": "https://example.com/pay/cancel"}}'
        nonce = "021a6bb9-ed18-4562-b9bd-ad07a27532f6"
        api._create_nonce = MagicMock(return_value=nonce)
        result = api.sign(api.headers, "/v3/payments/request", body_str)
        print(result)
        self.assertEqual(result["X-LINE-ChannelId"], channel_id)
        self.assertEqual(result["Content-Type"], "application/json")
        self.assertEqual(result["X-LINE-Authorization-Nonce"], nonce)
        self.assertEqual(result["X-LINE-Authorization"], "Rz5VEwPHChlQgN+dEmYWWbtWKw0XS41MblRB/dRdygE=")

    def test_request(self):
        with patch('linepay.api.requests.post') as post:
            mock_api_result = MagicMock(return_value={"returnCode": "0000"})
            post.return_value.json = mock_api_result
            mock_sign = MagicMock(return_value={"X-LINE-Authorization": "dummy"})
            api = linepay.LinePayApi("channel_id", "channel_secret", is_sandbox=True)
            api.sign = mock_sign
            request_options = {"hoge": "fuga"}
            result = api.request(request_options)
            self.assertEqual(result, mock_api_result.return_value)
            mock_sign.assert_called_once_with(api.headers, "/v3/payments/request", json.dumps(request_options))

    def test_request_raise_api_error(self):
        with patch('linepay.api.requests.post') as post:
            post.return_value.json = MagicMock(return_value={"returnCode": "1111"})
            api = linepay.LinePayApi("channel_id", "channel_secret", is_sandbox=True)
            request_options = {"hoge": "fuga"}
            with self.assertRaises(LinePayApiError):
                api.request(request_options)

    def test_confirm(self):
        with patch('linepay.api.requests.post') as post:
            mock_api_result = MagicMock(return_value={"returnCode": "0000"})
            post.return_value.json = mock_api_result
            mock_sign = MagicMock(return_value={"X-LINE-Authorization": "dummy"})
            api = linepay.LinePayApi("channel_id", "channel_secret", is_sandbox=True)
            api.sign = mock_sign
            transaction_id = "transaction-1234567890"
            amount = 10.0
            currency = "JPY"
            result = api.confirm(transaction_id, amount, currency)
            self.assertEqual(result, mock_api_result.return_value)
            path = "/v3/payments/{}/confirm".format(
                transaction_id
            )
            request_options = {
                "amount": amount,
                "currency": currency
            }
            mock_sign.assert_called_once_with(api.headers, path, json.dumps(request_options))

    def test_confirm_raise_api_error(self):
        with patch('linepay.api.requests.post') as post:
            post.return_value.json = MagicMock(return_value={"returnCode": "1101"})
            api = linepay.LinePayApi("channel_id", "channel_secret", is_sandbox=True)
            with self.assertRaises(LinePayApiError):
                transaction_id = "transaction-1234567890"
                amount = 10.0
                currency = "JPY"
                result = api.confirm(transaction_id, amount, currency)
