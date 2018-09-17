import re, string
import numpy as np
text = """W We   ﴾no numbers, no, a
punctuation﴿ space.
Write a line﴿ input, and to
produce, in order, on separate lines:"""
lines = text.split('\n')

data = [sent.split() for sent in lines]
# print(data)
words = re.findall('\w+', text)
result = []
for word in words:
    if len(word) == 1 and word.isupper():
        continue
    else:
        result.append(word)
print(result)


def sortFreqDict(freqdict):
    aux = [(freqdict[key], key) for key in freqdict]
    aux.sort()
    aux.reverse()
    return aux


def wordListToFreqDict(wordlist):
    wordfreq = [wordlist.count(p) for p in wordlist]
    return dict(zip(wordlist, wordfreq))


dict_word_freq = sortFreqDict(wordListToFreqDict(result))
# print(dict_word_freq)
for s in dict_word_freq:
    print(str(s))
