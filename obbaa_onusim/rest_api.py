import json

from obbaa_onusim.database import Results
from obbaa_onusim import *
from obbaa_onusim.mib import mibs
from obbaa_onusim.util import indices
import onusim as onusim
from sanic import Sanic
from sanic.response import json
from obbaa_onusim.connection_info import ConnectionInfo


onu_config_api = Sanic("ONU_Config")

def index_to_mask(indexes):
    str_mask = ''
    for i in range(1, 17):
        if i in indexes:
            str_mask = str_mask + '1'
        else:
            str_mask = str_mask + '0'
    return str_mask, int(str_mask, 2)

def order_values(indexes, values):
    ordred_values = [0]*16
    for idx, val in zip(indexes, values):
        ordred_values[idx-1] = val
    dict_values = {i:j for i, j in zip(range(1, len(ordred_values)), ordred_values)}
    return dict_values

def input_values_formating(list_values, me_class):
    mib = mibs.get(me_class, None)
    values = {}
    attr_names = mib.attr_names().split(", ")    
    for attr_name, value in zip(attr_names, list_values.values()):
        attr_name = attr_name[attr_name.find("(")+1:attr_name.find(")")]
        attr = mib.attr(attr_name)
        values[attr.name] = (value,)
    return values

def create_mask(req):
    indexes = []
    values = []    
    for attr in req["attributes"]:
        indexes.append(attr["index"])
        if req["action"] in ("SET", "CREATE"): 
            values.append(attr["value"])
    mask = index_to_mask(indexes)
    ordred_val = order_values(indexes, values)
    return mask, ordred_val

def get_me(req, mask):
    result = ConnectionInfo.get_connection().database.get(req["onu_id"], req["class_id"], req["instance_id"], mask[1])
    attrs = [a for a in result.attrs]
    attr_vals = []
    for attr in attrs:
        if isinstance(attr[1], (list, tuple)):
            attr_vals.append(attr[1][0])
        else:
            attr_vals.append(attr[1])
    idxs = list(i[0] for i in indices(result.attr_mask))
    attrs_dict = [{"index": i, "value": v} for i, v in zip(idxs, attr_vals)]
    req['attributes'] = attrs_dict
    req['status'] = result.reason
    return req

def set_me(req, mask, ordred_val):
    result = ConnectionInfo.get_connection().database.set(req["onu_id"], req["class_id"], req["instance_id"], mask[1], input_values_formating(ordred_val ,req["class_id"]), check_access=False)
    req['status'] = result.reason
    return req

def create_me(req, ordred_val):
    result = ConnectionInfo.get_connection().database.create(req["onu_id"], req["class_id"], req["instance_id"], input_values_formating(ordred_val,req["class_id"]))
    req['status'] = result.reason
    return req

def delete_me(req):
    result = ConnectionInfo.get_connection().database.delete(req["onu_id"], req["class_id"], req["instance_id"])
    req['status'] = result.reason
    return req

def send_alarm(req):
    result = onusim.send_alarm(req["onu_id"],
                               int(req["class_id"]),
                               int(req["instance_id"]),
                               int(req["bit_map"],16).to_bytes(28,'big'),
                               int(req["seq_number"]))            
    req['status'] = result.reason
    return req

def process_request(requests) -> json:
    result = {"responses": []}
    for req in requests:
        if req["action"] == "DELETE":
            response = delete_me(req)
        elif req["action"] == "ALARM":
            response = send_alarm(req)
        else:
            mask, ordred_val = create_mask(req)
            if req["action"] == "SET":                  
                response = set_me(req, mask, ordred_val)
            elif req["action"] == "CREATE":
                response = create_me(req, ordred_val)
            elif req["action"] == "GET":
                response = get_me(req, mask)
        result["responses"].append(response)
    return result

@onu_config_api.route('onu/action_on_mes', methods=["POST"])
def action_on_mes(request) -> json:
    return json(process_request(request.json["requests"]))

