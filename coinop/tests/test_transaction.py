import pytest
import yaml

from binascii import hexlify, unhexlify
from coinop.bit.transaction import Transaction
from coinop.bit.script import from_string
from bitcoin.core.serialize import Hash
from bitcoin.core import b2lx

@pytest.fixture
def data():
    with open(u"coinop/tests/data/unsigned_payment.yaml", u"r") as file:
        data = yaml.load(file)
    return data



def test_from_data(data):
    tx = Transaction(data=data)

    print tx.to_hex()
    print tx.hex_hash()


