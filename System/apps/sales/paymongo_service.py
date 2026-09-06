import base64
import json
import urllib.request
import urllib.error
from django.conf import settings

PAYMONGO_API_BASE = "https://api.paymongo.com/v1"

def get_paymongo_secret_key():
    """Retrieve PayMongo secret key from DB settings or Django settings/env."""
    try:
        from apps.sales.models import PaymentSetting
        db_settings = PaymentSetting.get_settings()
        if db_settings and db_settings.paymongo_secret_key:
            return db_settings.paymongo_secret_key.strip()
    except Exception:
        pass
    return (getattr(settings, 'PAYMONGO_SECRET_KEY', '') or '').strip()

def get_auth_header(secret_key=None):
    if not secret_key:
        secret_key = get_paymongo_secret_key() or 'sk_test_placeholder'
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
    secret_key = get_paymongo_secret_key()
    
    # If no live/test PayMongo secret key configured, prompt admin to configure it
    if not secret_key or secret_key.startswith('placeholder'):
        return {
            'id': None,
            'checkout_url': None,
            'simulated': False,
            'error': 'PayMongo Secret Key not configured yet. Please enter your PayMongo Secret Key (sk_test_... or sk_live_...) in Orders & Deliveries → Payment Settings panel.'
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
            headers=get_auth_header(secret_key),
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
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        print("PayMongo API HTTP Error:", err_body)
        try:
            err_json = json.loads(err_body)
            err_msg = err_json.get('errors', [{}])[0].get('detail', err_body)
        except Exception:
            err_msg = err_body
        return {
            'id': None,
            'checkout_url': None,
            'simulated': False,
            'error': f"PayMongo API Error: {err_msg}"
        }
    except Exception as e:
        print("PayMongo API Connection Error:", e)
        return {
            'id': None,
            'checkout_url': None,
            'simulated': False,
            'error': f"PayMongo Connection Error: {str(e)}"
        }
