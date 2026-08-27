import base64
import json
import urllib.request
import urllib.error
from django.conf import settings

PAYMONGO_API_BASE = "https://api.paymongo.com/v1"

def get_auth_header():
    secret_key = getattr(settings, 'PAYMONGO_SECRET_KEY', '') or 'sk_test_placeholder'
    auth_str = f"{secret_key}:"
    encoded_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
    return {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Authorization": f"Basic {encoded_auth}"
    }

def create_paymongo_checkout_session(orders, customer, success_url, cancel_url):
    """
    Creates a PayMongo Checkout Session for GCash / Maya / Card.
    Returns: dict with 'id', 'checkout_url', and 'simulated' flag.
    """
    secret_key = getattr(settings, 'PAYMONGO_SECRET_KEY', '').strip()
    
    # If no live/test PayMongo secret key configured, allow seamless automated simulation
    if not secret_key or secret_key.startswith('placeholder'):
        return {
            'id': 'sim_cs_' + str(orders[0].id),
            'checkout_url': None,
            'simulated': True
        }

    line_items = []
    for order in orders:
        amount_cents = int(round(float(order.total_amount) * 100))
        if amount_cents <= 0:
            amount_cents = 100
        is_kg = '[KG]' in (order.notes or '')
        unit_label = 'kg' if is_kg else 'pcs'
        prod_name = order.product.name if order.product else 'Farm Product'
        line_items.append({
            "currency": "PHP",
            "amount": amount_cents,
            "name": f"{prod_name} ({order.quantity_kg} {unit_label})",
            "quantity": 1
        })

    payload = {
        "data": {
            "attributes": {
                "billing": {
                    "name": getattr(customer, 'name', 'Customer') or "Customer",
                    "email": getattr(customer, 'email', '') or "customer@lantad.com",
                    "phone": getattr(customer, 'phone', '') or "09171234567"
                },
                "send_email_receipt": True,
                "show_description": True,
                "show_line_items": True,
                "payment_method_types": ["gcash", "paymaya", "grab_pay", "card"],
                "line_items": line_items,
                "description": f"Order #{orders[0].order_number}",
                "success_url": success_url,
                "cancel_url": cancel_url
            }
        }
    }

    try:
        req = urllib.request.Request(
            f"{PAYMONGO_API_BASE}/checkout_sessions",
            data=json.dumps(payload).encode('utf-8'),
            headers=get_auth_header(),
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            cs_id = res_data['data']['id']
            checkout_url = res_data['data']['attributes']['checkout_url']
            return {
                'id': cs_id,
                'checkout_url': checkout_url,
                'simulated': False
            }
    except Exception as e:
        print("PayMongo API Connection Error:", e)
        return {
            'id': 'sim_cs_' + str(orders[0].id),
            'checkout_url': None,
            'simulated': True,
            'error': str(e)
        }
