import os
import sys
import ROOT
import warnings

import AbstractClasses
from AbstractClasses.Helper.BetterConfigParser import BetterConfigParser

from AbstractClasses.GeneralTestResult import GeneralTestResult
import subprocess


class TestResult(GeneralTestResult):
    def CustomInit(self):
        self.NameSingle = 'ConnectionTest'
        self.Name = 'CMSPixel_QualificationGroup_{NameSingle}_TestResult'.format(NameSingle=self.NameSingle)
        self.Title = str(self.Attributes['ModuleID']) + ' ' + self.Attributes['StorageKey']
        self.Attributes['TestedObjectType'] = 'CMSPixel_Module'
        self.Attributes['NumberOfChips'] = self.nTotalChips
        self.Attributes['StartChip'] = 0
        self.Attributes['ModuleVersion'] = 1
        self.Attributes['isDigital'] = 1

        self.AddCommentsToKeyValueDictPairs = True
        self.ResultData['SubTestResultDictList'] = [
            {
                'Key': 'Logfile',
                'DisplayOptions': {
                    'Order': 2010,
                    'Width': 1,
                    'Show': True,
                },
                'InitialAttributes': {
                    'ModuleVersion': self.Attributes['ModuleVersion'],
                },
            },
            {
                'Key': 'SignalTest',
                'DisplayOptions': {
                    'Order': 2500,
                    'Width': 3,
                    'Show': True,
                },
                'InitialAttributes': {
                    'ModuleVersion': self.Attributes['ModuleVersion'],
                },
            },
            {
                'Key': 'ProgramROC',
                'DisplayOptions': {
                    'Order': 320,
                    'Width': 1,
                    'Show': True,
                },
                'InitialAttributes': {
                    'ModuleVersion': self.Attributes['ModuleVersion'],
                },
            },
            {
                'Key': 'LeakageCurrent',
                'DisplayOptions': {
                    'Order': 305,
                    'Width': 1,
                    'Show': True,
                },
                'InitialAttributes': {
                    'ModuleVersion': self.Attributes['ModuleVersion'],
                },
            },
            {
                'Key': 'Grading',
                'DisplayOptions': {
                    'Order': 100,
                    'Width': 1,
                    'Show': False,
                },
                'InitialAttributes': {
                    'ModuleVersion': self.Attributes['ModuleVersion'],
                },
            },
        ]

    def OpenFileHandle(self):
        self.check_Test_Software()
        fileHandlePath = self.RawTestSessionDataPath + '/pxar.root'
        self.FileHandle = ROOT.TFile.Open(fileHandlePath)
        if not self.FileHandle:
            print 'problem to find %s' % fileHandlePath
            files = [f for f in os.listdir(self.RawTestSessionDataPath) if f.endswith('.root')]
            i = 0
            if len(files) > 1:
                print '\nPossible Candidates for ROOT files are:'
                for f in files:
                    print '\t[%3d]\t%s' % (i, f)
                    i += 1
                i = len(files)
                if self.HistoDict.has_option('RootFile', 'filename'):
                    print 'checking for backup rootfile name'
                    if self.HistoDict.has_option('RootFile', 'filename'):
                        if self.HistoDict.get('RootFile', 'filename') in files:
                            i = files.index(self.HistoDict.get('RootFile', 'filename'))
                            print 'rootfile exists: index ', i
                while i < 0 or i >= len(files):
                    try:
                        # TODO: How to continue when it happens in automatic processing...
                        rawInput = ''
                        i = 0
                        if self.verbose:
                            rawInput = raw_input(
                                'There are more than one possbile candidate for the ROOT file. Which file should be used? [0-%d]\t' % (
                                    len(files) - 1))
                            i = int(rawInput)
                        elif self.HistoDict.has_option('RootFile', 'filename'):
                            if self.HistoDict.get('RootFile', 'filename') in files:
                                i = files.index(self.HistoDict.get('RootFile', 'filename'))
                        else:
                            i = 0
                    except TypeError:
                        print '%s is not an integer, please enter a valid integer' % rawInput
                    except ValueError:
                        print '%s is not an integer, please enter a valid integer' % rawInput

                fileHandlePath = self.RawTestSessionDataPath + '/' + files[i]
                print "open '%s'" % fileHandlePath
                self.FileHandle = ROOT.TFile.Open(fileHandlePath)
            elif len(files) == 1:
                i = 0
                fileHandlePath = self.RawTestSessionDataPath + '/' + files[i]
                print "only one other ROOT file exists. Open '%s'" % fileHandlePath
                self.FileHandle = ROOT.TFile.Open(fileHandlePath)
            else:
                print 'There exist no ROOT file in "%s"' % self.RawTestSessionDataPath

        # find pxar logfile of fulltest
        logfilePath = ("%s.log" % fileHandlePath[:-5]) if len(fileHandlePath) > 4 else ''
        self.pxarVersion = None
        self.logfilePath = None
        if os.path.isfile(logfilePath):
            self.logfilePath = logfilePath
            try:
                with open(logfilePath, 'r') as logFile:
                    for line in logFile:
                        if 'Instanciating API for pxar' in line:
                            posPxar = line.find('pxar')
                            if posPxar >= 0:
                                self.pxarVersion = line[posPxar + 5:] if len(line) > posPxar + 5 else '?'
            except:
                pass

    def CustomWriteToDatabase(self, ParentID):
        if self.verbose:
            print 'Write to DB: ', ParentID

        Comment = ""
        try:
            Comment = self.ResultData['SubTestResults']['Grading'].ResultData['KeyValueDictPairs']['Comment']['Value']
        except:
            pass

        try:
            if self.ParentObject.CommentFromFile:
                if len(Comment) < 1:
                    Comment = self.ParentObject.CommentFromFile
                else:
                    Comment += "; " + self.ParentObject.CommentFromFile
        except:
            pass

        try:
            if self.CommentFromFile:
                if len(Comment) < 1:
                    Comment = self.CommentFromFile
                else:
                    Comment += "; " + self.CommentFromFile
        except:
            pass

        # fill DB row
        Row = {
            'ModuleID': self.Attributes['ModuleID'],
            'TestDate': self.Attributes['TestDate'],
            'TestType': self.Attributes['TestType'],
            'QualificationType': self.ParentObject.Attributes['QualificationType'],
            'Grade': None,
            'PixelDefects': -1,
            'ROCsLessThanOnePercent': -1,
            'ROCsMoreThanOnePercent': -1,
            'ROCsMoreThanFourPercent': -1,
            'Noise': -1,
            'Trimming': -1,
            'PHCalibration': -1,
            'CurrentAtVoltage150V': -1,
            'CurrentAtVoltage100V': -1,
            'IVSlope': -1,
            'IVCurveFilePath': '',
            'TestTemperature': -1,
            'Temperature': -1,
            'nCycles': 0,
            'CycleTempLow': -1,
            'CycleTempHigh': -1,
            'nMaskDefects': -1,
            'nDeadPixels': -1,
            'nBumpDefects': -1,
            'nTrimDefects': -1,
            'nNoisyPixels': -1,
            'nGainDefPixels': -1,
            'nPedDefPixels': -1,
            'nPar1DefPixels': -1,
            'RecalculatedVoltage': -1,
            'RelativeModuleFinalResultsPath': os.path.relpath(self.TestResultEnvironmentObject.FinalModuleResultsPath,
                                                              self.TestResultEnvironmentObject.GlobalOverviewPath),
            'FulltestSubfolder': os.path.relpath(self.FinalResultsStoragePath,
                                                 self.TestResultEnvironmentObject.FinalModuleResultsPath),
            # needed for PixelDB
            'AbsModuleFulltestStoragePath': self.TestResultEnvironmentObject.FinalModuleResultsPath,
            'AbsFulltestSubfolder': self.FinalResultsStoragePath,
            'InputTarFile': os.environ.get('TARFILE', None),
            'MacroVersion': os.environ.get('MACROVERSION', None),

            'initialCurrent': -1,

            'TestCenter': self.Attributes['TestCenter'],
            'Hostname': self.Attributes['Hostname'],
            'Operator': self.Attributes['Operator'],
            'Comments': Comment,
        }

        try:
            Row.update({
                'Grade': self.ResultData['SubTestResults']['Grading'].ResultData['KeyValueDictPairs']['Grade']['Value'],
            })
        except:
            Row['Grade'] = 'C'
            Row['Comments'] = Row['Comments'] + '/ incomplete test' if ('Comments' in Row and len(Row['Comments'].strip()) > 0) else 'incomplete test'

        print 'fill row end'

        if self.TestResultEnvironmentObject.Configuration['Database']['UseGlobal']:
            from PixelDB import *
            # modified by Tommaso
            #
            # try and speak directly with PixelDB
            #

            #            fake = int(os.environ.get('FAKE',1))

            #            insertedID=7
            pdb = PixelDBInterface(operator="tommaso", center="pisa")
            pdb.connectToDB()

            #            if (0 == 0):
            OPERATOR = os.environ['PIXEL_OPERATOR']
            CENTER = os.environ['PIXEL_CENTER']
            s = Session(CENTER, OPERATOR)
            pdb.insertSession(s)
            print "--------------------"
            print "INSERTING INTO DB", self.TestResultEnvironmentObject.FinalModuleResultsPath, s.SESSION_ID, Row
            print "--------------------"
            pp = pdb.insertTestFullModuleDirPlusMapv96Plus(s.SESSION_ID, Row)

            if pp is None:
                print "INSERTION FAILED!"
                sys.exit(31)
            insertedID = pp.TEST_ID

        else:
            with self.TestResultEnvironmentObject.LocalDBConnection:
                self.TestResultEnvironmentObject.LocalDBConnectionCursor.execute(
                    'DELETE FROM ModuleTestResults WHERE ModuleID = :ModuleID AND TestType=:TestType AND QualificationType=:QualificationType AND TestDate <= :TestDate',
                    Row)
                self.TestResultEnvironmentObject.LocalDBConnectionCursor.execute(
                    '''INSERT INTO ModuleTestResults
                    (
                        ModuleID,
                        TestDate,
                        TestType,
                        QualificationType,
                        Grade,
                        PixelDefects,
                        ROCsLessThanOnePercent,
                        ROCsMoreThanOnePercent,
                        ROCsMoreThanFourPercent,
                        CurrentAtVoltage150V,
                        RecalculatedVoltage,
                        IVSlope,
                        Temperature,
                        RelativeModuleFinalResultsPath,
                        FulltestSubfolder,
                        initialCurrent,
                        Comments
                    )
                    VALUES (
                        :ModuleID,
                        :TestDate,
                        :TestType,
                        :QualificationType,
                        :Grade,
                        :PixelDefects,
                        :ROCsLessThanOnePercent,
                        :ROCsMoreThanOnePercent,
                        :ROCsMoreThanFourPercent,
                        :CurrentAtVoltage150V,
                        :RecalculatedVoltage,
                        :IVSlope,
                        :Temperature,
                        :RelativeModuleFinalResultsPath,
                        :FulltestSubfolder,
                        :initialCurrent,
                        :Comments
                    )
                    ''', Row)
                return self.TestResultEnvironmentObject.LocalDBConnectionCursor.lastrowid
