#!/usr/bin/python2.7
"""The Fitter class is a link to ROOTs TFitter, but enhanced with better management of parameters and covariant / correlation matrix"""

__author__ = "Benjamin Rottler (benjamin@dierottlers.de)"

#from scipy.stats import chi2            # for p-value of chi^2
from ROOT import TF1, TVirtualFitter    # ROOT library
from txtfile import TxtFile             # basic output to txt files, can be found the /lib directory


class Fitter:

    """This class is a tool for fitting experimental data"""

    def __init__(self, name, function, own=None):
        """Constructor, sets some constants for fitting function and initializes fields

        Arguments:
        name     -- ROOT internal name of function
        function -- function to fit, use conventions from ROOT
        """
        if not own is None:
            xmin, xmax, npar = own
            self._function = TF1(name, function, xmin, xmax, npar)
        else:
            self._function = TF1(name, function)
        self._function.SetLineColor(2)  # red
        self._function.SetLineWidth(1)
        self.params = dict()
        self.virtualFitter = None
        self._covMatrix = None
        self._corrMatrix = None

    def setParam(self, index, name, value=1, fixed=False):
        """initializes parameter

        Arguments:
        index      -- index of parameter (has to be the same as in the function of constructor)
        name       -- name of parameter
        value -- value of parameter for fit (default = 1)
        fixed -- if true fixes parameter (no fitting)
        """
        if not fixed:
            self.params[index] = {'name': name, 'startvalue': value, 'value': 0, 'error': 0, 'fixed': False}
            self._function.SetParameter(index, value)
        else:
            self.params[index] = {'name': name, 'startvalue': value, 'value': value, 'error': 0, 'fixed': True}
            self._function.FixParameter(index, value)
        self._function.SetParName(index, name)

    def fit(self, graph, xstart, xend, options=''):
        """computes fit and stores calculated parameters with errors in parameter dict. 
        Also extracts covariance matrix and calculates correlation matrix

        Arguments:
        graph   -- an instance of ROOTs TGraph with data to fit
        xstart  -- start value for x interval  
        xend    -- end value for x interval
        options -- fitting options (see ROOT documentation)
        """
        graph.Fit(self._function, 'Q' + options, '', xstart, xend)  # Q = quit mode, no print out on console
        # get fitted params
        self.virtualFitter = TVirtualFitter.GetFitter()
        for i in self.params:
            self.params[i]['value'] = self.virtualFitter.GetParameter(i)
            self.params[i]['error'] = self.virtualFitter.GetParError(i)
        # get cov. and corr. matrix
        freeparams = dict()  # map cov. matrix index to params index, only not fixed params are in cov. matrix
        freecount = 0
        fixedcount = 0
        for i, param in self.params.items():
            if param['fixed']:
                fixedcount += 1
            else:
                freecount += 1
                freeparams[i - fixedcount] = i
        self._covMatrix = [[self.virtualFitter.GetCovarianceMatrixElement(col, row) for row in range(freecount)] for col in range(freecount)]
        self._corrMatrix = [[self._covMatrix[col][row] / (self.params[freeparams[col]]['error'] * self.params[freeparams[row]]['error']) for row in range(freecount)] for col in range(freecount)]

    def getFunction(self):
        """returns fit function"""
        return self._function

    function = property(getFunction)

    def getChisquare(self):
        """returns chi^2 of fit"""
        return self._function.GetChisquare()

    def getDoF(self):
        """returns degrees of freedom of fit"""
        return self._function.GetNDF()

    def getChisquareOverDoF(self):
        """returns chi^2 over degrees of freedom of fit"""
        return self.getChisquare() / self.getDoF()

    # def getPValue(self):
    #     """returns p-value of chi^2 test"""
    #     p = chi2.cdf(self.getChisquare(), self.getDoF())
    #     if p < 0.5:
    #         return p, 'l'
    #     else:
    #         return 1 - p, 'r'

    def getCovMatrix(self):
        """returns covariance matrix of fit"""
        return self._covMatrix

    def getCovMatrixElem(self, col, row):
        """returns entry of covariance matrix

        Arguments:
        col -- column of element
        row -- row of element
        """
        return self._covMatrix[col][row]

    def getCorrMatrix(self):
        """returns correlation matrix"""
        return self._corrMatrix

    def getCorrMatrixElem(self, col, row):
        """returns entry of correlation matrix

        Arguments:
        col -- column of element
        row -- row of element
        """
        return self._corrMatrix[col][row]

    def saveData(self, path, mode='w', enc='utf-8'):
        """saves fitting info (chi^2, DoF, chi^2/DoF, paramters with values and errors, covariance and correlation matrix)

        Arguments:
        path -- relative path to file
        mode -- write mode (usually 'w' for overwriting or 'a' for appending)
        enc  -- encoding (default = 'utf-8')
        """
        with TxtFile.fromRelPath(path, mode) as f:
            f.writeline('fitting info')
            f.writeline('============')
            f.writeline(TxtFile.CHISQUARE + ':\t\t' + str(self.getChisquare()))
            f.writeline('DoF:\t' + str(self.getDoF()))
            f.writeline(TxtFile.CHISQUARE + '/DoF:\t' + str(self.getChisquareOverDoF()))
            #f.writeline('\t', 'p-value:', *map(str, self.getPValue()))
            f.writeline('')
            f.writeline('parameters')
            f.writeline('==========')
            for i, param in self.params.items():
                f.writeline('\t', str(i), param['name'], str(param['value']), TxtFile.PM, str(param['error']))
            f.writeline('')
            f.writeline('covariance matrix')
            f.writeline('=================')
            f.writelines('\t'.join(str(j) for j in i) + '\n' for i in self._covMatrix)
            f.writeline('')
            f.writeline('correlation matrix')
            f.writeline('==================')
            f.writelines('\t'.join(str(j) for j in i) + '\n' for i in self._corrMatrix)
            f.writeline()
            f.close()

    def addParamsToLegend(self, legend, formatStyle='', chisquare=True, chisquareformat='%.2e', advancedchi=False, units=None, lang='de'):
        """adds fit information to legend

        Arguments:
        legend          -- TLegend object
        formatStyle     -- formatStyle of values and errors, list of two entry tuples, if empty ('%e', '%e') will be used
        chisquare       -- show chi^2 (Default=True)
        chisquareformat -- formatStyle string for chi^2 value (Default='%e')
        lang            -- langeuage for parameter heading, 'de' or 'en' (default='de')         
        """
        # chi squared
        if chisquare:
            if not advancedchi:
                legend.AddEntry(0, '#chi^{2} / DoF = ' + chisquareformat % self.getChisquareOverDoF(), '')
            else:
                chistring = '#chi^{2} / DoF = %s / %s = %s' % (chisquareformat, '%d', chisquareformat)
                legend.AddEntry(0, chistring % (self.getChisquare(), self.getDoF(), self.getChisquareOverDoF()), '')
        # parameter label
        lang_param = 'Parameter:'
        if lang == 'en':
            lang_param = 'parameters:'
        legend.AddEntry(0, lang_param, '')
        # add params
        for i, param in self.params.items():
            if param['fixed']:
                label = '%s'
                if units:
                    label = label + ' ' + units[i]
                if formatStyle:
                    label = '%s: ' + label % formatStyle[i]
                else:
                    label = '%s: ' + label % '%e'
                legend.AddEntry(0, label % (param['name'], param['value']), '')

            else:
                label = '%s #pm %s'
                if units:
                    label = '(' + label + ') ' + units[i]
                if formatStyle:
                    label = '%s: ' + label % formatStyle[i]
                else:
                    label = '%s: ' + label % ('%e', '%e')
                legend.AddEntry(0, label % (param['name'], param['value'], param['error']), '')
