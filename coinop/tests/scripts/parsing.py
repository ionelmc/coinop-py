from binascii import hexlify, unhexlify

from coinop.bit.script import cscript_to_string
from bitcoin.core.script import CScript, OPCODES_BY_NAME, OP_CHECKMULTISIG, CScriptTruncatedPushDataError, CScriptInvalidError


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

from pycoin.tx.script.tools import compile

string = "OP_HASH160 ba2fc407b830d432483556aa2111c01ca7de6598 OP_EQUAL"
string = "OP_DUP OP_HASH160 b53915aa830a67fa59b23fda020ce540ef63e953 OP_EQUALVERIFY OP_CHECKSIG"

#x = compile(string)
#print 'pycoin', repr(x)
#print repr(CScript(x))


cscript = from_string(string)
print repr(cscript)
