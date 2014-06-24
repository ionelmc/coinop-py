# Annoying warning at startup:
# https://github.com/pyca/pynacl/issues/62
# Fixed June 18th 2014.
from nacl.secret import SecretBox
import nacl.utils

from Crypto.Protocol.KDF import PBKDF2

class PassphraseBox:

    ITERATIONS = 10000

    @classmethod
    def encrypt(cls, passphrase, plaintext):
        box = cls(passphrase)
        return box._encrypt(plaintext)

    @classmethod
    def decrypt(cls, passphrase, encrypted):
        salt = encrypted['salt']
        iterations = encrypted['iterations']

        ppbox = cls(passphrase, salt, iterations)
        return ppbox._decrypt(encrypted['ciphertext'], encrypted['nonce'])

    def __init__(self, passphrase, salt=None, iterations=None):
        if salt is None:
            salt = nacl.utils.random(16)
            iterations = self.ITERATIONS
        else:
            salt = salt.decode('hex')

        key = PBKDF2(passphrase, salt, 32, iterations)

        self.salt = salt
        self.iterations = iterations
        self.box = SecretBox(key)


    def _encrypt(self, plaintext):
        nonce = nacl.utils.random(SecretBox.NONCE_SIZE)
        encrypted = self.box.encrypt(plaintext, nonce)
        ciphertext = encrypted.ciphertext
        return dict(
            salt=self.salt.encode('hex'), iterations=self.iterations,
            nonce=nonce.encode('hex'), ciphertext=ciphertext.encode('hex')
        )

    def _decrypt(self, ciphertext, nonce):
        return self.box.decrypt(ciphertext.decode('hex'), nonce.decode('hex'))


