#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Marvin with a simple menu to start up with.
Marvin doesnt do anything, just presents a menu with some choices.
You should add functinoality to Marvin.

"""
import random
import math


def greet():
    """
    Read the users name and say hello to the entity.
    """
    name = input("What is your name? ")
    print("\nThe entity says:\n")
    print("Hello %s - a pleasure to encounter you!" % name)
    print("Know the answere to the magic question 1+1, and i will grant you knowledge if asked!")

def quitIt():
    """
    function for quitting the entity
    """
    print("Bye, bye - and welcome back anytime!")

def invalid():
    """
    function for invalidating the input
    """
    print("That is not a valid choice. You can only choose from the menu.")

def ageCheck():
    """
    transform years to seconds
    """
    years = input("Give me your age... ")
    seconds = int(years) * 52 * 7 * 24 * 60 * 60
    print("You have lived for " + str(seconds) + " seconds")

def moonKGs():
    """
    transforms earth KGs to moon KGs
    """
    eKG = input("Tell me your earthly weight in kilos... ")
    moonKG = float(eKG) * 0.165
    print("You weigh is {0} kilos on the moon!".format(str(moonKG)))

def minToHour():
    """
    transforms minutes to hours
    """
    minutes = input("Enter minutes... ")
    h, m = divmod(int(minutes), 60)
    print("You entered the equivalence of {0} hours and {1} minutes!".format(h, m))

def celcius_to_farenheit():
    """
    converts celcius to farenheit
    """
    celc = input("Tell me the real temperature and i shall return the pretend temperature... ")
    farenheit = round(float(celc)*9/5+32, 2)
    print("The make believe temperature(farenheit) is {0} degrees".format(farenheit))



def word_manipulation():
    """
    prints the word x number of times
    """
    words = input("Bestow on me the word will boost your ego... ")
    times = input("How many times do you want it to boost your ego? ")
    print(multiply_str(words, times))


def randomNumbers():
    """
    Generates random number 10 times between x and n
    """
    minV, maxV = input("Enter a Min and max value... ").split()
    res = ""
    i = 0
    while i < 9:
        i += 1
        res = res + (str(random.randrange(int(minV), int(maxV))) + ", ")
    res = res + (str(random.randrange(int(minV), int(maxV))) + ".")
    print("I give you these generated numbers {0}".format(res))

def sum_and_average():
    """
    generates numbers util stoped
    """
    numbers = 0
    times = 0
    while True:
        inp = input("Feed me a number, or write done... ")
        print(inp)
        try:
            numbers += float(inp)
            times += 1
        except Exception:
            if inp == "done":
                break
    print("Your sum is {0} and the average is {1}".format(numbers, round(numbers/times, 2)))

def points_to_grade(maxP, currP):
    """
    converts points to grades
    """
    grade = ''
    maxP = int(maxP)
    currP = int(currP)

    if currP > maxP:
        grade = 'F, because you failed to type in your points correctly!'
    elif currP >= maxP*0.9:
        grade = 'A'
    elif currP >= maxP*0.8:
        grade = 'B'
    elif currP >= maxP*0.7:
        grade = 'C'
    elif currP >= maxP*0.6:
        grade = 'D'
    else:
        grade = 'F'
    return f"score: {grade}"

def cirArea():
    """
    claculates the area of a circle
    """
    radius = input("Enter the radius of your circle... ")
    area = math.pi * float(radius) * float(radius)
    print("the area is {0}".format(area))

def hypot():
    """
    calculate hypotenuse of a triangle
    """
    v1, v2 = input("What are the length of the other two sides? ").split()
    print("The length of the hypotenuse is {0}".format(str(math.hypot(int(v1), int(v2)))))

def compare_numbers():
    """
    tells comparson of number to previous number
    """
    currNr = 0
    lastNr = None
    while True:
        inp = input("Feed me a number, or write done... ")
        try:
            currNr = int(inp)
            if currNr > lastNr:
                print("{0} is larger! than {1}".format(str(currNr), str(lastNr)))
            elif currNr < lastNr:
                print("{0} is smaller! than {1}".format(str(currNr), str(lastNr)))
            else:
                print("{0} is same! to {1}".format(str(currNr), str(lastNr)))
            lastNr = currNr
        except Exception:
            if inp == "done":
                break
            elif lastNr is None and int(currNr):
                lastNr = currNr
            else:
                print("Thats not a number!")

def hyphen_string():
    """
    For each letter in word repeat it with the number of letter it is in the word.
    """
    word = input("Give me a word: ")
    new = []
    for i, l in enumerate(word):
        new.append(l * (i + 1))
    print("-".join(new))



def is_isogram():
    """
    Check if word is Isogram
    """
    word = input("Give me a word: ")
    for l in word:
        if word.count(l) != 1:
            print("No match!")
            return 0
    print("Match!")

def check_letters():
    """
    Check if all letters from input is in other string
    """
    word = input("Give me a word: ").lower()
    letters = input("Give letters to check for in word: ")
    for l in letters:
        if l not in word:
            print("No match")
            return 0
    print("Match")



def match_brackets():
    """
    count brackets so only one is open at time
    """
    bracks = input("Enter string with brackets")
    b1 = 0
    b2 = 0
    b3 = 0
    for b in bracks:
        if b == "(":
            if b1 > 0:
                print("No match")
                return 0
            else:
                b1 += 1
        elif b == "[":
            if b2 > 0:
                print("No match")
                return 0
            else:
                b2 += 1
        elif b == "{":
            if b3 > 0:
                print("No match")
                return 0
            else:
                b3 += 1
        elif b == ")":
            if b1 != 1:
                print("No match")
                return 0
            else:
                b1 -= 1
        elif b == "]":
            if b2 != 1:
                print("No match")
                return 0
            else:
                b2 -= 1
        elif b == "}":
            if b3 != 1:
                print("No match")
                return 0
            else:
                b3 -= 1
    print("Match")



def check_brack_o(count):
    """
    Help funktion for balance brackets
    """
    if count > 0:
        print("No match")
        return 0
    return 1



def check_brack_c(inp, brack, count):
    """
    Help funktion for balance brackets
    """
    if inp == brack:
        if count != 1:
            print("No match")
            return 0
        else:
            count -= 1
    return 1

def randomize_string(word):
    """
    Randomize strukture of word
    """
    w2 = list(word)
    random.shuffle(w2)
    result = ''.join(w2)
    return f"{word} --> {result}"



def anagram():
    """
    Check if strings are anagram
    """
    word = sorted(input("Enter first word: ").lower())
    word2 = sorted(input("Enter second word: ").lower())

    if word == word2:
        print("Match")
        return 0
    print("No Match")


def get_acronym(word):
    """
    Create acronym
    """
    acr = ""
    for l in word:
        if l.isupper():
            acr += l
    return acr



def mask_string(word):
    """
    mask_string characters in string
    """
    l = len(word)
    return multiply_str("#", l-4) + word[-4:]



def multiply_str(char, times):
    """
    Return multiplied character in string
    """
    return char * times



def has_strings(word, s, c, e):
    """
    Compare a string to 3 other
    """
    if word.startswith(s):
        if word.index(c) > -1:
            if word.endswith(e):
                return "Match"
    return "No match"



def find_all_indexes(inp, search):
    indexes = ""
    length = len(inp)
    pos = 0
    while pos < length:
        try:
            i = inp.index(search, pos)
            indexes += str(i) + ","
            pos = i + 1
        except ValueError:
            return indexes.rstrip(",")
    return indexes.rstrip(",")
