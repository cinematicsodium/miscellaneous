'''
AES-256 encryption and decryption.
-------------------------------------------
AES (Advanced Encryption Standard) is an encoding algorithm that transforms 
plain text data into a version known as ciphertext that’s not possible for 
humans or machines to understand without an encryption key―a password.

For example, you use AES in software development to securely store passwords 
in a database. Storing a password as plain text would allow anyone with access 
to the database to log in to user accounts, so encrypting them is the first 
step to adding a layer of security to your authentication system.

AES requires a secret passphrase known as a “key” to encrypt/decrypt data. 
Anybody with the key can decrypt your data, so you need it to be strong and 
hidden from everyone―only the software program should be able to access it.

The key can be either 128, 192, 256, or 512 bit long. An AES cipher using a 
512-bit key is abbreviated as AES 512, for example. The longer the key, the 
more secure it is, but the slower the encryption/decryption will be as well. 
128 bits is equivalent to 32 characters in base64 encoding, 64 characters 
for 256 bits. Since storage space isn't usually a problem and the difference 
in speed between the versions is negligible, a good rule of thumb is to use 
256-bit keys.
'''

import json
from base64 import b16encode, b16decode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# Encrypting the message
message: str = str(input("\nEnter your secret message: \n"))

data = message.encode()
key = get_random_bytes(32)
key16 = b16encode(key).decode('utf-8')
cipher = AES.new(key, AES.MODE_CBC)
ct_bytes: bytes = cipher.encrypt(pad(data, AES.block_size))
iv = b16encode(cipher.iv).decode('utf-8')
ct = b16encode(ct_bytes).decode('utf-8')
encrypted = {"key": key16, "iv": iv, "ciphertext": ct}

with open('encrypted.json', 'w') as f:
    json.dump(encrypted, f, indent=4)

print(json.dumps(encrypted, indent=4))

# Decrypting the message
with open('encrypted.json', 'r') as f:
    decrypted = json.load(f)

try:
    ct = b16decode(decrypted['ciphertext'])
    iv = b16decode(decrypted['iv'])
    key = b16decode(decrypted['key'])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    print("Decrypted message: ", pt)
except (ValueError, KeyError):
    print("Incorrect decryption")
