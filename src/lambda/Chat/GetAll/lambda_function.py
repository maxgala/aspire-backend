import json
import logging

from chat import Chat, ChatType, ChatStatus
from base import Session, row2dict
# from role_validation import UserGroups, validate_group

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # # check authorization
    # authorized_groups = [
    #     UserGroups.ADMIN,
    #     UserGroups.MENTOR,
    #     UserGroups.PAID
    # ]
    # err, group_response = validate_group(event['requestContext']['authorizer']['claims'], authorized_groups)
    # if err:
    #     return {
    #         "statusCode": 401,
    #         "body": json.dumps({
    #             "errorMessage": group_response
    #         })
    #     }

    status_filter = event["queryStringParameters"].get("status", "") if event["queryStringParameters"] else ""

    session = Session()
    # TODO: more filters?
    filtered_query = session.query(Chat)
    if status_filter:
        filtered_query = filtered_query.filter(Chat.chat_status == status_filter)

    chats = filtered_query.all()
    session.close()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "chats": [row2dict(r) for r in chats],
            "count": len(chats)
        })
    }

    # user info? line 67

    # session = Session()
    # chats = session.query(Chat).all()
    # session.close()

    # chat_attribs = []
    # pruned_attribs = [] # can set attribs to skip, empty list for now

    # for attrib in dir(Chat):
    #     if not (attrib.startswith('_') or attrib.strip() == "metadata"\
    #             or attrib in pruned_attribs):
    #         chat_attribs.append(attrib)

    # chats_list = [None] * len(chats) # preallocate in case table is large

    # for i in range(len(chats)):
    #     chat_dict = {}
    #     for attrib in chat_attribs:
    #         chat_dict[attrib] = str(getattr(chats[i], attrib))
    #     response = client.list_users(
    #         UserPoolId='us-east-1_T02rYkaXy',
    #         AttributesToGet=[
    #             'given_name','family_name','custom:company'
    #         ],
    #         Filter = 'email="{}"'.format(chats[i].senior_executive)
    #     )
    #     atts = response['Users'][0]['Attributes']
    #     for att in atts:
    #         if att['Name'] == 'given_name':
    #             chat_dict['given_name'] = att['Value']
    #         elif att['Name'] == 'family_name':
    #             chat_dict['family_name'] = att['Value']
    #         elif att['Name'] == 'custom:company':
    #             chat_dict['custom:company'] = att['Value']

    #     chats_list[i] = chat_dict

    # chats_dict = {}
    # chats_dict["chats"] = chats_list
    # chats_dict["count"] = len(chats_list)
    # return {
    #     "statusCode": 200,
    #     "body": json.dumps(chats_dict)
    # }
