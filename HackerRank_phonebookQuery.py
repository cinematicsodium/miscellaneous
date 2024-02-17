'''
# 1. Create a phone book using a dictionary data structure.
# 2. Read the number of entries in the phone book.
# 3. Read the name and phone number for each entry and add it to the phone book.
# 4. Read the queries and print the corresponding phone number for each query.
# 5. If the name is not found in the phone book, print "Not found".
'''

phonebookDict: dict = {}

numEntries: int = int(input())

entryCount: int = 0

while entryCount < numEntries:
    name, phone = input().split()
    phonebookDict[name] = phone
    entryCount += 1

while True:
    try:
        query: str = input()
        if query in phonebookDict:
            print(f"{query}={phonebookDict[query]}")
        else:
            print("Not found")
    except:
        break  # Exit, Ctrl+D