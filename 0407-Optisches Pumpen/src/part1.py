#!/usr/bin/python

__author__ = "Benjamin Rottler (benjamin@dierottlers.de)"

from functions import setupROOT
import os
from evalEtalon import evalEtalonData


def main():
    for file in os.listdir(os.path.join(os.getcwd(), '../data/part1/')):
        if file.endswith('.tab'):
            evalEtalonData(1, file)

if __name__ == '__main__':
    setupROOT()
    main()
