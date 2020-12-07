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
        paymentMethod_Dict= json.loads(event["body"])
        if "payment_method_id" in paymentMethod_Dict:
            intent = stripe.PaymentIntent.create(
                payment_method = paymentMethod_Dict["payment_method_id"], #attribute depends on request body
                amount = paymentMethod_Dict["amount"], #change the amount
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
                }           
    except Exception as e:
        return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": 'Payment failed. '+ str(e),
                }),
            }

def generate_response(intent):
        if intent.status == 'succeeded':
            return {
                    "statusCode": 200,
                    "body": json.dumps({
                        'message': 'Payment succeeded',
                    }),
                }
        else:
            return {
                    "statusCode": 400,
                    "body": json.dumps({
                        'message': 'Payment failed. Invalid payment status',
                    }),
                } 
