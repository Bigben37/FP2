#!/usr/bin/python2.7
"""The Data and DataErros class encapsulate a list of experimental data and is used as a link between python and the ROOT library. 
If you want to use them properly, you need to derive the class you need and add the function loadData(), in which u specify how the data 
from the given path is loaded.
"""

__author__ = "Benjamin Rottler (benjamin@dierottlers.de)"

import numpy as np  # Numpy
from ROOT import TGraph, TGraphErrors  # ROOT library  #@UnresolvedImport
import array  # C-like arrays (for ROOT library)
from txtfile import TxtFile  # basic output to txt files, can be found the /lib directory


class GeneralData(object):

    """Generl data class, is used as super class for Data and DataErrors"""

    def __init__(self):
        """Constructor, sets empty list for field _points. 
        Usually, you dont want to use this, instead use Data.fromPath() or Data.fromLists()
        """
        self.path = ''
        self._points = []

    def getPoints(self):
        """points stores the values in a list, i.e points = [p1, p2, p3, ...]"""
        return self._points

    def setPoints(self, points):
        self._points = points

    points = property(getPoints, setPoints)

    def getPoint(self, i):
        """ Returns the i-th point of points

        Arguments:
        i -- index of the point, which will be returned
        """
        if i < len(self._points):
            return self._points[i]
        else:
            return None

    def getLength(self):
        """returns the number of points in the list"""
        return len(self._points)

    def getByX(self, xvalue):
        """get point by x-value

        Arguments:
        xvalue -- x-value of point
        """
        for point in self.points:
            if point[0] == xvalue:
                return point
        return None

    def getByY(self, yvalue):
        """get point by y-value

        Arguments:
        yvalue -- y-value of point
        """
        for point in self.points:
            if point[1] == yvalue:
                return point
        return None

    def getX(self):
        """returns all x-values in a list"""
        return list(zip(*self._points))[0]

    def getY(self):
        """returns all y-values in a list"""
        return list(zip(*self._points))[1]

    def getMinX(self):
        """returns lowest x-value"""
        return min(self.getX())

    def getMaxX(self):
        """returns highest x-value"""
        return max(self.getX())

    def getMinY(self):
        """returns lowest y-value"""
        return min(self.getY())

    def getMaxY(self):
        """returns highest y-value"""
        return max(self.getY())

    @classmethod
    def fromPath(cls, path):
        """Creates a new instance of Data from a given file. Make sure to implement your loadData() function, so that the class knows how to 
        load the file

        Arguments:
        path -- relative path to file
        """
        data = cls()
        data.path = path
        if path:
            try:
                data.loadData()
            except NameError:
                print(data.__class__.__name__ + ".loadData() not in scope! Please implement. ")
        return data

    def filterX(self, lower=None, upper=None):
        """deletes all values with are lower then the lower bound or higher than the higher bound

        Arguments:
        lower -- lower bound
        higher -- higher bound
        """
        marks = []
        for i, point in enumerate(self.points):
            if not lower is None:
                if point[0] < lower:
                    marks.append(i)
            if not upper is None:
                if point[0] > upper:
                    marks.append(i)
        for mark in reversed(marks):
            del self._points[mark]

    def filterY(self, lower=None, upper=None):
        """deletes all values with are lower then the lower bound or higher than the higher bound

        Arguments:
        lower -- lower bound
        higher -- higher bound
        """
        marks = []
        for i, point in enumerate(self.points):
            if not lower is None:
                if point[1] < lower:
                    marks.append(i)
            if not upper is None:
                if point[1] > upper:
                    marks.append(i)
        for mark in reversed(marks):
            del self._points[mark]


class Data(GeneralData):

    """Data class for x-y values (without errors)"""

    def __init__(self):
        """Constructor, sets empty list for field _points. 
        Usually, you dont want to use this, instead use Data.fromPath() or Data.fromLists()
        """
        super(Data, self).__init__()

    def addPoint(self, x, y):
        """adds the point [x, y] to the list of points

        Arguments:
        x -- x value of point
        y -- y value of point
        """
        self._points.append((x, y))

    def setXY(self, xlist, ylist):
        """sets points from two given lists, one for x-values and one for y-values

        Arguments:
        xlist -- list for x values
        ylist -- list for y values
        """
        if len(xlist) == len(ylist):
            self._points = list(zip(xlist, ylist))
        else:
            print('Data.setXY(x, ypyth):ERROR - lists have to be the same length')

    @classmethod
    def fromLists(cls, x, y):
        """Creates a new instance of Data from two given lists, one for x-values and one for y-values

        Arguments:
        xlist -- list for x values
        ylist -- list for y values
        """
        if len(x) == len(y):
            data = cls()
            data.setXY(x, y)
            return data
        else:
            print('Data.fromLists(x, y):ERROR - lists have to be the same length')
            return None

    def makeGraph(self, name='', xtitle='', ytitle=''):
        """This function returns an instance of ROOTs TGraph, made with the points in from this class.
        Some of the graph's default settings are changed:
          - black points
          - every point has the symbol of 'x'
          - x- and y-axis are centered

        Arguments:
        name   -- ROOT internal name of graph (default = '')
        xtitle -- title of x-axis (default = '')
        ytitle -- title of y-axis (default = '')
        """
        x = self.getX()
        y = self.getY()
        graph = TGraph(self.getLength(), array.array('f', x), array.array('f', y))
        graph.SetName(name)
        graph.SetMarkerColor(1)
        graph.SetMarkerStyle(5)
        graph.SetTitle("")
        graph.GetXaxis().SetTitle(xtitle)
        graph.GetXaxis().CenterTitle()
        graph.GetYaxis().SetTitle(ytitle)
        graph.GetYaxis().CenterTitle()
        return graph

    def saveDataToLaTeX(self, thead, format, caption, label, path, mode, encoding='utf-8'):
        """prints all points formatted into an latex file and saves it.

        Arguments:
        thead    -- list of descriptions for columns, is used as first row
        format   -- list of formatting rules, how to convert numbers into strings
        caption  -- caption of table in latex
        label    -- label of table in latex
        path     -- relative path to file in which the data is saved to
        mode     -- write mode (usually 'w' for overwriting or 'a' for appending)
        encoding -- file encoding (default = 'utf-8')        
        """
        i = '  '  # intendation
        with TxtFile(path, mode, encoding) as f:
            f.writeline('\\begin{table}[H]')
            f.writeline('\\caption{' + caption + '}')
            f.writeline('\\begin{center}')
            f.writeline('\\begin{tabular}{' + '|c' * len(self.points[0]) + '|}')
            f.writeline(i + '\hline')
            f.writeline(i + ' & '.join(thead) + ' \\\\ \hline ')
            for point in self.points:
                f.writeline(i + ' & '.join(format) % (point[0], point[1]) + ' \\\\ \hline')
            f.writeline('\\end{tabular}')
            f.writeline('\\end{center}')
            f.writeline('\\label{' + label + '}')
            f.writeline('\\end{table}')

    def multiplyX(self, mult):
        """multiply x-value with constant

        Arguments:
        mult -- multiplier
        """
        for i in range(self.getLength()):
            self.points[i] = (mult * self.points[i][0], self.points[i][1])

    def multiplyY(self, mult):
        """multiply y-value with constant

        Arguments:
        mult -- multiplier
        """
        for i in range(self.getLength()):
            self.points[i] = (self.points[i][0], mult * self.points[i][1])

    def __add__(self, other):
        """addition operator for two instances, adds y-values, while not changing the x-values"""
        if isinstance(other, Data):
            if self.getLength() == other.getLength():
                y = []
                ys = self.getY()
                yo = other.getY()
                for i in range(self.getLength()):
                    y.append(ys[i] + yo[i])
                return Data.fromLists(self.getX(), y)
            else:
                return NotImplemented
        else:
            return NotImplemented

    def __sub__(self, other):
        """subtraction operator for two instances, subtracts y-values, while not changing the x-values"""
        if isinstance(other, Data):
            if self.getLength() == other.getLength():
                y = []
                ys = self.getY()
                yo = other.getY()
                for i in range(self.getLength()):
                    y.append(ys[i] - yo[i])
                return Data.fromLists(self.getX(), y)
            else:
                return NotImplemented
        else:
            return NotImplemented


class DataErrors(GeneralData):

    """Data class for x-y values with errors for x and y"""

    def __init__(self):
        """Constructor, sets empty list for field _points. 
        Usually, you dont want to use this, instead use Data.fromPath() or Data.fromLists()
        """
        super(DataErrors, self).__init__()

    def getEX(self):
        """returns all x-error-values in a list"""
        return list(zip(*self._points))[2]

    def getEY(self):
        """returns all y-error-values in a list"""
        return list(zip(*self._points))[3]

    def addPoint(self, x, y, ex, ey):
        """adds the point [x, y, ex, ey] to the list of points

        Arguments:
        x  -- x value of point
        y  -- y value of point
        ex -- x error of point
        ey -- y error of point
        """
        self._points.append((x, y, ex, ey))

    def setXY(self, xlist, ylist, exlist, eylist):
        """sets points from two given lists, one for x-values and one for y-values

        Arguments:
        xlist  -- list for x values
        ylist  -- list for y values
        exlist -- list for x error values
        eylist -- list for y error values
        """
        if len(xlist) == len(ylist) == len(exlist) == len(eylist):
            self._points = list(zip(xlist, ylist, exlist, eylist))
        else:
            print('Data.setXY(x, y, ex, ey):ERROR - lists have to be the same length')

    @classmethod
    def fromLists(cls, x, y, ex, ey):
        """Creates a new instance of Data from two given lists, one for x-values and one for y-values

        Arguments:
        xlist -- list for x values
        ylist -- list for y values
        """
        if len(x) == len(y) == len(ex) == len(ey):
            data = cls()
            data.setXY(x, y, ex, ey)
            return data
        else:
            print('DataErrors.fromLists():ERROR - lists have to be the same length')
            return None

    def makeGraph(self, name='', xtitle='', ytitle=''):
        """This function returns an instance of ROOTs TGraphErrors, made with the points in from this class.
        Some of the graph's default settings are changed:
          - black points
          - every point has the symbol of 'x'
          - x- and y-axis are centered

        Arguments:
        name   -- ROOT internal name of graph (default = '')
        xtitle -- title of x-axis (default = '')
        ytitle -- title of y-axis (default = '')
        """
        if self.points:
            x = self.getX()
            y = self.getY()
            ex = self.getEX()
            ey = self.getEY()
            graph = TGraphErrors(self.getLength(), array.array('f', x), array.array('f', y), array.array('f', ex), array.array('f', ey))
            graph.SetName(name)
            graph.SetMarkerColor(1)
            graph.SetMarkerStyle(5)
            graph.SetTitle("")
            graph.GetXaxis().SetTitle(xtitle)
            graph.GetXaxis().CenterTitle()
            graph.GetYaxis().SetTitle(ytitle)
            graph.GetYaxis().CenterTitle()
            return graph
        else:
            return None

    def invertX(self):
        """inverses x values"""
        for i in range(self.getLength()):
            self.points[i] = (1. / self.points[i][0], self.points[i][1], 1. / (self.points[i][0] ** 2) * self.points[i][2], self.points[i][3])

    def invertY(self):
        """inverses y values"""
        for i in range(self.getLength()):
            self.points[i] = (self.points[i][0], 1. / self.points[i][1], self.points[i][2], 1. / (self.points[i][1] ** 2) * self.points[i][3])

    def multiplyX(self, mult):
        """multiply x-value with constant

        Arguments:
        mult -- multiplier
        """
        for i in range(self.getLength()):
            self.points[i] = (mult * self.points[i][0], self.points[i][1], mult * self.points[i][2], self.points[i][3])

    def multiplyY(self, mult):
        """multiply y-value with constant

        Arguments:
        mult -- multiplier
        """
        for i in range(self.getLength()):
            self.points[i] = (self.points[i][0], mult * self.points[i][1], self.points[i][2], mult * self.points[i][3])

    def setXErrorAbs(self, error):
        """sets absolute x-error, same error for every data point

        Arguments:
        error -- absolute error
        """
        for i in range(self.getLength()):
            self.points[i] = (self.points[i][0], self.points[i][1], error, self.points[i][3])

    def setXErrorRel(self, relerror):
        """sets relative x-error, the absolute error is calculated with x-value * relative error

        Arguments:
        relerror -- relative error
        """
        for i in range(self.getLength()):
            self.points[i] = (self.points[i][0], self.points[i][1], abs(self.points[i][0] * relerror), self.points[i][3])

    def setXErrorFunc(self, f):
        """calculates x-error with given function from x-value

        Arguments:
        f -- error function
        """
        for i in range(self.getLength()):
            self.points[i] = (self.points[i][0], self.points[i][1], f(self.points[i][0]), self.points[i][3])

    def setYErrorAbs(self, error):
        """sets absolute y-error, same error for every data point

        Arguments:
        error -- absolute error
        """
        for i in range(self.getLength()):
            self.points[i] = (self.points[i][0], self.points[i][1], self.points[i][2], error)

    def setYErrorRel(self, relerror):
        """sets relative y-error, the absolute error is calculated with y-value * relative error

        Arguments:
        relerror -- relative error
        """
        for i in range(self.getLength()):
            self.points[i] = (self.points[i][0], self.points[i][1], self.points[i][2], abs(self.points[i][1] * relerror))

    def setYErrorFunc(self, f):
        """calculates y-error with given function from y-value

        Arguments:
        f -- error function
        """
        for i in range(self.getLength()):
            self.points[i] = (self.points[i][0], self.points[i][1], self.points[i][2], f(self.points[i][1]))

    def saveDataToLaTeX(self, thead, format, caption, label, path, mode, encoding='utf-8'):
        """prints all points formatted into an latex file and saves it.

        Arguments:
        thead    -- list of descriptions for columns, is used as first row
        format   -- list of formatting rules, how to convert numbers into strings
        caption  -- caption of table in latex
        label    -- label of table in latex
        path     -- relative path to file in which the data is saved to
        mode     -- write mode (usually 'w' for overwriting or 'a' for appending)
        encoding -- file encoding (default = 'utf-8')        
        """
        i = '  '  # intendation
        with TxtFile(path, mode, encoding) as f:
            f.writeline('\\begin{table}[H]')
            f.writeline('\\caption{' + caption + '}')
            f.writeline('\\begin{center}')
            f.writeline('\\begin{tabular}{' + '|c' * len(self.points[0]) + '|}')
            f.writeline(i + '\hline')
            f.writeline(i + ' & '.join(thead) + ' \\\\ \hline ')
            for point in self.points:
                f.writeline(i + ' & '.join(format) % (point[0], point[2], point[1], point[3]) + ' \\\\ \hline')
            f.writeline('\\end{tabular}')
            f.writeline('\\end{center}')
            f.writeline('\\label{' + label + '}')
            f.writeline('\\end{table}')

    def __add__(self, other):
        """addition operator for two instances, adds y-values, while not changing the x-values.
        The error of y values is calculated by the propagation of error:
        yerror = sqrt(y1error^2 + y2error^2)
        The error of x values is set to 0
        """
        if isinstance(other, DataErrors):
            if self.getLength() == other.getLength():
                y = []
                yerror = []
                ys = self.getY()
                yse = self.getEY()
                yo = other.getY()
                yoe = other.getEY()
                for i in range(self.getLength()):
                    y.append(ys[i] + yo[i])
                    yerror.append(np.sqrt((yse[i]) ** 2 + (yoe[i]) ** 2))
                return DataErrors.fromLists(self.getX(), y, [0] * self.getLength(), yerror)
            else:
                return NotImplemented
        else:
            return NotImplemented

    def __sub__(self, other):
        """subtraction operator for two instances, subtracts y-values, while not changing the x-values.
        The error of y values is calculated by the propagation of error:
        yerror = sqrt(y1error^2 + y2error^2)
        The error of x values is set to 0
        """
        if isinstance(other, DataErrors):
            if self.getLength() == other.getLength():
                y = []
                yerror = []
                ys = self.getY()
                yse = self.getEY()
                yo = other.getY()
                yoe = other.getEY()
                for i in range(self.getLength()):
                    y.append(ys[i] - yo[i])
                    yerror.append(np.sqrt((yse[i]) ** 2 + (yoe[i]) ** 2))
                return DataErrors.fromLists(self.getX(), y, [0] * self.getLength(), yerror)
            else:
                return NotImplemented
        else:
            return NotImplemented
