import ROOT

class ModuleMap:
    ModuleMapIDCounter = 0

    def __init__(self, Name='', nChips = 16, StartChip = 1, nCols = 8, nRows = 2, nColsRoc = 52, nRowsRoc = 80, nPixelsX = 1784, nPixelsY = 412):
        self.Name = Name
        self.nCols = nCols
        self.nRows = nRows # has to be equal to 2
        self.nColsRoc = nColsRoc
        self.nRowsRoc = nRowsRoc
        self.nPixelsX = nPixelsX
        self.nPixelsY = nPixelsY
        self.nChips = nChips
        self.StartChip = StartChip

        xBins = self.nCols * self.nColsRoc
        yBins = self.nRows * self.nRowsRoc
        self.Map2D = ROOT.TH2D(self.GetUniqueID(), "", xBins, 0., xBins, yBins, 0., yBins)


    def UpdatePlot(self, chipNo, col, row, value):
        if chipNo < self.nCols:
            tmpCol = self.nCols * self.nColsRoc - 1 - chipNo * self.nColsRoc - col
            tmpRow = self.nRows * self.nRowsRoc - 1 - row
        else:
            tmpCol = (chipNo % self.nCols * self.nColsRoc + col)
            tmpRow = row

        if self.Map2D:
            self.Map2D.Fill(tmpCol, tmpRow, value)

    def GetUniqueID(self):
        self.ModuleMapIDCounter += 1
        return "ModuleMap_%s%d"%(self.Name, self.ModuleMapIDCounter)

    def GetHistogram(self):
        return self.Map2D

    def SetContour(self, NContours):
        if self.Map2D:
            self.Map2D.SetContour(NContours)

    def Draw(self, Canvas, TitleZ = None):

        ROOT.gPad.SetLogy(0)
        ROOT.gPad.SetLogx(0)

        try:
            self.Map2D.GetXaxis().SetTickLength(0.015)
            self.Map2D.GetYaxis().SetTickLength(0.012)
            self.Map2D.GetXaxis().SetAxisColor(1, 0.4)
            self.Map2D.GetYaxis().SetAxisColor(1, 0.4)
            Canvas.SetFrameLineStyle(0)
            Canvas.SetFrameLineWidth(1)
            Canvas.SetFrameBorderMode(0)
            Canvas.SetFrameBorderSize(1)
            Canvas.SetCanvasSize(self.nPixelsX, self.nPixelsY)
        except:
            pass

        try:
            self.Map2D.SetTitle("")
            self.Map2D.GetXaxis().SetTitle("Column No.")
            self.Map2D.GetYaxis().SetTitle("Row No.")
            self.Map2D.GetXaxis().CenterTitle()
            self.Map2D.GetYaxis().SetTitleOffset(0.5)
            self.Map2D.GetYaxis().CenterTitle()
            if TitleZ:
                self.Map2D.GetZaxis().SetTitle(TitleZ)
                self.Map2D.GetZaxis().SetTitleOffset(0.5)
                self.Map2D.GetZaxis().CenterTitle()
            self.Map2D.Draw('colz')
        except:
            pass

        boxes = []
        startChip = self.StartChip
        endChip = self.nChips + startChip - 1

        for i in range(0,16):
            if i < startChip or endChip < i:
                if i < self.nCols:
                    j = self.nCols*self.nRows - 1 - i
                else:
                    j = i - self.nCols
                beginX = (j % self.nCols) * self.nColsRoc
                endX = beginX + self.nColsRoc
                beginY = int(j / self.nCols) * self.nRowsRoc
                endY = beginY + self.nRowsRoc
                newBox = ROOT.TPaveText(beginX, beginY, endX, endY)
                newBox.SetFillColor(29)
                newBox.SetLineColor(29)
                newBox.SetFillStyle(3004)
                newBox.SetShadowColor(0)
                newBox.SetBorderSize(1)
                newBox.Draw()
                boxes.append(newBox)