import json
import stripe
import requests
import os
from dotenv import load_dotenv
from base import Session, engine, Base
import logging
import http_status

load_dotenv()

stripe.api_key= os.getenv('STRIPE_KEY')

def handler(event, context):

    try:
        req_body = json.loads(event["body"])
        if "payment_method_id" in req_body:
            _amount = int(float(req_body["amount"]) * 100)
            intent = stripe.PaymentIntent.create(
                payment_method = req_body["payment_method_id"],
                amount = _amount,
                currency = 'cad',
                confirmation_method = 'automatic',
                confirm = True,
                payment_method_types=["card"]
                )
            return generate_response(intent)
        else:
            return http_status.bad_request('Payment failed')
    except Exception as e:
        return http_status.bad_request('Payment failed. '+ str(e))

def generate_response(intent):
        if intent.status == 'succeeded':
            return http_status.success()
        else:
            return http_status.bad_request('Payment failed. Invalid payment status')
