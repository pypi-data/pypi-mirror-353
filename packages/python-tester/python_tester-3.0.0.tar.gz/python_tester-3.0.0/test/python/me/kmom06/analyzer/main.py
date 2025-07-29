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

def read_file(file_path):
    """
    Read all text in from file
    """
    global TEXT
    with open(file_path) as file_object:
        TEXT = file_object.read()

def main():
    """
    This is the main method, I call it main by convention.
    Its an eternal loop, until q is pressed.
    It should check the choice done by the user and call a appropriate
    function.
    """
    filen = "phil.txt"
    while True:
        menu()
        read_file(filen)
        command = input("--> ")
        if command == "lines":
            analyzer.line_count(TEXT)
        elif command == "change":
            filen = input("Enter filename: ")

        elif command == "words":
            analyzer.word_count(TEXT)

        elif command == "letters":
            analyzer.letter_count(TEXT)

        elif command == "word_frequency":
            analyzer.word_frequency(TEXT)
        
        elif command == "letter_frequency":
            analyzer.letter_frequency(TEXT)

        elif command == "all":
            analyzer.analyze_all(TEXT)
        if command == "q":
            # marvin.quitIt()
            return
        # input("Enter to continue...")
        input("\nThe knowledge has been granted. Now go bother someone else...")
        
        continue


        if choice == "1":
            marvin.myNameIs()

        elif choice == "2":
            marvin.ageCheck()

        elif choice == "3":
            marvin.moonKGs()

        elif choice == "4":
            marvin.minToHour()

        elif choice == "5":
            marvin.celToFar()

        elif choice == "6":
            marvin.wordMultiplier()

        elif choice == "7":
            marvin.randomNumbers()

        elif choice == "8":
            marvin.sumMed()

        elif choice == "9":
            marvin.gradesConv()

        elif choice == "10":
            marvin.cirArea()

        elif choice == "11":
            marvin.hypot()

        elif choice == "12":
            marvin.nextNr()

        elif choice == "13":
            marvin.guessNumber()

        elif choice == "14":
            marvin.stringPrinter()

        elif choice == "15":
            marvin.randomWord()

        elif choice == "16":
            marvin.guessWord()

        elif "citat" in choice:
            marvin.quote()

        elif "hej" in choice:
            marvin.hello()

        elif "lunch" in choice:
            marvin.lunch()

        elif choice == "inv":
            marvin.showInv()

        elif "inv pick " in choice:
            marvin.pickUp(choice.split()[2])

        elif "inv drop " in choice:
            marvin.drop(choice.split()[2])

        elif choice == "17":
            marvin.analyzeFiles()

        elif choice == "18":
            matrix.main()

        elif choice == "19":
            marvin.rot13()

        elif choice == "20":
            marvin.ceasarEnc()

        elif choice == "21":
            marvin.ceasarDec()

        else:
            marvin.invalid()

        input("\nThe knowledge has been granted. Now go bother someone else...")

if __name__ == "__main__":
    main()

