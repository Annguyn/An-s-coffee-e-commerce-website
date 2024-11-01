import random
import urllib.request
import urllib.parse
from flask import Blueprint, request, jsonify
from datetime import datetime
from time import time
import hmac
import hashlib
import json

from models import PaymentDetails

refund_bp = Blueprint('refund', __name__)

config = {
    "app_id": 2553,
    "key1": "PcY4iZIKFCIdgZvA6ueMcMHHUbRLYjPL",
    "key2": "kLtgPl8HHhfvMuDHPwKfgfsY4Ydm9eIz",
    "refund_url": "https://sb-openapi.zalopay.vn/v2/refund"
}

@refund_bp.route('/process_refund/<payment_detail_id>', methods=['POST'])
def process_refund(payment_detail_id):
    try:
        payment_detail = PaymentDetails.query.get(payment_detail_id)
        zp_trans_id = payment_detail.zp_trans_id
        amount = payment_detail.amount
        description = "Refund_for_order"
        timestamp = int(round(time() * 1000))
        uid = "{}{}".format(timestamp, random.randint(111, 999))

        order = {
            "app_id": config["app_id"],
            "m_refund_id": "{:%y%m%d}_{}_{}".format(datetime.today(), config["app_id"], uid),
            "timestamp": timestamp,
            "zp_trans_id": zp_trans_id,
            "amount": amount,
            "description": description,
        }

        data = "{}|{}|{}|{}|{}".format(order["m_refund_id"], order["zp_trans_id"], order["amount"],
                                       order["description"], order["timestamp"])
        order["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()

        response = urllib.request.urlopen(url=config["refund_url"], data=urllib.parse.urlencode(order).encode())
        result = json.loads(response.read())

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
