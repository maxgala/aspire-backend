import json
from connect_se import *
from base import Session

def handler(event, context):
    session = Session()
    connects = session.query(ConnectSE).all()
    session.close()

    attribs = []
    pruned_attribs = [] # can set attribs to skip, empty list for now

    for attrib in dir(ConnectSE):
        if not (attrib.startswith('_') or attrib.strip() == "metadata"\
                or attrib in pruned_attribs):
            attribs.append(attrib)

    connects_list = [None] * len(connects) # preallocate in case table is large
    
    for i in range(len(connects)):
        connect_dict = {}
        for attrib in attribs:
            connect_dict[attrib] = str(getattr(connects[i], attrib))
            
        connects_list[i] = connect_dict

    json_dict = {}
    json_dict["connects"] = connects_list;
    json_dict["count"] = len(connects_list);
    return {"statusCode": 200,
            "body": json.dumps(json_dict)
    }
