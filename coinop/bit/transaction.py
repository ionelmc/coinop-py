from binascii import hexlify, unhexlify

from bitcoin.core.script import CScript, SignatureHash, SIGHASH_ALL

from coinop.bit.script import Script

class Input:

    def __init__(self, data, transaction=None, index=None):
        pass

    def sig_hash(self, redeem_script=None):
        return self.transaction.sig_hash(self, redeem_script)

class Output:

    def __init__(self, data, transaction=None, index=None):
        if transaction:
            self.transaction = transaction
        elif 'transaction_hash' in data:
            self._hash = data['transaction_hash']

        self.index = index
        self.value = data.get('value', -1)
        self.address = data.get('address', None)
        self.metadata = data.get('metadata', {})

        if 'script' in data:
            self.script = Script(**data['script'])
        else:
            self.script = None


class Transaction:


    def __init__(self, **options):
        self.inputs = []
        self.outputs = []
        if 'data' in options:
            self.set_data(options['data'])
        else:
            raise Exception("Invalid options")

    def set_data(self, data):
        self.version = data.get('version', 1)
        self.lock_time = data.get('lock_time', 0)
        self.hash = data.get('hash', None)

        for input_data in data.get('inputs', []):
            index = len(self.inputs)
            _input = Input(transaction=self, data=input_data, index=index)
            self.inputs.append(_input)

        for output_data in data.get('outputs', []):
            index = len(self.outputs)
            output = Output(transaction=self, data=output_data, index=index)
            self.inputs.append(output)



    def sig_hash(input, redeem_script=None):
        #redeem_script = redeem_script or input.prev_out.script
        return SignatureHash(redeem_script, self.native, 0, SIGHASH_ALL)
