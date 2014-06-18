import pytest
import yaml

from binascii import hexlify, unhexlify
from coinop.bit.multiwallet import MultiWallet
from coinop.bit.script import Script

from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret
from bitcoin.core import Hash160


@pytest.fixture
def generated():
    return MultiWallet.generate(["primary", "backup"])

@pytest.fixture
def imported_data():
    with open(u"coinop/tests/data/multi_wallet.yaml", u"r") as file:
        data = yaml.load(file)
    return data

@pytest.fixture
def imported(imported_data):
    private = imported_data['private']
    return MultiWallet(private=private)

def test_properties(generated):
    assert sorted(generated.trees.keys()), ["backup", "primary"]
    assert sorted(generated.private_trees.keys()), ["backup", "primary"]
    assert sorted(generated.public_trees.keys()), []

def test_individual_seeds(generated):
    seed = generated.private_seed("backup")
    assert seed.find("tprv") == 0

    seed = generated.public_seed("backup")
    assert seed.find("tpub") == 0

def test_private_seeds(generated):
    for name, seed in generated.private_seeds().iteritems():
        assert seed.find("tprv") == 0

def test_reconstructing_from_seeds(generated):
    reconstructed = MultiWallet(private=generated.private_seeds())
    assert generated.private_seeds() == reconstructed.private_seeds()

def test_node_for_path(imported, imported_data):
    for path, values in imported_data['paths'].iteritems():
        node = imported.path(path)
        address = node.address()

        assert values["address"] == address
        #multisig_script = node.script()
        #assert values["multisig_script"] == multisig_script.to_string()


def test_compatibility(imported, imported_data):
    for path, values in imported_data['paths'].iteritems():
        node = imported.path(path)
        multisig_script = node.script()
        assert values["multisig_script"] == multisig_script.to_string()

    


