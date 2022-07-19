#!/usr/bin/env python3

'''                                                
 ╭―――――――――――――――――――――――――――――――――――――――――――――――――
 │ Countdown_Solver_CLI_Edition.py 
 │ Author: Eric Errickson -- 18 July 2022 05:14
 │ Brute forcing the Countdown Numbers Game in Python.
 ╰―――――――――――――――――――――――――――――――――――――――――――――――――
'''                                                

# imports
import sys
from itertools import combinations, product, zip_longest
from functools import lru_cache
import PySimpleGUI as sg

assert sys.version_info >= (3, 6)


# set the theme for the main window
sg.theme('LightBlue2')

# set the layout for the window
layout = [
    [sg.Text("Eric's Countdown Numbers Game Solver", text_color='midnightblue', font='arial 16')],
    [sg.Text(" ")],
    [sg.Text('Please enter the Target Number and Chosen Numbers.', text_color='mediumblue', font='arial 14')],
    [sg.Text(" ")],
    [sg.Text('Target Number:  ', text_color='darkblue', font='arial 12', size =(20, 2)), sg.InputText()], # saves this input as values[0]
    [sg.Text('Chosen Number One:  ', text_color='darkblue', font='arial 12', size =(20, 1)), sg.InputText()],  # saves this input as values[1]
    [sg.Text('Chosen Number Two:  ', text_color='darkblue', font='arial 12', size =(20, 1)), sg.InputText()],# and saves this input as values[2] et c.
    [sg.Text('Chosen Number Three:  ', text_color='darkblue', font='arial 12', size =(20, 1)), sg.InputText()],
    [sg.Text('Chosen Number Four:  ', text_color='darkblue', font='arial 12', size =(20, 1)), sg.InputText()],
    [sg.Text('Chosen Number Five:  ', text_color='darkblue', font='arial 12', size =(20, 1)), sg.InputText()],
    [sg.Text('Chosen Number Six:  ', text_color='darkblue', font='arial 12', size =(20, 1)), sg.InputText()],
    [sg.Text(" ")],
    [sg.Button("Let's Countdown!"), sg.Button("Exit")],
    ]

window = sg.Window("Eric's Countdown Solver", layout, use_custom_titlebar=True, grab_anywhere=True, titlebar_background_color='#8790a7')

while True:
    event, values = window.read()
    if event == "Let's Countdown!" or event == "Exit" or event == sg.WIN_CLOSED:
        break

# window.close()


class Solutions:

    def __init__(self, numbers):
        self.all_numbers = numbers
        self.size = len(numbers)
        self.all_groups = self.unique_groups()

    def unique_groups(self):
        all_groups = {}
        all_numbers, size = self.all_numbers, self.size
        for m in range(1, size+1):
            for numbers in combinations(all_numbers, m):
                if numbers in all_groups:
                    continue
                all_groups[numbers] = Group(numbers, all_groups)
        return all_groups

    def walk(self):
        for group in self.all_groups.values():
            yield from group.calculations


class Group:

    def __init__(self, numbers, all_groups):
        self.numbers = numbers
        self.size = len(numbers)
        self.partitions = list(self.partition_into_unique_pairs(all_groups))
        self.calculations = list(self.perform_calculations())

    def __repr__(self):
        return str(self.numbers)

    def partition_into_unique_pairs(self, all_groups):
        # The pairs are unordered: a pair (a, b) is equivalent to (b, a).
        # Therefore, for pairs of equal length only half of all combinations
        # need to be generated to obtain all pairs; this is set by the limit.
        if self.size == 1:
            return
        numbers, size = self.numbers, self.size
        limits = (self.halfbinom(size, size//2), )
        unique_numbers = set()
        for m, limit in zip_longest(range((size+1)//2, size), limits):
            for numbers1, numbers2 in self.paired_combinations(numbers, m, limit):
                if numbers1 in unique_numbers:
                    continue
                unique_numbers.add(numbers1)
                group1, group2 = all_groups[numbers1], all_groups[numbers2]
                yield (group1, group2)

    def perform_calculations(self):
        if self.size == 1:
            yield Calculation.singleton(self.numbers[0])
            return
        for group1, group2 in self.partitions:
            for calc1, calc2 in product(group1.calculations, group2.calculations):
                yield from Calculation.generate(calc1, calc2)

    @classmethod
    def paired_combinations(cls, numbers, m, limit):
        for cnt, numbers1 in enumerate(combinations(numbers, m), 1):
            numbers2 = tuple(cls.filtering(numbers, numbers1))
            yield (numbers1, numbers2)
            if cnt == limit:
                return

    @staticmethod
    def filtering(iterable, elements):
        # filter elements out of an iterable, return the remaining elements
        elems = iter(elements)
        k = next(elems, None)
        for n in iterable:
            if n == k:
                k = next(elems, None)
            else:
                yield n

    @staticmethod
    @lru_cache()
    def halfbinom(n, k):
        if n % 2 == 1:
            return None
        prod = 1
        for m, l in zip(reversed(range(n+1-k, n+1)), range(1, k+1)):
            prod = (prod*m)//l
        return prod//2


class Calculation:

    def __init__(self, expression, result, is_singleton=False):
        self.expr = expression
        self.result = result
        self.is_singleton = is_singleton

    def __repr__(self):
        return self.expr

    @classmethod
    def singleton(cls, n):
        return cls(f"{n}", n, is_singleton=True)

    @classmethod
    def generate(cls, calca, calcb):
        if calca.result < calcb.result:
            calca, calcb = calcb, calca
        for result, op in cls.operations(calca.result, calcb.result):
            expr1 = f"{calca.expr}" if calca.is_singleton else f"({calca.expr})"
            expr2 = f"{calcb.expr}" if calcb.is_singleton else f"({calcb.expr})"
            yield cls(f"{expr1} {op} {expr2}", result)

    @staticmethod
    def operations(x, y):
        yield (x + y, '+')
        if x > y:                     # exclude non-positive results
            yield (x - y, '-')
        if y > 1 and x > 1:           # exclude trivial results
            yield (x * y, 'x')
        if y > 1 and x % y == 0:      # exclude trivial and non-integer results
            yield (x // y, '/')


def countdown_solver():
    # input: target and numbers. If you want to play with more or less than
    # 6 numbers, use the second version of 'unsorted_numbers'.
    try:
        target = int(values[0])
        unsorted_numbers = (int(sys.argv[n+2]) for n in range(6))  # for 6 numbers
#        unsorted_numbers = (int(n) for n in sys.argv[2:])         # for any numbers
        # numbers = tuple(sorted(unsorted_numbers, reverse=True))
        # numbers = [int(x) for x in input("Numbers: ").split()]
        numbers = [int(values[1]), int(values[2]), int(values[3]), int(values[4]), int(values[5]), int(values[6]), ]
    except (IndexError, ValueError):
        print("You must provide a target and numbers!")
        return

    solutions = Solutions(numbers)
    smallest_difference = target
    bestresults = []
    for calculation in solutions.walk():
        diff = abs(calculation.result - target)
        if diff <= smallest_difference:
            if diff < smallest_difference:
                bestresults = [calculation]
                smallest_difference = diff
            else:
                bestresults.append(calculation)
    output(target, smallest_difference, bestresults)


def output(target, diff, results):
    print(f"\nThe closest results differ from {target} by {diff}. They are:\n")
    for calculation in results:
        print(f"{calculation.result} = {calculation.expr}")
        sg.popup('Yes, it can be done:\n\n'+ calculation.expr+'\n\n Press OK for the next solution.')


if __name__ == "__main__":
    countdown_solver()