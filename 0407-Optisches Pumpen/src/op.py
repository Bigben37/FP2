import os
# ========================================================================
# make sure to add ../../lib to your project path or copy files from there
from data import DataErrors
# ========================================================================
from numpy import sqrt, mean


class OPData(DataErrors):

    CH1 = 1
    CH2 = 2
    OFFSET = 0.000275
    CH1COLOR = 4
    CH1ECOLOR = 64
    CH2COLOR = 1
    CH2ECOLOR = 15

    def __init__(self):
        super().__init__()
        self.channel = OPData.CH1

    @classmethod
    def fromPath(cls, path, channel):
        data = cls()
        data.path = path
        data.channel = channel
        if path:
            data.loadData()
        return data

    def loadData(self):
        d = os.getcwd()
        p = os.path.abspath(os.path.join(d, self.path))
        with open(p, 'r') as f:
            i = 0
            for row in f:
                if i > 0:
                    datapoint = list(map(float, row.strip().split('\t')))
                    x = datapoint[0]
                    y = datapoint[self.channel]
                    self.addPoint(x, y, 0, 0)
                i += 1
        self.setYErrorAbs(self.getMinDeltaY() / 2)

    def rebin(self, binsize):
        """rebins data

        Arguments:
        binsize -- number of bins/values to average
        """
        xvals = self.getX()
        yvals = self.getY()
        exvals = self.getEX()
        eyvals = self.getEY()
        i = 0
        data = OPData()
        while i <= self.getLength():
            currxs = xvals[i:i + binsize]
            currys = yvals[i:i + binsize]
            currexs = exvals[i:i + binsize]
            curreys = eyvals[i:i + binsize]
            x = mean(currxs)
            y = mean(currys)
            ex = mean(currexs)
            ey = mean(curreys)
            data.addPoint(x, y, ex, ey)
            i += binsize
        return data

    def findExtrema(self, steps, xstart, xend, minimum=True):
        """finds extrema in data points by comparing nearby values

        Arguments:
        steps   -- number of comparisons to right and left side
        xstart  -- start of x interval in which extrema are analyzed
        xend    -- end of x interval in which extrema are anayzed
        minimum -- if true searches for minima, if false searches for maxima (default = True)
        """
        m = 1 if minimum else -1  # modifier for maxima/minimia
        data = OPData()
        minDeltaY = 3 * self.getMinDeltaY()
        for i in range(steps, self.getLength() - steps):
            if xstart <= self.points[i][0] <= xend:
                passed = True
                sumDeltaY = 0
                for j in range(-steps, steps + 1):
                    passed = passed and (m * self.points[i][1] <= m * self.points[i + j][1])
                    sumDeltaY += abs(self.points[i][1] - self.points[i + j][1])
                if passed and sumDeltaY > minDeltaY:
                    data.addPoint(*self.points[i])
        return data

    def getMinDeltaX(self):
        """get x bin error"""
        deltas = set()
        for i in range(self.getLength() - 1):
            deltas.add(self.points[i + 1][0] - self.points[i][0])
        return min(deltas)

    def getMinDeltaY(self):
        """get y bin error"""
        deltas = set()
        for i in range(self.getLength() - 1):
            deltas.add(abs(self.points[i + 1][1] - self.points[i][1]))
        deltas.discard(0)
        return min(deltas)


def prepareGraph(g, channel=1):
    g.SetMarkerStyle(8)  # round points
    g.SetMarkerSize(0.3)  # size of points
    g.SetLineWidth(0)  # error bar width
    if channel == 1:
        g.SetMarkerColor(OPData.CH1COLOR)
        g.SetLineColor(OPData.CH1ECOLOR)  # color error bars
    elif channel == 2:
        g.SetMarkerColor(OPData.CH2COLOR)
        g.SetLineColor(OPData.CH2ECOLOR)  # color error bars


inductorIToBVals = {1: (7.99e-4, 0.01e-4), 2: (8.14e-4, 0.01e-4), 4: (4.76e-4, 0.01e-4)}


def inductorIToB(number, current, error):
    IToB, sIToB = inductorIToBVals[number]
    B = IToB * current
    if not current == 0:
        sB = B * sqrt((sIToB / IToB) ** 2 + (error / current) ** 2)
    else:
        sB = 0
    return B, sB


def avgCloseValues(list, epsilon):
    i = 0
    avgList = []
    l = len(list)
    while i < l:
        currxs = [list[i]]
        j = i + 1
        while j < l and abs(list[j] - list[i]) <= epsilon:
            currxs.append(list[j])
            i += 1
            j += 1
        avgList.append(mean(currxs))
        i = j
    return avgList


def getRootColor(i):
    colors = [3, 6, 7, 8, 28]
    l = len(colors)
    while i < 0:
        i += l
    while i >= l:
        i -= l
    return colors[i]
