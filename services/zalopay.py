import json
import hmac
import hashlib
import os
import urllib.request
import urllib.parse
import random
from time import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
from flask import jsonify, request

config = {
    "app_id": 2553,
    "key1": "PcY4iZIKFCIdgZvA6ueMcMHHUbRLYjPL",
    "key2": "kLtgPl8HHhfvMuDHPwKfgfsY4Ydm9eIz",
    "endpoint": "https://sb-openapi.zalopay.vn/v2/create",
    "callback_url": os.getenv("CALLBACK_URL"),
}

def create_zalopay_order(amount, description, app_trans_id):
    transID = random.randrange(1000000)
    order = {
        "app_id": config["app_id"],
        "app_trans_id": app_trans_id,
        "app_user": "user123",
        "app_time": int(round(time() * 1000)),
        "embed_data": json.dumps({
            "redirecturl": "http://127.0.0.1:5000/order",
        }),
        "item": json.dumps([{}]),
        "amount": amount,
        "description": description,
        "bank_code": "zalopayapp",
        "callback_url": config["callback_url"]

    }

    data = "{}|{}|{}|{}|{}|{}|{}".format(order["app_id"], order["app_trans_id"], order["app_user"],
                                         order["amount"], order["app_time"], order["embed_data"], order["item"])

    order["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()

    response = urllib.request.urlopen(url=config["endpoint"], data=urllib.parse.urlencode(order).encode())
    result = json.loads(response.read())
    # print result
    print(f"result['return_code'] ={result['return_code']} " )
    return result

def query_zalopay_order(app_trans_id):
    params = {
        "app_id": config["app_id"],
        "app_trans_id": app_trans_id
    }

    data = "{}|{}|{}".format(config["app_id"], params["app_trans_id"], config["key1"])
    params["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()

    response = urllib.request.urlopen(url="https://sb-openapi.zalopay.vn/v2/query", data=urllib.parse.urlencode(params).encode())
    result = json.loads(response.read())

    return result