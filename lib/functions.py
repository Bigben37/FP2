#!/usr/bin/python2.7
"""some useful functions which dont fit in any class"""

__author__ = "Benjamin Rottler (benjamin@dierottlers.de)"

from ROOT import gROOT, gStyle
import os

import numpy as np


def loadCSVToList(path, delimiter='\t'):
    """loads data in CSV-file to a list of lists.

    Arguments:
    path      -- relative path to file
    delimiter -- delimiter of file (default='\t')
    """
    if path:
        d = os.getcwd()
        p = os.path.abspath(os.path.join(d, path))
        data = []
        with open(p, 'r') as f:
            for line in f:
                try:
                    data.append(list(map(lambda x: float(x) if x else None, line.strip().split(delimiter))))  # remove \n, split by delimiter, convert to float
                except ValueError:
                    print('Warning: Could not convert %s' % line)
        return data


def avgerrors(values, errors):
    """calculates weighted average with error

    Arguments:
    values -- list of values
    errors -- list of errors
    """
    var = 1. / sum(map(lambda e: 1. / (e ** 2), errors))
    avg = sum(map(lambda v, e: v / (e ** 2), values, errors)) * var
    return avg, np.sqrt(var)

def setupROOT():
    """sets up ROOT """
    gROOT.Reset()
    gROOT.SetStyle('Plain')
    gStyle.SetPadTickY(1)
    gStyle.SetPadTickX(1)