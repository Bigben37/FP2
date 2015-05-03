import os
import numpy as np
# ========================================================================
from data import DataErrors
from functions import loadCSVToList
# make sure to add ../../lib to your project path or copy files from there
# ========================================================================


class MyonData(DataErrors):

    def __init__(self):
        super(DataErrors, self).__init__()
        self.time = 0
        self.timed = 0

    def loadData(self):
        d = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(d, self.path))
        with open(path, 'r') as f:
            lines = -1  # lines 1 and 2 are time information, line 3 starts with channel 1
            for row in f:
                if lines == -1:
                    self.time = float(row)
                elif lines == 0:
                    self.timed = float(row)
                else:
                    self.addPoint(lines, float(row), 0, np.sqrt(float(row)))
                lines += 1

    def convertToCountrate(self):
        self.multiplyY(1. / self.time)

    def convertChannelToTime(self):
        calibration = loadCSVToList('../calc/timeCalibration.txt')
        ((a, sa), (b, sb), (cov,)) = calibration
        for i in range(self.getLength()):
            x = self.points[i][0]
            t = a + x * b
            st = np.sqrt(sa ** 2 + (x * sb) ** 2 + 2 * x * cov)
            self.points[i] = (t, self.points[i][1], st, self.points[i][3])

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
        data = MyonData()
        while i <= self.getLength():
            currxs = xvals[i:i + binsize]
            currys = yvals[i:i + binsize]
            currexs = exvals[i:i + binsize]
            curreys = eyvals[i:i + binsize]
            if currxs:
                x = np.mean(currxs)
                y = np.mean(currys)
                ex = np.sqrt(sum(map(lambda x: x ** 2, currexs))) / len(currexs)
                ey = np.sqrt(sum(map(lambda x: x ** 2, curreys))) / len(curreys)
                data.addPoint(x, y, ex, ey)
            i += binsize
        return data


def prepareGraph(g):
    g.SetMarkerStyle(8)
    g.SetMarkerSize(0.3)
    g.SetLineColor(15)
    g.SetLineWidth(0)
