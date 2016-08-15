from PyQt4.QtGui import *
from PyQt4.QtCore import *
import ui_searchwindow

class SearchWindow(QDialog, ui_searchwindow.Ui_Dialog):

    def __init__(self, table, blocklist, blocklines, \
                 parent=None, TxtToSearch=None):
        super(SearchWindow, self).__init__(parent)
        self.setupUi(self)
        self.inputtable = table
        self.blocklines = blocklines
        
        self.connect(self.searchbutton, SIGNAL("clicked()"), self.doSearch)
        self.connect(self.cancel, SIGNAL("clicked()"), self.close)
        self.searchText.setText(TxtToSearch)
        
        self.searchFile = QTextEdit()
        self.blocks.clear()
        self.blocks.addItems(blocklist)

        self.Dirty = False
        
        
        
    def doSearch(self):
        row = self.inputtable.rowCount()
        
        if self.checkBox.isChecked():
            self.checked()
        else:
            self.startI = -1
            self.maxI = row - 1

        if not self.Dirty:
            self.i = self.startI
        
        self.searchFile.clear()
        tried = 0

        if self.i < self.startI or self.i > self.maxI:
            self.i = self.startI
        
        while self.i != self.maxI:
            self.i += 1
            self.searchFile.append(self.inputtable.item(self.i, 1).text())
            if self.searchText.text().toLower() \
               in self.searchFile.toPlainText().toLower():
                self.inputtable.setCurrentCell(self.i, 0)
                self.Dirty = True
                break
            if self.i == self.maxI:
                tried += 1
                self.i = self.startI
            if tried == 2:
                not_found = QMessageBox.about(self, "FIND",
                                              """<p>Finished searching file.</p>
                                                No matches found.""")
                break

    def checked(self):
        index = self.blocks.currentIndex()
        self.startI = self.blocklines[index]
        self.maxI = self.blocklines[index+1]
        self.startI -= 1
        self.maxI -= 1
        
