from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from subprocess import call
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import (QWebView, QWebSettings)
import ui_feqinput
import datacontainer
import mapview
import searchwindow
import ctypes

# FEQinput
__version__ = "1.0"
__nickname__ = ""
__date__ = "Jul/14/2016"
# Developers:
# David S Ancalle (Hydrology Trainee at USGS Illinois Water Science Center)
# Pablo J Ancalle (Computer Intern at USGS Illinois Water Science Center)


class FEQinput(QMainWindow, QDialog, ui_feqinput.Ui_FEQinput):

    # =================================================================================
    # GUI setup
    
    def __init__(self, parent=None):
        super(FEQinput, self).__init__(parent)
        self.__index = 0

        self.setupUi(self)
        self.setWindowTitle("FEQinput %s" % __version__)

        self.datacontainer = datacontainer.DataContainer()

        self.table.currentCellChanged.connect(self.readLine)

        self.connect(self.actionOpen_FEQ_file, SIGNAL("triggered()"), self.fileOpen)
        self.connect(self.actionOpen_FTL_file, SIGNAL("triggered()"), self.fileOpenFTL)
        self.connect(self.actionSave, SIGNAL("triggered()"), self.fileSave)
        self.connect(self.actionSave_As, SIGNAL("triggered()"), self.fileSaveAs)
        self.connect(self.actionExit, SIGNAL("triggered()"), self.close)
        self.connect(self.actionMulti_line_Text, SIGNAL("triggered()"), self.multiLineEditor)
        self.connect(self.actionMap_Mode, SIGNAL("triggered()"), self.mapView)
        self.connect(self.actionGraphs, SIGNAL("triggered()"), self.feqGDI)
        self.connect(self.actionRun, SIGNAL("triggered()"), self.runProgram)
        self.connect(self.actionReload, SIGNAL("triggered()"), self.reloadFile)
        self.connect(self.actionUser_Guide, SIGNAL("triggered()"), self.FEQinputUserManual)
        self.connect(self.actionAbout, SIGNAL("triggered()"), self.helpAbout)
        self.connect(self.actionFEQ_manual, SIGNAL("triggered()"), self.openManual)
        self.connect(self.actionFEQUTL_manual, SIGNAL("triggered()"), self.openFEQUTLmanual)
        self.connect(self.actionFEQ_website, SIGNAL("triggered()"), self.openFEQwebsite)  # website
        self.connect(self.runButton, SIGNAL("clicked()"), self.runProgram)
        self.connect(self.mapButton, SIGNAL("clicked()"), self.feqGDI)
        self.connect(self.reloadButton, SIGNAL("clicked()"), self.reloadFile)
        self.connect(self.textButton, SIGNAL("clicked()"), self.multiLineEditor)
        self.connect(self.search, SIGNAL("clicked()"), self.searchDialog)

        self.textBrowser.anchorClicked.connect(self.openSection)
        self.textBrowser.setOpenLinks(False)
        self.mapButton.setEnabled(False)
        self.hidebuttons()

        self.updateUi()

        self.multiLine = None
        self.form = None
        self.filename = None
        global filetype
        filetype = None

# =================================================================================
#Menu setup

    def fileOpen(self):
        path = (QFileInfo(self.datacontainer.filename()).path()
                if not self.datacontainer.filename().isEmpty() else ".")
        fname = QFileDialog.getOpenFileName(self,
                "FEQ Input - Choose input file", path,
                "FEQ input files (*.feq);;All Files (*.*)")
        if not fname.isEmpty():
            ok, msg = self.datacontainer.load(fname)
            global filetype
            filetype = "FEQ"
            self.updateTable()
            self.textBrowser.clear()
            self.textBrowser.append("""Loaded <font color="blue">%s</font>""" % fname)
            self.FileNameBrowser.clear()
            self.FileNameBrowser.append("""<p align="right"><b><font color=blue>%s</font></b></p>""" % fname)
            self.filename = fname
            self.runButton.setEnabled(True)
            self.actionRun.setEnabled(True)
            self.reloadButton.setEnabled(True)
            self.actionReload.setEnabled(True)
            self.actionMulti_line_Text.setEnabled(True)
            self.mapButton.setEnabled(True)
            self.textButton.setEnabled(True)
            self.actionMap_Mode.setEnabled(True)
            self.actionGraphs.setEnabled(True)
            self.actionSave.setEnabled(True)
            self.actionSave_As.setEnabled(True)
            self.hidebuttons()
            self.showbuttons()
            self.cancelEdits()

    def fileOpenFTL(self):
        path = (QFileInfo(self.datacontainer.filename()).path()
                if not self.datacontainer.filename().isEmpty() else ".")
        fname = QFileDialog.getOpenFileName(self,
                "FEQ Input - Choose input file", path,
                "FEQUTL files (*.ftl);;All Files (*.*)")
        if not fname.isEmpty():
            ok, msg = self.datacontainer.loadFTL(fname)
            global filetype
            filetype = "FTL"
            self.updateTable()
            self.textBrowser.clear()
            self.textBrowser.append("""Loaded <font color="blue">%s</font>""" % fname)
            self.FileNameBrowser.clear()
            self.FileNameBrowser.append("""<p align="right"><b><font color=blue>%s</font></b></p>""" % fname)
            self.filename = fname
            self.runButton.setEnabled(True)
            self.actionRun.setEnabled(True)
            self.reloadButton.setEnabled(True)
            self.actionReload.setEnabled(True)
            self.actionMulti_line_Text.setEnabled(True)
            self.mapButton.setEnabled(True)
            self.textButton.setEnabled(True)
            self.actionMap_Mode.setEnabled(False)
            self.actionGraphs.setEnabled(True)
            self.actionSave.setEnabled(True)
            self.actionSave_As.setEnabled(True)
            self.hidebuttons()
            self.cancelEdits()
            
             
    def fileSave(self):
        if self.filename is None:
            self.fileSaveAs()
        else:
            self.inputText = QTextEdit()
            i = -1
            row = self.table.rowCount()
            while i != row -1:
                i += 1
                self.inputText.append(self.table.item(i, 1).text())
            with open('%s' % self.filename, 'w') as saveFile:
                saveFile.write(str(self.inputText.toPlainText()))

    def fileSaveAs(self):
        fname = self.filename if self.filename is not None else "."
        fname = unicode(QFileDialog.getSaveFileName(self,
                                                    "FEQ Input - Save File", fname))
        if fname:
            self.filename = fname
            self.fileSave()


    def reloadFile(self):
        inputText = QTextEdit()
        i = -1
        row = self.table.rowCount()
        while i != row -1:
            i += 1
            inputText.append(self.table.item(i, 1).text())
        with open('input', 'w') as inputFile:
            inputFile.write(str(inputText.toPlainText()))
        fname = QString("input")
        global filetype
        if filetype == "FEQ":
            ok, msg = self.datacontainer.load(fname)
            self.updateTable()
            self.textBrowser.clear()
        elif filetype == "FTL":
            ok, msg = self.datacontainer.loadFTL(fname)
            self.updateTable()
            self.textBrowser.clear()
        tempFile = QFile("input")
        tempFile.remove()

    def FEQinputUserManual(self):
        # os.startfile("usermanual.pdf")
        os.startfile("fact_sheet.pdf")


    def helpAbout(self):
        aboutbox = QMessageBox.about(self, "About FEQinput",
                          """<center><img src=":/images/resources/logo.png" width="200" height="50"><br>
%s - %s <br></center>
<p>This program interprets input files for FEQ version <b>10.61</b> and FEQUTL version <b>5.80</b></p>
<p>Questions or feedback can be directed to:<br>
Center Director, USGS Illinois-Iowa Water Science Center<br>
405 N Goodwin Ave, Urbana, IL 61801<br>
Tel: (217) 328-8747<br>
E-mail: <a href="mailto:dc_ilia@usgs.gov">dc_ilia@usgs.gov</a><br></p>
<p><b>Disclaimer</b>:</p>
<p>This software has been approved for release by the U.S. Geological Survey (USGS). 
Although the software has been subjected to rigorous review, the USGS reserves the right 
to update the software as needed pursuant to further analysis and review. No warranty, 
expressed or implied, is made by the USGS or the U.S. Government as to the functionality 
of the software and related material nor shall the fact of release constitute any 
such warranty. Furthermore, the software is released on condition that neither the 
USGS nor the U.S. Government shall be held liable for any damages resulting from 
its authorized or unauthorized use.</p>
""" % (__version__, __date__))

    def openManual(self):
        self.manual = QWebView()
        self.manual.setWindowTitle("FEQ Manual")
        self.manual.load(QUrl('http://il.water.usgs.gov/proj/feq/feqdoc/contents_1.html'))
        self.manual.show()

    def openFEQUTLmanual(self):
        self.manual = QWebView()
        self.manual.setWindowTitle("FEQUTL Manual")
        self.manual.load(QUrl('http://il.water.usgs.gov/proj/feq/fequtl/fequtl.toc_1.html'))
        self.manual.show()

    def openFEQwebsite(self):
        self.manual = QWebView()
        self.manual.setWindowTitle("FEQ Full Equations Model")
        self.manual.load(QUrl('http://il.water.usgs.gov/proj/feq/'))
        self.manual.show()

# ===================================================================================
#Updater (called at the beginning of the program).

    def updateUi(self):
        printout =  "Please load an input file."
        self.textBrowser.clear()
        self.textBrowser.append(printout)

# ===================================================================================
#Hide/Show buttons (called at the beginning of the progtram or when loading a file)

    def hidebuttons(self):
        self.blockRunCtrl.setEnabled(False)
        self.blockBranch.setEnabled(False)
        self.blockTributary.setEnabled(False)
        self.blockMatrix.setEnabled(False)
        self.blockSpecialOut.setEnabled(False)
        self.blockInput.setEnabled(False)
        self.blockOutput.setEnabled(False)
        self.blockStructures.setEnabled(False)
        self.blockFnTables.setEnabled(False)
        self.blockFreeNode.setEnabled(False)
        self.blockBackwater.setEnabled(False)
        self.blockRunCtrl.hide()
        self.blockBranch.hide()
        self.blockTributary.hide()
        self.blockMatrix.hide()
        self.blockSpecialOut.hide()
        self.blockInput.hide()
        self.blockOutput.hide()
        self.blockStructures.hide()
        self.blockFnTables.hide()
        self.blockFreeNode.hide()
        self.blockBackwater.hide()

        self.blockList = []
        self.blockLines = []

    def showbuttons(self):
        self.blockRunCtrl.show()
        self.blockBranch.show()
        self.blockTributary.show()
        self.blockMatrix.show()
        self.blockSpecialOut.show()
        self.blockInput.show()
        self.blockOutput.show()
        self.blockStructures.show()
        self.blockFnTables.show()
        self.blockFreeNode.show()
        self.blockBackwater.show()
        
        i = -1
        row = self.table.rowCount()
        while i != row -1:
            i += 1
            if self.table.item(i, 0).text() == "BLK":
                if self.table.item(i, 1).text().startsWith("RUN CONTROL"):
                    self.blockRunCtrl.setEnabled(True)
                    self.run = i
                    self.connect(self.blockRunCtrl, SIGNAL("clicked()"), self.gotoRUN)
                    self.blockList += ["RUN CONTROL"]
                elif self.table.item(i, 1).text().startsWith("BRANCH DESCRIPTION"):
                    self.blockBranch.setEnabled(True)
                    self.bra = i
                    self.connect(self.blockBranch, SIGNAL("clicked()"), self.gotoBRA)
                    self.blockList += ["BRANCH"]
                elif self.table.item(i, 1).text().startsWith("TRIBUTARY AREA"):
                    self.blockTributary.setEnabled(True)
                    self.tri = i
                    self.connect(self.blockTributary, SIGNAL("clicked()"), self.gotoTRI)
                    self.blockList += ["TRIBUTARY"]
                elif "MATRIX" in self.table.item(i, 1).text():
                    self.blockMatrix.setEnabled(True)
                    self.mat = i
                    self.connect(self.blockMatrix, SIGNAL("clicked()"), self.gotoMAT)
                    self.blockList += ["MATRIX"]
                elif "OUTPUT LOCATIONS" in self.table.item(i, 1).text():
                    self.blockSpecialOut.setEnabled(True)
                    self.spe = i
                    self.connect(self.blockSpecialOut, SIGNAL("clicked()"), self.gotoSPE)
                    self.blockList += ["SPECIAL OUTPUT"]
                elif "INPUT FILE" in self.table.item(i, 1).text():
                    self.blockInput.setEnabled(True)
                    self.inp = i
                    self.connect(self.blockInput, SIGNAL("clicked()"), self.gotoINP)
                    self.blockList += ["INPUT"]
                elif "OUTPUT FILE" in self.table.item(i, 1).text():
                    self.blockOutput.setEnabled(True)
                    self.out = i
                    self.connect(self.blockOutput, SIGNAL("clicked()"), self.gotoOUT)
                    self.blockList += ["OUTPUT"]
                elif self.table.item(i, 1).text().startsWith("OPERATION OF CONTROL"):
                    self.blockStructures.setEnabled(True)
                    self.con = i
                    self.connect(self.blockStructures, SIGNAL("clicked()"), self.gotoCON)
                    self.blockList += ["CTRL STRUCTURES"]
                elif self.table.item(i, 1).text().startsWith("FUNCTION"):
                    self.blockFnTables.setEnabled(True)
                    self.fun = i
                    self.connect(self.blockFnTables, SIGNAL("clicked()"), self.gotoFUN)
                    self.blockList += ["FUNCTION TABLES"]
                elif self.table.item(i, 1).text().startsWith("FREE NODE"):
                    self.blockFreeNode.setEnabled(True)
                    self.fre = i
                    self.connect(self.blockFreeNode, SIGNAL("clicked()"), self.gotoFRE)
                    self.blockList += ["FREE NODE"]
                elif self.table.item(i, 1).text().startsWith("BACKWATER"):
                    self.blockBackwater.setEnabled(True)
                    self.bw = i
                    self.connect(self.blockBackwater, SIGNAL("clicked()"), self.gotoBW)
                    self.blockList += ["BACKWATER"]
                self.blockLines += [i]

# ===================================================================================
#Stroll to a block (takes arguments from Hide/Show buttons functions above)
    def gotoRUN(self):
        self.table.setCurrentCell(self.table.rowCount()-1, 0)
        self.table.setCurrentCell(self.run, 0)
    def gotoBRA(self):
        self.table.setCurrentCell(self.table.rowCount()-1, 0)
        self.table.setCurrentCell(self.bra, 0)
    def gotoTRI(self):
        self.table.setCurrentCell(self.table.rowCount()-1, 0)
        self.table.setCurrentCell(self.tri, 0)
    def gotoMAT(self):
        self.table.setCurrentCell(self.table.rowCount()-1, 0)
        self.table.setCurrentCell(self.mat, 0)
    def gotoSPE(self):
        self.table.setCurrentCell(self.table.rowCount()-1, 0)
        self.table.setCurrentCell(self.spe, 0)
    def gotoINP(self):
        self.table.setCurrentCell(self.table.rowCount()-1, 0)
        self.table.setCurrentCell(self.inp, 0)
    def gotoOUT(self):
        self.table.setCurrentCell(self.table.rowCount()-1, 0)
        self.table.setCurrentCell(self.out, 0)
    def gotoCON(self):
        self.table.setCurrentCell(self.table.rowCount()-1, 0)
        self.table.setCurrentCell(self.con, 0)
    def gotoFUN(self):
        self.table.setCurrentCell(self.table.rowCount()-1, 0)
        self.table.setCurrentCell(self.fun, 0)
    def gotoFRE(self):
        self.table.setCurrentCell(self.table.rowCount()-1, 0)
        self.table.setCurrentCell(self.fre, 0)
    def gotoBW(self):
        self.table.setCurrentCell(self.table.rowCount()-1, 0)
        self.table.setCurrentCell(self.bw, 0)

# ===================================================================================
#INPUT TABLE SETUP (called when a file is opened or reloaded)

    def updateTable(self, current=None):
        self.table.clear()
        self.table.setRowCount(len(self.datacontainer))
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Code", "Text"])
        self.table.setAlternatingRowColors(False)
        self.table.setStyleSheet(("background-color: rgb(255, 255, 255);\n"
"font: 8pt \"Courier\";"))
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        selected = None
        for row, datatext in enumerate(self.datacontainer):
            item = QTableWidgetItem(datatext.linenumber)
            if current is not None and current == id(datatext):
                selected = item
            self.updateItem(row, datatext, item)
        self.table.setVisible(False)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.setVisible(True)
        if selected is not None:
            selected.setSelected(True)
            self.table.setCurrentItem(selected)
            self.table.scrollToItem(selected)

    def updateItem(self, row, datatext, item):
        item.setData(Qt.UserRole,
                        QVariant(long(id(datatext))))
        code = datatext.code
        if code != datatext.UNKNOWNCODE:
            item = QTableWidgetItem("{0}".format(code))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item)
        todisplay = datatext.todisplay
        self.table.setItem(row, 1, QTableWidgetItem(todisplay))

# ===================================================================================
#LINE INTERPRETER (called when a line on the table is clicked)

    def readLine(self):
        rcode = None
        rtext = None
        row = self.table.currentRow()
        self.table.setCurrentCell(row, 0)
        if row > -1:
            item = self.table.item(row, 0)
            rcode = item.text()
            item2 = self.table.item(row, 1)
            rtext = item2.text()
        if rcode is not None and rtext is not None:
            global filetype
            if filetype == "FEQ":
                tobrowser = self.datacontainer.interpret(rcode, rtext)
            elif filetype == "FTL":
                tobrowser = self.datacontainer.interpretFTL(rcode, rtext)
            self.textBrowser.clear()
            self.textBrowser.append(tobrowser)
        else:
            self.textBrowser.clear()            
            self.textBrowser.append("No data.")

# ===================================================================================
#MULTILINE EDITOR (opens a text editor for easy multi-line editing)

    def multiLineEditor(self):
        row = self.table.currentRow()
        self.multiLine = QTextEdit(self.splitter)
        self.multiLine.clear()
        i = -1
        row = self.table.rowCount()
        while i != row -1:
            i += 1
            self.multiLine.append(self.table.item(i, 1).text())
        cursor = QTextCursor(self.multiLine.document().findBlockByLineNumber(row))
        self.multiLine.setGeometry(10, 70, 745, 561)
        self.multiLine.setLineWrapMode(QTextEdit.NoWrap)
        #self.multiLine.moveCursor(cursor)
        self.multiLine.setWindowTitle("Multi Line Text Editor")
        font = QFont()
        font.setFamily(QString.fromUtf8("Courier"))
        self.multiLine.setFont(font)

        global filetype
        if filetype is None:
            # self.multiLine.createFeqButton = QPushButton(self.multiLine)
            # self.multiLine.createFeqButton.setMinimumSize(QSize(200,70))
            # self.multiLine.createFeqButton.setText("Create FEQ file")
            # self.connect(self.multiLine.createFeqButton, SIGNAL("clicked()"), self.applyFEQ)
            # self.multiLine.createFequtlButton = QPushButton(self.multiLine)
            # self.multiLine.createFequtlButton.setMinimumSize(QSize(200,70))
            # self.multiLine.createFequtlButton.setText("Create FEQUTL file")
            # self.connect(self.multiLine.createFequtlButton, SIGNAL("clicked()"), self.applyUTL)

            self.multiLine.hbox = QHBoxLayout()
            self.multiLine.hbox.addStretch(1)
            # self.multiLine.hbox.addWidget(self.multiLine.createFeqButton)
            # self.multiLine.hbox.addWidget(self.multiLine.createFequtlButton)
            self.multiLine.vbox = QVBoxLayout()
            self.multiLine.vbox.addStretch(1)
            self.multiLine.vbox.addLayout(self.multiLine.hbox)
            self.multiLine.setLayout(self.multiLine.vbox)
            
        else:
            self.multiLine.insertEditsButton = QPushButton(self.multiLine)
            self.multiLine.insertEditsButton.setMinimumSize(QSize(200,70))
            self.multiLine.insertEditsButton.setText("Apply Edits")
            self.connect(self.multiLine.insertEditsButton, SIGNAL("clicked()"), self.applyEdits)

            self.multiLine.hbox = QHBoxLayout()
            self.multiLine.hbox.addStretch(1)
            self.multiLine.hbox.addWidget(self.multiLine.insertEditsButton)
            self.multiLine.vbox = QVBoxLayout()
            self.multiLine.vbox.addStretch(1)
            self.multiLine.vbox.addLayout(self.multiLine.hbox)
            self.multiLine.setLayout(self.multiLine.vbox)

        self.multiLine.cancelButton = QPushButton(self.multiLine)
        self.multiLine.cancelButton.setMinimumSize(QSize(200,70))
        self.multiLine.cancelButton.setText("Back to Main Window")
        self.connect(self.multiLine.cancelButton, SIGNAL("clicked()"), self.cancelEdits)
        self.multiLine.hbox.addWidget(self.multiLine.cancelButton)

        self.table.hide()
        self.textBrowser.hide()
        if self.form is not None:
            self.form.close()
        if filetype != "FTL":
            self.mapButton.setEnabled(True)
            self.actionMap_Mode.setEnabled(True)
        self.textButton.setEnabled(False)
        self.actionMulti_line_Text.setEnabled(False)
        self.multiLine.show()

    def applyEdits(self):
        global filetype
        with open('input', 'w') as inputFile:
            inputFile.write(str(self.multiLine.toPlainText()))
        fname = QString("input")
        if filetype == "FEQ":
            ok, msg = self.datacontainer.load(fname)
            self.updateTable()
            self.textBrowser.clear()
        elif filetype == "FTL":
            ok, msg = self.datacontainer.loadFTL(fname)
            self.updateTable()
            self.textBrowser.clear()
                
        tempFile = QFile("input")
        tempFile.remove()
        self.multiLine.close()
        self.table.show()
        self.textBrowser.show()
        self.textButton.setEnabled(True)
        self.actionMulti_line_Text.setEnabled(True)

    def cancelEdits(self):
        if self.multiLine is not None:
            self.multiLine.close()
        if self.form is not None:
            self.form.close()
        self.table.show()
        self.textBrowser.show()
        self.textButton.setEnabled(True)
        self.actionMulti_line_Text.setEnabled(True)
        global filetype
        if filetype != "FTL":
            self.mapButton.setEnabled(True)
            self.actionMulti_line_Text.setEnabled(True)

    def applyFEQ(self):
        global filetype
        filetype = "FEQ"
        self.applyEdits()
        self.runButton.setEnabled(True)
        self.actionRun.setEnabled(True)
        self.reloadButton.setEnabled(True)
        self.actionReload.setEnabled(True)
        self.mapButton.setEnabled(True)
        self.actionSave.setEnabled(True)
        self.actionSave_As.setEnabled(True)
        self.hidebuttons()
        self.showbuttons()
        self.cancelEdits()
    def applyUTL(self):
        global filetype
        filetype = "FTL"
        self.applyEdits()
        self.runButton.setEnabled(True)
        self.actionRun.setEnabled(True)
        self.reloadButton.setEnabled(True)
        self.actionReload.setEnabled(True)
        self.mapButton.setEnabled(False)
        self.actionSave.setEnabled(True)
        self.actionSave_As.setEnabled(True)
        self.hidebuttons()
        self.cancelEdits()
        

            
# ===================================================================================
#DISPLAY MANUAL FROM LINKS

    def openSection(self, url):
        self.section = QWebView()
        self.section.setWindowTitle("Manual")
        self.section.load(QUrl(url))
        self.section.show()

# ===================================================================================
#RUN FEQ OR FEQUTL MODEL

    def runProgram(self):
        global filetype

        if filetype == "FEQ":
            if os.path.isfile("feq_1061.exe"):
                pass
            else:
                ctypes.windll.user32.MessageBoxW(0, "Missing file error. - Unable to find locale feq_1061.exe file", "Error", 0)
                return
        elif filetype == "FTL":        
            if os.path.isfile("fequtl.exe"):
                pass
            else:
                ctypes.windll.user32.MessageBoxW(0, "Missing file error. - Unable to find locale fequtl.exe file", "Error", 0)
                return

        # Here we create a TextBox that contains all of the data from the table
        # That text box is saved to a file named "input"
        inputText = QTextEdit()
        i = -1
        row = self.table.rowCount()
        while i != row -1:
            i += 1
            inputText.append(self.table.item(i, 1).text())
        with open('input', 'w') as inputFile:
            inputFile.write(str(inputText.toPlainText()))
        # The file "input" is run through the models.
        fname = "input"
        if " " in fname:
            warning_space = QMessageBox.about(self, "WARNING",
                          """<p><b><font color=red>WARNING:</font></b></p>
                            FEQ and FEQUTL cannot read files within paths that contain
                            spaces, please remove spaces from the filename or folders in
                            the path.""")
        if len(fname) > 64:
            warning_length = QMessageBox.about(self, "WARNING",
                          """<p><b><font color=red>WARNING:</font></b></p>
                            FEQ and FEQUTL cannot read files whose paths exceed 64 characters,
                            please move file to a shorter path.""")
        if filetype == "FEQ":
            call("feq_1061.exe %s output" % fname)
            self.viewresults = QPlainTextEdit()
            self.viewresults.setGeometry(10, 70, 745, 561)
            self.viewresults.setWindowTitle("results")
            results = open("output").read()
            self.viewresults.setPlainText(results)
            self.viewresults.show()
        elif filetype == "FTL":
            call("fequtl.exe %s output outtable" % fname)
            self.viewresults = QPlainTextEdit()
            self.viewresults.setGeometry(10, 70, 745, 561)
            self.viewresults.setWindowTitle("results")
            results = open("output").read()
            self.viewresults.setPlainText(results)
            self.viewresults.show()
            self.viewtable = QPlainTextEdit()
            self.viewtable.setGeometry(10, 70, 745, 561)
            self.viewtable.setWindowTitle("tables")
            tables = open("outtable").read()
            self.viewtable.setPlainText(tables)
            self.viewtable.show()

            self.viewtable.save_table_file = QPushButton(self.table)
            self.viewtable.save_table_file.setMinimumSize(QSize(100, 20))
            self.viewtable.save_table_file.setText("Save Table File")
            self.connect(self.viewtable.save_table_file, SIGNAL("clicked()"), self.Save_Table_File)
            self.viewtable.hbox = QHBoxLayout()
            self.viewtable.hbox.addStretch(1)
            self.viewtable.hbox.addWidget(self.viewtable.save_table_file)
            self.viewtable.vbox = QVBoxLayout()
            self.viewtable.vbox.addLayout(self.viewtable.hbox)
            self.viewtable.vbox.addStretch(1)
            self.viewtable.setLayout(self.viewtable.vbox)
        
        self.viewresults.save_output_file = QPushButton(self.viewresults)
        self.viewresults.save_output_file.setMinimumSize(QSize(100, 20))
        self.viewresults.save_output_file.setText("Save Output File")
        self.connect(self.viewresults.save_output_file, SIGNAL("clicked()"), self.Save_Output_File)
        self.viewresults.hbox = QHBoxLayout()
        self.viewresults.hbox.addStretch(1)
        self.viewresults.hbox.addWidget(self.viewresults.save_output_file)
        self.viewresults.vbox = QVBoxLayout()
        self.viewresults.vbox.addLayout(self.viewresults.hbox)
        self.viewresults.vbox.addStretch(1)
        self.viewresults.setLayout(self.viewresults.vbox)
        

        tempFile = QFile("input")
        tempFile.remove()

    def Save_Output_File(self):
        outname = unicode(QFileDialog.getSaveFileName(self,
                                                    "FEQ Input - Save Output", "."))
        if outname:
            with open('%s' % outname, 'w') as saveFile:
                saveFile.write(str(self.viewresults.toPlainText()))

    def Save_Table_File(self):
        outname = unicode(QFileDialog.getSaveFileName(self,
                                                    "FEQ Input - Save Tables", "."))
        if outname:
            with open('%s' % outname, 'w') as saveFile:
                saveFile.write(str(self.viewtable.toPlainText()))
        
        
# ===================================================================================
#MAP VIEW (window that displays input information in the form of a dialog)

    def mapView(self):
        if filetype == None:
            self.form = mapview.MapView(self.mapButton, self.actionMap_Mode, \
                                        self.textBrowser, None, self)
        else:
            self.form = mapview.MapView(self.mapButton, self.actionMap_Mode, \
                                        self.textBrowser, self.table, self)
        self.table.hide()
        self.textBrowser.hide()
        if self.multiLine is not None:
            self.multiLine.close()
        self.textButton.setEnabled(True)
        self.actionMulti_line_Text.setEnabled(True)
        self.mapButton.setEnabled(False)
        self.actionMap_Mode.setEnabled(False)
        self.splitter.addWidget(self.form)

# ===================================================================================
#SEARCH BAR

    def searchDialog(self):
        TxtToSearch = self.searchbar.text()
        form = searchwindow.SearchWindow(self.table, self.blockList, self.blockLines, \
                                         self, TxtToSearch)
        form.show()
        
        

# ===================================================================================
#GRAPHS (OPENS FEQ-GDI)

    def feqGDI(self):
        inputText = QTextEdit()
        i = -1
        row = self.table.rowCount()
        while i != row -1:
            i += 1
            inputText.append(self.table.item(i, 1).text())
        if filetype == "FEQ":
            with open('input.feq', 'w') as inputFile:
                inputFile.write(str(inputText.toPlainText()))
            fname = "input.feq"
        elif filetype == "FTL":
            with open('input.ftl', 'w') as inputFile:
                inputFile.write(str(inputText.toPlainText()))
            fname = "input.ftl"
        else:
            fname = None
        
        if os.path.isfile("FEQ-GDI.jar"):
            # os.system("FEQ-GDI.jar %s" % fname)
            os.system("javaw -jar FEQ-GDI.jar %s" % fname)
        else:
            ctypes.windll.user32.MessageBoxW(0, "Missing file error. - Unable to find locale FEQ-GDI.jar file", "Error", 0)
            return

        tempFile = QFile(fname)
        tempFile.remove()


# ===================================================================================
#These lines call for the application to display    


app = QApplication(sys.argv)
form = FEQinput()

form.show()
app.exec_()
