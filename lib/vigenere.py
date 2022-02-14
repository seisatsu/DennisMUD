# Python code to implement
# Vigenere Cipher
 
# This function generates the
# key in a cyclic manner until
# it's length isn't equal to
# the length of original text
def generateKey(string, key):
    key = list(key)
    if len(string) == len(key):
        return(key)
    else:
        for i in range(len(string) -
                       len(key)):
            key.append(key[i % len(key)])
    return("" . join(key))
     
# This function returns the
# encrypted text generated
# with the help of the key
def cipherText(string, key):
    cipher_text = []
    for i in range(len(string)):
        if string[i].isalpha():
            x = (ord(string[i]) +
                ord(key[i])) % 26
            x += ord('A')
            cipher_text.append(chr(x))
        else: cipher_text.append(string[i])
    return("" . join(cipher_text))
     
# This function decrypts the
# encrypted text and returns
# the original text
#def originalText(cipher_text, key):
#    orig_text = []
#    for i in range(len(cipher_text)):
#        x = (ord(cipher_text[i]) -
#             ord(key[i]) + 26) % 26
#        x += ord('A')
#        orig_text.append(chr(x))
#    return("" . join(orig_text))
     
# Driver code
def encvigenere(string, keyword):
    wordlist=list(string.split(' '))
    for word in range(len(wordlist)):
        key = generateKey(wordlist[word], keyword)
        if word == 0: wordlist[word]= cipherText(wordlist[word],key).capitalize()
        else: wordlist[word]= cipherText(wordlist[word],key).lower()
    cipt=' '.join(wordlist)
    return cipt

# This code is contributed
# by Pratik Somwanshi