import sys
import os
import unittest
from unittest import mock
from unittest.mock import patch, Mock

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/../../../src/lambda/payment" % (CURRENT_DIRECTORY))
sys.path.insert(0, "%s/../../../src/models/" % (CURRENT_DIRECTORY))
import json
import stripe
from stripe.util import convert_to_stripe_object
import lambda_function as process_payment

class TestStudent(unittest.TestCase):

    msg_status_code = "Expected status code {}, but returned {}"
          
    def test_process_payment_success(self):
        event = {
                    'httpMethod': 'POST', 
                    'body': '{"payment_method_id":"pm_1HGTb2GPqNNATumTCzrTXZ9e"}'
                }
        
        response = {
                "id": "pi_1HGUDMGPqNNATumT8OaJSeU1",
                "object": "payment_intent",
                "amount": 1555,
                "amount_capturable": 0,
                "amount_received": 1555,
                "application": None,
                "application_fee_amount": None,
                "canceled_at": None,
                "cancellation_reason": None,
                "capture_method": "automatic",
                "charges": {
                    "object": "list",
                    "data": [
                    {
                        "id": "ch_1HGUDMGPqNNATumTROQBrEox",
                        "object": "charge",
                        "amount": 1555,
                        "amount_refunded": 0,
                        "application": None,
                        "application_fee": None,
                        "application_fee_amount": None,
                        "balance_transaction": "txn_1HGUDNGPqNNATumTIynuf12T",
                        "billing_details": {
                        "address": {
                            "city": None,
                            "country": None,
                            "line1": None,
                            "line2": None,
                            "postal_code": "12345",
                            "state": None
                        },
                        "email": None,
                        "name": "Jenny Rosen",
                        "phone": None
                        },
                        "calculated_statement_descriptor": "Stripe",
                        "captured": True,
                        "created": 1597516488,
                        "currency": "usd",
                        "customer": None,
                        "description": None,
                        "destination": None,
                        "dispute": None,
                        "disputed": False,
                        "failure_code": None,
                        "failure_message": None,
                        "fraud_details": {
                        },
                        "invoice": None,
                        "livemode": False,
                        "metadata": {
                        },
                        "on_behalf_of": None,
                        "order": None,
                        "outcome": {
                        "network_status": "approved_by_network",
                        "reason": None,
                        "risk_level": "normal",
                        "risk_score": 42,
                        "seller_message": "Payment complete.",
                        "type": "authorized"
                        },
                        "paid": True,
                        "payment_intent": "pi_1HGUDMGPqNNATumT8OaJSeU1",
                        "payment_method": "pm_1HGTb2GPqNNATumTCzrTXZ9e",
                        "payment_method_details": {
                        "card": {
                            "brand": "visa",
                            "checks": {
                            "address_line1_check": None,
                            "address_postal_code_check": "pass",
                            "cvc_check": None
                            },
                            "country": "US",
                            "exp_month": 1,
                            "exp_year": 2023,
                            "fingerprint": "pMFSyWvZ3QpTYsgN",
                            "funding": "credit",
                            "installments": None,
                            "last4": "4242",
                            "network": "visa",
                            "three_d_secure": None,
                            "wallet": None
                        },
                        "type": "card"
                        },
                        "receipt_email": None,
                        "receipt_number": None,
                        "receipt_url": "https://pay.stripe.com/receipts/acct_1H0cpsGPqNNATumT/ch_1HGUDMGPqNNATumTROQBrEox/rcpt_HqAYgMMV5LFTdJIjf4X6KM1AF4v20zJ",
                        "refunded": False,
                        "refunds": {
                        "object": "list",
                        "data": [
                        ],
                        "has_more": False,
                        "total_count": 0,
                        "url": "/v1/charges/ch_1HGUDMGPqNNATumTROQBrEox/refunds"
                        },
                        "review": None,
                        "shipping": None,
                        "source": None,
                        "source_transfer": None,
                        "statement_descriptor": None,
                        "statement_descriptor_suffix": None,
                        "status": "succeeded",
                        "transfer_data": None,
                        "transfer_group": None
                    }
                    ],
                    "has_more": False,
                    "total_count": 1,
                    "url": "/v1/charges?payment_intent=pi_1HGUDMGPqNNATumT8OaJSeU1"
                },
                "client_secret": "pi_1HGUDMGPqNNATumT8OaJSeU1_secret_UVS0G2GE2S8SlKLS6teTjipNC",
                "confirmation_method": "automatic",
                "created": 1597516488,
                "currency": "usd",
                "customer": None,
                "description": None,
                "invoice": None,
                "last_payment_error": None,
                "livemode": False,
                "metadata": {
                },
                "next_action": None,
                "on_behalf_of": None,
                "payment_method": "pm_1HGTb2GPqNNATumTCzrTXZ9e",
                "payment_method_options": {
                    "card": {
                    "installments": None,
                    "network": None,
                    "request_three_d_secure": "automatic"
                    }
                },
                "payment_method_types": [
                    "card"
                ],
                "receipt_email": None,
                "review": None,
                "setup_future_usage": None,
                "shipping": None,
                "source": None,
                "statement_descriptor": None,
                "statement_descriptor_suffix": None,
                "status": "succeeded",
                "transfer_data": None,
                "transfer_group": None
            }

        with mock.patch('stripe.PaymentIntent.create') as mock_process_payment:
            stripe_obj = convert_to_stripe_object(response)
            mock_process_payment.return_value= stripe_obj
            ret = process_payment.handler(event, "")

        self.assertEqual(ret["statusCode"], 200, self.msg_status_code.format(200, ret["statusCode"]))
        

    def test_process_payment_failure(self):
        event = {
            'httpMethod': 'POST', 
            'body': '{"payment_id":"pm_1HGTb2GPqNNATumTCzrTXZ9e"}'
            }
        
        response = {}            

        with mock.patch('stripe.PaymentIntent.create') as mock_process_payment:
            stripe_obj = convert_to_stripe_object(response)
            mock_process_payment.return_value= stripe_obj
            ret = process_payment.handler(event, "")

        self.assertEqual(ret["statusCode"], 400, self.msg_status_code.format(400, ret["statusCode"]))


    def test_process_payment_exception(self):
        event = {
            'httpMethod': 'POST', 
            'body': '{"payment_method_id":"pm_1HGTb2GPqNNATumTCzrTXZ9e"}'
            }
                   
        def except_error(*args, **kwargs):
            raise Exception("The provided PaymentMethod was previously used with a PaymentIntent without Customer attachment, shared with a connected account without Customer attachment, or was detached from a Customer. It may not be used again. To use a PaymentMethod multiple times, you must attach it to a Customer first.")

        response = {}            
    
        with mock.patch('stripe.PaymentIntent.create') as mock_process_payment:
            stripe_obj = convert_to_stripe_object(response)
            mock_process_payment.return_value= stripe_obj
            mock_process_payment.side_effect= except_error
            ret= process_payment.handler(event, "")
            getmessage= json.loads(ret['body'])
            getmessageFinal= getmessage["message"]

        self.assertEqual("Payment failed. The provided PaymentMethod was previously used with a PaymentIntent without Customer attachment, shared with a connected account without Customer attachment, or was detached from a Customer. It may not be used again. To use a PaymentMethod multiple times, you must attach it to a Customer first.", getmessageFinal)


if __name__ == "__main__":
    unittest.main(exit= False)

        



