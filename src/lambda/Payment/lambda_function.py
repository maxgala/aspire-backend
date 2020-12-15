import json
import stripe
import requests
import os
from dotenv import load_dotenv
from base import Session, engine, Base
import logging

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
            return {
                    "statusCode": 400,
                    "body": json.dumps({
                        'message': 'Payment failed',
                    }),
                    "headers": {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                        'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
                    }
                }           
    except Exception as e:
        return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": 'Payment failed. '+ str(e),
                }),
                "headers": {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                    'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
                }
            }

def generate_response(intent):
        if intent.status == 'succeeded':
            return {
                    "statusCode": 200,
                    "body": json.dumps({
                        'message': 'Payment succeeded',
                    }),
                    "headers": {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                        'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
                    }
                }
        else:
            return {
                    "statusCode": 400,
                    "body": json.dumps({
                        'message': 'Payment failed. Invalid payment status',
                    }),
                    "headers": {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                        'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
                    }
                } 
