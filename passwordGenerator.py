import secrets as s
import sys

def random_password():
    # User Input
    # Length of the password
    attempt: int = 0
    while attempt < 5:
        try:
            passLength: int = int(input("\nEnter the length of the password (range: 6-32 characters): "))
            if passLength not in range(6, 33):
                attempt += 1
                if attempt == 5:
                    print("\nMaximum number of attempts reached. Exiting.")
                    sys.exit()
                print("\nInvalid input. Please enter a number between 6 and 32.")
                continue
            break
        except ValueError:
            attempt += 1
            if attempt == 5:
                print("\nMaximum number of attempts reached. Exiting.")
                sys.exit()
            print("\nInvalid input. Please enter a numeric value.")
  
    validInput: list = ['n', 'no', 'y', 'yes']
    
    # Check if user wants a special character in the password
    charCheck: bool = False
    attempt: int = 0
    while attempt < 3:
        spChar: str = input("\nDo you want a special character in your password? (Y/N): ").lower()
        if spChar in validInput:
            if spChar in validInput[2:]:
                charCheck = True
                passLength -= 1
                break
            break
        else:
            attempt += 1
            if attempt == 3:
                print("\nMaximum number of attempts reached. Exiting.")
                sys.exit()
            print("\nInvalid input. Please enter 'Y' or 'N'.")

    # Check if user wants a number in the password
    numCheck: bool = False
    attempt = 0
    while attempt < 3:
        containsNumbers: str = input("\nDo you want a number in your password? (Y/N): ").lower()
        if containsNumbers in validInput:
            if containsNumbers in validInput[2:]:
                numCheck = True
                passLength -= 1
                break
            break
        else:
            attempt += 1
            if attempt == 3:
                print("\nMaximum number of attempts reached. Exiting.")
                sys.exit()
            print("\nInvalid input. Please enter 'Y' or 'N'.")
  
    # Check if user wants to generate multiple passwords
    attempt: int = 0
    while attempt < 3:
        try:
            passCount: int = int(input("\nHow many passwords do you want to generate? (range: 1-32 passwords): "))
            if passCount not in range(1, 33):
                attempt += 1
                if attempt == 3:
                    print("\nMaximum number of attempts reached. Exiting.")
                    sys.exit()
                print("\nInvalid input. Please enter a number between 1 and 32.")
                continue
            break
        except ValueError:
            attempt += 1
            if attempt == 3:
                print("\nMaximum number of attempts reached. Exiting.")
                sys.exit()
            print("\nInvalid input. Please enter a numeric value.")

  # Password Constraints
    consonants: list = ['b', 'd', 'f', 'g', 'j', 'k', 'm', 'n', 'p', 'r', 's', 't', 'z']
    vowels: list = ['a', 'e', 'i', 'o', 'u']
    specials: list = ['!', '@', '#', '$', '%', '^', '&', '*', '-', '+', '?', '=', '~']
    numbers: list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']    
    
    # Generate Password
    pw = 1
    for i in range(passCount):
        randChar: int = s.randbelow(passLength + 1)
        randNum: int = s.randbelow(passLength + 1)
        password: list = []
        max_consonant_vowel_pairs: int = passLength // 2

        for i in range(1, max_consonant_vowel_pairs + 1):
            password.append(s.choice(consonants))
            password.append(s.choice(vowels))

        if charCheck:
            password.insert(randChar, s.choice(specials))
        if numCheck: 
            password.insert(randNum, s.choice(numbers))
        
        passString = ' '.join([''.join(password[i:i+4]) for i in range(0, len(password), 4)])

        print(f'Pw_{pw}: \t{passString}')
        pw += 1

    print('\nSpaces are added for readability.\n')

random_password()