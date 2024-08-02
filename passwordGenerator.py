from secrets import choice

NOUNS_PATH = r'username_password_generator/nounsList.txt'


def get_noun() -> str:
	nouns: list = []
	noun: str = ''
	coin: int = choice(range(2))
	with open(NOUNS_PATH, 'r') as f:
		nouns = f.read().splitlines()
		noun: str = str(choice(nouns))
	if coin == 1:
		noun = noun.capitalize()
	return noun

def nouns_password() -> None:
	print()
	print('Nouns Password')
	print()
	for i in range(3):
		nounsList: list[str] = [
		get_noun(),
		get_noun(),
		get_noun(),
		]
		password: str = '-'.join(nounsList) + "-" + str(choice(range(100))).zfill(2) +' '
		print(f"\tpassword: {password.ljust(40,'.')} len: {len(password)}")
		print()

def consonant_vowel_password(passLen: int = 0) -> None:
	consonants: list[str] = [
		'b', 'c', 'd', 'f', 'g', 'j', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', 'x', 'y', 'z'
	]
	vowels: list[str] = [
		'a', 'e', 'i', 'o', 'u'
	]
	specials: list[str] = [
		'!', '@', '#', '$', '%', '^', '&', '*', '-', '+', '?', '=', '~'
	]
	numbers: list[str] = [
		'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
	]
	
	print('\nConsonant-Vowel Passwords\n')
	
	if not passLen:
		while True:
			try:
				passLen = int(input('Enter a password length: '))
				if passLen <= 0:
					raise ValueError
				break
			except ValueError:
				print("Please enter a valid positive integer.")
	
	for _ in range(3):
		password: list[str] = [choice(specials)]
		for i in range(passLen):
			if i % 2 == 0:
				password.append(choice(consonants))
			else:
				password.append(choice(vowels))
			if (i + 1) % 4 == 0 and i != passLen - 1:
				password.append("-")
		
		password.append("-")
		password.extend(choice(numbers))
		password.append(' ')
		
		final_password = ''.join(password)
		print(f"\tpassword: {final_password.ljust(40,'.')} len: {len(final_password)}\n")
	
if __name__ == '__main__':

	consonant_vowel_password(passLen=16)
	nouns_password()

