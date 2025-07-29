#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module for analyzing text files
"""

import json

def analyzeFiles():
    """
    Analize files for words.
    """
    fileN = input("Enter the file you want me too analyze... ")
    if fileN == "":
        fileN = "phil.txt"


    data = ""
    with open(fileN) as dFile:
        data = dFile.read()
    word_count(data)
    line_count(data)
    letter_count(data)
    word_frequency(data)
    letter_frequency(data)

def analyze_all(text):
    """
    Analize files for words.
    """
    word_count(text)
    line_count(text)
    letter_count(text)
    word_frequency(text)
    letter_frequency(text)

def strip_non_alpa(text):
    """
    Strip string from non alpha caracters
    """
    letters = []
    for let in list(text):
        if let.isalpha():
            letters.append(let)
    return letters
    
def strip_punctuation(text):
    """
    Strip string from punctuations
    """
    return "".join(c for c in text if c not in (',', '.'))

def word_count(text):
    """
    Count number of words in string
    """
    words = text.split(" ")
    nr_words = len(words)
    js = json.loads('{"nr_of_words": %s }' % (nr_words))
    # print(json.dumps(js, indent=4))
    print(nr_words)
    
def line_count(text):
    """
    Count number of lines in string
    """
    lines = text.split("\n")        
    lines = list(filter(None, lines)) # Remove empty lines
    nr_lines = len(lines)
    # print("\nTotal lines count: %d" % nr_lines)
    js = json.loads('{"nr_of_lines": %s }' % (nr_lines))
    # print(json.dumps(js, indent=4))
    print(nr_lines)
    
def letter_count(text):
    """
    Count number of letters in string
    """
    nr_letters = len(strip_non_alpa(text))
    # print("\nTotal letter count: %d" % nr_letters)
    js = json.loads('{"nr_of_letters": %s }' % (nr_letters))
    # print(json.dumps(js, indent=4))
    print(nr_letters)


def word_frequency(text):
    """
    Calculate seven most frequent words
    """
    counts = dict()
    text = strip_punctuation(text)
    words = text.split()
    for word in words:
        if word.lower() in counts:
            counts[word.lower()] += 1
        else:
            counts[word.lower()] = 1

    lst = list()
    for key, value in  counts.items():
        lst.append((value, key))
    lst.sort(reverse=True)
    js = {}
    js["most_frequent_words"] = {}
    for key, val in lst[:7]:
        js["most_frequent_words"].update({val: str(key) + " | " + str("{:.1%}".format(key/len(words)))})
        # js += '"'+ val + '": ' + str(key)+ ','
    # print(json.dumps(js, indent=4))
    for key, value in js["most_frequent_words"].items():
        print(f"{key}: {value}")
    # print(js["most_frequent_words"])
    
    # lst = list()
    # for key, value in  counts.items():
    #     lst.append((value, key.lower()))


def nonCommonWords(words):
    """
    Calculate seven most frequent that arnt common
    """
    print("\nSeven most frequent words, that arn't common")
    with open("common-words.txt") as dFile:
        res = list()
        lst = dFile.readlines()
        # lst = [re.sub('[^a-zA-Z]+', '', x) for x in lst]
        lst = [str.rstrip(x) for x in lst]
        lst = [x.lower() for x in lst]
        for word in words:
            if word[1] not in lst:
                res.append(word)
        res.sort(reverse=True)
        for key, val in res[:7]:
            print(str(val) +" : " + str(key))

        #lst = list()
        #for key, value in  res:
        #    lst.append((value, key))
        correctSpelledWords(res)

def correctSpelledWords(words):
    """
    Only show correctly spelled words
    """
    print("\nShows top 7 that arn't common and spelled correct: ")
    with open("words.txt") as dFile:
        res = list()
        lst = dFile.readlines()
        # lst = [re.sub('[^a-zA-Z]+', '', x) for x in lst]
        lst = [str.rstrip(x) for x in lst]
        lst = [x.lower() for x in lst]
        for word in words:
            if word[1] in lst:
                res.append(word)
        res.sort(reverse=True)
        for key, val in res[:7]:
            print(str(val) +" : " + str(key))

def letter_frequency(text):
    """
    Calculate top 7 letter frequenzy of letters in text
    """
    # print("\nTop 7 most frequent letters: ")
    counts = dict()
    letters = strip_non_alpa(text)
    tot_letters = len(letters)
    for letter in letters:
        if letter.lower() in counts:
            counts[letter.lower()] += 1
        else:
            counts[letter.lower()] = 1
    lst = list()
    for key, val in counts.items():
        lst.append((val, key))
    lst.sort(reverse=True)
    # for key, val in lst[:7]:
    #     print(val + " : " + str(key) + " % " + str("{:.1%}".format(key/tot_letters)))

    js = {}
    js["most_frequent_letters"] = {}
    for key, val in lst[:7]:
        js["most_frequent_letters"].update({val: str(key) + " | " + str("{:.1%}".format(key/tot_letters))})
        # js += '"'+ val + '": ' + str(key)+ ','
    # print(json.dumps(js, indent=4))
    for key, value in js["most_frequent_letters"].items():
        print(f"{key}: {value}")
    # print(js["most_frequent_letters"])
    

if __name__ == "__main__":
    analyzeFiles()
