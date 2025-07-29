#!/usr/bin/env python3
"""
Write your code in this file. Fill out the defined functions with your solutions.
You are free to write additional functions and modules as you see fit.
"""
import analyze_functions
from operator import itemgetter

def analyze_text():
    """
    Assignment 1
    """
    choice = input("Enter what to do: ")
    with open("title.basics.csv") as fd:
        data = fd.read().split("\n")[1:]
    if choice == "year":
        analyze_functions.year(data)
    elif choice == "title":
        for row in data:
            cells = row.split(",")

            if cells[1] != cells[2]:
                print(cells[1], end=":")
                analyze_functions.get_with_key(cells[0], 1)
    else:
        print("Not an option!")

def reversed_sum(numbers, operator):
    """
    Assignment 2
    """
    l = len(numbers)
    count = 0
    while count < l:
        numbers[count] = int(str(numbers[count])[::-1])
        count +=2

    if operator == "+":
        sum_ = 0
        for n in numbers:
            sum_ += n
    elif operator == "-":
        sum_ = numbers[0]
        for n in numbers[1:]:
            sum_ -= n
    return sum_



def repeating_letter_distance(string):
    """
    Assignment 3
    """
    counter = {}
    for ind, char in enumerate(string):
        count = ind+1
        while count < len(string):
            if char == string[count]:
                length = count-ind
                if char not in counter:
                    counter[char] = length
                else:
                    if length < counter[char]:
                        counter[char] = length
            count += 1
    return counter



def find_word(line, n, option=None):
    """
    Assignment 3
    """
    no_want = ".,-?!\t\n-;'/"
    for char in no_want:
        line = line.replace(char, " ")
    words = line.split(" ")
        
    found = []
    for word in words:
        if len(word) == n:
            found.append(word)
    
    if option is None:
        return found[0]
    elif isinstance(option, int):
        return found[option-1]
    else:
        for word in found:
            if word.startswith(option):
                return word



def frequency_sort(sequence):
    """
    Assignment 3
    """
    counter = {}
    for ele in sequence:
        counter[ele] = counter.get(ele, 0) + 1
    new_l = []
    for key, v in sorted(counter.items(), key=itemgetter(1), reverse=True):
        l = []
        for _ in range(v):
            l.append(key)
        new_l.extend(l)
    return new_l



if __name__ == '__main__':
    # analyze_text()
    # reversed_sum()
    # frequency_sort()
    # find_word()
    # repeating_letter_distance()
    pass