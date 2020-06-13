import sys

sys.path.insert(0, '../models/')

from CreateChat import lambda_function
import chat


ch = chat.Chat()
ch.chat_id = 1234
ch.date = "MMDDYYY"
ch.chat_type = chat.ChatType(1)
ch.description = "talk 2 me"
ch.credits = 200
ch.chat_status = chat.ChatStatus(1)
ch.aspiring_professionals =  ["Meep"]
ch.senior_executive = "Merp"
ch.created_on = "today"
ch.updated_on = "yesterday"

event = ch.__dict__

lambda_function.handler(event, 'context')
