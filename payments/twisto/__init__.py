from __future__ import unicode_literals
import zlib
import struct
import base64
import binascii
try:
    # For Python 3.0 and later
    from urllib.error import URLError
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import URLError
    from urllib import urlencode
from django.http import HttpResponseRedirect

from .forms import DummyForm
from .. import PaymentError, PaymentStatus, RedirectNeeded
from ..core import BasicProvider

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash.HMAC import HMAC
from Crypto.Hash.SHA256 import SHA256Hash
import json

PRODUCT = 0
SHIPPING = 1

class TwistoProvider(BasicProvider):
    '''
    Dummy payment provider
    '''

    def process_data(self, payment, request, **kwargs):
        orders_array = []
        orders = kwargs['orders']
        for order in orders:
            orders_array.append(self.serialize_order(order))

        twisto_payload = {
            #'random_nonce':uniqid('', True),
            'customer':{
                'email':order.user_email,
            },
            'order':orders_array.pop(0),
            'previous_orders':orders_array,
        }
        print(twisto_payload)

    def encrypt(self):
        # získání key a salt
        key_part = secret_encryption_key[8:]
        binary_key = binascii.unhexlify(key_part)
        key, salt = binary_key[:16], binary_key[16:]
        # Inicializační vektor
        iv = Random.new().read(AES.block_size)
        # získání šifry.
        cipher = AES.new(key, AES.MODE_CBC, iv)
        # konverze do UTF-8
        serialized_data = json.dumps(data).encode('utf-8')
        # komprese dat
        serialized_data = zlib.compress(serialized_data, 9)
        # připojení velikosti dat v bajtech (big-endian)
        serialized_data = struct.pack('!L', len(serialized_data)) + serialized_data
        # kontrolní součet
        digest = HMAC(salt, serialized_data + iv, SHA256Hash()).digest()
        # padding
        serialized_data += bytes(16 - len(serialized_data) % 16)
        # šifrování
        encrypted_data = cipher.encrypt(serialized_data)
        str = base64.b64encode((iv + digest + encrypted_data), encoding='utf-8')
        return str

    def serialize_address(self, address):
        address = {
            'type':1,
            'name':address.full_name,
            'street':address.street_address_1,
            'city':address.city,
            'zipcode':address.postal_code,
            'phone_number':address.phone,
            'country':address.country.code,
        }
        return address

    def serialize_item(self, item):
        item = {
            'type':PRODUCT,
            'name':item.product_name,
            'product_id':item.id,
            'quantity':item.quantity,
            'price_vat':float(item.unit_price_net * item.quantity),
            'vat':21,
        }
        return item

    def serialize_shipping(self, service, price):
        shipping = {
            'type':SHIPPING,
            'name':'doprava',
            'product_id':service,
            'quantity':1,
            'price_vat':float(price[0]),
            'vat':21,
        }
        return shipping

    def serialize_order(self, order):
        ship_address = order.shipping_address
        bill_address = order.billing_address
        items = order.get_items()

        item_array = []
        for item in items:
            item_array.append(self.serialize_item(item))

        shipping_cost = order.get_delivery_total()
        item_array.append(self.serialize_shipping('shipping', shipping_cost))

        date_created = order.created.strftime("%Y-%m-%dT%H:%M:%S")

        serialized_order = {
            'date_created':date_created,
            'billing_address':self.serialize_address(bill_address),
            'delivery_address':self.serialize_address(ship_address),
            'items':item_array,
        }
        return serialized_order