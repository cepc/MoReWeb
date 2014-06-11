import ROOT
import AbstractClasses
import ROOT
class TestResult(AbstractClasses.GeneralTestResult.GeneralTestResult):
    def CustomInit(self):
        self.Name='CMSPixel_QualificationGroup_Fulltest_Chips_Chip_TrimBitMap_TestResult'
        self.NameSingle='TrimBitMap'
        self.Attributes['TestedObjectType'] = 'CMSPixel_QualificationGroup_Fulltest_ROC'
        
    def PopulateResultData(self):
        
        
        ROOT.gStyle.SetOptStat(0);
        self.ResultData['Plot']['ROOTObject'] =  ROOT.TH2D(self.GetUniqueID(), "", self.nCols, 0., self.nCols, self.nRows, 0., self.nRows ) # htm
        # TH2D
        
        ChipNo=self.ParentObject.Attributes['ChipNo']
        histname = self.ParentObject.ParentObject.ParentObject.HistoDict.get(self.NameSingle,'TrimBitMap')%ChipNo
        self.ResultData['Plot']['ROOTObject_TrimMap'] =  self.ParentObject.ParentObject.FileHandle.Get(histname).Clone(self.GetUniqueID())
        
        if self.ResultData['Plot']['ROOTObject']:
            for i in range(self.nCols): # Columns
                for j in range(self.nRows): # Rows
                    self.ResultData['Plot']['ROOTObject'].SetBinContent(i+1, j+1, self.ResultData['Plot']['ROOTObject_TrimMap'].GetBinContent(i+1, j+1))
            
            self.ResultData['Plot']['ROOTObject'].SetTitle("");
            self.ResultData['Plot']['ROOTObject'].GetZaxis().SetRangeUser(0., self.nTotalChips);
            self.ResultData['Plot']['ROOTObject'].GetXaxis().SetTitle("Trim bit Map");
            self.ResultData['Plot']['ROOTObject'].GetYaxis().SetTitle("entries");
            self.ResultData['Plot']['ROOTObject'].GetXaxis().SetTitle("Column No.");
            self.ResultData['Plot']['ROOTObject'].GetYaxis().SetTitle("Row No.");
            self.ResultData['Plot']['ROOTObject'].GetXaxis().CenterTitle();
            self.ResultData['Plot']['ROOTObject'].GetYaxis().SetTitleOffset(1.5);
            self.ResultData['Plot']['ROOTObject'].GetYaxis().CenterTitle();
            self.ResultData['Plot']['ROOTObject'].Draw('colz');
            

        if self.SavePlotFile:
            self.Canvas.SaveAs(self.GetPlotFileName())      
        self.ResultData['Plot']['Enabled'] = 1
        self.Title = 'Trim Bit Map'
        self.ResultData['Plot']['ImageFile'] = self.GetPlotFileName()
