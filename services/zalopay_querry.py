import json
import logging
from time import time
import hmac
import hashlib
import urllib.parse
import urllib.request

config = {
    "app_id": 2553,
    "key1": "PcY4iZIKFCIdgZvA6ueMcMHHUbRLYjPL",
    "key2": "kLtgPl8HHhfvMuDHPwKfgfsY4Ydm9eIz",
    "endpoint": "https://sb-openapi.zalopay.vn/v2/query"
}

def query_zalopay_order(app_trans_id):
    params = {
        "app_id": config["app_id"],
        "app_trans_id": app_trans_id
    }

    data = "{}|{}|{}".format(config["app_id"], params["app_trans_id"], config["key1"])
    params["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()

    response = urllib.request.urlopen(url=config["endpoint"], data=urllib.parse.urlencode(params).encode())
    result = json.loads(response.read())

    return result

def check_payment_status(app_trans_id):
    result = query_zalopay_order(app_trans_id)
    if result['return_code'] == 1 and not result['is_processing']:
        if result['zp_trans_id']:
            logging.info(f"Payment for transaction {app_trans_id} was successful.")
            return 'Success'
        else:
            logging.info(f"Payment for transaction {app_trans_id} failed.")
            return 'Failed'
    else:
        logging.info(f"Payment for transaction {app_trans_id} is still processing or failed.")
        return 'Processing or Failed'