#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main file for the marvin bot
"""
import analyzer

TEXT = ""

def meImage():
    """
    Store my ascii image in a separat variabel as a raw string
    """
    return r"""
                    Θ
                   ╞|╡
                   ╞|╡
                Θ==[Φ]==Θ
                   |||
                   |||
                   |||
                   |||
                   |||
                   \|/

         _.--~~.--._ _.--~~.--._
        |-.~_--.~.._╪-.~_--.~..~|
        |..--~~--..~╪..--~~--..-|
        |.-~~~.-.--\|/.-~~~.-.~-|
        └=========\\|//=========┘
    """

def menu():
    """
    Display the menu with the options that the entity can do.
    """
    print(chr(27) + "[2J" + chr(27) + "[;H")
    # print(meImage())
    # print("Hi, I'm the entity. I know it all. What can I do you for?")
    # print("1) Present yourself to the entity.")
    # print("2) Grant me the knowledge of you age and i shall grant you the " \
    #       "knowledge of your time!. (Obviously in seconds!)")
    # print("3) Want to dwell on your weight on the moon?")
    # print("4) Enter minutes receive hours AND minutes. See I can be generous!")
    # print("5) Want to know how cold you would be in USA?")
    # print("6) Lets play parrot! You say it, ill repeat it.")
    # print("7) Lets play a game! You say min and max, ill tell you ten numbers between.")
    # print("8) Sure i can do your math for you!")
    # print("9) I know your grades!")
    # print("10) Calculate area of circle!")
    # print("11) Calculate hypotenuse of a triangle.")
    # print("12) Is smaller, bigger or equal.")
    # print("13) Guess the number!")
    # print("14) Print date, time and other info.")
    # print("15) Shuffle a word.")
    # print("16) Guess a shuffled word.")
    # print("17) Words words words in files")
    # print("18) Play tic-tac-toe with the Entity!")
    # print("19) Encrypth with ROT13")
    # print("20) Encrypt with Ceasar")
    # print("21) Decrypt a Ceasar cipher")
    print(
            "lines) Count lines",
            "words) Count words",
            "letters) Count letters",
            "word_frequency) Find 7 most used words",
            "letter_frequency) Find 7 most used letters",
            "all) Do everything",
            "change) Change file",
            "q) quit.", sep="\n")

if __name__ == "__main__":
    main()