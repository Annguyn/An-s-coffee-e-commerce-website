# services/zalopay.py

import json
import hmac
import hashlib
import urllib.request
import urllib.parse
import random
from time import time
from datetime import datetime

config = {
    "app_id": 2553,
    "key1": "PcY4iZIKFCIdgZvA6ueMcMHHUbRLYjPL",
    "key2": "kLtgPl8HHhfvMuDHPwKfgfsY4Ydm9eIz",
    "endpoint": "https://sb-openapi.zalopay.vn/v2/create"
}

def create_zalopay_order(amount, description):
    transID = random.randrange(1000000)
    order = {
        "app_id": config["app_id"],
        "app_trans_id": "{:%y%m%d}_{}".format(datetime.today(), transID),
        "app_user": "user123",
        "app_time": int(round(time() * 1000)),
        "embed_data": json.dumps({}),
        "item": json.dumps([{}]),
        "amount": amount,
        "description": description,
        "bank_code": "zalopayapp"
    }

    data = "{}|{}|{}|{}|{}|{}|{}".format(order["app_id"], order["app_trans_id"], order["app_user"],
                                         order["amount"], order["app_time"], order["embed_data"], order["item"])

    order["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()

    response = urllib.request.urlopen(url=config["endpoint"], data=urllib.parse.urlencode(order).encode())
    result = json.loads(response.read())

    return result