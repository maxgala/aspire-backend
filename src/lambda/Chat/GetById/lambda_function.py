import json
import logging

from chat import Chat
from base import Session, row2dict

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    chatId = event["pathParameters"].get("chatId") if event["pathParameters"] else None
    if not chatId:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing path parameter(s): 'chatId'"
            }),
            "headers": {
                'Access-Control-Allow-Origin': 'https://aspire.maxgala.com,https://max-aspire-frontend.herokuapp.com',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    session = Session()
    chat = session.query(Chat).get(chatId)
    session.close()
    if not chat:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "errorMessage": "chat with id '{}' not found".format(chatId)
            }),
            "headers": {
                'Access-Control-Allow-Origin': 'https://aspire.maxgala.com,https://max-aspire-frontend.herokuapp.com',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
                'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
            }
        }

    return {
        "statusCode": 200,
        "body": json.dumps(
            row2dict(chat)
        ),
        "headers": {
            'Access-Control-Allow-Origin': 'https://aspire.maxgala.com,https://max-aspire-frontend.herokuapp.com',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
            'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin'"
        }
    }
