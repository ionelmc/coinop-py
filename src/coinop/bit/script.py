from binascii import hexlify, unhexlify

#python-bitcoinlib

from bitcoin.core.script import CScript, OPCODES_BY_NAME, OP_CHECKMULTISIG, OP_HASH160, OP_EQUAL, CScriptTruncatedPushDataError, CScriptInvalidError

import bitcoin
from bitcoin.wallet import CBitcoinAddress
from bitcoin.core import b2x, Hash160
from bitcoin.base58 import encode, decode

def encode_address(data, network):
    if network == "mainnet":
        version = 5
    elif network == "testnet":
        version = 196
    else:
        raise ValueError("Unknown network")

    data = chr(version) + data
    check = bitcoin.core.Hash(data)[0:4]
    return encode(data + check)
            

# adapted from python-bitcoinlib's tests
def from_string(string):
    def ishex(s):
        return set(s).issubset(set('0123456789abcdefABCDEF'))

    r = []

    # Create an opcodes_by_name table with both OP_ prefixed names and
    # shortened ones with the OP_ dropped.
    opcodes_by_name = {}
    for name, code in OPCODES_BY_NAME.items():
        opcodes_by_name[name] = code
        opcodes_by_name[name[3:]] = code

    for word in string.split():
        if word.isdigit() or (word[0] == '-' and word[1:].isdigit()):
            r.append(CScript([long(word)]))
        elif ishex(word):
            word_bytes = unhexlify(word.encode('utf8'))
            push_code = chr(len(word_bytes))
            r.append(push_code + word_bytes)

        elif len(word) >= 2 and word[0] == "'" and word[-1] == "'":
            r.append(CScript([bytes(word[1:-1].encode('utf8'))]))
        elif word in opcodes_by_name:
            r.append(CScript([opcodes_by_name[word]]))
        else:
            raise ValueError("Error parsing script: %r" % string)

    return CScript(b''.join(r))

def from_p2sh_address(address):
    return CScript([OP_HASH160, CBitcoinAddress(address), OP_EQUAL])


def multisig(**options):
    m = options['needed']
    keys = options['public_keys']
    return CScript([m] + keys + [3, OP_CHECKMULTISIG])


# adapted from python-bitcoinlib
def cscript_to_string(cscript):
    def to_s(o):
        if isinstance(o, bytes):
            return b2x(o)
        else:
            return repr(o)

    ops = []
    i = iter(cscript)
    while True:
        op = None
        try:
            op = to_s(next(i))
        except CScriptTruncatedPushDataError as err:
            op = '%s...<ERROR: %s>' % (to_s(err.data), err)
            break
        except CScriptInvalidError as err:
            op = '<ERROR: %s>' % err
            break
        except StopIteration:
            break
        finally:
            if op is not None:
                ops.append(op)
    return ' '.join(ops)



class Script:

    def __init__(self, **options):
        if 'cscript' in options:
            self.set_cscript(options['cscript'])
        elif 'string' in options:
            self.set_cscript(from_string(options['string']))
        elif 'binary' in options:
            self.set_cscript(CScript(options['binary']))
        elif 'hex' in options:
            binary = unhexlify(options['hex'])
            self.set_cscript(CScript(binary))
        else:
            if 'p2sh_address' in options:
                self.set_cscript(from_p2sh_address(options['p2sh_address']))
            elif ('public_keys' in options) and ('needed' in options):
                self.set_cscript(multisig(**options))
            #elif 'signatures' in options:
                #pass
            else:
                raise Exception("Invalid options")

    def set_cscript(self, cscript):
        self.cscript = cscript

    def to_string(self):
        return cscript_to_string(self.cscript)

    def __str__(self):
        return cscript_to_string(self.cscript)

    def to_hex(self):
        return hexlify(self.cscript)

    def to_binary(self):
        pass

    def hash160(self):
        return Hash160(self.cscript)

    def p2sh_script(self):
        cscript = self.cscript.to_p2sh_scriptPubKey()
        return Script(cscript=cscript)

    def p2sh_address(self, network="testnet"):
        return encode_address(self.hash160(), network)

