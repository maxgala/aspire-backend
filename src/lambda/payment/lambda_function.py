import json
import stripe
import requests
import logging

stripe.api_key= "sk_test_51H0cpsGPqNNATumTocDFOQBCm29E08vroVYDfbduGfSf2bOUzjX0fbOUtPtuJ7xJRi7xGLZIU9SnZXK6cKE1ld0T00MOwM7rEP"

def handler(event, context):

    try:
        # print(event)
        # data = json.loads(event['object'])
        intent = stripe.PaymentIntent.create(
            amount=1555,
            currency="usd",
            payment_method_types=["card"]
        )
        return {
        "statusCode": 200,
        "body": json.dumps({
            'clientSecret': intent['client_secret'],
            # "location": ip.text.replace("\n", "")
        }),
    }
    except Exception as e:
        print("FAILED")
        return {
        "body": json.dumps({
            "message": str(e),
            # "location": ip.text.replace("\n", "")
        }),
    }

    # print('Create charge')
    # print(event)
    # requestBody = json.loads(event['body'])
    # #print(requestBody)

    # token= requestBody.token
    # amount= requestBody.charge.amount
    # currency= requestBody.charge.currency

    # try:
    #     chargeResponse= stripe.Charge.create(
    #         amount,
    #         currency,
    #         source= token,
    #         description= "Test charge",
    #     )
    # except stripe.error.CardError as e:
    #     body = e.json_body
    #     err = body.get('error', {})
    #     return {
    #         "statusCode": 500,
    #         "body": err,
    #     }
    # else:
    #     return chargeResponse['status']

