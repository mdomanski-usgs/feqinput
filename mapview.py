from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_mapview
import datacontainer

class MapView(QDialog, ui_mapview.Ui_mapView):

    def __init__(self, mapbutton, mapaction, textBrowser, table=None, \
                 parent=None):
        super(MapView, self).__init__(parent)
        self.setupUi(self)
        self.connect(self.applybutton1, SIGNAL("clicked()"), \
                     self.insertMapEdits)
        self.connect(self.applybutton2, SIGNAL("clicked()"), \
                     self.insertMapEdits)
        self.connect(self.cancelbutton1, SIGNAL("clicked()"), \
                     self.cancelMapEdits)
        self.connect(self.cancelbutton2, SIGNAL("clicked()"), \
                     self.cancelMapEdits)

        self.table = table
        self.textBrowser = textBrowser
        self.mapButton = mapbutton
        self.actionMap_Mode = mapaction
        
        if table is not None:
            maxrow = table.rowCount()
            row = -1
            while row != (maxrow - 1):
                row += 1
                code = self.updateCode(row)
                text = self.updateText(row)
                if code == "TITLE":
                    self.projectName.setText(text)
                    row += 1
                    code = self.updateCode(row)
                    text = self.updateText(row)
                    while code == "TITLE" or code == "COM":
                        self.projectDetails.appendPlainText(text)
                        row += 1
                        code = self.updateCode(row)
                        text = self.updateText(row)
                    row -= 1
                elif code == "STIM":
                    self.STYEAR.setText(text[6:10])
                    self.STMONTH.setText(text[11:13])
                    self.STDAY.setText(text[14:16])
                    self.STTIME.setText(text[17:])
                elif code == "ETIM":
                    self.ETYEAR.setText(text[6:10])
                    self.ETMONTH.setText(text[11:13])
                    self.ETDAY.setText(text[14:16])
                    self.ETTIME.setText(text[17:])
                elif code == "NBRA":
                    self.NBRA.setText(text[5:])
                elif code == "NEX":
                    self.NEX.setText(text[4:])
                elif code == "SOPER":
                    if "YES" in text:
                        self.SOPERyes.setChecked(True)
                    elif "NO" in text:
                        self.SOPERno.setChecked(True)
                elif code == "DIFF":
                    if "YES" in text:
                        self.DIFFUSyes.setChecked(True)
                    elif "NO" in text:
                        self.DIFFUSno.setChecked(True)
                elif code == "WIND":
                    if "YES" in text:
                        self.WINDyes.setChecked(True)
                    elif "NO" in text:
                        self.WINDno.setChecked(True)
                elif code == "ZL":
                    self.ZL.setText(text[3:])
                elif code == "GRAV":
                    if "32.2" in text:
                        self.GRAVenglish.setChecked(True)
                    elif "9.8" in text:
                        self.GRAVmetric.setChecked(True)
                elif code == "SSEPS":
                    self.SSEPS.setText(text[6:])
                elif code == "PAGE":
                    self.PAGE.setText(text[5:])
                elif code == "EPSSYS":
                    self.EPSSYS.setText(text[7:])
                elif code == "EPSFAC":
                    self.EPSFAC.setText(text[7:])
                elif code == "MKNT":
                    self.MKNT.setText(text[5:])
                elif code == "NUMGT":
                    self.NUMGT.setText(text[6:])
                elif code == "PRTINT":
                    self.PRTINT.setText(text[7:])
                elif code == "GEQOPT":
                    if "STDX" in text:
                        self.STDX.setChecked(True)
                    elif "STDW" in text:
                        self.STDW.setChecked(True)
                    elif "STDCX" in text:
                        self.STDCX.setChecked(True)
                    elif "STDCW" in text:
                        self.STDCW.setChecked(True)
                elif code == "EPSB":
                    self.EPSB.setText(text[5:])
                elif code == "MAXIT":
                    self.MAXIT.setText(text[6:])
                elif code == "SFAC":
                    self.SFAC.setText(text[5:])
                elif code == "TAUFAC":
                    self.TAUFAC.setText(text[7:])
                elif code == "QSMALL":
                    self.QSMALL.setText(text[7:])

    def updateCode(self, row):
        code = self.table.item(row, 0).text()
        return code

    def updateText(self, row):
        text = self.table.item(row, 1).text()
        return text

    def cancelMapEdits(self):
        if self.table is not None:
            self.table.show()
        self.textBrowser.show()
        self.close()
        self.mapButton.setEnabled(True)
        self.actionMap_Mode.setEnabled(True)

    def insertMapEdits(self):
        if self.table is not None:
            maxrow = self.table.rowCount()
            row = -1
            while row != (maxrow - 1):
                row += 1
                code = self.updateCode(row)
                text = self.updateText(row)
                if code == "STIM":
                    newtext = "STIME="
                    newtext += self.STYEAR.text()
                    newtext += "/"
                    newtext += self.STMONTH.text()
                    newtext += "/"
                    newtext += self.STDAY.text()
                    newtext += ":"
                    newtext += self.STTIME.text()
                    self.table.item(row, 1).setText(newtext)
                elif code == "ETIM":
                    newtext = "ETIME="
                    newtext += self.ETYEAR.text()
                    newtext += "/"
                    newtext += self.ETMONTH.text()
                    newtext += "/"
                    newtext += self.ETDAY.text()
                    newtext += ":"
                    newtext += self.ETTIME.text()
                    self.table.item(row, 1).setText(newtext)
                elif code == "NBRA":
                    newtext = "NBRA="
                    newtext += self.NBRA.text()
                    self.table.item(row, 1).setText(newtext)
                elif code == "NEX":
                    newtext = "NEX="
                    newtext += self.NEX.text()
                    self.table.item(row, 1).setText(newtext)
                elif code == "SOPER":
                    if self.SOPERyes.isChecked():
                        newtext = "SOPER=YES"
                    elif self.SOPERno.isChecked():
                        newtext = "SOPER=NO"
                    self.table.item(row, 1).setText(newtext)
                elif code == "DIFF":
                    if self.DIFFUSyes.isChecked():
                        newtext = "DIFFUS=YES"
                    elif self.DIFFUSno.isChecked():
                        newtext = "DIFFUS=NO"
                    self.table.item(row, 1).setText(newtext)
                elif code == "WIND":
                    if self.WINDyes.isChecked():
                        newtext = "WIND=YES"
                    elif self.WINDno.isChecked():
                        newtext = "WIND=NO"
                    self.table.item(row, 1).setText(newtext)
                elif code == "ZL":
                    newtext = "ZL="
                    newtext += self.ZL.text()
                    self.table.item(row, 1).setText(newtext)
                elif code == "GRAV":
                    if self.GRAVenglish.isChecked():
                        newtext = "GRAV=32.2"
                    elif self.GRAVmetric.isChecked():
                        newtext = "GRAV=9.8"
                    self.table.item(row, 1).setText(newtext)
                elif code == "SSEPS":
                    newtext = "SSEPS="
                    newtext += self.SSEPS.text()
                    self.table.item(row, 1).setText(newtext)
                elif code == "PAGE":
                    newtext = "PAGE="
                    newtext += self.PAGE.text()
                    self.table.item(row, 1).setText(newtext)
                elif code == "EPSYSS":
                    newtext = "EPSYSS="
                    newtext += self.EPSYSS.text()
                    self.table.item(row, 1).setText(newtext)
                elif code == "EPSFAC":
                    newtext = "EPSFAC="
                    newtext += self.EPSFAC.text()
                    self.table.item(row, 1).setText(newtext)
                elif code == "MKNT":
                    newtext = "MKNT="
                    newtext += self.MKNT.text()
                    self.table.item(row, 1).setText(newtext)
                elif code == "NUMGT":
                    newtext = "NUMGT="
                    newtext += self.NUMGT.text()
                    self.table.item(row, 1).setText(newtext)
                elif code == "PRTINT":
                    newtext = "PRTINT="
                    newtext += self.PRTINT.text()
                    self.table.item(row, 1).setText(newtext)
                elif code == "GEQOPT":
                    if self.STDX.isChecked():
                        newtext = "GEQOPT=STDX"
                    elif self.STDW.isChecked():
                        newtext = "GEQOPT=STDW"
                    elif self.STDCX.isChecked():
                        newtext = "GEQOPT=STDCX"
                    elif self.STDCW.isChecked():
                        newtext = "GEQOPT=STDCW"
                    self.table.item(row, 1).setText(newtext)
                elif code == "EPSB":
                    newtext = "EPSB="
                    newtext += self.EPSB.text()
                    self.table.item(row, 1).setText(newtext)
                elif code == "MAXIT":
                    newtext = "MAXIT="
                    newtext += self.MAXIT.text()
                    self.table.item(row, 1).setText(newtext)
                elif code == "SFAC":
                    newtext = "SFAC="
                    newtext += self.SFAC.text()
                    self.table.item(row, 1).setText(newtext)
                elif code == "TAUFAC":
                    newtext = "TAUFAC="
                    newtext += self.TAUFAC.text()
                    self.table.item(row, 1).setText(newtext)
                elif code == "QSMALL":
                    newtext = "QSMALL="
                    newtext += self.QSMALL.text()
                    self.table.item(row, 1).setText(newtext)
                
            self.table.show()
        self.textBrowser.show()
        self.mapButton.setEnabled(True)
        self.actionMap_Mode.setEnabled(True)
        self.close()
                    
        
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    form = MapView(set())
    form.show()
    app.exec_()
