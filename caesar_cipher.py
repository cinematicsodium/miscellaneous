# The Caesar cipher is a substitution cipher where each letter in the plaintext 
# is shifted a certain number of places down or up the alphabet. Julius Caesar, 
# the Roman Emperor, is said to have used a shift of 3. Here's a quick example:
#
# Original:     A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
# Shifted by 3: D E F G H I J K L M N O P Q R S T U V W X Y Z A B C
#
# So, using a shift of 3, "HELLO" would be encrypted as "KHOOR." To decrypt, 
# you'd simply shift the letters in the opposite direction. The Caesar cipher is 
# a basic and easily breakable encryption method, but it serves as a foundation 
# for more complex algorithms.

def caesar_cipher(message: str, shift: int) -> None:
    from string import ascii_lowercase, ascii_uppercase
    from unicodedata import normalize

    NFKDmsg = normalize('NFKD', message)
    ascii_encode = NFKDmsg.encode('ascii', 'ignore')
    message = ascii_encode.decode()

    lowercase: list = [i for i in ascii_lowercase]
    uppercase: list = [i for i in ascii_uppercase]

    encoded_message: str = ''

    for char in message:
        if char in uppercase:
            encoded_message += uppercase[(uppercase.index(char) + shift) % 26]
        elif char in lowercase:
            encoded_message += lowercase[(lowercase.index(char) + shift) % 26]
        elif char.isdigit():
            encoded_message += str((int(char) + shift) % 10)
        else:
            encoded_message += char

    print('\nEncrypted message:')
    print(encoded_message)

while True:
    try:
        print('\nCaesar cipher.')
        print('\nExample: ')
        print('\n\tOriginal: \tTesting, testing, 1, 2, 3.')
        print('\tShift number: \t5')
        print('\n\tEncrypted: \tYjxynsl, yjxynsl, 6, 7, 8.')
        while True:
            try:
                message: str = input('\nEnter message to encrypt: ').strip()
                shift: int = int(input('\nEnter shift number: ').strip())
                caesar_cipher(message, shift)
                continue
            except Exception:
                print('\nError. Please try again.')
            else:
                break
    except Exception:
        print('\nError. Please try again.')
    else:
        break