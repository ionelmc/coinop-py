from binascii import hexlify, unhexlify

from nacl.utils import random
from pycoin.key import bip32

from .script import Script
from .keys import PrivateKey, PublicKey


class MultiWallet(object):

    @classmethod
    def generate(cls, names, network="testnet"):
        seeds = {}
        def create_node(name):
            secret = random(32)
            # FIXME: set blockchain/network correctly
            tree = bip32.Wallet.from_master_secret(secret, netcode='XTN')
            return tree

        for name in names:
            seeds[name] = create_node(name).wallet_key(as_private=True)

        return cls(private=seeds)


    def __init__(self, private={}, public={}):
        self.trees = {}
        self.private_trees = {}
        self.public_trees = {}

        for name, seed in private.iteritems():
            tree = bip32.Wallet.from_wallet_key(seed)
            self.private_trees[name] = self.trees[name] = tree

        for name, seed in private.iteritems():
            tree = bip32.Wallet.from_wallet_key(seed)
            self.public_trees[name] = self.trees[name] = tree

    def private_seed(self, name):
        try:
            return self.private_trees[name].wallet_key(as_private=True)
        except KeyError:
            raise Exception("No private tree for '{0}'".format(name))


    def public_seed(self, name):
        try:
            return self.public_trees[name].wallet_key()
        except KeyError:
            raise Exception("No public tree for '{0}'".format(name))

    def private_seeds(self):
        out = {}
        for name, tree in self.private_trees.iteritems():
            out[name] = self.private_seed(name)
        return out
        

    def public_seeds(self):
        out = {}
        for name, tree in self.public_trees.iteritems():
            out[name] = self.private_seed(name)
        return out
        

    def path(self, path):
        _path = path[2:]
        options = { 'private': {}, 'public': {} }

        for name, tree in self.private_trees.iteritems():
            options['private'][name] = tree.subkey_for_path(_path)
        for name, tree in self.public_trees.iteritems():
            options['public'][name] = tree.subkey_for_path(_path)

        return MultiNode(path, **options)

    def is_valid_output(self, output):
        try:
            path = output['metadata']['wallet_path']
            node = self.path(path)
            # TODO: use python equiv of ruby to_s
            # apparently the global str() ?
            node.p2sh_script.string() == output.script.string()
        except KeyError:
            return True


    def signatures(self, transaction):
        return map(sign_input, transaction.inputs)

    def sign_input(input):
        path = input['output']['metadata']['wallet_path']
        node = self.path(path)
        sig_hash = input.sig_hash(node.script)
        return node.signatures(sig_hash)


class MultiNode:

    def __init__(self, path, private={}, public={}):
        self.path = path
        self.private = private
        self.public = public

        self.private_keys = {}
        self.public_keys = {}

        for name, node in private.iteritems():
            priv = PrivateKey.from_secret(node.secret_exponent_bytes)
            self.private_keys[name] = priv

            pub = priv.public_key()
            self.public_keys[name] = pub

        for name, node in public.iteritems():
            pub = PublicKey.from_pair(node.public_pair)
            self.public_keys[name] = pub
            pass

    def script(self, m=2):
        names = sorted(self.public_keys.keys())
        keys = [self.public_keys[name].compressed() for name in names]

        return Script(public_keys=keys, needed=m)

    def address(self):
        return self.script().p2sh_address()


    def p2sh_script(self):
        return Script(address=self.address)

    def signatures(self, value):
        names = self.public_keys.keys().sort()
        return dict((name, self.sign(value)) for name in names)

    def sign(self, name, value):
        try:
            key = self.private_keys[name]
            key.sign(value) # probably need to add \x01 ??
        except KeyError:
            raise Exception("No such key: '{0}'".format(name))


    def script_sig(self, signatures):
        self.script.p2sh_sig(signatures=signatures)


