from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

from sys import argv

if len(argv) != 4:
    print('python3 verify.py <filename> <signature> <publik_key>')
else:
    file_path, signature_path, pub_path = argv[1], argv[2], argv[3]
    with open(file_path, 'rb') as f:
        file = f.read()
    with open(signature_path, 'rb') as f:
        signature = f.read()
    with open(pub_path, 'rb') as f:
        key = RSA.import_key(f.read())

    hash = SHA256.new(file)
    try:
        pkcs1_15.new(key).verify(hash, signature)
        print(True)
    except:
        print(False)
