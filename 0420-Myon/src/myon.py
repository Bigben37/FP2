import os
import numpy as np
# ========================================================================
from data import DataErrors
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


def prepareGraph(g):
    g.SetMarkerStyle(8)
    g.SetMarkerSize(0.3)
    g.SetLineColor(15)
    g.SetLineWidth(0)
