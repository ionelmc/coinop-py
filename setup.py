from setuptools import setup

setup(name='coinop',
      version='0.0.1',
      description='Crypto-currency conveniences',
      url='http://github.com/BitVault/coinop-py',
      author='Matthew King',
      author_email='matthew@bitvault.io',
      license='MIT',
      packages=['coinop'],
      install_requires=[
          'cffi',
          'pytest',
          'pycrypto',
          'pynacl',
          'python-bitcoinlib',
          'pycoin',
          'PyYAML',
          'ecdsa'
      ],
      zip_safe=False)
