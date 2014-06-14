import pytest
import yaml

from coinop.bit.multiwallet import MultiWallet
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret


@pytest.fixture
def wallet():
    return MultiWallet.generate(["primary", "backup"])


def test_properties(wallet):
    assert sorted(wallet.trees.keys()), ["backup", "primary"]
    assert sorted(wallet.private_trees.keys()), ["backup", "primary"]
    assert sorted(wallet.public_trees.keys()), []

def test_individual_seeds(wallet):
    seed = wallet.private_seed("backup")
    assert seed.find("tprv") == 0

    seed = wallet.public_seed("backup")
    assert seed.find("tpub") == 0

def test_private_seeds(wallet):
    for name, seed in wallet.private_seeds().iteritems():
        assert seed.find("tprv") == 0

def test_reconstructing_from_seeds(wallet):
    reconstructed = MultiWallet(private=wallet.private_seeds())
    assert wallet.private_seeds() == reconstructed.private_seeds()

#def test_node_for_path(wallet):
    #node = wallet.path("m/0/0/2")
    #print node.address()

def test_compatibility():
    with open(u"coinop/tests/data/multi_wallet.yaml", u"r") as file:
        data = yaml.load(file)
    private = data['private']
    wallet = MultiWallet(private=private)

    print
    for path, values in data['paths'].iteritems():
        node = wallet.path(path)
        multisig_script = node.script()
        print "rb", values["multisig_script"]
        print "py", multisig_script.to_string()
        #print multisig_script.to_hex()

    


