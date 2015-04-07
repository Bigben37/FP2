#!/usr/bin/python2.7
"""Basic writing to encoded text files"""

__author__ = "Benjamin Rottler (benjamin@dierottlers.de)"

import os
import codecs  # paths, encoded text files


class TxtFile(object):

    """Basic writing to encoded text files"""

    PM = chr(0x00B1)                      # plus/minus
    CHI = chr(0x03C7)
    SQUARE = chr(0x00B2)
    CHISQUARE = chr(0x03C7) + chr(0x00B2)

    def __init__(self, path, mode, enc='utf-8'):
        """Constructor, opens file

        Arguments:
        path -- absolute path to file
        mode -- write mode (usually 'w' for overwriting or 'a' for appending)
        enc  -- encoding (default = 'utf-8')
        """
        # if file/directory does not exist create dirs and file
        if not os.path.exists(path):
            if not os.path.exists(os.path.dirname(path)):
                os.mkdir(os.path.dirname(path))
            codecs.open(path, 'a', enc).close()
        # open file with actual mode
        self._file = codecs.open(path, mode, enc)

    @classmethod
    def fromRelPath(cls, path, mode, enc='utf-8'):
        """Creates a new instance of TxtFile from a relative path

        Arguments:
        path -- relative path to file
        mode -- write mode (usually 'w' for overwriting or 'a' for appending)
        enc  -- encoding (default = 'utf-8')
        """
        d = os.getcwd()
        p = os.path.abspath(os.path.join(d, path))
        return cls(p, mode, enc)

    def getFile(self):
        """returns handle to file"""
        return self._file

    def write(self, text):
        """writes text to file

        Arguments:
        text -- text to write
        """
        self._file.write(text)

    def writeline(self, text='', *args):
        """writes text and finishes line with a linebreak. 
        If more than one argument is given, joins 2nd to last argument with first one and finishes line with a linebreak

        Arguments:
        text  -- text to write or text, which is used to join other arguments
        *args -- additional arguments, which are joined by first one
        """
        if not args:
            self._file.write(text + '\n')
        else:
            self._file.write(text.join(args) + '\n')

    def writelines(self, lines):
        """writes multiple lines

        Arguments:
        lines -- a list of lines to write
        """
        self._file.writelines(lines)
        
    def write2DArrayToLatexTable(self, data, thead, format, caption, label):
        """writes an 2d-array (list of lists) to an formatted latex table
        
        Arguments:
        data    -- 2darray, list of rows, each row is a list of data
        thead    -- list of descriptions for columns, is used as first row
        format   -- list of formatting rules, how to convert numbers into strings
        caption  -- caption of table in latex
        label    -- label of table in latex
        """
        if len(thead) == len(format):
            l = len(thead)
            i = '  '  # indentation
            self.writeline(r'\begin{table}[H]')
            self.writeline(r'\caption{%s}' % caption)
            self.writeline(r'\begin{center}')
            self.writeline(r'\begin{tabular}{' + '|c' * l + '|}')
            self.writeline(i + r'\hline')
            self.writeline(i + ' & '.join(thead) + r' \\ \hline')
            for row in data:
                self.writeline(i + ' & '.join(format) % tuple(row) + r' \\ \hline')
            self.writeline('\\end{tabular}')
            self.writeline('\\end{center}')
            self.writeline('\\label{' + label + '}')
            self.writeline('\\end{table}')
        else:
            print("WARNING[TxtFile.write2DArrayToLatexTable]: lists have to be the same length.")

    def close(self):
        """closes file"""
        self._file.close()

    def __enter__(self):
        """if entering with-statement, returns instance"""
        return self

    def __exit__(self, type, value, traceback):
        """if exiting with-statement, close file"""
        self.close()
