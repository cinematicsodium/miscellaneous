from unicodedata import normalize
from time import sleep
morseDict={'.-':'A','-...':'B','-.-.':'C','-..':'D','.':'E','..-.':'F','--.':'G','....':'H','..':'I','.---':'J','-.-':'K','.-..':'L','--':'M','-.':'N','---':'O','.--.':'P','--.-':'Q','.-.':'R','...':'S','-':'T','..-':'U','...-':'V','.--':'W','-..-':'X','-.--':'Y','--..':'Z','.----':'1','..---':'2','...--':'3','....-':'4','.....':'5','-....':'6','--...':'7','---..':'8','----.':'9','-----':'0','.-.-.-':'.','--..--':',','..--..':'?','.----.':"'",'-.-.--':'!','-..-.':'/','-.--.':'(','-.--.-':')','.-...':'&','---...':':','-.-.-.':';','-...-':'=','.-.-.':'+','-....-':'-','..--.-':'_','.-..-.':'"','...-..-':'$','.--.-.':'@','...---...':'SOS', ' ':' '}

morse = '--.- - .-.. -.-.-. -.- -. --.- .-- ....- ----. ----- ---.. .... -.-.-. .-.. -.- .-. --.- .-- . .-. ..-. .- ... -.. ..-. ..... ....- ----. -..-. ..--.. .- ----. . .-.'

def morse_to_alpha(morse: str):
    while True:
        try:
            morseChars = ['.', '-', ' ']
            invalidList = []
            for char in morse:
                if char not in morseChars:
                    invalidList.append(char)
            if len(invalidList) > 0:
                invalidSetList = ', '.join(sorted(list(set(invalidList))))
                sleep(1)
                print(f'\nInvalid character(s): \n{invalidSetList} \n\nMorse code only consists of dots (.) and dashes (-). \n"Letters" must be separated with a single space. \n"Words" must be separated with three spaces.\n')
                print('Example: \n.... . .-.. .-.. --- --..--    -- --- - --- .-.-.-')
                sleep(3)
                break
            decoded_message = ''
            for word in morse.split('   '):
                for char in word.split():
                    if char not in morseDict.keys():
                        decoded_message += '?'
                        continue
                    decoded_message += morseDict[char]
                decoded_message += ' '
            sleep(1)
            print('\nDecoded Morse code message:\n\t', decoded_message)
        except Exception:
            sleep(1)
            print('\nError. Please try again.')
        else:
            break

def alpha_to_morse(alpha: str):
    while True:
        try:
            morseValues = [i for i in morseDict.values()]
            msgStrip = alpha.strip()
            msgNFKD = normalize('NFKD', msgStrip)
            msgEncode = msgNFKD.encode('ascii', 'ignore')
            msgDecode = msgEncode.decode()
            msgFormat = []
            for i in msgDecode:
                if i.isalpha():
                    msgFormat.append(i.upper())
                elif i not in morseValues and i != ' ':
                    msgFormat.append('?')
                else:
                    msgFormat.append(i)
            filtered_text = ''.join(msgFormat)
            encoded_message = ''
            for word in filtered_text.split():
                for char in word:
                    char = list(morseDict.keys())[list(morseDict.values()).index(char)] + ' '
                    encoded_message += char
                encoded_message += '   '
            encoded_message = encoded_message.strip()
            sleep(1)
            print('\nMessage encoded to Morse code:\n\t', encoded_message)
            sleep(5)
        except Exception:
            sleep(1)
            print('\nError. Please try again.')
        else:
            break

while True:
    try:
        sleep(1)
        print("\n\nEnter 'T' to convert text into to Morse code.")
        print("Enter 'M' to convert Morse code into text.")
        print("Enter 'Q' to quit.")
        sleep(3)
        selection: str = input('\nEnter selection: ').strip().lower()
        options: list = ['t','m', 'q']
        if selection not in options:
            sleep(1)
            print('\nInvalid selection. Please try again.')
            continue
        elif selection == 't':
            sleep(1)
            print('\n\nEnter text to convert to Morse code:')
            text = input('Text: ').strip()
            alpha_to_morse(text)
            continue
        elif selection == 'm':
            sleep(1)
            print('\n\nEnter Morse code to convert to text:')
            sleep(1)
            morse = input('Morse code: ').strip()
            morse_to_alpha(morse)
            continue
        elif selection == 'q':
            sleep(1)
            print('\n\nGoodbye!\n\n')
            exit()
        else:
            continue
    except Exception:
        sleep(1)
        print('\nError. Please try again.')
    else:
        break