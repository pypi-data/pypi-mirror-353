#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Marvin with a simple menu to start up with.
Marvin doesnt do anything, just presents a menu with some choices.
You should add functinoality to Marvin.

"""

from marvin import *

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
    print(meImage())
    print("Hi, I'm the entity. I know it all. What can I do you for?")
    print("1) Present yourself to the entity.")
    print("2) Celcius to farenheit")
    print("3) Lets play parrot! You say it, ill repeat it.")
    print("4) Sure i can do your math for you!")
    print("5) Repeat letters in word")
    print("6) Isogram")
    print("7) Is smaller, bigger or equal.")
    print("8) Shuffle a word.")
    print("9) Create acronym.")
    print("10) Mask characters.")
    print("11) Find indexes.")
    print("A1) Check if all letters in a word.")
    print("A2) Match brackets.")
    print("b1) Grade converter.")
    print("b2) Check word contains.")
    print("q) quit.")



def main():
    """
    This is the main method, I call it main by convention.
    Its an eternal loop, until q is pressed.
    It should check the choice done by the user and call a appropriate
    function.
    """
    while True:
        menu()
        choice = input("--> ")

        if choice == "q":
            quitIt()
            return

        elif choice == "1":
            greet()

        elif choice == "2":
            celcius_to_farenheit()

        elif choice == "3":
            word_manipulation()

        elif choice == "4":
            sum_and_average()

        elif choice == "5":
            hyphen_string()

        elif choice == "6":
            is_isogram()

        elif choice == "7":
            compare_numbers()

        elif choice == "A1":
            check_letters()

        elif choice == "A2":
            match_brackets()

        elif choice == "8":
            word = input("Enter word you want me to randomize... ")
            print(randomize_string(word))

        elif choice == "9":
            word = input("Enter word: ")
            print(get_acronym(word))

        elif choice == "10":
            word = input("Enter string: ")
            print(mask_string(word))

        elif choice == "11":
            string = input("Enter string to search in: ")
            search = input("Enter string to search for: ")
            print(find_all_indexes(string, search))

        elif choice == "b1":
            maxP = input("Enter the max point")
            currP = input("Enter your points... ")

            print("You will recieve the grade of...... {0}".format(points_to_grade(maxP, currP)))

        elif choice == "b2":
            word = input("Enter comparing word: ")
            s = input("Enter word to check start: ")
            c = input("Enter word to check contains: ")
            e = input("Enter word to check ends: ")
            print(has_strings(word, s, c, e))

        else:
            invalid()

        input("\nThe knowledge has been granted. Now go bother someone else...")



if __name__ == "__main__":
    main()
