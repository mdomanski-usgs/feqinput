from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *

import bisect
import codecs
import copy_reg
import pickle
import gzip
import re
from PyQt4.QtCore import (QDataStream, QDate, QFile, QFileInfo,
        QIODevice, QString, QTextStream, Qt)
from PyQt4.QtCore import pyqtSignal as Signal
#from PyQt4.QtXml import (QDomDocument, QDomNode, QXmlDefaultHandler,
#        QXmlInputSource, QXmlSimpleReader)

#This is the data container for FEQinput. It will manage the data of the
#input files
#Developed by David & Pablo Ancalle at the USGS Illinois Water Science Center

# ===================================================================================
#READ

CODEC = "UTF-8"

def intFromQStr(qstr): #Check if necessary
    i, ok = qstr.toInt()
    if not ok:
        raise ValueError, unicode(qstr)
    return i

class DataText(object):

    UNKNOWNCODE = 0

    def __init__(self, linenumber=None, code=UNKNOWNCODE,
                 todisplay=None):
        self.linenumber = linenumber
        self.code = code
        self.todisplay = todisplay

class DataContainer(object):


    def __init__(self):
        self.__fname = QString()
        self.__datalist = []
        self.__dataFromId = {}
        self.__dirty = False
        self.globalVariables()

        
    def filename(self):
        return self.__fname
    

    @staticmethod #Check if still needed, probably not.
    def formats():
        return "*.feq"
    

    def __len__(self):
        return len(self.__datalist)


    def __iter__(self):
        for pair in iter(self.__datalist):
            yield pair[1]
            

    def load(self, fname=QString()):
        if not fname.isEmpty():
            self.__fname = fname
        return self.loadQTextStream()
        return False, "Failed to load: invalid file extension"
    

    def loadFTL(self, fname=QString()):
        if not fname.isEmpty():
            self.__fname = fname
        return self.loadQTextStreamFTL()
        return False, "Failed to load: invalid file extension"


  
    def loadQTextStream(self):
        error = None
        fh = None
        if fh is None: #check this, should be a TRY
            fh = QFile(self.__fname)
            if not fh.open(QIODevice.ReadOnly):
                raise IOError, unicode(fh.errorString())
            stream = QTextStream(fh)
            stream.setCodec(CODEC)
            self.clear(False)
            lino = 0
            keepadd = True
            while not stream.atEnd():
                if keepadd is not False:
                    line = stream.readLine()
                else:
                    keepadd = True
                lino += 1
                linenumber = lino
                todisplay = line
                if lino <= 3:                                          #Headings
                    code = "TITLE"
                elif line.startsWith(";") or line.startsWith("*"):     #Comments
                    code = "COM"
                elif line.startsWith("RUN CONTROL"):                   #Run Control Block
                    code = "BLK"
                elif line.startsWith("NBRA"):
                    code = "NBRA"
                elif line.startsWith("NEX"):
                    code = "NEX"
                elif line.startsWith("SOPER"):
                    code = "SOPER"
                elif line.startsWith("POINT"):
                    code = "POINT"
                elif line.startsWith("DIFFUS"):
                    code = "DIFFUS"
                elif line.startsWith("MINPRT"):
                    code = "MINPRT"
                elif line.startsWith("LAGTSF"):
                    code = "LAGTSF"
                elif line.startsWith("WIND"):
                    code = "WIND"
                elif line.startsWith("UNDERFLOW"):
                    code = "UNDERF"
                elif line.startsWith("ZL"):
                    code = "ZL"
                elif line.startsWith("STIME"):
                    code = "STIME"
                elif line.startsWith("ETIME"):
                    code = "ETIME"
                elif line.startsWith("GRAV"):
                    code = "GRAV"
                elif line.startsWith("NODEID"):
                    code = "NODEID"
                elif line.startsWith("SSEPS"):
                    code = "SSEPS"
                elif line.startsWith("PAGE"):
                    code = "PAGE"
                elif line.startsWith("EPSSYS"):
                    code = "EPSSYS"
                elif line.startsWith("ABSTOL"):
                    code = "ABSTOL"
                elif line.startsWith("EPSFAC"):
                    code = "EPSFAC"
                elif line.startsWith("MKNT"):
                    code = "MKNT"
                elif line.startsWith("NUMGT"):
                    code = "NUMGT"
                elif line.startsWith("OUTPUT="):
                    code = "OUTPUT"
                elif line.startsWith("PRTINT"):
                    code = "PRTINT"
                elif line.startsWith("DPTIME"):
                    code = "DPTIME"
                elif line.startsWith("GEQOPT"):
                    code = "GEQOPT"
                elif line.startsWith("EPSB"):
                    code = "EPSB"
                elif line.startsWith("MAXIT"):
                    code = "MAXIT"
                elif line.startsWith("SFAC"):
                    code = "SFAC"
                elif line.startsWith("TAUFAC"):
                    code = "TAUFAC"
                elif line.startsWith("QSMALL"):
                    code = "QSMALL"
                elif line.startsWith("QCHOP"):
                    code = "QCHOP"
                elif line.startsWith("IFRZ"):
                    code = "IFRZ"
                elif line.startsWith("MAXDT"):
                    code = "MAXDT"
                elif line.startsWith("MINDT"):
                    code = "MINDT"
                elif line.startsWith("AUTO"):
                    code = "AUTO"
                elif line.startsWith("SITER"):
                    code = "SITER"
                elif line.startsWith("LFAC"):
                    code = "LFAC"
                elif line.startsWith("HFAC"):
                    code = "HFAC"
                elif line.startsWith("MRE"):
                    code = "MRE"
                elif line.startsWith("FAC"):
                    code = "FAC"
                elif line.startsWith("DWT"):
                    code = "DWT"
                elif line.startsWith("BWT"):
                    code = "BWT"
                elif line.startsWith("BWFDSN"):
                    code = "BWFDSN"
                elif line.startsWith("CHKGEO"):
                    code = "CHKGEO"
                elif line.startsWith("ISTYLE"):
                    code = "ISTYLE"
                elif line.startsWith("EXTTOL"):
                    code = "EXTTOL"
                elif line.startsWith("SQREPS"):
                    code = "SQREPS"
                elif line.startsWith("OLD_SUMMARY"):
                    code = "OLD"
                elif line.startsWith("NEW GENSCN OUTPUT"):
                    code = "GENSCN"
                    while line != ';':
                        if line.startsWith(';'):
                            self.add(DataText(linenumber, "COM", todisplay))
                        else:
                            self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line

                elif line.startsWith("BRANCH DESCRIPTION"):            #Branch Description
                    code = "BLK"
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while line.startsWith("BNUM") \
                          or line.startsWith(";") \
                          or line.startsWith(" ") \
                          or line[0:] == "" \
                          or line.startsWith("1") \
                          or line.startsWith("2") \
                          or line.startsWith("3") \
                          or line.startsWith("4") \
                          or line.startsWith("5") \
                          or line.startsWith("6") \
                          or line.startsWith("7") \
                          or line.startsWith("8") \
                          or line.startsWith("9") \
                          or line.startsWith("0") \
                          or line.startsWith("*") \
                          or line.startsWith("-"):
                        if line.startsWith("BNUM"):
                            bnum = line[5:10]
                            if " " in bnum:
                                bnum.replace(" ", "")
                            code = "BRA %s" % bnum
                            
                            
                            self.add(DataText(linenumber, code, todisplay))
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line
                            while line.startsWith(";") or line.startsWith("*"):
                                self.add(DataText(linenumber, code, todisplay))
                                line = stream.readLine()
                                lino += 1
                                linenumber = lino
                                todisplay = line
                                if line.startsWith(" NODE") or "NODE" in line:
                                    break

                            if "NODE" in line:

                                maxee = len(line)
                                order = code[4:]

                                cc = 0
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global nodeL
                                nodeL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global nodeidL
                                nodeidL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global xnumL
                                xnumL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global stationL
                                stationL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global elevationL
                                elevationL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global kaL
                                kaL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global kdL
                                kdL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global htabL
                                htabL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global azmL
                                azmL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global cfL
                                cfL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global ycL
                                ycL[order] = ee
                            

                            
                                
                                
                            
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    lino -= 1
                    keepadd = False
                    

                
                elif line.startsWith("TRIBUTARY AREA"):                #Tributary area
                    code = "BLK"
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while line.startsWith("HOME") \
                          or line.startsWith("TSFDSN") \
                          or line.startsWith("FFFDSN") \
                          or line.startsWith("NLUSE") \
                          or line.startsWith("NGAGE") \
                          or line.startsWith(" ") \
                          or line.startsWith("BRANCH") \
                          or line[0:] == "" \
                          or line.startsWith("NODE") \
                          or line.startsWith(";") \
                          or line.startsWith("*"):
                        if stream.atEnd():
                            break
                        if not line.startsWith("BRANCH"):
                            code = "TRBP"
                            self.add(DataText(linenumber, code, todisplay))
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line
                        else:
                            tbnum = line[7:12]
                            if " " in tbnum:
                                tbnum.replace(" ", "")
                            code = "TBRA %s" % tbnum
                            
                            self.add(DataText(linenumber, code, todisplay))
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line

                            while line.startsWith(";") or line.startsWith("*"):
                                self.add(DataText(linenumber, code, todisplay))
                                line = stream.readLine()
                                lino += 1
                                linenumber = lino
                                todisplay = line
                                if line.startsWith(" NODE") or line.startsWith("NODE"):
                                    break

                            if line.startsWith(" NODE") or line.startsWith("NODE"):
                                maxee = len(line)
                                order = code[5:]

                                cc = 0
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global tnodeL
                                tnodeL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global tgageL
                                tgageL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global timprvL
                                timprvL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global tfgrssL
                                tfgrssL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global tmgrssL
                                tmgrssL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global tsgrssL
                                tsgrssL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global tforstL
                                tforstL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break  
                                ee -= 1
                                global tagricL
                                tagricL[order] = ee

                                cc = ee
                                ee = cc + 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        cc = tagricL[order]
                                        ee = tagricL[order] + 1
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee: 
                                        break  
                                ee -= 1
                                global ttotalL
                                ttotalL[order] = ee

                                self.add(DataText(linenumber, code, todisplay))
                                line = stream.readLine()
                                lino += 1
                                linenumber = lino
                                todisplay = line

                            while line.startsWith(" ") or line.startsWith("*") \
                                  or line.startsWith(";") or line.startsWith("DTEN") \
                                  or line.startsWith("DLAY") or line.startsWith("-1"):
                                self.add(DataText(linenumber, code, todisplay))
                                line = stream.readLine()
                                lino += 1
                                linenumber = lino
                                todisplay = line

                    lino -= 1
                    keepadd = False
                                

                                                                       #Network Matrix
                elif "MATRIX" in line:
                    code = "BLK"
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    mxnum = 0
                    while not "-1" in line[:5]:
                        if line.startsWith(" CODE"):
                            code = "MHEAD"
                        else:
                            if line.startsWith(";") or line.startsWith("*"):
                                code = "MXC"
                            else:
                                cc = 0
                                ee = 1
                                while line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > 10:
                                        break
                                while not line[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if not line[cc:ee] == " ":
                                        break
                                    if ee > 10:
                                        break
                                mtrxcd = line[:ee]
                                mtrxcd.replace(" ","")
                                mtrxcd.replace("	","")
                                global mxstore
                                if not mtrxcd == "":
                                    code = "MX%s" % mtrxcd
                                    alsocode = code
                                    #if mtrxcd == "5":             
                                    mxstore = str(line)      # Here I am storing the contents of the line in 'mxstore'
                                if mtrxcd == "":
                                    mxnum += 1                  # This integer will identify matrix lines in interpret
                                    mxnumb = str(mxnum)
                                    global mxparent
                                    mxparent[mxnumb] = mxstore   # Here I am storing the contents of the parent line in 'mxparent'
                                    code = "%s-%s" % (alsocode, mxnum)       # and assigning a new code to later use in interpret
                                    
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    code = "MX"
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while line.startsWith(";") or line.startsWith("*") or line == "":
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    if line.startsWith("BNODE"):
                        code = "MTXB"
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    lino -= 1
                    keepadd = False
                

                elif "OUTPUT LOCATIONS" in line:                       #Special Output Locations
                    code = "BLK"
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while not line.startsWith("   -1"):
                        code = "OUTL"
                        if "BRA" in line or "NODE" in line:
                            cc = 0
                            ee = cc + 1
                            maxee = len(line)
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            global outbraL
                            outbraL = cc
                            global outbraT
                            outbraT = line[:cc]
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            global outnodeL
                            outnodeL = cc
                            global outnodeT
                            outnodeT = line[outbraL:cc]
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            global outhead1L
                            outhead1L = cc
                            global outhead1T
                            outhead1T = line[outnodeL:cc]
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            global outhead2L
                            outhead2L = cc
                            global outhead2T
                            outhead2T = line[outhead1L:cc]
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    code = "OUTL"
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    lino -= 1
                    keepadd = False

                elif "INPUT FILE" in line:                             #Input Files Block
                    code = "BLK"
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while not line.startsWith("   -1") and not line.startsWith("  -1"):
                        code = "INPF"
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    code = "INPF"
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    lino -= 1
                    keepadd = False


                elif "OUTPUT FILE" in line:                            #Output Files Block
                    code = "BLK"
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while not line.startsWith("   -1") and not line.startsWith("  -1"):
                        code = "OUTF"
                        if line.startsWith(" UNIT") or line.startsWith(" ACTN") \
                           or "ACTN" in line:
                            cc = 0
                            ee = cc + 1
                            maxee = len(line)
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            global outfunitL
                            outfunitL = cc
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            global outfbraL
                            outfbraL = cc
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            global outfnodeL
                            outfnodeL = cc
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            global outfitemL
                            outfitemL = cc
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            global outftypeL
                            outftypeL = cc
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            global outfnameL
                            outfnameL = cc
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    code = "OUTF"
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    lino -= 1
                    keepadd = False

                    
                elif line.startsWith("OPERATION OF CONTROL"):          #Control Structures
                    code = "BLK"
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while line.startsWith(";") or line.startsWith("*"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenymber = lino
                        todisplay = line
                    while not line.startsWith("BLK=-1"):
                        csnum = line[3:]
                        if csnum.startsWith("=0000"):
                            csnum.replace("=0000", "")
                        if csnum.startsWith("=000"):
                            csnum.replace("=000", "")
                        if csnum.startsWith("=00"):
                            csnum.replace("=00", "")
                        if csnum.startsWith("=0"):
                            csnum.replace("=0", "")
                        csnum.replace("=", "")
                        code = "CtrS %s" % csnum

                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line

                        while line.startsWith(";") or line.startsWith("*"):
                            self.add(DataText(linenumber, code, todisplay))
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line

                        btype = line[8:]
                        global csBLKTYPE
                        if btype.startsWith("GATE"):
                            csBLKTYPE[csnum] = "GATE"
                        elif btype.startsWith("PUMP"):
                            csBLKTYPE[csnum] = "PUMP"

                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line

                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line

                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line

                        global csbranL
                        global csnodeL
                        global cskeyL
                        global csmnrateL

                        if csBLKTYPE[csnum] == "GATE":
                            maxee = len(line)
                            order = csnum

                            cc = 0
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            csbranL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            csnodeL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            cskeyL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            global csmodeL
                            csmodeL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            csmnrateL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            global cslrateL
                            cslrateL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            global cslowlimL
                            cslowlimL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            global cshghlimL
                            cshghlimL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            global cshrateL
                            cshrateL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            global cslpriL
                            cslpriL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            global csnpriL
                            csnpriL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            global cshpriL
                            cshpriL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            global csdpdtL
                            csdpdtL[order] = ee

                            self.add(DataText(linenumber, code, todisplay))
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line


                        elif csBLKTYPE[csnum] == "PUMP":
                            maxee = len(line)
                            order = csnum

                            cc = 0
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            csbranL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            csnodeL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            cskeyL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            csmnrateL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            global csriseL
                            csriseL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            global csfallL
                            csfallL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            global csonprL
                            csonprL[order] = ee

                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break  
                            ee -= 1
                            global csofprL
                            csofprL[order] = ee
                        

                        while not line.startsWith("   -1"):
                            self.add(DataText(linenumber, code, todisplay))
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line

                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line

                    code = "CtrlS"
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    lino -= 1
                    keepadd = False



                    
                elif line.startsWith("FUNCTION"):                      #Function Tables
                    code = "BLK"
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while not line.startsWith("TABID=    -1") \
                          and not line.startsWith("TABID=   -1"):
                        if line.startsWith("TABID") or line.startsWith("TABLE"):
                            if line.startsWith("TABID"):
                                tabnum = line[6:]
                                tabnum.replace(" ","")
                                code = "TAB %s" % tabnum
                            elif line.startsWith("TABLE"):
                                tabnum = line[7:]
                                tabnum.replace(" ","")
                                code = "TAB %s" % tabnum
                            if tabnum.startsWith("-") and not tabnum == "-1":
                                code = "TAB-"
                                self.add(DataText(linenumber, code, todisplay))
                                line = stream.readLine()
                                lino += 1
                                linenumber = lino
                                todisplay = line
                            elif not tabnum.startsWith("-"):
                                self.add(DataText(linenumber, code, todisplay))
                                line = stream.readLine()
                                lino += 1
                                linenumber = lino
                                todisplay = line
                                tabtype = line[5:]
                                tabtype.replace(" ","")

                                if tabtype == 2:
                                    self.add(DataText(linenumber, code, todisplay))
                                    line = stream.readLine()
                                    lino += 1
                                    linenumber = lino
                                    todisplay = line

                                    self.add(DataText(linenumber, code, todisplay))
                                    line = stream.readLine()
                                    lino += 1
                                    linenumber = lino
                                    todisplay = line

                                while not "-1" in line:
                                    self.add(DataText(linenumber, code, todisplay))
                                    line = stream.readLine()
                                    lino += 1
                                    linenumber = lino
                                    todisplay = line

                                self.add(DataText(linenumber, code, todisplay))
                                line = stream.readLine()
                                lino += 1
                                linenumber = lino
                                todisplay = line
                            elif tabnum == "-1":
                                break
                        else:
                            code = "TAB F"
                            self.add(DataText(linenumber, code, todisplay))
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line

                        if line.startsWith("TABLE=-1") or line.startsWith("TABID=-1"):
                            break

                    code = "TAB E"
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line

                    lino -= 1
                    keepadd = False

                elif line.startsWith("FREE NODE"):                                    #FREE NODE
                    code = "BLK"
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line

                    code = "FRND"

                    while line.startsWith("*") or line.startsWith(";"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    
                    maxee = len(line)

                    cc = 0
                    ee = cc + 1
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break  
                    ee -= 1
                    global fnnodeL
                    fnnodeL = ee

                    cc = ee
                    ee = cc + 1
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break  
                    ee -= 1
                    global fnnodeidL
                    fnnodeidL = ee

                    cc = ee
                    ee = cc + 1
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break  
                    ee -= 1
                    global fndepthL
                    fndepthL = ee

                    cc = ee
                    ee = cc + 1
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break  
                    ee -= 1
                    global fndischargeL
                    fndischargeL = ee

                    cc = ee
                    ee = cc + 1
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break  
                    ee -= 1
                    global fnelevationL
                    fnelevationL = ee

                    while line.startsWith(" ") or line.startsWith("*") \
                          or line.startsWith(";") or line == "" or line.startsWith("F"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line

                    lino -= 1
                    keepadd = False
   

                elif line.startsWith("BACKWATER"):                                #BACKWATER ANALYSIS
                    code = "BLK"
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line

                    code = "BW"

                    end = False

                    while end == False:
                        while not " BRA" in line or line.startsWith(";") or line.startsWith("*"):
                            self.add(DataText(linenumber, code, todisplay)) #add table option
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line

                        maxee = len(line)

                        cc = 0
                        ee = cc + 1
                        while line[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not line[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        ee -= 1
                        global bwbraL
                        bwbraL = ee
                        cc = ee
                        ee = cc + 1
                        while line[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        ee -= 1
                        global bwcode1L
                        bwcode1L = ee
                        cc = ee
                        ee = cc + 1   

                        while not line[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break  
                        ee -= 1
                        global bwcode2L
                        bwcode2L = ee

                        cc = ee
                        ee = cc + 1
                        while line[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        ee -= 1
                        global bwelev1L
                        bwelev1L = ee

                        cc = ee
                        ee = cc + 1
                        while not line[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break  
                        ee -= 1
                        global bwelev2L
                        bwelev2L = ee

                        cc = ee
                        ee = cc + 1
                        while line[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        ee -= 1
                        global bwexnL
                        bwexnL = ee

                        cc = ee
                        ee = cc + 1
                        while not line[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break 

                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line

                        
                        while end == False:
                            bwbraLL = bwbraL + 1
                            if "-1" in line[:bwbraL] or "-1" in line[:bwbraLL]:
                                end = True
                            self.add(DataText(linenumber, code, todisplay))
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line
                        

                    lino -= 1
                    keepadd = False  


           
                    

                else:
                    code = "NOREAD"
                if keepadd is not False:
                    self.add(DataText(linenumber, code, todisplay))
            if fh is not None:
                fh.close()
            if error is not None:
                return False, error
            self.__dirty = False
            return True, "Loaded {0} records from {1}".format(
                    len(self.__datalist),
                    QFileInfo(self.__fname).fileName())




    def loadQTextStreamFTL(self):
        error = None
        fh = None
        if fh is None:
            fh = QFile(self.__fname)
            if not fh.open(QIODevice.ReadOnly):
                raise IOError, unicode(fh.errorString())
            stream = QTextStream(fh)
            stream.setCodec(CODEC)
            self.clear(False)
            lino = 0
            keepadd = True
            culvert = 0
            embankq = 0
            expcon = 0
            while not stream.atEnd():
                if keepadd is not False:
                    line = stream.readLine()
                else:
                    keepadd = True
                lino += 1
                linenumber = lino
                todisplay = line
                if line.startsWith("STDIN") or line.startsWith("STDOUT") \
                   or line.startsWith("STDTAB"):                         
                    code = "TITLE"
                elif line.startsWith(";") or line.startsWith("*"): 
                    code = "COM"
                elif line.startsWith("UNITS"):                 #HEADERS block
                    code = "UNIT"
                elif line.startsWith("NCMD"):
                    code = "NCMD"
                    global commands
                    commands = line[5:]
                    commands.replace(" ","")
                    commands = int(commands)
                    count = 1
                    while count <= commands:
                        count += 1
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                elif line.startsWith("DZLIM"):
                    code = "DZLI"
                elif line.startsWith("NRZERO"):
                    code = "NRZE"
                elif line.startsWith("USGSBETA"):
                    code = "USBE"
                elif line.startsWith("EPSARG"):
                    code = "EPSA"
                elif line.startsWith("EPSF"):
                    code = "EPSF"
                elif line.startsWith("EXTEND"):
                    code = "EXTE"
                elif line.startsWith("FEQX"):                           #FEQX block
                    if line.startsWith("FEQXLST"):
                        code = "FEQXL"
                        while not "-1" in line:
                            self.add(DataText(linenumber, code, todisplay))
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line
                    else:
                        if line.startsWith("FEQXEXT"):
                            code = "FEQXE"
                        else:
                            code = "FEQX"
                        while not " -1" in line[20:25]:
                            self.add(DataText(linenumber, code, todisplay))
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line
                elif line.startsWith("FTABIN"):                         #FTABIN block
                    code = "FTAB"
                    tabid = 0
                    while not tabid == "-1":
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                        if line.startsWith("TABLE"):
                            tabid = line[7:]
                            tabid.replace(" ","")
                        elif line.startsWith("TABID"):
                            tabid = line[6:]
                            tabid.replace(" ","")
                        elif line.startsWith("TABL"):
                            tabid = line[5:]
                            tabid.replace(" ","")
#################################################
                        """elif line.startsWith("REFL"):
                            self.add(DataText(linenumber, code, todisplay))
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line
                            maxee = len(line)
                            cc = 0
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            ee -= 1
                            global ftheadL
                            ftheadL = ee
                            cc = ee
                            ee = cc + 1
                            while line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            ee -= 1
                            global ftlowL
                            ftlowL = ee
                            cc = ee
                            ee = cc + 1   

                            while not line[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break

                            self.add(DataText(linenumber, code, todisplay))
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line"""

#######################################################
                        
                elif line.startsWith("CULVERT"):                        #CULVERT block
                    culvert += 1
                    code = "CULV %i" % culvert
                    while not line.startsWith("SFAC"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while line.startsWith(";") or line.startsWith("*"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    cc = 0
                    ee = cc + 1
                    maxee = len(line)
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global culvnode
                    culvnode[culvert] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global culvnodeid
                    culvnodeid[culvert] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global culvxnum
                    culvxnum[culvert] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global culvstation
                    culvstation[culvert] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global culvelev
                    culvelev[culvert] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global culvka
                    culvka[culvert] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global culvkd
                    culvkd[culvert] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global culvhtab
                    culvhtab[culvert] = cc
                    code = "CULVt %i" % culvert
                    while not "-1" in line[:culvnode[culvert]]:
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    code = "CULV %i" % culvert
                    while not line.startsWith("GSUBTB"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while line.startsWith(";") or line.startsWith("*"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    code = "CULVo %i" % culvert
                    cc = 0
                    ee = cc + 1
                    maxee = len(line)
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global culvoffset
                    culvoffset[culvert] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global culvcrest
                    culvcrest[culvert] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global culvwidth
                    culvwidth[culvert] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global culvapproach
                    culvapproach[culvert] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global culvsurface
                    culvsurface[culvert] = cc
                    while not "END" in line[:culvsurface[culvert]]:
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while line.startsWith(";") or line.startsWith("*"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    code = "CULVh %i" % culvert
                    while not "-1" in line:
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                elif line == "CHANRAT":                        #CHANRAT block
                    code = "CHAR"
                    while not "-1." in line:
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                elif line.startsWith("EMBANKQ"):                        #EMBANKQ block
                    embankq += 1
                    code = "EMBA %i" % embankq
                    while not line.startsWith("LABEL"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while line.startsWith(";") or line.startsWith("*"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    code = "EMBAo %i" % embankq
                    cc = 0
                    ee = cc + 1
                    maxee = len(line)
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global embaoffset
                    embaoffset[embankq] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global embacrest
                    embacrest[embankq] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global embawidth
                    embawidth[embankq] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global embaapproach
                    embaapproach[embankq] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global embasurface
                    embasurface[embankq] = cc
                    while not "END" in line[:embasurface[embankq]]:
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while line.startsWith(";") or line.startsWith("*"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    code = "EMBAh %i" % culvert
                    while not "-1" in line:
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                elif line == "EXPCON":                         #EXPCON block
                    expcon += 1
                    code = "EXPC %i" % expcon
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while line.startsWith(";") or line.startsWith("*"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while line.startsWith(";") or line.startsWith("*"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    cc = 00
                    ee = cc + 1
                    maxee = len(line)
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global exploc
                    exploc[expcon] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global exptab
                    exptab[expcon] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global expdist
                    expdist[expcon] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global expdatum
                    expdatum[expcon] = cc
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while line.startsWith(";") or line.startsWith("*"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while line.startsWith(";") or line.startsWith("*"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while line.startsWith(";") or line.startsWith("*"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while line.startsWith(";") or line.startsWith("*"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    cc = 00
                    ee = cc + 1
                    maxee = len(line)
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global expdir
                    expdir[expcon] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global exptab2
                    exptab2[expcon] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global expka
                    expka[expcon] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global expkd
                    expkd[expcon] = cc
                    while line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not line[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    global explabel
                    explabel[expcon] = cc
                    while not "-1." in line:
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    
                elif line == "MULCON":                                  #MULCON
                    code = "MULC"
                    while not line.startsWith("ROUG"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while line.startsWith(";") or line.startsWith("*"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    if line.startsWith("MUDL"):
                        while not line.startsWith("ROUG"):
                            self.add(DataText(linenumber, code, todisplay))
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                        while line.startsWith(";") or line.startsWith("*"):
                            self.add(DataText(linenumber, code, todisplay))
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line
                    keepadd = False
                elif line == "QCLIMIT":                                 #QCLIMIT
                    code = "QLIM"
                    while not line.startsWith("FACTOR"):
                        self.add(DataText(linenumber, code, todisplay))
                        line  = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    
                    while line.startsWith(";") or line.startsWith("*"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    keepadd = False

                elif line.startsWith("SEWER"):                                   #SEWER
                    code = "SEWR"
                    while not line.startsWith("N="):
                        self.add(DataText(linenumber, code, todisplay))
                        line  = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    
                    while line.startsWith(";") or line.startsWith("*"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    if line.startsWith("MUDL"):
                        while not line.startsWith("NMUD"):
                            self.add(DataText(linenumber, code, todisplay))
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line
                            if line.startsWith("MUDN"):
                                break
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                        while line.startsWith(";") or line.startsWith("*"):
                            self.add(DataText(linenumber, code, todisplay))
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line
                    keepadd = False
                elif line == "CRITQ":                                   #CRITQ
                    code = "CRITQ"
                    while not line.startsWith("DISCOEF"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    
                    while line.startsWith(";") or line.startsWith("*"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line

                elif line == "GRITTER":                                 #GRITTER
                    code = "GRIT"
                    while code == "GRIT":
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                        if "-1" in line:
                            break

                elif line == "MULPIPES":                                #MULPIPES
                    code = "MULP"
                    while code == "MULP":
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                        if line.startsWith("ROUG"):
                            break
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line
                    while line.startsWith(";") or line.startsWith("*"):
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    if line.startsWith("MUDL"):
                        while code == "MULP":
                            self.add(DataText(linenumber, code, todisplay))
                            line = stream.readLine()
                            lino += 1
                            linenumber = lino
                            todisplay = line
                            if line.startsWith("ROUG"):
                                break
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                    keepadd = False
                elif line == "XSINTERP":                                #XSINTERP
                    code = "XSIN"
                    while code == "XSIN":
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                        if "-1" in line[:5] and not (line.startsWith(";") or line.startsWith("*")):
                            break
                elif line == "HEC2X":                                   #HEC2X
                    code = "HEC2"
                    while code == "HEC2":
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                        if line.startsWith("SFAC"):
                            break
                elif line == "CHANNEL":                                 #CHANNEL
                    code = "CHAN"
                    while code == "CHAN":
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                        if line.startsWith("END"):
                            break
                elif line.startsWith("ENDCHAN"):
                    code = "CHAN"

                elif line == "UFGATE":                                  #UFGATE
                    code = "UFGT"
                    while code == "UFGT":
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                        if line.startsWith("FINPOW"):
                            break

                elif line == "ORIFICE":                                 #ORIFICE
                    code = "ORIF"
                    while code == "ORIF":
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                        if "Numbr" in line:
                            if not line.startsWith(";"):
                                break
                            if not line.startsWith("*"):
                                break
                    code = "ORIFa"
                    while code == "ORIFa":
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                        if "AppTb" in line:
                            if not line.startsWith(";"):
                                break
                            if not line.startsWith("*"):
                                break
                    code = "ORIFb"
                    self.add(DataText(linenumber, code, todisplay))
                    line = stream.readLine()
                    lino += 1
                    linenumber = lino
                    todisplay = line

                elif line == "AXIALPMP":                                #AXIALPMP
                    code = "AXLP"
                    while code == "AXLP":
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                        if "-1" in line:
                            break

                elif line == "PUMPLOSS":                                #PUMPLOSS
                    code = "PMPL"
                    while code == "PMPL":
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                        if "-1" in line:
                            break

                elif line.startsWith("SETSLOT"):                        #SETSLOT
                    code = "SETS"
                    while code == "SETS":
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                        if line.startsWith("ESLOT") or line.startsWith("YSLOT"):
                            break

                elif line == "LPRFIT":                                  #LPRFIT
                    code = "LPRF"
                    while code == "LPRF":
                        self.add(DataText(linenumber, code, todisplay))
                        line = stream.readLine()
                        lino += 1
                        linenumber = lino
                        todisplay = line
                        if "-1" in line:
                            break


                elif line.startsWith("        "):
                    code = "COM"
                elif line == "" or line == " ":
                    code = "blank"
                elif line.startsWith("FINISH"):                         #File end
                    code = "FIN"
                else:
                    code = "NOREAD"
                if keepadd is not False:
                    self.add(DataText(linenumber, code, todisplay))
            if fh is not None:
                fh.close()
            if error is not None:
                return False, error
            self.__dirty = False
            return True, "Loaded {0} records from {1}".format(
                    len(self.__datalist),
                    QFileInfo(self.__fname).fileName())
    

    def clear(self, clearFilename=True):
        self.__datalist = []
        self.__dataFromId = {}
        if clearFilename:
            self.__fname = QString()
        self.__dirty = False

    def add(self, datatext):
        key = datatext.linenumber
        bisect.insort_left(self.__datalist, [key, datatext])
        self.__dataFromId[id(datatext)] = datatext
        self.__dirty = True
        return True


    def dataFromId(self, id):
        return self.__dataFromId[id]


# ===================================================================================
#Global Variables - these will be defined at LOAD and called at INTERPRET

    def globalVariables(self):
        global nodeL           #Branch Description
        nodeL = {}
        global nodeidL
        nodeidL = {}
        global xnumL
        xnumL = {}
        global stationL
        stationL = {}
        global elevationL
        elevationL = {}
        global kaL
        kaL = {}
        global kdL
        kdL = {}
        global htabL
        htabL = {}
        global azmL
        azmL = {}
        global cfL
        cfL = {}
        global ycL
        ycL = {}

        global tnodeL          #Tributary Area
        tnodeL = {}
        global tgageL
        tgageL = {}
        global timprvL
        timprvL = {}
        global tfgrssL
        tfgrssL = {}
        global tmgrssL
        tmgrssL = {}
        global tsgrssL
        tsgrssL = {}
        global tforstL
        tforstL = {}
        global tagricL
        tagricL = {}
        global ttotalL
        ttotalL = {}

        global mxparent       #Matrix
        mxparent = {}

        global csBLKTYPE      #Control Structures
        csBLKTYPE = {}
        global csbranL
        csbranL = {}
        global csnodeL
        csnodeL = {}
        global cskeyL
        cskeyL = {}
        global csmodeL
        csmodeL = {}
        global csmnrateL
        csmnrateL = {}
        global cslrateL
        cslrateL = {}
        global cslowlimL
        cslowlimL = {}
        global cshghlimL
        cshghlimL = {}
        global cshrateL
        cshrateL = {}
        global cslpriL
        cslpriL = {}
        global csnpriL
        csnpriL = {}
        global cshpriL
        cshpriL = {}
        global csdpdtL
        csdpdtL = {}
        global csriseL
        csriseL = {}
        global csfallL
        csfallL = {}
        global csonprL
        csonprL = {}
        global csofprL
        csofprL = {}

        #------------------------------------

        global culvnode       # CULVERT block
        culvnode = {}
        global culvnodeid
        culvnodeid = {}
        global culvxnum
        culvxnum = {}
        global culvstation
        culvstation = {}
        global culvelev
        culvelev = {}
        global culvka
        culvka = {}
        global culvkd
        culvkd = {}
        global culvhtab
        culvhtab = {}
        global culvoffset
        culvoffset = {}
        global culvcrest
        culvcrest = {}
        global culvwidth
        culvwidth = {}
        global culvapproach
        culvapproach = {}
        global culvsurface
        culvsurface = {}

        global embaoffset     # EMBANKQ block
        embaoffset = {}
        global embacrest
        embacrest = {}
        global embawidth
        embawidth = {}
        global embaapproach
        embaapproach = {}
        global embasurface
        embasurface = {}

        global exploc         # EXPCON block
        exploc = {}
        global exptab
        exptab = {}
        global expdist
        expdist = {}
        global expdatum
        expdatum = {}
        global expdir
        expdir = {}
        global exptab2
        exptab2 = {}
        global expka
        expka = {}
        global expkd
        expkd = {}
        global explabel
        explabel = {}

# ===================================================================================
#INTERPRET

    def interpret(self, rcode, rtext):
        
        if rcode == "TITLE":                                           #Headings
            textback = """<b></b>The first three lines of the file are used to name
                        and describe
                        the project."""


        elif rcode == "COM":                                           #Comments
            textback = """Comment:<br>
                        <font color="blue">%s</font>""" % rtext[1:]
            
        elif rcode == "BLK":                                           #Blocks
            if rtext.startsWith(";") or rtext.startsWith("*"):
                textback = """Comment:<br><font color=blue>%s</font>""" % rtext
            else:
                textback = """<b>%s</b><br><br>
                        The input file is divided into several blocks that
                        describe different characteristics of the system.<br><br>

                        <b>Run Control Block</b> - general parameters of the
                        system<br><br>

                        <b>Branch Description Tables</b> - describes location
                        and elevation of nodes in each branch of the system<br><br>

                        <b>Tributary Area Specification</b> - areas for each
                        land use that are tributary to each computational
                        element.<br><br>

                        <b>Network Matrix Control</b> - defines flow and depth
                        relationship equations, boundary conditions, etc.<br><br>

                        <b>Special Output Locations</b> - specifies nodes where
                        output will be written to a designated file.<br><br>

                        <b>Input File Specification</b> - describes files used to input
                        flow or water-surface elevation at a flow-path end node.<br><Br>

                        <b>Output File Specification</b> - describes files to output
                        flow or water-surface elevation at any node in the stream
                        system.<br><br>

                        <b>Operation of Control Structures</b> - operation rules for
                        any dynamically operated control structure.<br><br>

                        <b>Function Tables</b> - tables referenced in other blocks
                        with flow, head, or other data.<br><br>

                        <b>Free Node Initial Conditions</b> - sign, elevation and
                        initial values of free nodes.<br><br>

                        <b>Backwater Analysis</b> - specifies initial flows and starting
                        depth at control points to perform B.W. computations.<br><br><br>

                        <a href="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_1.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext
            
        elif rcode == "NBRA":                                          #Run Control Block
            textback = """<b>NBRA</b> - Number of branches: <font color="blue">%s
                        </font><br><br>

                        Total number of branches in the stream system.<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[5:]
            
        elif rcode == "NEX":
            textback = """<b>NEX</b> - Number of flow-path end nodes: <font color="blue">
                        %s</font><br><br>

                        The numer of flow-path end nodes in the stream system must be
                        even because end nodes are always in pairs.<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[4:]
            
        elif rcode == "SOPER":
            what = "Control structures"
            if "YES" in rtext:
                textback = """%s are present.""" % what
            elif "NO" in rtext:
                textback = """%s are not present.""" % what
            else:
                textback = """<b><font color="red">Warning: User should specify if %s
                                are present (YES) or not (NO).</font></b>""" % what

            textback += """<br><br>If control structures are present, they will be operated
                        dynamically and the <b>OPERATION OF CONTROL STRUCTURES</b> block must
                        be present in the input file.<br><br>

                        Format:<br>
                        <b>SOPER</b> = YES if control structures are present.<br>
                        <b>SOPER</b> = NO if control structures are not present.<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
                
        elif rcode == "POINT":
            what = "Point flows"
            if "YES" in rtext:
                textback = """%s are present.""" % what
            elif "NO" in rtext:
                textback = """%s are not present.""" % what
            else:
                textback = """<b><font color="red">Warning: User should specify if %s
                                are present (YES) or not (NO).</font></b>""" % what

            textback += """<br><br>If point flows are present, the POINT FLOWS Block
                        needs to be included in the input file.<br><br>

                        Format:<br>
                        <b>POINT</b> = YES if point flows are present<br>
                        <b>POINT</b> = NO if point flows are not present<br>
                        <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
                
        elif rcode == "DIFFUS": #add DIFFUS numerical values (from manual)
            what = "Diffuse inflows from tributary areas"
            if "YES" in rtext:
                textback = """%s are present.""" % what
            elif "NO" in rtext:
                textback = """%s are not present.""" % what
            else:
                textback = """<b><font color="red">Warning: User should specify if %s
                                are present (YES) or not (NO).</font></b>""" % what

            textback += """<br><br>If tributaries are present, diffuse inflows from the land area
                        tributary to the stream system will be used in the simulation, and a
                        <b>TRIBUTARY AREA</b> block must be included in the input file. Additionally,
                        a <b>DTSF</b> must be present for computations.<br><br>

                        Format:<br>
                        <b>DIFFUS</b> = YES if tributaries are present.<br>
                        <b>DIFFUS</b> = NO if tributaries are not present.
                        <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

        elif rcode == "MINPRT":
            if rtext[7:] or rtext[8:] or rtext[9:] == "0":
                textback = """Summary output of each time step will be printed."""
            elif rtext[7:] or rtext[8:] or rtext[9:] == "1":
                textback = """Summary output of each time step will not be printed."""
            else:
                textback = """<b><font color="red">Warning: User should specify if summary
                                output will be printed (MINPRT=1) or not
                                (MINPRT=0).</font></b>"""

            textback += """<br><br>Format:<br>
                        If <b>MINPRT</b> = 0, summaries will be printed<br>
                        if <b>MINPRT</b> = 1, summary output will be supressed.
                        <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

        elif rcode == "LAGTSF":
            textback = """<b>LAGTSF</b> - This variable is a flag to signal lagging of diffuse inflows.<br><br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
                

        elif rcode == "WIND":
            if "YES" in rtext:
                textback = """Wind shear stress will be simulated."""
            elif "NO" in rtext:
                textback = """Wind shear stress will not be simulated."""
            else:
                textback = """<b><font color="red">Warning: User should specify
                                if wind shear
                                stress will be simulated (YES) or not (NO).</font></b>"""

            textback += """<br><br>If wind shear stress is to be simulated, the <b>WIND INFORMATION</b>
                        block must be present in the input file. Wind-shear stress is computed
                        for branches only and cannot be computed for level-pool reservoirs.<br><br>
                        Format:<br>
                        <b>WIND</b> = YES if wind shear stress will be simulated.<br>
                        <b>WIND</b> = NO if wind shear stress will not be simulated.
                        <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

        elif rcode == "UNDERF":
            textback = """<b>UNDERF</b> - This variable is used to suppress underflow messages and should
                        always be =NO. It is not currently used in FEQ but is retained for possible
                        future use.
                        <br><br>"""
            if rtext[10:12] == "NO":
                textback += """This line should not be changed (currently not used)."""
            else:
                textback += """<b><font color="red">Warning: This line should always be
                            UNDERFLOW=NO</font></b>
                        <br><br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

        elif rcode == "ZL":
            textback = """<b>ZL</b> - Zero-inertia cutoff depth: <font color="blue">%s</font><br><br>
                        Inertia terms will not be used when depth is less
                        than %s.<br><br>

                        Unless special problems arise, ZL should be set to 0.<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % (rtext[3:], rtext[3:])
                
        elif rcode == "STIME":
            textback = """<b>STIME</b> - Simulation starts at: <font color="blue">%s</font><br><br>

                        The date:time format for this line is:<br>
                        Characters 1-4: YEAR (all four digits)<br>
                        Character 5: separator (/ or space)<br>
                        Characters 6-7: MONTH (two digits)<br>
                        Character 8: separator (/ or space)<br>
                        Characters 9-10: DAY (two digits)<br>
                        Character 11: separator (: or space)<br>
                        Characters 12-23: HOUR (in 00.0 format)<br><br>

                        Example, simulation on the 20th of January 1980 at noon (12pm) is:<br>
                        <b>STIME</b>=1980/01/20:12.0<br><br>

                        Time can range from 00.0 to 24.0<br>
                        Year should be later than 1859
                        <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[6:]

        elif rcode == "ETIME":
            textback = """<b>ETIME</b> - Simulation ends at: <font color="blue">%s</font><br><br>

                        The date:time format for this line is:<br>
                        Characters 1-4: YEAR (all four digits)<br>
                        Character 5: separator (/ or space)<br>
                        Characters 6-7: MONTH (two digits)<br>
                        Character 8: separator (/ or space)<br>
                        Characters 9-10: DAY (two digits)<br>
                        Character 11: separator (: or space)<br>
                        Characters 12-23: HOUR (in 00.0 format)<br><br>

                        Example, simulation on the 20th of January 1980 at noon (12pm) is:<br>
                        <b>STIME</b>=1980/01/20:12.0<br><br>

                        Time can range from 00.0 to 24.0<br>
                        Year should be later than 1859<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[6:]

        elif rcode == "GRAV":
            if "32.2" in rtext:
                units = "English"
                textback = """%s units are used.""" % units
            elif "9.8" in rtext:
                units = "Metric"
                textback = """%s units are used.""" % units
            else:
                textback = """<b><font color="red">Warning: Gravity should be 32.2 (English)
                            or 9.8 (Metric)</font></b>"""

            textback += """<br><br>The format for this line should always be <b>GRAV</b>=32.2 or
                        <b>GRAV</b>=9.8 to allow for proper unit assignment.<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

        elif rcode == "NODEID":
            if "YES" in rtext:
                textback = """Nodes can be identified with a name (up to 8 letters)."""
            elif "NO" in rtext:
                textback = """Nodes will not be identified with a name.<br>
                            <b><font color="red">Warning: it is suggested to use NODEID=YES
                            to allow for a clearer output</font></b>"""
            else:
                textback = """<b><font color="red">Warning: User should specify if nodes can be
                            named (YES) or not (NO)</font></b>"""
                
            textback += """<br><br>If <b>NODEID</b>=YES, an id string of eight or less characters
                        may be given in the Branch Tables for each node on a branch.<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

        elif rcode == "SSEPS":
            textback = """<b>SSEPS</b> - Convergence tolerance for volume of water in ponding
                        storage when sewers are simulated:
                        <font color="blue">%s</font><br><br>

                        This variable specifies the maximum relative change in surcharge storage
                        volume allowed anywhere in the system during the iterative computation
                        of the surcharge storage.<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[6:]

        elif rcode == "PAGE":
            textback = """<b>PAGE</b> - Number of lines per page of special output file: <font color="blue">
                        %s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[5:]

        elif rcode == "EPSSYS":
            textback = """<b>EPSSYS</b> - Convergence tolerances for the matrix solution:<br><br>
                        Maximum relative change in the value of an unknown 
                        between iterations: <font color=blue>%s</font>.<br><br>

                        Depending on the context, the unknown can be either flow or water-surface
                        height. The maximum relative change as computed is based on the last
                        correction from Newton's method. The last correction is made so that the
                        relative error in the unknowns is probably much less than the stated
                        tolerance.<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]

        elif rcode == "ABSTOL":
            textback = """<b>ABSTOL</b> - Convergence tolerances for the matrix solution:<br><br>
                        Tolerance on the change in water surface height at nodes
                        on branches: <font color=blue>%s</font><br><br>

                        <b>ABSTOL</b> must be nonzero if small depths are to be simulated.<br><Br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]

        elif rcode == "EPSFAC":
            textback = """<b>EPSFAC</b> - Convergence tolerances for the matrix solution:<br><br>
                        Secondary relative tolerance factor: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]            
        
        elif rcode == "MKNT":
            textback = """<b>MKNT</b> - Convergence tolerances for the matrix solution:<br><br>
                        Maximum number of iterations for the matrix system: 
                        <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[5:]

        elif rcode == "NUMGT":
            textback = """<b>NUMGT</b> - Convergence tolerances for the matrix solution:<br><br>
                        Number of nodes at which the secondary relative convergence 
                        criterion may be applied: <font color=blue>%s</font><br><br>

                        Use of this variable solves a frequent problem of robustness.<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[6:]

        elif rcode == "OUTPUT":
            textback = """<b>OUTPUT</B> - Output level of detail: <font color=blue>%s</font><br><br>

                        Ranges from 00000 to 00005, with 00000 being minimum output detail and 00005
                        being maximum output detail.<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]

        elif rcode == "PRTINT":
            textback = """<b>PRTINT</b> - Output is printed at every <font color=blue>%s</font> time
                        steps<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]

        elif rcode == "DPTIME":
            textback = """<b>DPTIME</b> - Start time for debugging print output: <font color=blue>%s</font><br><br>

                        Format is same as <b>ETIME</b><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]

        elif rcode == "GEQOPT":
            textback = """<b>GEQOPT</B> - Governing equation for the branches in the stream system:
                          <font color=blue>%s</font><br><br>

                        <b>STDX</b> - the weight coefficients for curvilinearity are assumed to
                        always be equal to 1.<br><br>
                        
                        <b>STDW</b> - A special user-controlled variable weight for certain distance
                        integrals is added to the equations applied in <b>STDX</b>. This variable weight
                        is important for simulating shallow flows.<br><br>

                        <b>STDCX</b>, <b>STDCW</b> - The weights to account for channel curvilinearity
                        are added to the previous two options. These optiones can be selected on
                        branch basis. In <b>STDCW</b> these equations are solved approximately by converting
                        then to algebraic equations using approximate integration over a computational
                        element.

                        <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]

        elif rcode == "EPSB":
            textback = """<b>EPSB</b> - Convergence tolerance for steady-state
                        flow analysis used to define initial conditions in the stream
                        system: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[5:]

        elif rcode == "MAXIT":
            textback = """<b>MAXIT</b> - Maximum number of iterations in steady-state flow analysis:
                          <font color=blue>%s</font><br><br>

                        This variable specifies the maximun number of iterations permitted in the
                        steady-state flow analysis to define the initial conditions in the stream
                        system.

                        <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[6:]

        elif rcode == "SFAC":
            textback = """<b>SFAC</b> - Factor to convert node stations
                        to internal units: <font color=blue>%s</font><br><br>
                        Example: if stations are in miles, <b>SFAC</b> = 5280 to convert to
                        feet<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[5:]

        elif rcode == "TAUFAC":
            textback = """<b>TAUFAC</b> - Tributary area factor for unit
                        conversion: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]

        elif rcode == "QSMALL":
            textback = """<b>QSMALL</b> - Small value of flow rate to add to a flow before 
                        computing a relative change in flow. This prevents a division
                        by zero: <font color=blue>%s</font><br><br>

                        Use of <b>QSMALL</b> prevents a division by zero if the flow is zero.
                        <b>QSMALL</b> should be small relative to the flows of interest, but it should not
                        be made too small because unneeded computational effort is required for reducing
                        the relative changes between iterations to a value smaller than needed. 

                        <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]
        elif rcode == "QCHOP":
            textback = """<b>QCHOP</b> - Truncation level for output of flows: <font color=blue>%s</font><br><br>
                        Any flow lessthan or equal to <b>QCHOP</b> is set to zero. This option is used to
                        eliminate the output of small flows that result from roundoff during the
                        computations. The default value for <b>QCHOP</b> is 0.001.""" % rtext[6:]

        elif rcode == "IFRZ":
            ifrz = rtext[5:].replace(" ","<br>")
            ifrz = ifrz.replace("<br><br>", "<br>")
            ifrz = ifrz.replace("<br><br>", "<br>")
            textback = """<b>IFRZ</b> - Time steps that will be used during "frozen" simulated time conditions.<br><br>
                        The following time steps will be computed using constant "frozen" time to
                        determine initial conditions that include losses from flow through control
                        structures: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % ifrz

        elif rcode == "MAXDT":
            text = rtext.replace(" M", "<br>M")
            text.replace(" A", "<br>A")
            text.replace(" S", "<br>S")
            text.replace(" H", "<br>H")
            text.replace(" L", "<br>L")
            text.replace(" ", "")
            textback = """<b>MAXDT</b> - maximum time step for unsteady flow.<br><br>
                        <b>MINDT</b> - minimum time step for unsteady flow.<br><br>
                        <b>AUTO</b> - weight factor to compute a weighted running sum of the number
                        of iterations.<br><br>
                        <b>SITER</b> - initial value for the computation of the weighted running
                        sum of the number of iterations.<br><br>
                        <b>HIGH</b> - upper bound on weighted running sum.<br><br>
                        <b>LOW</b> - lower bound on weighted running sum.<br><br>
                        <b>HFAC</b> - factor to increase computational time step.<br><br>
                        <b>LFAC</b> - factor to decrease computational time step.<br><br>
                        <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % text

        elif rcode == "MINDT":
            textback = """<b>MINDT</b> - Minimum time step in seconds: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]

        elif rcode == "AUTO":
            textback = """<b>AUTO</b> - Weighting factor for running sum of iteration
                        count: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[6:]

        elif rcode == "SITER":
            rtext.replace(" H","<br>H")
            rtext.replace(" L","<br>L")
            rtext.replace(" ","")
            textback = """<b>SITER</b> - The initial value of running sum of iteration count.<br><br>
                        The HIGH value is the upper value for the running sum.<br><br>
                        The LOW value is the lower value for the running sum.<br><br>
                        <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext

        elif rcode == "LFAC":
            textback = """<b>LFAC</b> - Multiplier used to decrease the computational time step to improve computational
                        convergence: <font color=blue>%s</font><br><br>""" % rtext[5:11]
            textback +="""HFAC - Multiplier used to increase the computational time step to improve computational convergence:
                         <font color=blue>%s</font><br>""" % rtext[16:]

        elif rcode == "HFAC":
            rtext.replace(" L","<br>L")
            rtext.replace(" ","")
            textback = """<b>HFAC</b> - The factor for increasing time step.<br><br>
                        <b>LFAC</b> - The factor for decreasing time step.<br><br>
                        <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext


        elif rcode == "MRE":
            textback = """<b>MRE</b> - Maximum relative change permitted in a
                        variable during extrapolation: <font color=blue>%s</font><br><br>""" % rtext[4:13]
            if "FAC" in rtext:
                textback +="""<b>FAC</b> - Factor used to regulate the degree of extrapolation from previous values
                        at reach to aid in the solution of equations: <font color=blue>%s</font><br><br>""" % rtext[20:]  
            
            textback += """<a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" 

        elif rcode == "FAC":
            textback = """<b>FAC</b> - Extrapolation factor: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[4:]

        elif rcode == "DWT":
            textback = """<b>DWT</b> - Change in the current value of Wt: <font color=blue>%s</font><br><br>
                        Wt is the weight factor for approximating integrals with respect
                        to time.<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[4:]

        elif rcode == "BWT":
            textback = """<b>BWT</b> - Base value of the weight factor for
                        approximating integrals with respect to time: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[4:]

        elif rcode == "BWFDSN":
            textback = """<b>BWFDSN</b> - Fortran unit number for the file used to save the initial conditions when
                        tributaries are present: <font color=blue>%s</font><br><br>

                        This is the name for the file opened in FEQ simulation to store the initial
                        conditions needed for events in the DTSF.

                        <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]

        elif rcode == "CHKGEO":
            textback = """<b>CHKGEO</b> - Check geometry? <font color=blue>%s</font><br><br>

                        This variable selects geometric checking. If geometric checking is selected, then
                        execution of FEQ is terminated at the end of the checking process so that changes
                        to the input can be made.<br><br>

                        Format:
                        <b>CHKGEO</b>=YES or <b>CHKGEO</b>=NO


                        <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]

        elif rcode == "ISTYLE":
            textback = """<b>ISTYLE</b> - Use the following style of labeling flow-path end
                        nodes: <font color=blue>%s</font><br><br>

                        If <b>ISTYLE</b>=OLD, then flow-path end nodes are numbered and the Branch-Exterior
                        Node Block must appear in the input. If <b>ISTYLE</b>=NEW, then the flow-path end nodes
                        are labeled with a prefix character and the branch number if on a branch. An
                        upstream branch end node is labeled with the prefix letter "U". A downstream
                        branch end node is labeled with the prefix letter "D". Labels for level-pool
                        reservoir and dummy-branch end nodes are prefixed by the letter "F".


                        <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]

        elif rcode == "GENSCN":
            textback = """<b>Genscn Output Locations</b>: Specifies nodes or branches where output will be written to 
                        designated files in a format read by GenScn."""
            if "NEW GENSCN OUTPUT" in rtext:
                textback += """<br><br><b>NEW GENSCN OUTPUT</b>: Use the new GENSCN output option."""
            elif "FILE" in rtext:
                textback += """<br><br><b>FILE</b> - Base filename for the three files (*.FEO, *.FTF, *.TSD) created
                        for GENSCN: <font color=blue>%s</font>""" % re.split(r'FILE\s*=\s*', rtext)[-1]
            elif "OPT" in rtext:
                textback += """<br><br><b>OPT</b> - Add or subtract nodes from the GENSCN output list."""
                if "BRA" in rtext:
                    textback += """<br><br><b>BRA</b> - Branch number (if 0, the node column contains an exterior node label)."""
                if "NODE" in rtext:
                    textback += """<br><br><b>NODE</b> - Node number."""
            elif "END" in rtext:
                textback += """<br><br><b>END</b> - End of GenScn output locations table."""
            elif "ADD=" in rtext:
                textback += ""
            elif "SUB=" in rtext:
                textback += ""
            elif rtext.startsWith(';'):
                textback += ""
            else:
                if "ADD" or "SUB" in rtext:
                    textback += """<br><br><b>OPT</b> - Add or subtract nodes from the GENSCN output list: 
                            <font color=blue>%s</font>""" % re.split(r'\s+', rtext)[1]
                textback += """<br><br><b>BRA</b> - Branch number (if 0, the node column contains an exterior node label):
                            <font color=blue>%s</font>""" %  re.split(r'\s+', rtext)[2]
                textback += """<br><br><b>NODE</b> - Node number: <font color=blue>%s</font>""" %  re.split(r'\s+', rtext, 3)[3]
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

        elif rcode == "EXTTOL":
            textback = """<b>EXTTOL</b> - Distance above the top of sections that can be extrapolated during unsteady-flow
                        computations: <font color=blue>%s</font>.<br><br>

                        The extension of each cross section by the <b>EXT</b> option is checked to determine whether the
                        maximum elevation of water exceeds the unextended maximum level of the cross-section table
                        by more than <b>EXTTOL</b> length units.


                        <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]

        elif rcode == "SQREPS":
            textback = """<b>SQREPS</b> - Tolerance on the change in the squared sum
                        residual when using Newton's method: <font color=blue>%s</font>


                        <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]

        elif rcode == "OLD":
            textback = """<b>OLD</b> - Use old form of summary output? <font color=blue>%s
                        </font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_2.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[12:]



        elif rcode.startsWith("BRA"):                                  #Branch Description Block
            textback = """Branch #<font color=blue>%s</font><br><br>""" % rcode[4:]

            if rtext.startsWith("BNUM"):
                properties = rtext.replace(" I", "<br>I")
                properties.replace(" C", "<br>C")
                properties.replace(" W", "<br>W")
                properties.replace(" A", "<br>A") #Describe each property
                textback += """Branch properties:<br> <font color=blue>
                                %s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_3.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % properties

            elif rtext.startsWith(" NODE"):
                headings = rtext.replace(" ", "<br>")
                headings.replace("<br><br>", "<br>")
                headings.replace("<br><br>", "<br>")
                textback += """Headings:<br> <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_3.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % headings

            elif rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_3.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext

            elif " -1" in rtext or rtext == "-1":
                textback += """Branch end.<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_3.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

            else:
                order = unicode(rcode[4:])
                cc = 0
                ee = nodeL[order]
                nodeH = rtext[cc:ee]
                cc = ee
                ee = nodeidL[order]
                nodeidH = rtext[cc:ee]
                cc = ee
                ee = xnumL[order]
                xnumH = rtext[cc:ee]
                cc = ee
                ee = stationL[order]
                stationH = rtext[cc:ee]
                cc = ee
                ee = elevationL[order]
                elevationH = rtext[cc:ee]
                cc = ee
                ee = kaL[order]
                kaH = rtext[cc:ee]
                cc = ee
                ee = kdL[order]
                kdH = rtext[cc:ee]
                cc = ee
                ee = htabL[order]
                htabH = rtext[cc:ee]
                cc = ee
                ee = azmL[order]
                azmH = rtext[cc:ee]
                cc = ee
                ee = cfL[order]
                cfH = rtext[cc:ee]
                cc = ee
                ee = ycL[order]
                ycH = rtext[cc:ee]
                textback += """Parameters:<br><br>
                            <b>NODE</b>: <font color=blue>%s</font><br><br>
                            <b>NODE ID</b>: <font color=blue>%s</font><br><br>
                            <b>XNUM</b>: <font color=blue>%s</font><br>
                            number of the table listing the hydraulic
                            characteristics of the cross section at the node<br><br>
                            <b>STATION</b>: <font color=blue>%s</font><br><br>
                            <b>ELEVATION</b>: <font color=blue>%s</font><br><br>
                            <b>KA</b>: <font color=blue>%s</font><br>
                            loss factor to apply to the difference in
                            velocity head in the computational element upstream from the node when
                            the flow is accelerating with respect to distance<br><br>
                            <b>KD</b>: <font color=blue>%s</font><br>
                            loss factor to apply to the difference in
                            velocity head in the computational element upstream from the node when
                            the flow is decelerating with respect to distance<br><br>
                            <b>HTAB</b>: <font color=blue>%s</font><br>
                            number of the table listing the factor applied
                            to the mean velocity head in the element as an estimate of point losses
                            <br><Br>
                            <b>AZM</b>: <font color=blue>%s</font><br>
                            azimuth of the downstream flow direction
                            <br><br>
                            <b>CF</b>: <font color=blue>%s</font><br>
                            effective area of the inlets to a storm
                            sewer<br><br>
                            <b>YC</b>: <font color=blue>%s</font><br>
                            depth of water(distance of hydraulic-grade line above
                            invert) when ponding begins
                            <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_3.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % (nodeH, nodeidH, xnumH, stationH, elevationH, \
                                       kaH, kdH, htabH, azmH, cfH, ycH)
                
            
            
        elif rcode == "TRBP":                                          #Tributary Area
            if rtext.startsWith("HOME"):
                textback = """<b>HOME</b> - Default directory for time series file: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_3update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[5:]

            elif rtext.startsWith("TSFDSN"):
                textback = """<b>TSFDSN</b> - Diffuse Time Series File containing the unit-area
                            runoff intensities on the tributary areas: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_3update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]

            elif rtext.startsWith("TSFNAM"):
                textback = """<b>TSFNAM</b> - Name for the Diffuse Time Series File containing the unit-area
                            runoff intensities on the tributary areas: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_3update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]

            elif rtext.startsWith("FFFDSN"):
                textback = """<b>FFFDSN</b> - Fortran unit number for the
                            file used to store the flows and stages required for a flood-
                            frequency analysis: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_3update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]

            elif rtext.startsWith("FFFNAM"):
                textback = """<b>FFFNAM</b> - Name for the
                            file used to store the flows and stages required for a flood-
                            frequency analysis: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_3update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[7:]

            elif rtext.startsWith("NLUSE"):
                textback = """<b>NLUSE</b> - Number of land-cover type and rain-gage combinations represented
                            by the tributary areas: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_3update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>
                            """ % rtext[6:]

            elif rtext.startsWith("NGAGE"):
                textback = """<b>NGAGE</b> - Number of rain gages used to
                            define the runoff intensities on the tributary area for the
                            watershed: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_3update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[6:]

            elif rtext.startsWith(" ") and "GAGE" in rtext:
                textback = """Table headers:<br><br>
                            <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_3update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext

            elif rtext.startsWith(" ") and not "GAGE" in rtext:
                textback = """Table values.<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_3update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

            elif rtext.startsWith(";") or rtext.startsWith("*"):
                textback = """Comment: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_3update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext

            else:
                textback = """Cannot interpret.<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_3update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

        elif rcode.startsWith("TBRA"):
            order = unicode(rcode[5:])
            textback = """Branch #<font color=blue>%s</font><br><br>""" % order
            if "-1" in rtext:
                textback += """Branch end.<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_3update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

            elif rtext.startsWith("BRANCH"):
                prop = rtext.replace(" F", "<br>F")
                prop.replace(" ", "")
                textback += """Branch properties: <font color=blue>%s</font><br><br>

                            <b>BRANCH</b> - the branch number for the table<br>
                            <b>FAC</b> - a multiplier on the areas given in the branch.<br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_3update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % prop

            elif rtext.startsWith(" NODE"):
                headrs = rtext.replace(" ","<br>")
                while "<br><br>" in headrs:
                    headrs.replace("<br><br>","<br>")
                
                textback += """Table headers: <font color=blue>%s</font>
                            <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_3update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % headrs

            elif rtext.startsWith("*") or rtext.startsWith(";"):
                textback += """Comment: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_3update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext

            elif rtext.startsWith("DLAY"):
                textback += """<b>DLAY</b> - This variable calls for an additional delay and attenuation.
                                This is followed by either an explicit specification
                                of the delay time in hours, or by requesting an equation by name to
                                compute the delay time from area and the fraction of impervious cover.
                                <br><br>""" % rtext

            elif rtext.startsWith("DTEN"):

                if "FRACTION" in rtext[4:]:
                    fraction = rtext[14:]
                else:
                    fraction = "no fraction"
                
                textback += """<b>FRACTION</b> - Detention storage fraction: <font color=blue>%s</font> <br><br>
                            This variable request detention storage. It is followed by the identifier
                            name <b>FRACTION</b>(defines what fraction of the tributary area be subjected to
                            detention).<br><br>

                            Example:<br>
                            If <b>FRACTION</b>=1.0 then the entire tributary area is subject to
                            detention.<br><br>"""  % fraction
            else:
                cc = 0
                ee = tnodeL[order]
                tnodeH = rtext[cc:ee]
                cc = ee
                ee = tgageL[order]
                tgageH = rtext[cc:ee]
                cc = ee
                ee = timprvL[order]
                timprvH = rtext[cc:ee]
                cc = ee
                ee = tfgrssL[order]
                tfgrssH = rtext[cc:ee]
                cc = ee
                ee = tmgrssL[order]
                tmgrssH = rtext[cc:ee]
                cc = ee
                ee = tsgrssL[order]
                tsgrssH = rtext[cc:ee]
                cc = ee
                ee = tforstL[order]
                tforstH = rtext[cc:ee]
                cc = ee
                ee = tagricL[order]
                tagricH = rtext[cc:ee]
                cc = ee
                ee = ttotalL[order]
                ttotalH = rtext[cc:ee]
                cc = ee
                comments = rtext[cc:]
                textback += """Tributary areas:<br>
                            <b>Node</b>: <font color=blue>%s</font><br>
                            <b>Gage</b>: <font color=blue>%s</font><br>
                            <b>Imprv</b>: <font color=blue>%s</font><br>
                            <b>FGRSS</b>: <font color=blue>%s</font><br>
                            <b>MGRSS</b>: <font color=blue>%s</font><br>
                            <b>SGRSS</b>: <font color=blue>%s</font><br>
                            <b>FORST</b>: <font color=blue>%s</font><br>
                            <b>AGRIC</b>: <font color=blue>%s</font><br>
                            <b>TOTAL</b>: <font color=blue>%s</font><br>
                            Comments: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_3update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>
                            """ % (tnodeH, tgageH, timprvH, tfgrssH, tmgrssH, \
                                   tsgrssH, tforstH, tagricH, ttotalH, comments)

        
        elif rcode == "MHEAD":                                         #Network Matrix
            textback = """<b>Network Matrix Control</b><br><br>
                        Table headers: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext

        elif rcode.startsWith("MX"):
            textback = """<b>Network Matrix Control</b><br><br>"""

            if rcode == "MX1":
                textback += """This code identifies a branch: <font color=blue>%s</font>
                            <br><br>"""

                maxee = len(rtext)
                cc = 5
                st = cc
                ee = cc + 1
                mvar = "mint"
                while rtext[cc:ee] == " ":
                    cc +=1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    if rtext[cc:ee] == "'":
                        mvar = "mcom"
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                if mvar == "mint":
                    n1 = rtext[st:cc]
                    com = rtext[cc:]
                else:
                    while not rtext[cc:ee] == " ":
                        cc -= 1
                        ee = cc + 1
                    com = rtext[ee:]

                
                textback += """Branch number: <font color=blue>%s</font><br><br>""" % n1
                textback += """Comments: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % com
            
            elif rcode == "MX2":
                maxee = len(rtext)
                mvar = "mint"
                cc = 5
                st = cc
                ee = cc + 1
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    if rtext[cc:ee] == "'":
                        mvar = "mcom"
                        n1 = " "
                        break
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                if mvar == "mint":
                    n1 = rtext[st:cc]
                    st = cc
                    beg = cc
                    mvar = "mcom"
                    while not rtext[cc:ee] == "'":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                else:
                    while not rtext[cc:ee] == " ":
                        cc -= 1
                        ee = cc + 1
                if mvar == "mcom":
                    com = rtext[cc:]

                nodes = rtext[st:cc]
                nodes.replace(" ","<br>")
                while "<br><br>" in nodes:
                    nodes.replace("<br><br>","<br>")
                textback += """Number of nodes at a junction: <font color=blue>%s</font><br><br>
                            Number of nodes: <br><br>
                            Nodes: <font color=blue>%s</font><br><br>
                            Comments: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % (n1, nodes, com)

            elif rcode == "MX3":
                maxee = len(rtext)
                cc = 5
                st = cc
                ee = cc + 1
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                n1 = rtext[st:cc]
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                n2 = rtext[st:cc]
                com = rtext[cc:]
                textback += """Code: <font color=blue>3</font><br><br>
                            Water surface elevations
                            will be equal between nodes <font color=blue>%s</font> and
                            <font color=blue>%s</font>.<br><br>

                            Comments: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % (n1, n2, com)

            elif rcode == "MX4":                                                                   # Matrix for CODE 4
                textback += """Code: <font color=blue>%s</font><br><br>
                            One-node head-discharge relation.<br><br>""" % rtext[:5]                 #



                
                                                                                                     #
                mtype = rtext[5:10]                                                                  # Characters 5-10 in the line should contain
                mtype.replace(" ","")                                                                # the line's TYPE, stored in 'mtype'
                mvar = "mint"                                                                        # ------------------------------------------

                if mtype == "":
                    dd = 5
                    while mtype == "":
                        dd += 1
                        mtype = rtext[5:dd]
                        mtype = mtype.replace(" ","")
                    cc = dd
                else:
                    cc = 10

                st = cc
                                                                                                     # The variable type will default to integer
                maxee = len(rtext)                                                                   # 'mint'
                                                                                                     # ------------------------------------------
                ee = cc + 1                                                                          #
                while rtext[cc:ee] == " ":                                                           # Here the code will read and assign the
                    cc += 1                                                                          # variables 'n2', 'n3', and 'n4 which are
                    ee = cc + 1                                                                      # common to all Code 4 types.
                    if ee > maxee:                                                                   #
                        break                                                                        #
                while not rtext[cc:ee] == " ":                                                       #
                    cc += 1                                                                          #
                    ee = cc + 1                                                                      # A space after each variable stops the
                    if ee > maxee:                                                                   # reading.
                        break                                                                        #
                n2 = rtext[st:cc]                                                                    #
                st = cc                                                                              #
                                                                                                     # 
                while rtext[cc:ee] == " ":                                                           # 
                    cc += 1                                                                          #
                    ee = cc + 1                                                                      #
                    if ee > maxee:                                                                   #
                        break                                                                        #
                while not rtext[cc:ee] == " ":                                                       #
                    cc += 1                                                                          #
                    ee = cc + 1                                                                      #
                    if ee > maxee:                                                                   #
                        break                                                                        #
                n3 = rtext[st:cc]                                                                    #
                st = cc                                                                              #
                                                                                                     # 
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                n4 = rtext[st:cc]
                st = cc
                
                
                if mtype == "1":                                                                     # Matrix for CODE 4 - TYPE 1
                    while rtext[cc:ee] == " ":                                                       #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  # ------------------------------------------
                        if ee > maxee:                                                               # Here the code will read and assign a value
                            break                                                                    # to variable 'n5'
                    while not rtext[cc:ee] == " ":                                                   #
                        if rtext[cc:ee] == ".":                                                      # If the variable is a float instead of an
                            mvar = "mfloat"                                                          # integer, a blank value will be assigned to
                            n5 = " "                                                                 # 'n5'. Same case if it's a comment
                            break                                                                    #
                        elif rtext[cc:ee] == "'":                                                    #
                            mvar = "mcom"                                                            #
                            n5 = " "                                                                 #
                            break
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  #
                        if ee > maxee:                                                               #
                            break
                    if mvar == "mint":
                        n5 = rtext[st:cc]
                        st = cc
                        mvar = "mfloat"
                    else:
                        while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                            cc -= 1                                                                  # the code will go back to the beginning of
                            ee = cc + 1                                                              # the variable to read again

                    if mvar == "mfloat":                                                             # Read and assign variable 'f1'
                        while rtext[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        f1 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":                                                   # Read and assign variable 'f2'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == "'":                                                # If the variable is a comment, a blank
                                mvar = "mcom"                                                        # value will be assigned to 'f2'
                                f2 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mfloat":
                            f2 = rtext[st:cc]
                            st = cc
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1

                        if mvar == "mfloat":
                            com = rtext[st:]
                        elif mvar == "mcom":
                            com = rtext[ee:]

                    elif mvar == "mcom":                                                             # If the variable is a comment, then the 
                        f1 = " "                                                                     # remainder of the line will be assigned to
                        f2 = " "                                                                     # 'com', and a blank value will be assigned
                        com = rtext[ee:]                                                             # to 'f1' and 'f2'

                    
                        
                    
                    textback += """Type <font color=blue>%s</font>: flow over weir.<br><br>

                                Number of the flow-path end
                                node at which the head is specified: <font color=blue>%s</font><br><br>
                                Direction of positive flow. (1 means
                                flow into system, -1 means flow out of system): <font color=blue>%s</font><br><br>
                                Number of the flow-path end
                                node at which the flow is specified: <font color=blue>%s</font><br><br>

                                Number of the table that includes
                                the weir coefficient as a function of head: <font color=blue>%s</font><br><br>
                                Elevation of the reference point
                                used for defining head: <font color=blue>%s</font><br><br>
                                Weir length: <font color=blue>%s</font><br><br>
                                Comments: <font color=blue>%s</font>
                                """ % (mtype, n2, n3, n4, n5, f1, f2, com)

                elif mtype == "2":                                                                   # Matrix for CODE 4 - TYPE 2
                    while rtext[cc:ee] == " ":                                                       #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  # ------------------------------------------
                        if ee > maxee:                                                               # Here the code will read and assign a value
                            break                                                                    # to variable 'n5'
                    while not rtext[cc:ee] == " ":                                                   #
                        if rtext[cc:ee] == ".":                                                      # If the variable is a float instead of an
                            mvar = "mfloat"                                                          # integer, a blank value will be assigned to
                            n5 = " "                                                                 # 'n5'. Same case if it's a comment
                            break                                                                    #
                        elif rtext[cc:ee] == "'":                                                    #
                            mvar = "mcom"                                                            #
                            n5 = " "                                                                 #
                            break                                                                    #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  #
                        if ee > maxee:                                                               #
                            break
                    if mvar == "mint":
                        n5 = rtext[st:cc]
                        st = cc
                        mvar = "mfloat"
                    else:
                        while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                            cc -= 1                                                                  # the code will go back to the beginning of
                            ee = cc + 1                                                              # the variable to read again

                    if mvar == "mfloat":                                                             # Read and assign variable 'f1'
                        while rtext[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        f1 = rtext[st:cc]
                        st = cc
                        com = rtext[st:]

                    elif mvar == "mcom":                                                             # If the variable is a comment, then the 
                        f1 = " "                                                                     # remainder will be assigned to 'com' and
                        com = rtext[ee:]                                                             # a blank value will be assigned to 'f1'
                        
                    textback += """Type <font color=blue>%s</font>: table relating discharge
                                and head.<br><br>

                                Number of the flow-path end
                                node at which the head is specified: <font color=blue>%s</font><br><br>
                                Direction of positive flow. (1 means
                                flow into system, -1 means flow out of system): <font color=blue>%s</font><br><br>
                                Number of the flow-path end
                                node at which the flow is specified: <font color=blue>%s</font><br><br>

                                Number of the table specifying
                                flow as a function of head: <font color=blue>%s</font><br><br>
                                Elevation of the reference point
                                used for defining head: <font color=blue>%s</font><br><br>
                                Comments: <font color=blue>%s</font>
                                """ % (mtype, n2, n3, n4, n5, f1, com)

                elif mtype == "3": #check                                                            # Matrix for CODE 4 - TYPE 3
                    while rtext[cc:ee] == " ":                                                       #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  # ------------------------------------------
                        if ee > maxee:                                                               # Here the code will read and assign a value
                            break                                                                    # to variable 'n5'
                    while not rtext[cc:ee] == " ":                                                   #
                        if rtext[cc:ee] == ".":                                                      # If the variable is a float instead of an
                            mvar = "mfloat"                                                          # integer, a blank value will be assigned to
                            n5 = " "                                                                 # 'n5'. Same case if it's a comment
                            break                                                                    #
                        elif rtext[cc:ee] == "'":                                                    #
                            mvar = "mcom"                                                            #
                            n5 = " "                                                                 #
                            break                                                                    #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  #
                        if ee > maxee:                                                               #
                            break
                    if mvar == "mint":
                        n5 = rtext[st:cc]
                        st = cc
                        mvar = "mfloat"
                    else:
                        while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                            cc -= 1                                                                  # the code will go back to the beginning of
                            ee = cc + 1                                                              # the variable to read again

                    if mvar == "mfloat":                                                             # Read and assign variable 'f1'
                        while rtext[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        f1 = rtext[st:cc]
                        st = cc
                        com = rtext[st:]

                    elif mvar == "mcom":                                                             # If the variable is a comment, then the 
                        f1 = " "                                                                     # remainder will be assigned to 'com' and
                        com = rtext[ee:]                                                             # a blank value will be assigned to 'f1'
                    textback += """Type <font color=blue>%s</font>: channel control of flow.<br><br>

                                Number of the flow-path end
                                node at which the head is specified: <font color=blue>%s</font><br><br>
                                Direction of positive flow. (1 means
                                flow into system, -1 means flow out of system): <font color=blue>%s</font><br><br>
                                Number of the flow-path end
                                node at which the flow is specified: <font color=blue>%s</font><br><br>

                                Slope source for defining flow: <font color=blue>%s</font><br><br>
                                If -1, slope is given in next value<br>
                                If 0, bottom slope of the stream channel is used<br>
                                If 1, water-surface slope at previous time point is used<br><br>
                                Value of slope (if slope source = -1): <font color=blue>%s</font>
                                <br><br>Comments: <font color=blue>%s</font>
                                """ % (mtype, n2, n3, n4, n5, f1, com)

                elif mtype == "4":                                                                   # Matrix for CODE 4 - TYPE 4
                    while rtext[cc:ee] == " ":                                                       #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  # ------------------------------------------
                        if ee > maxee:                                                               # Here the code will read and assign a value
                            break                                                                    # to variable 'n5'
                    while not rtext[cc:ee] == " ":                                                   #
                        if rtext[cc:ee] == ".":                                                      # If the variable is a float instead of an
                            mvar = "mfloat"                                                          # integer, a blank value will be assigned to
                            n5 = " "                                                                 # 'n5' and 'n6'. Same case if it's a comment
                            n6 = " "
                            break                                                                    #
                        elif rtext[cc:ee] == "'":                                                    #
                            mvar = "mcom"                                                            #
                            n5 = " "                                                                 #
                            n6 = " "
                            break                                                                    #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  #
                        if ee > maxee:                                                               #
                            break
                    if mvar == "mint":
                        n5 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == ".":
                                mvar = "mfloat"
                                n6 = " "
                                break
                            elif rtext[cc:ee] == "'":
                                mvar = "mcom"
                                n6 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mint":
                            n6 = rtext[st:cc]
                            st = cc
                            mvar = "mfloat"
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    else:
                        while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                            cc -= 1                                                                  # the code will go back to the beginning of
                            ee = cc + 1                                                              # the variable to read again

                    if mvar == "mfloat":
                        while rtext[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == "'":
                                mvar = "mcom"
                                f1 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mfloat":
                            f1 = rtext[st:cc]
                            st = cc
                            com = rtext[st:]
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    if mvar == "mcom":
                        com = rtext[st:]

                    
                    
                    textback += """Type <font color=blue>%s</font>: structure capacity given
                                as a function of time.<br><br>

                                Number of the flow-path end
                                node at which the head is specified: <font color=blue>%s</font><br><br>
                                Direction of positive flow. (1 means
                                flow into system, -1 means flow out of system): <font color=blue>%s</font><br><br>
                                Number of the flow-path end
                                node at which the flow is specified: <font color=blue>%s</font><br><br>

                                Number of the table specifying
                                the maximum flow through the structure as a function of head: <font color=blue>%s</font><br><br>
                                Number of the table specifying
                                proportion of maximum flow as a function of time: <font color=blue>%s</font><br><br>
                                Elevation of the reference point used
                                for defining head: <font color=blue>%s</font><br><br>
                                Comments: <font color=blue>%s</font>
                                """ % (mtype, n2, n3, n4, n5, n6, f1, com)

                elif mtype == "5":                                                                   # Matrix for CODE 4 - TYPE 5
                    while rtext[cc:ee] == " ":                                                       #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  # ------------------------------------------
                        if ee > maxee:                                                               # Here the code will read and assign a value
                            break                                                                    # to variable 'n5'
                    while not rtext[cc:ee] == " ":                                                   #
                        if rtext[cc:ee] == ".":                                                      # If the variable is a float instead of an
                            mvar = "mfloat"                                                          # integer, a blank value will be assigned to
                            n5 = " "                                                                 # 'n5' and 'n6'. Same case if it's a comment
                            n6 = " "
                            break                                                                    #
                        elif rtext[cc:ee] == "'":                                                    #
                            mvar = "mcom"                                                            #
                            n5 = " "                                                                 #
                            n6 = " "
                            break                                                                   #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  #
                        if ee > maxee:                                                               #
                            break
                    if mvar == "mint":
                        n5 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == ".":
                                mvar = "mfloat"
                                n6 = " "
                                break
                            elif rtext[cc:ee] == "'":
                                mvar = "mcom"
                                n6 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mint":
                            n6 = rtext[st:cc]
                            st = cc
                            mvar = "mfloat"
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    else:
                        while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                            cc -= 1                                                                  # the code will go back to the beginning of
                            ee = cc + 1                                                              # the variable to read again

                    if mvar == "mfloat":
                        while rtext[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == "'":
                                mvar = "mcom"
                                f1 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mfloat":
                            f1 = rtext[st:cc]
                            st = cc
                            com = rtext[st:]
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    if mvar == "mcom":
                        com = rtext[st:]
                    textback += """Type <font color=blue>%s</font>: structure capacity
                                varied dynamically in FEQ computations.<br><br>

                                Number of the flow-path end
                                node at which the head is specified: <font color=blue>%s</font><br><br>
                                Direction of positive flow. (1 means
                                flow into system, -1 means flow out of system): <font color=blue>%s</font><br><br>
                                Number of the flow-path end
                                node at which the flow is specified: <font color=blue>%s</font><br><br>

                                Number of the table specifying
                                maximum flow through the structure as a function of head: <font color=blue>%s</font><br><br>
                                Number of the operation block controlling
                                the operation of the structure: <font color=blue>%s</font><br><br>
                                Elevation of the reference point
                                used for defining head: <font color=blue>%s</font><br><br>
                                Comments: <font color=blue>%s</font>
                                """ % (mtype, n2, n3, n4, n5, n6, f1, com)

                elif mtype == "6":
                    while rtext[cc:ee] == " ":                                                       #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  # ------------------------------------------
                        if ee > maxee:                                                               # Here the code will read and assign a value
                            break                                                                    # to variable 'n5'
                    while not rtext[cc:ee] == " ":                                                   #
                        if rtext[cc:ee] == ".":                                                      # If the variable is a float instead of an
                            mvar = "mfloat"                                                          # integer, a blank value will be assigned to
                            n5 = " "                                                                 # 'n5' and 'n6'. Same case if it's a comment
                            n6 = " "
                            n7 = " "
                            break                                                                    #
                        elif rtext[cc:ee] == "'":                                                    #
                            mvar = "mcom"                                                            #
                            n5 = " "                                                                 #
                            n6 = " "
                            n7 = " "
                            break                                                                   #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  #
                        if ee > maxee:                                                               #
                            break
                    if mvar == "mint":
                        n5 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == ".":
                                mvar = "mfloat"
                                n6 = " "
                                n7 = " "
                                break
                            elif rtext[cc:ee] == "'":
                                mvar = "mcom"
                                n6 = " "
                                n7 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mint":
                            n6 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == ".":
                                    mvar = "mfloat"
                                    n7 = " "
                                    break
                                elif rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    n7 = " "
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mint":
                                n7 = rtext[st:cc]
                                st = cc
                                mvar = "mfloat"
                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    else:
                        while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                            cc -= 1                                                                  # the code will go back to the beginning of
                            ee = cc + 1                                                              # the variable to read again

                    if mvar == "mfloat":
                        while rtext[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == "'":
                                mvar = "mcom"
                                f1 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mfloat":
                            f1 = rtext[st:cc]
                            st = cc
                            com = rtext[st:]
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    if mvar == "mcom":
                        com = rtext[st:]
                    textback += """Type <font color=blue>%s</font>: pump with capacity limited
                                by tailwater.<br><br>

                                Number of the flow-path end
                                node at which the head is specified: <font color=blue>%s</font><br><br>
                                Direction of positive flow. (1 means
                                flow into system, -1 means flow out of system): <font color=blue>%s</font><br><br>
                                Number of the flow-path end
                                node at which the flow is specified: <font color=blue>%s</font><br><br>

                                Number of the table specifying
                                the pumping rate as a function of upstream head only: <font color=blue>%s</font><br><br>
                                Source for the controlling level in the
                                tail water (time-series table number if > 0; or Fortran unit
                                number for a point-time-series file if < 0): <font color=blue>%s</font><br><br>
                                Number of the table in which the
                                tail-water level is converted into a limiting flow for the
                                pumping rate: <font color=blue>%s</font><br><br>
                                Elevation of the reference point
                                used for defining head for the table: <font color=blue>%s</font><br><br>
                                Comments: <font color=blue>%s</font>
                                """ % (mtype, n2, n3, n4, n5, n6, n7, f1, com)

                textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""


                                

            elif rcode.startsWith("MX5"):
                textback += """Code <font color=blue>5</font>: Two-node head-discharge
                            relations.<br><br>"""
                maxeecode = 10
                cccode = 0
                eecode = cccode + 1
                while rtext[cccode:eecode] == " ":
                    cccode += 1
                    eecode = cccode + 1
                    if eecode > maxeecode:
                        cccode -= 1
                        eecode -= 1
                        break

                if cccode < 5:
                    cctype = 5
                else:
                    cctype = cccode + 1
                sttype = cctype

                maxeetype = 10
                eetype = cctype + 1
                while rtext[cctype:eetype] == " ":
                    cctype += 1
                    eetype = cctype + 1
                    if eetype > maxeetype:
                        eetype -= 1
                        break
                mtype = rtext[sttype:eetype]
                mtype.replace(" ","")
                mvar = "mint"                                                                        # ------------------------------------------
                child = False


                if mtype == "" and not "5" in rtext[:eecode]:
                    global mxparent
                    numb = str(rcode[4:])
                    othertext = rtext
                    rtext = mxparent[numb]
                    child = True
                    mtype = rtext[5:10]
                    mtype = mtype.replace(" ","")


                if mtype == "":
                    dd = eecode
                    while mtype == "":
                        dd += 1
                        mtype = rtext[eecode:dd]
                        mtype = mtype.replace(" ","")
                    cc = dd
                else:
                    cc = eetype
                        
                
                                                                                                     # The variable type will default to integer
                maxee = len(rtext)                                                                   # ------------------------------------------
                st = cc
                ee = cc + 1                                                                          #
                while rtext[cc:ee] == " ":                                                           # Here the code will read and assign the
                    cc += 1                                                                          # variables 'n2', 'n3', and 'n4 which are
                    ee = cc + 1                                                                      # common to all Code 4 types.
                    if ee > maxee:                                                                   #
                        break                                                                        #
                while not rtext[cc:ee] == " ":                                                       #
                    cc += 1                                                                          #
                    ee = cc + 1                                                                      # A space after each variable stops the
                    if ee > maxee:                                                                   # reading.
                        break                                                                        #
                n2 = rtext[st:cc]                                                                    #
                st = cc                                                                              #
                                                                                                     # 
                while rtext[cc:ee] == " ":                                                           # 
                    cc += 1                                                                          #
                    ee = cc + 1                                                                      #
                    if ee > maxee:                                                                   #
                        break                                                                        #
                while not rtext[cc:ee] == " ":                                                       #
                    cc += 1                                                                          #
                    ee = cc + 1                                                                      #
                    if ee > maxee:                                                                   #
                        break                                                                        #
                n3 = rtext[st:cc]                                                                    #
                st = cc                                                                              #
                                                                                                     # 
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                n4 = rtext[st:cc]
                st = cc

                if child == True:
                    rtext = othertext
                    mtype = "6"
                                            

                
                if mtype == "1":
                    while rtext[cc:ee] == " ":                                                       #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  # ------------------------------------------
                        if ee > maxee:                                                               # Here the code will read and assign a value
                            break                                                                    # to variable 'n5'
                    while not rtext[cc:ee] == " ":                                                   #
                        if rtext[cc:ee] == ".":                                                      # If the variable is a float instead of an
                            mvar = "mfloat"                                                          # integer, a blank value will be assigned to
                            n5 = " "                                                                 # 'n5' and 'n6'. Same case if it's a comment
                            n6 = " "
                            break                                                                    #
                        elif rtext[cc:ee] == "'":                                                    #
                            mvar = "mcom"                                                            #
                            n5 = " "                                                                 #
                            n6 = " "
                            break                                                                    #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  #
                        if ee > maxee:                                                               #
                            break
                    if mvar == "mint":
                        n5 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == ".":
                                mvar = "mfloat"
                                n6 = " "
                                break
                            elif rtext[cc:ee] == "'":
                                mvar = "mcom"
                                n6 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mint":
                            n6 = rtext[st:cc]
                            st = cc
                            mvar = "mfloat"
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    else:
                        while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                            cc -= 1                                                                  # the code will go back to the beginning of
                            ee = cc + 1                                                              # the variable to read again

                    if mvar == "mfloat":
                        while rtext[cc:ee] == " ":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == "'":
                                mvar = "mcom"
                                f1 = " "
                                f2 = " "
                                f3 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mfloat":
                            f1 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    f2 = " "
                                    f3 = " "
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mfloat":
                                f2 = rtext[st:cc]
                                st = cc
                                while rtext[cc:ee] == " ":
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not rtext[cc:ee] == " ":
                                    if rtext[cc:ee] == "'":
                                        mvar = "mcom"
                                        f3 = " "
                                        break
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break

                                if mvar == "mfloat":
                                    f3 = rtext[st:cc]
                                    st = cc
                                    com = rtext[cc:]
                                else:
                                    while not rtext[cc:ee] == " ":
                                        cc -= 1
                                        ee = cc + 1
                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    if mvar == "mcom":
                        com = rtext[st:]
                    
                    textback += """Type <font color=blue>%s</font>: expansion or contraction
                                with critical flow.<br><br>

                                Upstream node: <font color=blue>%s</font><br><br>
                                Downstream node: <font color=blue>%s</font><br><br>
                                Node at which the flow through the
                                structure is specified: <font color=blue>%s</font><br><br>

                                Sign of the transition (+1 if
                                expansion in flow results when flow is from upstream node to
                                downstream node; otherwise -1): <font color=blue>%s</font><br><br>
                                Number of the table giving the
                                hydraulic characteristics of the cross section where critical
                                flow is computed: <font color=blue>%s</font><br><br>
                                Loss factor on velocity-head change
                                for flow from upstream node to downstream node: <font color=blue>%s</font><br><br>
                                Loss factor on velocity-head change
                                for flow from downstream node to upstream node: <font color=blue>%s</font><br><br>
                                Elevation for defining depth in the
                                section of critical flow: <font color=blue>%s</font><br><br>
                                Comments: <font color=blue>%s</font>
                                """ % (mtype, n2, n3, n4, n5, n6, f1, f2, f3, com) #check

                elif mtype == "2":
                    while rtext[cc:ee] == " ":                                                       #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  # ------------------------------------------
                        if ee > maxee:                                                               # Here the code will read and assign a value
                            break                                                                    # to variable 'n5'
                    while not rtext[cc:ee] == " ":                                                   #
                        if rtext[cc:ee] == ".":                                                      # 
                            mvar = "mfloat"                                                          # 
                            n5 = " "                                                                 #
                            n6 = " "
                            n7 = " "
                            n8 = " "
                            n9 = " "
                            n10 = " "
                            break                                                                    #
                        elif rtext[cc:ee] == "'":                                                    #
                            mvar = "mcom"                                                            #
                            n5 = " "                                                                 #
                            n6 = " "
                            n7 = " "
                            n8 = " "
                            n9 = " "
                            n10 = " "
                            break                                                                    #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  #
                        if ee > maxee:                                                               #
                            break
                    if mvar == "mint":
                        n5 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":                                                   # 'n6'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == ".":
                                mvar = "mfloat"
                                n6 = " "
                                n7 = " "
                                n8 = " "
                                n9 = " "
                                n10 = " "
                                break
                            elif rtext[cc:ee] == "'":
                                mvar = "mcom"
                                n6 = " "
                                n7 = " "
                                n8 = " "
                                n9 = " "
                                n10 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mint":
                            n6 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":                                               # 'n7'
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == ".":
                                    mvar = "mfloat"
                                    n7 = " "
                                    n8 = " "
                                    n9 = " "
                                    n10 = " "
                                    break
                                elif rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    n7 = " "
                                    n8 = " "
                                    n9 = " "
                                    n10 = " "
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mint":
                                n7 = rtext[st:cc]
                                st = cc

                                while rtext[cc:ee] == " ":                                           # 'n8'
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not rtext[cc:ee] == " ":
                                    if rtext[cc:ee] == ".":
                                        mvar = "mfloat"
                                        n8 = " "
                                        n9 = " "
                                        n10 = " "
                                        break
                                    elif rtext[cc:ee] == "'":
                                        mvar = "mcom"
                                        n8 = " "
                                        n9 = " "
                                        n10 = " "
                                        break
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                if mvar == "mint":
                                    n8 = rtext[st:cc]
                                    st = cc

                                    while rtext[cc:ee] == " ":                                       # 'n9'
                                        cc += 1
                                        ee = cc + 1
                                        if ee > maxee:
                                            break
                                    while not rtext[cc:ee] == " ":
                                        if rtext[cc:ee] == ".":
                                            mvar = "mfloat"
                                            n9 = " "
                                            n10 = " "
                                            break
                                        elif rtext[cc:ee] == "'":
                                            mvar = "mcom"
                                            n9 = " "
                                            n10 = " "
                                            break
                                        cc += 1
                                        ee = cc + 1
                                        if ee > maxee:
                                            break
                                    if mvar == "mint":
                                        n9 = rtext[st:cc]
                                        st = cc

                                        while rtext[cc:ee] == " ":                                   # 'n10'
                                            cc += 1
                                            ee = cc + 1
                                            if ee > maxee:
                                                break
                                        while not rtext[cc:ee] == " ":
                                            if rtext[cc:ee] == ".":
                                                mvar = "mfloat"
                                                n10 = " "
                                                break
                                            elif rtext[cc:ee] == "'":
                                                mvar = "mcom"
                                                n10 = " "
                                                break
                                            cc += 1
                                            ee = cc + 1
                                            if ee > maxee:
                                                break
                                        if mvar == "mint":
                                            n10 = rtext[st:cc]
                                            st = cc
                                            mvar = "mfloat"

                                        else:
                                            while not rtext[cc:ee] == " ":
                                                cc -=1
                                                ee = cc + 1
                                        
                                    else:
                                        while not rtext[cc:ee] == " ":
                                            cc -= 1
                                            ee = cc + 1

                                else:
                                    while not rtext[cc:ee] == " ":
                                        cc -= 1
                                        ee = cc + 1
                                
                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                            
                    else:
                        while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                            cc -= 1                                                                  # the code will go back to the beginning of
                            ee = cc + 1                                                              # the variable to read again

                    if mvar == "mfloat":
                        while rtext[cc:ee] == " ":                                                   # 'f1'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == "'":
                                mvar = "mcom"
                                f1 = " "
                                f2 = " "
                                f3 = " "
                                f4 = " "
                                f5 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mfloat":
                            f1 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":                                               # 'f2'
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    f2 = " "
                                    f3 = " "
                                    f4 = " "
                                    f5 = " "
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mfloat":
                                f2 = rtext[st:cc]
                                st = cc
                                
                                while rtext[cc:ee] == " ":                                           # 'f3'
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not rtext[cc:ee] == " ":
                                    if rtext[cc:ee] == "'":
                                        mvar = "mcom"
                                        f3 = " "
                                        f4 = " "
                                        f5 = " "
                                        break
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                if mvar == "mfloat":
                                    f3 = rtext[st:cc]
                                    st = cc

                                    while rtext[cc:ee] == " ":                                       # 'f4'
                                        cc += 1
                                        ee = cc + 1
                                        if ee > maxee:
                                            break
                                    while not rtext[cc:ee] == " ":
                                        if rtext[cc:ee] == "'":
                                            mvar = "mcom"
                                            f4 = " "
                                            f5 = " "
                                            break
                                        cc += 1
                                        ee = cc + 1
                                        if ee > maxee:
                                            break
                                    if mvar == "mfloat":
                                        f4 = rtext[st:cc]
                                        st = cc

                                        while rtext[cc:ee] == " ":                                   # 'f5'
                                            cc += 1
                                            ee = cc + 1
                                            if ee > maxee:
                                                break
                                        while not rtext[cc:ee] == " ":
                                            if rtext[cc:ee] == "'":
                                                mvar = "mcom"
                                                f5 = " "
                                                break
                                            cc += 1
                                            ee = cc + 1
                                            if ee > maxee:
                                                break
                                        if mvar == "mfloat":
                                            f5 = rtext[st:cc]
                                            st = cc
                                            mvar = "mcom"

                                        else:
                                            while not rtext[cc:ee] == " ":
                                                cc -= 1
                                                ee = cc + 1

                                    else:
                                        while not rtext[cc:ee] == " ":
                                            cc -= 1
                                            ee = cc + 1
                                else:
                                    while not rtext[cc:ee] == " ":
                                        cc -= 1
                                        ee = cc + 1
                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    if mvar == "mcom":
                        com = rtext[st:]
                    textback += """Type <font color=blue>%s</font>: bidirectional flow given
                                by tables, plus pumping.<br><br>

                                Upstream node: <font color=blue>%s</font><br><br>
                                Downstream node: <font color=blue>%s</font><br><br>
                                Node at which the flow through the
                                structure is specified: <font color=blue>%s</font><br><br>

                                Number of the table specifying flow in
                                the positive direction (from upstream node to downstream
                                node): <font color=blue>%s</font><br><br>
                                Number of the table specifying
                                submergence reduction for positive flow. (If 0, conveyance option is
                                applied and pumping parameters are ignored): <font color=blue>%s</font><br><br>
                                Number of the table specifying
                                flow in the negative direction: <font color=blue>%s</font><br><br>
                                Number of the table specifying
                                submergence reduction for negative flow: <font color=blue>%s</font><br><br>
                                If 0, water-surface elevation is
                                detected at the destination node for control of the pump. If 1,
                                flow rate is detected at the destination node for control of
                                the pump: <font color=blue>%s</font><br><br>
                                Node; if flow at this node is > 0,
                                pump will be switched off: <font color=blue>%s</font><br><br>
                                Elevation for the reference point
                                used for computing head: <font color=blue>%s</font><br><br>
                                Flow distance for the conveyance
                                option: <font color=blue>%s</font><br><br>
                                Pumping rating. (if 0, no pump is
                                simulated; if >0, pumping is simulated from U.S. to D.S.; if <0,
                                pumping is simulated from D.S. to U.S. : <font color=blue>%s</font><br><br>
                                Inlet elevation for the pump: <font color=blue>%s</font><br><br>
                                Cutoff value at the destination
                                node: <font color=blue>%s</font><br><br>
                                Comments: <font color=blue>%s</font>
                                """ % (mtype, n2, n3, n4, n5, n6, n7, n8, n9, n10, f1, f2, \
                                       f3, f4, f5, com)

                elif mtype == "3":
                    while rtext[cc:ee] == " ":                                                       #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  # ------------------------------------------
                        if ee > maxee:                                                               # Here the code will read and assign a value
                            break                                                                    # to variable 'n5'
                    while not rtext[cc:ee] == " ":                                                   #
                        if rtext[cc:ee] == ".":                                                      # 
                            mvar = "mfloat"                                                          # 
                            n5 = " "                                                                 #
                            n6 = " "
                            n7 = " "
                            n8 = " "
                            n9 = " "
                            n10 = " "
                            break                                                                    #
                        elif rtext[cc:ee] == "'":                                                    #
                            mvar = "mcom"                                                            #
                            n5 = " "                                                                 #
                            n6 = " "
                            n7 = " "
                            n8 = " "
                            n9 = " "
                            n10 = " "
                            break                                                                    #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  #
                        if ee > maxee:                                                               #
                            break
                    if mvar == "mint":
                        n5 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":                                                   # 'n6'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == ".":
                                mvar = "mfloat"
                                n6 = " "
                                n7 = " "
                                n8 = " "
                                n9 = " "
                                n10 = " "
                                break
                            elif rtext[cc:ee] == "'":
                                mvar = "mcom"
                                n6 = " "
                                n7 = " "
                                n8 = " "
                                n9 = " "
                                n10 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mint":
                            n6 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":                                               # 'n7'
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == ".":
                                    mvar = "mfloat"
                                    n7 = " "
                                    n8 = " "
                                    n9 = " "
                                    n10 = " "
                                    break
                                elif rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    n7 = " "
                                    n8 = " "
                                    n9 = " "
                                    n10 = " "
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mint":
                                n7 = rtext[st:cc]
                                st = cc

                                while rtext[cc:ee] == " ":                                           # 'n8'
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not rtext[cc:ee] == " ":
                                    if rtext[cc:ee] == ".":
                                        mvar = "mfloat"
                                        n8 = " "
                                        n9 = " "
                                        n10 = " "
                                        break
                                    elif rtext[cc:ee] == "'":
                                        mvar = "mcom"
                                        n8 = " "
                                        n9 = " "
                                        n10 = " "
                                        break
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                if mvar == "mint":
                                    n8 = rtext[st:cc]
                                    st = cc

                                    while rtext[cc:ee] == " ":                                       # 'n9'
                                        cc += 1
                                        ee = cc + 1
                                        if ee > maxee:
                                            break
                                    while not rtext[cc:ee] == " ":
                                        if rtext[cc:ee] == ".":
                                            mvar = "mfloat"
                                            n9 = " "
                                            n10 = " "
                                            break
                                        elif rtext[cc:ee] == "'":
                                            mvar = "mcom"
                                            n9 = " "
                                            n10 = " "
                                            break
                                        cc += 1
                                        ee = cc + 1
                                        if ee > maxee:
                                            break
                                    if mvar == "mint":
                                        n9 = rtext[st:cc]
                                        st = cc

                                        while rtext[cc:ee] == " ":                                   # 'n10'
                                            cc += 1
                                            ee = cc + 1
                                            if ee > maxee:
                                                break
                                        while not rtext[cc:ee] == " ":
                                            if rtext[cc:ee] == ".":
                                                mvar = "mfloat"
                                                n10 = " "
                                                break
                                            elif rtext[cc:ee] == "'":
                                                mvar = "mcom"
                                                n10 = " "
                                                break
                                            cc += 1
                                            ee = cc + 1
                                            if ee > maxee:
                                                break
                                        if mvar == "mint":
                                            n10 = rtext[st:cc]
                                            st = cc
                                            mvar = "mfloat"

                                        else:
                                            while not rtext[cc:ee] == " ":
                                                cc -=1
                                                ee = cc + 1
                                        
                                    else:
                                        while not rtext[cc:ee] == " ":
                                            cc -= 1
                                            ee = cc + 1

                                else:
                                    while not rtext[cc:ee] == " ":
                                        cc -= 1
                                        ee = cc + 1
                                
                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                            
                    else:
                        while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                            cc -= 1                                                                  # the code will go back to the beginning of
                            ee = cc + 1                                                              # the variable to read again

                    if mvar == "mfloat":
                        while rtext[cc:ee] == " ":                                                   # 'f1'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == "'":
                                mvar = "mcom"
                                f1 = " "
                                f2 = " "
                                f3 = " "
                                f4 = " "
                                f5 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mfloat":
                            f1 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":                                               # 'f2'
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    f2 = " "
                                    f3 = " "
                                    f4 = " "
                                    f5 = " "
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mfloat":
                                f2 = rtext[st:cc]
                                st = cc
                                
                                while rtext[cc:ee] == " ":                                           # 'f3'
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not rtext[cc:ee] == " ":
                                    if rtext[cc:ee] == "'":
                                        mvar = "mcom"
                                        f3 = " "
                                        f4 = " "
                                        f5 = " "
                                        break
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                if mvar == "mfloat":
                                    f3 = rtext[st:cc]
                                    st = cc

                                    while rtext[cc:ee] == " ":                                       # 'f4'
                                        cc += 1
                                        ee = cc + 1
                                        if ee > maxee:
                                            break
                                    while not rtext[cc:ee] == " ":
                                        if rtext[cc:ee] == "'":
                                            mvar = "mcom"
                                            f4 = " "
                                            f5 = " "
                                            break
                                        cc += 1
                                        ee = cc + 1
                                        if ee > maxee:
                                            break
                                    if mvar == "mfloat":
                                        f4 = rtext[st:cc]
                                        st = cc

                                        while rtext[cc:ee] == " ":                                   # 'f5'
                                            cc += 1
                                            ee = cc + 1
                                            if ee > maxee:
                                                break
                                        while not rtext[cc:ee] == " ":
                                            if rtext[cc:ee] == "'":
                                                mvar = "mcom"
                                                f5 = " "
                                                break
                                            cc += 1
                                            ee = cc + 1
                                            if ee > maxee:
                                                break
                                        if mvar == "mfloat":
                                            f5 = rtext[st:cc]
                                            st = cc
                                            mvar = "mcom"

                                        else:
                                            while not rtext[cc:ee] == " ":
                                                cc -= 1
                                                ee = cc + 1

                                    else:
                                        while not rtext[cc:ee] == " ":
                                            cc -= 1
                                            ee = cc + 1
                                else:
                                    while not rtext[cc:ee] == " ":
                                        cc -= 1
                                        ee = cc + 1
                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    if mvar == "mcom":
                        com = rtext[st:]
                    textback += """Type <font color=blue>%s</font>: variable-speed variable-head
                                pump.<br><br>

                                Upstream node: <font color=blue>%s</font><br><br>
                                Downstream node: <font color=blue>%s</font><br><br>
                                Node at which the flow through the
                                structure is specified: <font color=blue>%s</font><br><br>

                                Flow direction (1 is from U.S. to D.S.;
                                -1 is from D.S. to U.S.): <font color=blue>%s</font><br><br>
                                Number of table giving the flow
                                through the pump for each head (pump performance curve): <font color=blue>%s</font><br><br>
                                Number of table giving the sum of
                                the entrance losses at the inlet, friction losses in the inlet
                                conduit, and friction losses in the outlet conduit: <font color=blue>%s</font><br><br>
                                Number of table giving the exit loss
                                coefficient on the velocity head difference between the end of
                                the outlet conduit and the destination node: <font color=blue>%s</font><br><br>
                                If less than 0, number of table specifying
                                the pump speed as a function of time. If greater than 0, operation block
                                number controlling the pump. If 0, pump will run at its base
                                speed all the time: <font color=blue>%s</font><br><br>
                                Optional name for the pump (4 characters
                                max): <font color=blue>%s</font><br><br>
                                Elevation of the outlet conduit: <font color=blue>%s</font><br><br>
                                Area of the outlet conduit when flowing
                                full: <font color=blue>%s</font><br><br>
                                Elevation of the inlet conduit: <font color=blue>%s</font><br><br>
                                Factor on the velocity head at the
                                source node: <font color=blue>%s</font><br><br>
                                Factor on the velicity head at the
                                destination node: <font color=blue>%s</font><br><br>
                                Comments: <font color=blue>%s</font>
                                """ % (mtype, n2, n3, n4, n5, n6, n7, n8, n9, n10, f1, f2, \
                                       f3, f4, f5, com)

                elif mtype == "4":
                    while rtext[cc:ee] == " ":                                                       #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  # ------------------------------------------
                        if ee > maxee:                                                               # Here the code will read and assign a value
                            break                                                                    # to variable 'n5'
                    while not rtext[cc:ee] == " ":                                                   #
                        if rtext[cc:ee] == ".":                                                      # 
                            mvar = "mfloat"                                                          # 
                            n5 = " "                                                                 #
                            n6 = " "
                            n7 = " "
                            n8 = " "
                            n9 = " "
                            n10 = " "
                            break                                                                    #
                        elif rtext[cc:ee] == "'":                                                    #
                            mvar = "mcom"                                                            #
                            n5 = " "                                                                 #
                            n6 = " "
                            n7 = " "
                            n8 = " "
                            n9 = " "
                            n10 = " "
                            break                                                                    #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  #
                        if ee > maxee:                                                               #
                            break
                    if mvar == "mint":
                        n5 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":                                                   # 'n6'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == ".":
                                mvar = "mfloat"
                                n6 = " "
                                n7 = " "
                                n8 = " "
                                n9 = " "
                                n10 = " "
                                break
                            elif rtext[cc:ee] == "'":
                                mvar = "mcom"
                                n6 = " "
                                n7 = " "
                                n8 = " "
                                n9 = " "
                                n10 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mint":
                            n6 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":                                               # 'n7'
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == ".":
                                    mvar = "mfloat"
                                    n7 = " "
                                    n8 = " "
                                    n9 = " "
                                    n10 = " "
                                    break
                                elif rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    n7 = " "
                                    n8 = " "
                                    n9 = " "
                                    n10 = " "
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mint":
                                n7 = rtext[st:cc]
                                st = cc

                                while rtext[cc:ee] == " ":                                           # 'n8'
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not rtext[cc:ee] == " ":
                                    if rtext[cc:ee] == ".":
                                        mvar = "mfloat"
                                        n8 = " "
                                        n9 = " "
                                        n10 = " "
                                        break
                                    elif rtext[cc:ee] == "'":
                                        mvar = "mcom"
                                        n8 = " "
                                        n9 = " "
                                        n10 = " "
                                        break
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                if mvar == "mint":
                                    n8 = rtext[st:cc]
                                    st = cc

                                    while rtext[cc:ee] == " ":                                       # 'n9'
                                        cc += 1
                                        ee = cc + 1
                                        if ee > maxee:
                                            break
                                    while not rtext[cc:ee] == " ":
                                        if rtext[cc:ee] == ".":
                                            mvar = "mfloat"
                                            n9 = " "
                                            n10 = " "
                                            break
                                        elif rtext[cc:ee] == "'":
                                            mvar = "mcom"
                                            n9 = " "
                                            n10 = " "
                                            break
                                        cc += 1
                                        ee = cc + 1
                                        if ee > maxee:
                                            break
                                    if mvar == "mint":
                                        n9 = rtext[st:cc]
                                        st = cc

                                        while rtext[cc:ee] == " ":                                   # 'n10'
                                            cc += 1
                                            ee = cc + 1
                                            if ee > maxee:
                                                break
                                        while not rtext[cc:ee] == " ":
                                            if rtext[cc:ee] == ".":
                                                mvar = "mfloat"
                                                n10 = " "
                                                break
                                            elif rtext[cc:ee] == "'":
                                                mvar = "mcom"
                                                n10 = " "
                                                break
                                            cc += 1
                                            ee = cc + 1
                                            if ee > maxee:
                                                break
                                        if mvar == "mint":
                                            n10 = rtext[st:cc]
                                            st = cc
                                            mvar = "mfloat"

                                        else:
                                            while not rtext[cc:ee] == " ":
                                                cc -=1
                                                ee = cc + 1
                                        
                                    else:
                                        while not rtext[cc:ee] == " ":
                                            cc -= 1
                                            ee = cc + 1

                                else:
                                    while not rtext[cc:ee] == " ":
                                        cc -= 1
                                        ee = cc + 1
                                
                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                            
                    else:
                        while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                            cc -= 1                                                                  # the code will go back to the beginning of
                            ee = cc + 1                                                              # the variable to read again

                    if mvar == "mfloat":
                        while rtext[cc:ee] == " ":                                                   # 'f1'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == "'":
                                mvar = "mcom"
                                f1 = " "
                                f2 = " "
                                f3 = " "
                                f4 = " "
                                f5 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mfloat":
                            f1 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":                                               # 'f2'
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    f2 = " "
                                    f3 = " "
                                    f4 = " "
                                    f5 = " "
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mfloat":
                                f2 = rtext[st:cc]
                                st = cc
                                
                                while rtext[cc:ee] == " ":                                           # 'f3'
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not rtext[cc:ee] == " ":
                                    if rtext[cc:ee] == "'":
                                        mvar = "mcom"
                                        f3 = " "
                                        f4 = " "
                                        f5 = " "
                                        break
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                if mvar == "mfloat":
                                    f3 = rtext[st:cc]
                                    st = cc

                                    while rtext[cc:ee] == " ":                                       # 'f4'
                                        cc += 1
                                        ee = cc + 1
                                        if ee > maxee:
                                            break
                                    while not rtext[cc:ee] == " ":
                                        if rtext[cc:ee] == "'":
                                            mvar = "mcom"
                                            f4 = " "
                                            f5 = " "
                                            break
                                        cc += 1
                                        ee = cc + 1
                                        if ee > maxee:
                                            break
                                    if mvar == "mfloat":
                                        f4 = rtext[st:cc]
                                        st = cc
                                        mvar = "mcom"

                                    else:
                                        while not rtext[cc:ee] == " ":
                                            cc -= 1
                                            ee = cc + 1
                                else:
                                    while not rtext[cc:ee] == " ":
                                        cc -= 1
                                        ee = cc + 1
                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    if mvar == "mcom":
                        com = rtext[st:]
                    textback += """Type <font color=blue>%s</font>: bridge with flow over the
                                roadway.<br><br>

                                Upstream node: <font color=blue>%s</font><br><br>
                                Downstream node: <font color=blue>%s</font><br><br>
                                Node at which the flow through the
                                structure is specified: <font color=blue>%s</font><br><br>

                                Number of the table specifying
                                the bridge-loss coefficient as a function of water-surface
                                height at the bridge opening for positive flow: <font color=blue>%s</font><br><br>
                                Number of the table specifying
                                the bridge-loss coefficient as a function of water-surface
                                height at the bridge opening for negative flow: <font color=blue>%s</font><br><br>
                                Number of the table specifying
                                the area of bridge opening as a function of water-surface height: <font color=blue>%s</font><br><br>
                                Number of the table specifying
                                flow over the roadway as a function of head for positive flow: <font color=blue>%s</font><br><br>
                                Number of the table specifying
                                flow over the roadway as a function of head for negative flow: <font color=blue>%s</font><br><br>
                                Number of the table specifying
                                the submergence effect as a function of head ratio for flow
                                over the roadway: <font color=blue>%s</font><br><br>
                                Maximum flow area through the bridge: <font color=blue>%s</font><br><br>
                                Elevation of the high point of the
                                bridge opening: <font color=blue>%s</font><br><br>
                                Submerged-flow discharge coefficient
                                for the bridge: <font color=blue>%s</font><br><br>
                                Elevation for computing head on the
                                roadway: <font color=blue>%s</font><br><br>
                                Comments: <font color=blue>%s</font>
                                """ % (mtype, n2, n3, n4, n5, n6, n7, n8, n9, n10, f1, f2, \
                                       f3, f4, com)

                elif mtype == "5":
                    while rtext[cc:ee] == " ":                                                       #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  # ------------------------------------------
                        if ee > maxee:                                                               # Here the code will read and assign a value
                            break                                                                    # to variable 'n5'
                    while not rtext[cc:ee] == " ":                                                   #
                        if rtext[cc:ee] == ".":                                                      # 
                            mvar = "mfloat"                                                          # 
                            n5 = " "                                                                 #
                            n6 = " "
                            n7 = " "
                            n8 = " "
                            n9 = " "
                            n10 = " "
                            break                                                                    #
                        elif rtext[cc:ee] == "'":                                                    #
                            mvar = "mcom"                                                            #
                            n5 = " "                                                                 #
                            n6 = " "
                            n7 = " "
                            n8 = " "
                            n9 = " "
                            n10 = " "
                            break                                                                    #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  #
                        if ee > maxee:                                                               #
                            break
                    if mvar == "mint":
                        n5 = rtext[st:cc]
                        st = cc
                        mvar = "mcom"
                        
                    else:
                        while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                            cc -= 1                                                                  # the code will go back to the beginning of
                            ee = cc + 1                                                              # the variable to read again

                    
                    if mvar == "mcom":
                        com = rtext[st:]
                    textback += """Type <font color=blue>%s</font>: abrupt expansion with
                                inflow or outflow.<br><br>

                                Upstream node: <font color=blue>%s</font><br><br>
                                Downstream node: <font color=blue>%s</font><br><br>
                                Node at which the flow through the
                                structure is specified: <font color=blue>%s</font><br><br>

                                Number of the table specifying the
                                critical flow as a function of depth at the upstream node for
                                the abrupt expansion: <font color=blue>%s</font><br><br>
                                Comments: <font color=blue>%s</font>
                                """ % (mtype, n2, n3, n4, n5, com)

                elif mtype == "6":
                    while rtext[cc:ee] == " ":                                                       #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  # ------------------------------------------
                        if ee > maxee:                                                               # Here the code will read and assign a value
                            break                                                                    # to variable 'n5'
                    while not rtext[cc:ee] == " ":                                                   #
                        if rtext[cc:ee] == ".":                                                      # 
                            mvar = "mfloat"                                                          # 
                            n5 = " "                                                                 #
                            n6 = " "
                            n7 = " "
                            n8 = " "
                            n9 = " "
                            n10 = " "
                            break                                                                    #
                        elif rtext[cc:ee] == "'":                                                    #
                            mvar = "mcom"                                                            #
                            n5 = " "                                                                 #
                            n6 = " "
                            n7 = " "
                            n8 = " "
                            n9 = " "
                            n10 = " "
                            break                                                                    #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  #
                        if ee > maxee:                                                               #
                            break
                    if mvar == "mint":
                        n5 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":                                                   # 'n6'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == ".":
                                mvar = "mfloat"
                                n6 = " "
                                n7 = " "
                                n8 = " "
                                n9 = " "
                                n10 = " "
                                break
                            elif rtext[cc:ee] == "'":
                                mvar = "mcom"
                                n6 = " "
                                n7 = " "
                                n8 = " "
                                n9 = " "
                                n10 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mint":
                            n6 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":                                               # 'n7'
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == ".":
                                    mvar = "mfloat"
                                    n7 = " "
                                    n8 = " "
                                    n9 = " "
                                    n10 = " "
                                    break
                                elif rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    n7 = " "
                                    n8 = " "
                                    n9 = " "
                                    n10 = " "
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mint":
                                n7 = rtext[st:cc]
                                st = cc

                                while rtext[cc:ee] == " ":                                           # 'n8'
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not rtext[cc:ee] == " ":
                                    if rtext[cc:ee] == ".":
                                        mvar = "mfloat"
                                        n8 = " "
                                        n9 = " "
                                        n10 = " "
                                        break
                                    elif rtext[cc:ee] == "'":
                                        mvar = "mcom"
                                        n8 = " "
                                        n9 = " "
                                        n10 = " "
                                        break
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                if mvar == "mint":
                                    n8 = rtext[st:cc]
                                    st = cc

                                    while rtext[cc:ee] == " ":                                       # 'n9'
                                        cc += 1
                                        ee = cc + 1
                                        if ee > maxee:
                                            break
                                    while not rtext[cc:ee] == " ":
                                        if rtext[cc:ee] == ".":
                                            mvar = "mfloat"
                                            n9 = " "
                                            n10 = " "
                                            break
                                        elif rtext[cc:ee] == "'":
                                            mvar = "mcom"
                                            n9 = " "
                                            n10 = " "
                                            break
                                        cc += 1
                                        ee = cc + 1
                                        if ee > maxee:
                                            break
                                    if mvar == "mint":
                                        n9 = rtext[st:cc]
                                        st = cc
                                        mvar = "mfloat"
                                        
                                    else:
                                        while not rtext[cc:ee] == " ":
                                            cc -= 1
                                            ee = cc + 1

                                else:
                                    while not rtext[cc:ee] == " ":
                                        cc -= 1
                                        ee = cc + 1
                                
                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                            
                    else:
                        while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                            cc -= 1                                                                  # the code will go back to the beginning of
                            ee = cc + 1                                                              # the variable to read again

                    if mvar == "mfloat":
                        while rtext[cc:ee] == " ":                                                   # 'f1'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == "'":
                                mvar = "mcom"
                                f1 = " "
                                f2 = " "
                                f3 = " "
                                f4 = " "
                                f5 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mfloat":
                            f1 = rtext[st:cc]
                            st = cc
                            mvar = "mcom"
                            
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    if mvar == "mcom":
                        com = rtext[st:]
                    textback += """Type <font color=blue>%s</font>: Two-dimensional tables.<br><br>

                                Upstream node: <font color=blue>%s</font><br><br>
                                Downstream node: <font color=blue>%s</font><br><br>
                                Node at which the flow through the
                                structure is specified: <font color=blue>%s</font><br><br>

                                Number of the table specifying flow
                                from the upstream node to the downstream node: <font color=blue>%s</font><br><br>
                                Number of the table specifying flow
                                from the downstream node to the upstream node: <font color=blue>%s</font><br><br>
                                Number of an optional table
                                specifying a multiplying factor to apply to the values derived
                                from the tables given above: <font color=blue>%s</font><br><br>
                                Number of an optional table specifying
                                the elevation for computing heads as a function of time: <font color=blue>%s</font><br><br>
                                Continuation field: <font color=blue>%s</font><br><br>
                                Elevation for computing heads: <font color=blue>%s</font><br><br>
                                Comments: <font color=blue>%s</font>
                                """ % (mtype, n2, n3, n4, n5, n6, n7, n8, n9, f1, com)
                    

                elif mtype == "7":
                    while rtext[cc:ee] == " ":                                                       #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  # ------------------------------------------
                        if ee > maxee:                                                               # Here the code will read and assign a value
                            break                                                                    # to variable 'n5'
                    while not rtext[cc:ee] == " ":                                                   #
                        if rtext[cc:ee] == ".":                                                      # 
                            mvar = "mfloat"                                                          # 
                            n5 = " "                                                                 #
                            n6 = " "
                            n7 = " "
                            n8 = " "
                            n9 = " "
                            n10 = " "
                            break                                                                    #
                        elif rtext[cc:ee] == "'":                                                    #
                            mvar = "mcom"                                                            #
                            n5 = " "                                                                 #
                            n6 = " "
                            n7 = " "
                            n8 = " "
                            n9 = " "
                            n10 = " "
                            break                                                                    #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  #
                        if ee > maxee:                                                               #
                            break
                    if mvar == "mint":
                        n5 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":                                                   # 'n6'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == ".":
                                mvar = "mfloat"
                                n6 = " "
                                n7 = " "
                                n8 = " "
                                n9 = " "
                                n10 = " "
                                break
                            elif rtext[cc:ee] == "'":
                                mvar = "mcom"
                                n6 = " "
                                n7 = " "
                                n8 = " "
                                n9 = " "
                                n10 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mint":
                            n6 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":                                               # 'n7'
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == ".":
                                    mvar = "mfloat"
                                    n7 = " "
                                    n8 = " "
                                    n9 = " "
                                    n10 = " "
                                    break
                                elif rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    n7 = " "
                                    n8 = " "
                                    n9 = " "
                                    n10 = " "
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mint":
                                n7 = rtext[st:cc]
                                st = cc

                                while rtext[cc:ee] == " ":                                           # 'n8'
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not rtext[cc:ee] == " ":
                                    if rtext[cc:ee] == ".":
                                        mvar = "mfloat"
                                        n8 = " "
                                        n9 = " "
                                        n10 = " "
                                        break
                                    elif rtext[cc:ee] == "'":
                                        mvar = "mcom"
                                        n8 = " "
                                        n9 = " "
                                        n10 = " "
                                        break
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                if mvar == "mint":
                                    n8 = rtext[st:cc]
                                    st = cc

                                    while rtext[cc:ee] == " ":                                       # 'n9'
                                        cc += 1
                                        ee = cc + 1
                                        if ee > maxee:
                                            break
                                    while not rtext[cc:ee] == " ":
                                        if rtext[cc:ee] == ".":
                                            mvar = "mfloat"
                                            n9 = " "
                                            n10 = " "
                                            break
                                        elif rtext[cc:ee] == "'":
                                            mvar = "mcom"
                                            n9 = " "
                                            n10 = " "
                                            break
                                        cc += 1
                                        ee = cc + 1
                                        if ee > maxee:
                                            break
                                    if mvar == "mint":
                                        n9 = rtext[st:cc]
                                        st = cc

                                        while rtext[cc:ee] == " ":                                   # 'n10'
                                            cc += 1
                                            ee = cc + 1
                                            if ee > maxee:
                                                break
                                        while not rtext[cc:ee] == " ":
                                            if rtext[cc:ee] == ".":
                                                mvar = "mfloat"
                                                n10 = " "
                                                break
                                            elif rtext[cc:ee] == "'":
                                                mvar = "mcom"
                                                n10 = " "
                                                break
                                            cc += 1
                                            ee = cc + 1
                                            if ee > maxee:
                                                break
                                        if mvar == "mint":
                                            n10 = rtext[st:cc]
                                            st = cc
                                            mvar = "mfloat"

                                        else:
                                            while not rtext[cc:ee] == " ":
                                                cc -=1
                                                ee = cc + 1
                                        
                                    else:
                                        while not rtext[cc:ee] == " ":
                                            cc -= 1
                                            ee = cc + 1

                                else:
                                    while not rtext[cc:ee] == " ":
                                        cc -= 1
                                        ee = cc + 1
                                
                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                            
                    else:
                        while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                            cc -= 1                                                                  # the code will go back to the beginning of
                            ee = cc + 1                                                              # the variable to read again

                    if mvar == "mfloat":
                        while rtext[cc:ee] == " ":                                                   # 'f1'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == "'":
                                mvar = "mcom"
                                f1 = " "
                                f2 = " "
                                f3 = " "
                                f4 = " "
                                f5 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mfloat":
                            f1 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":                                               # 'f2'
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    f2 = " "
                                    f3 = " "
                                    f4 = " "
                                    f5 = " "
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mfloat":
                                f2 = rtext[st:cc]
                                st = cc
                                mvar = "mcom"
                                
                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    if mvar == "mcom":
                        com = rtext[st:]
                    textback += """Type <font color=blue>%s</font>: variable-height weir.<br><br>

                                Upstream node: <font color=blue>%s</font><br><br>
                                Downstream node: <font color=blue>%s</font><br><br>
                                Node at which the flow through the
                                structure is specified: <font color=blue>%s</font><br><br>

                                Operation block number (if >0),
                                number of the table specifying the opening fraction as a
                                function of time (if <0): <font color=blue>%s</font><br><br>
                                Number of the table specifying
                                the elevation of the weir crest as a function of
                                the opening fraction: <font color=blue>%s</font><br><br>
                                Number of the table specifying
                                the weir coefficient for flow from the upstream node to the
                                downstream node as a function of the opening fraction: <font color=blue>%s</font><br><br>
                                Number of the table specifying
                                the weir coefficient for flow from the downstream node to the
                                upstream node as a function of the opening fraction: <font color=blue>%s</font><br><br>
                                Number of the table specifying
                                the submergence correction for flow over the weir: <font color=blue>%s</font><br><br>
                                Opetional name for the weir
                                (4 characters max.): <font color=blue>%s</font><br><br>
                                Weir length: <font color=blue>%s</font><br><br>
                                Factor to apply to velocity head
                                when computing the total head applicable to the weir equation: <font color=blue>%s</font><br>
                                <br>Comments: <font color=blue>%s</font>
                                """ % (mtype, n2, n3, n4, n5, n6, n7, n8, n9, n10, f1, f2, \
                                       com)

                elif mtype == "8": #check this type
                    while rtext[cc:ee] == " ":                                                       #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  # ------------------------------------------
                        if ee > maxee:                                                               # Here the code will read and assign a value
                            break                                                                    # to variable 'n5'
                    while not rtext[cc:ee] == " ":                                                   #
                        if rtext[cc:ee] == ".":                                                      # 
                            mvar = "mfloat"                                                          # 
                            n5 = " "                                                                 #
                            n6 = " "
                            n7 = " "
                            n8 = " "
                            n9 = " "
                            n10 = " "
                            break                                                                    #
                        elif rtext[cc:ee] == "'":                                                    #
                            mvar = "mcom"                                                            #
                            n5 = " "                                                                 #
                            n6 = " "
                            n7 = " "
                            n8 = " "
                            n9 = " "
                            n10 = " "
                            break                                                                    #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  #
                        if ee > maxee:                                                               #
                            break
                    if mvar == "mint":
                        n5 = rtext[st:cc]
                        st = cc
                        mvar = "mfloat"
                            
                    else:
                        while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                            cc -= 1                                                                  # the code will go back to the beginning of
                            ee = cc + 1                                                              # the variable to read again

                    if mvar == "mfloat":
                        while rtext[cc:ee] == " ":                                                   # 'f1'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == "'":
                                mvar = "mcom"
                                f1 = " "
                                f2 = " "
                                f3 = " "
                                f4 = " "
                                f5 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mfloat":
                            f1 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":                                               # 'f2'
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    f2 = " "
                                    f3 = " "
                                    f4 = " "
                                    f5 = " "
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mfloat":
                                f2 = rtext[st:cc]
                                st = cc
                                
                                while rtext[cc:ee] == " ":                                           # 'f3'
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not rtext[cc:ee] == " ":
                                    if rtext[cc:ee] == "'":
                                        mvar = "mcom"
                                        f3 = " "
                                        f4 = " "
                                        f5 = " "
                                        break
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                if mvar == "mfloat":
                                    f3 = rtext[st:cc]
                                    st = cc
                                    mvar = "mcom"
                                    
                                else:
                                    while not rtext[cc:ee] == " ":
                                        cc -= 1
                                        ee = cc + 1
                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    if mvar == "mcom":
                        com = rtext[st:]
                    textback += """Type <font color=blue>%s</font>: sluice gates at Stratton
                                Dam at McHenry, Ill.<br><br>

                                Upstream node: <font color=blue>%s</font><br><br>
                                Downstream node: <font color=blue>%s</font><br><br>
                                Node at which the flow through the
                                structure is specified: <font color=blue>%s</font><br><br>

                                Operation block number (if >0),
                                number of table specifying the gate opening as a function of
                                time (if greater than 0): <font color=blue>%s</font><br><br>
                                Sill elevation for the sluice
                                gates (731.15 ft): <font color=blue>%s</font><br><br>
                                Maximum gate opening, in feet: <font color=blue>%s</font><br><br>
                                Factor to apply to the flows to
                                represent change in width from the standard width at McHenry of
                                68.75 ft: <font color=blue>%s</font><br><br>
                                Comments: <font color=blue>%s</font>
                                """ % (mtype, n2, n3, n4, n5, f1, f2, f3, com)

                elif mtype == "9":
                    while rtext[cc:ee] == " ":                                                       #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  # ------------------------------------------
                        if ee > maxee:                                                               # Here the code will read and assign a value
                            break                                                                    # to variable 'n5'
                    while not rtext[cc:ee] == " ":                                                   #
                        if rtext[cc:ee] == ".":                                                      # 
                            mvar = "mfloat"                                                          # 
                            n5 = " "                                                                 #
                            n6 = " "
                            n7 = " "
                            n8 = " "
                            n9 = " "
                            n10 = " "
                            break                                                                    #
                        elif rtext[cc:ee] == "'":                                                    #
                            mvar = "mcom"                                                            #
                            n5 = " "                                                                 #
                            n6 = " "
                            n7 = " "
                            n8 = " "
                            n9 = " "
                            n10 = " "
                            break                                                                    #
                        cc += 1                                                                      #
                        ee = cc + 1                                                                  #
                        if ee > maxee:                                                               #
                            break
                    if mvar == "mint":
                        n5 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":                                                   # 'n6'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == ".":
                                mvar = "mfloat"
                                n6 = " "
                                n7 = " "
                                n8 = " "
                                n9 = " "
                                n10 = " "
                                break
                            elif rtext[cc:ee] == "'":
                                mvar = "mcom"
                                n6 = " "
                                n7 = " "
                                n8 = " "
                                n9 = " "
                                n10 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mint":
                            n6 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":                                               # 'n7'
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == ".":
                                    mvar = "mfloat"
                                    n7 = " "
                                    n8 = " "
                                    n9 = " "
                                    n10 = " "
                                    break
                                elif rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    n7 = " "
                                    n8 = " "
                                    n9 = " "
                                    n10 = " "
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mint":
                                n7 = rtext[st:cc]
                                st = cc

                                while rtext[cc:ee] == " ":                                           # 'n8'
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not rtext[cc:ee] == " ":
                                    if rtext[cc:ee] == ".":
                                        mvar = "mfloat"
                                        n8 = " "
                                        n9 = " "
                                        n10 = " "
                                        break
                                    elif rtext[cc:ee] == "'":
                                        mvar = "mcom"
                                        n8 = " "
                                        n9 = " "
                                        n10 = " "
                                        break
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                if mvar == "mint":
                                    n8 = rtext[st:cc]
                                    st = cc
                                    mvar = "mfloat"

                                else:
                                    while not rtext[cc:ee] == " ":
                                        cc -= 1
                                        ee = cc + 1
                                
                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                            
                    else:
                        while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                            cc -= 1                                                                  # the code will go back to the beginning of
                            ee = cc + 1                                                              # the variable to read again

                    if mvar == "mfloat":
                        while rtext[cc:ee] == " ":                                                   # 'f1'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == "'":
                                mvar = "mcom"
                                f1 = " "
                                f2 = " "
                                f3 = " "
                                f4 = " "
                                f5 = " "
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mfloat":
                            f1 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":                                               # 'f2'
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    f2 = " "
                                    f3 = " "
                                    f4 = " "
                                    f5 = " "
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mfloat":
                                f2 = rtext[st:cc]
                                st = cc
                                mvar = "mcom"
                                
                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    if mvar == "mcom":
                        com = rtext[st:]
                    textback += """Type <font color=blue>%s</font>: underflow fates tables.<br><br>

                                Upstream node: <font color=blue>%s</font><br><br>
                                Downstream node: <font color=blue>%s</font><br><br>
                                Node at which the flow through the
                                structure is specified: <font color=blue>%s</font><br><br>

                                Operation block number(if >0),
                                or number of table specifying the gate opening as a function
                                of time (if <0): <font color=blue>%s</font><br><br>
                                Name of the gate (max. 4 characters): <font color=blue>%s</font>
                                <br><br>
                                Number of a type 15 table for flow
                                from the upstream node to the downstream node: <font color=blue>%s</font><br><br>
                                Number of a type 15 table for flow
                                from the downstream node to the upstream node: <font color=blue>%s</font><br><br>
                                Sill elevation for the sluice
                                gates: <font color=blue>%s</font><br><br>
                                Maximum gate opening in feet: <font color=blue>%s</font><br><br>
                                Comments: <font color=blue>%s</font>
                                """ % (mtype, n2, n3, n4, n5, n6, n7, n8, f1, f2, com)


                textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
                                


                                
                

            elif rcode == "MX6":
                mtype = rtext[5:10]
                mtype.replace(" ","")
                mvar = "mint"                                                                        # ------------------------------------------
                                                                                                     # The variable type will default to integer
                maxee = len(rtext)                                                                   # 'mint'
                cc = 10                                                                              # ------------------------------------------
                ee = cc + 1                                                                          #
                st = cc

                n2 = " "
                n3 = " "
                n4 = " "
                f1 = " "
                f2 = " "
                com = " "

                while rtext[cc:ee] == " ":                                                       #
                    cc += 1                                                                      #
                    ee = cc + 1                                                                  # ------------------------------------------
                    if ee > maxee:                                                               # Here the code will read and assign a value
                        break                                                                    # to variable 'n2'
                while not rtext[cc:ee] == " ":                                                   #
                    if rtext[cc:ee] == ".":                                                      # 
                        mvar = "mfloat"                                                          # 
                        break                                                                    #
                    elif rtext[cc:ee] == "'":                                                    #
                        mvar = "mcom"                                                            #
                        break                                                                    #
                    cc += 1                                                                      #
                    ee = cc + 1                                                                  #
                    if ee > maxee:                                                               #
                        break
                if mvar == "mint":
                    n2 = rtext[st:cc]
                    st = cc

                    while rtext[cc:ee] == " ":                                                   # 'n3'
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        if rtext[cc:ee] == ".":
                            mvar = "mfloat"
                            break
                        elif rtext[cc:ee] == "'":
                            mvar = "mcom"
                            break
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    if mvar == "mint":
                        n3 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":                                               # 'n4'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == ".":
                                mvar = "mfloat"
                                break
                            elif rtext[cc:ee] == "'":
                                mvar = "mcom"
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mint":
                            n4 = rtext[st:cc]
                            st = cc
                            mvar = "mfloat"
                                
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    else:
                        while not rtext[cc:ee] == " ":
                            cc -= 1
                            ee = cc + 1
                            
                else:
                    while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                        cc -= 1                                                                  # the code will go back to the beginning of
                        ee = cc + 1                                                              # the variable to read again

                if mvar == "mfloat":
                    while rtext[cc:ee] == " ":                                                   # 'f1'
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        if rtext[cc:ee] == "'":
                            mvar = "mcom"
                            break
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    if mvar == "mfloat":
                        f1 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":                                               # 'f2'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == "'":
                                mvar = "mcom"
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mfloat":
                            f2 = rtext[st:cc]
                            st = cc
                            mvar = "mcom"
                                
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    else:
                        while not rtext[cc:ee] == " ":
                            cc -= 1
                            ee = cc + 1
                if mvar == "mcom":
                    com = rtext[st:]
                textback += """Code <font color=blue>6</font>: Node with forced value
                            of flow or elevation (Boundary conditions).<br><br>"""
                if mtype == "1":
                    textback += """Type <font color=blue>%s</font>: flow as a function of time.
                                <br><br>""" % mtype
                elif mtype == "2":
                    textback += """Type <font color=blue>%s</font>: elevation as a function of
                                time.<br><br>""" % mtype
                textback += """Number of the flow-path end node
                            where the forcing takes place: <font color=blue>%s</font><br><br>
                            Direction of flow (flow into system
                            if 1, flow out of system if -1): <font color=blue>%s</font><br><br>
                            Source for forcing values. Table number
                            if >0; constant value if =0; Fortran unit number if less than 0: <font color=blue>%s</font><br><br>
                            Constant flow value: <font color=blue>%s</font><br><Br>
                            Multiplier on the value given by the
                            source for flows and elevation: <font color=blue>%s</font><br><Br>
                            Comments: <font color=blue>%s</font>
                            """ % (n2, n3, n4, f1, f2, com)

                textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
                                   

            elif rcode == "MX7":
                mvar = "mint"                                                                        # ------------------------------------------
                                                                                                     # The variable type will default to integer
                maxee = len(rtext)                                                                   # 'mint'
                cc = 5                                                                              # ------------------------------------------
                ee = cc + 1                                                                          #
                st = cc

                n1 = " "
                n2 = " "
                n3 = " "
                n4 = " "
                f1 = " "
                com = " "

                while rtext[cc:ee] == " ":                                                       #
                    cc += 1                                                                      #
                    ee = cc + 1                                                                  # ------------------------------------------
                    if ee > maxee:                                                               # Here the code will read and assign a value
                        break                                                                    # to variable 'n1'
                while not rtext[cc:ee] == " ":                                                   #
                    if rtext[cc:ee] == ".":                                                      # 
                        mvar = "mfloat"                                                          # 
                        break                                                                    #
                    elif rtext[cc:ee] == "'":                                                    #
                        mvar = "mcom"                                                            #
                        break                                                                    #
                    cc += 1                                                                      #
                    ee = cc + 1                                                                  #
                    if ee > maxee:                                                               #
                        break
                if mvar == "mint":
                    n1 = rtext[st:cc]
                    st = cc

                    while rtext[cc:ee] == " ":                                                   # 'n2'
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        if rtext[cc:ee] == ".":
                            mvar = "mfloat"
                            break
                        elif rtext[cc:ee] == "'":
                            mvar = "mcom"
                            break
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    if mvar == "mint":
                        n2 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":                                               # 'n3'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == ".":
                                mvar = "mfloat"
                                break
                            elif rtext[cc:ee] == "'":
                                mvar = "mcom"
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mint":
                            n3 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":                                           # 'n4'
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == ".":
                                    mvar = "mfloat"
                                    break
                                elif rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mint":
                                n4 = rtext[st:cc]
                                st = cc
                                mvar = "mfloat"

                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1
                                
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    else:
                        while not rtext[cc:ee] == " ":
                            cc -= 1
                            ee = cc + 1
                            
                else:
                    while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                        cc -= 1                                                                  # the code will go back to the beginning of
                        ee = cc + 1                                                              # the variable to read again

                if mvar == "mfloat":
                    while rtext[cc:ee] == " ":                                                   # 'f1'
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        if rtext[cc:ee] == "'":
                            mvar = "mcom"
                            break
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    if mvar == "mfloat":
                        f1 = rtext[st:cc]
                        st = cc
                        mvar = "mcom"
                        
                    else:
                        while not rtext[cc:ee] == " ":
                            cc -= 1
                            ee = cc + 1
                if mvar == "mcom":
                    com = rtext[st:]
                textback += """Code <font color=blue>7</font>: Level-pool reservoir.<br><br>
                            Node number of the reservoir: <font color=blue>%s</font><br><br>
                            Number of the table specifying
                            storage as a function of elevation for the reservoir: <font color=blue>%s</font><br><br>
                            Number of inflow nodes (must be 1): <font color=blue>%s</font><br><Br>
                            Inflow node number: <font color=blue>%s</font><br><br>
                            Slope factor: <font color=blue>%s</font><br><br>
                            Comments: <font color=blue>%s</font>
                            """ % (n1, n2, n3, n4, f1, com)

                textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

            elif rcode == "MX8":
                textback += """Code <font color=blue>%s</font>: Critical depth.<br><br>
                            Number of the branch-end node where
                            cross-sectional hydraulic characteristics are defined: <font color=blue>%s</font><br><br>
                            Comments: <font color=blue>%s</font>
                            """ % (rtext[:5], rtext[5:55], rtext[55:])

                textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
                

            elif rcode == "MX9":
                textback += """Not in use: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[:5]

            elif rcode == "MX10":
                textback += """Not in use: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[:5]

            elif rcode == "MX11":
                maxee = len(rtext)
                cc = 5
                st = cc
                ee = cc + 1
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                n1 = rtext[st:cc]
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                n2 = rtext[st:cc]
                com = rtext[cc:]
                textback += """Code <font color=blue>11</font>: Conservation of momentum
                                or constant elevation between the following nodes:<br><br>
                                Upstream node: <font color=blue>%s</font><br><br>
                                Downstream node: <font color=blue>%s</font><br><br>
                                Comments: <font color=blue>%s</font>
                                <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % (n1, n2, com)
                
            elif rcode == "MX12":
                mvar = "mint"                                                                        # ------------------------------------------
                                                                                                     # The variable type will default to integer
                maxee = len(rtext)                                                                   # 'mint'
                cc = 5                                                                              # ------------------------------------------
                ee = cc + 1                                                                          #
                st = cc

                n1 = " "
                n2 = " "
                n3 = " "
                f1 = " "
                com = " "

                while rtext[cc:ee] == " ":                                                       #
                    cc += 1                                                                      #
                    ee = cc + 1                                                                  # ------------------------------------------
                    if ee > maxee:                                                               # Here the code will read and assign a value
                        break                                                                    # to variable 'n1'
                while not rtext[cc:ee] == " ":                                                   #
                    if rtext[cc:ee] == ".":                                                      # 
                        mvar = "mfloat"                                                          # 
                        break                                                                    #
                    elif rtext[cc:ee] == "'":                                                    #
                        mvar = "mcom"                                                            #
                        break                                                                    #
                    cc += 1                                                                      #
                    ee = cc + 1                                                                  #
                    if ee > maxee:                                                               #
                        break
                if mvar == "mint":
                    n1 = rtext[st:cc]
                    st = cc

                    while rtext[cc:ee] == " ":                                                   # 'n2'
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        if rtext[cc:ee] == ".":
                            mvar = "mfloat"
                            break
                        elif rtext[cc:ee] == "'":
                            mvar = "mcom"
                            break
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    if mvar == "mint":
                        n2 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":                                               # 'n3'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == ".":
                                mvar = "mfloat"
                                break
                            elif rtext[cc:ee] == "'":
                                mvar = "mcom"
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mint":
                            n3 = rtext[st:cc]
                            st = cc
                            mvar = "mfloat"
                                
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    else:
                        while not rtext[cc:ee] == " ":
                            cc -= 1
                            ee = cc + 1
                            
                else:
                    while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                        cc -= 1                                                                  # the code will go back to the beginning of
                        ee = cc + 1                                                              # the variable to read again

                if mvar == "mfloat":
                    while rtext[cc:ee] == " ":                                                   # 'f1'
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        if rtext[cc:ee] == "'":
                            mvar = "mcom"
                            break
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    if mvar == "mfloat":
                        f1 = rtext[st:cc]
                        st = cc
                        mvar = "mcom"
                        
                    else:
                        while not rtext[cc:ee] == " ":
                            cc -= 1
                            ee = cc + 1
                if mvar == "mcom":
                    com = rtext[st:]
                textback += """Code <font color=blue>12</font>: Match average elevation
                            at two nodes.<br><br>
                            Upstream node for averaging: <font color=blue>%s</font><br><br>
                            Downstream node for averaging: <font color=blue>%s</font><br><br>
                            Node at which average elevation
                            will be forced: <font color=blue>%s</font><br><br>
                            Weight to be used in computing
                            the average: <font color=blue>%s</font><br><br>
                            Comments: <font color=blue>%s</font>
                            <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % (n1, n2, n3, f1, com)
                
            elif rcode == "MX13":
                mvar = "mint"                                                                        # ------------------------------------------
                                                                                                     # The variable type will default to integer
                maxee = len(rtext)                                                                   # 'mint'
                cc = 5                                                                              # ------------------------------------------
                ee = cc + 1                                                                          #
                st = cc

                n1 = " "
                n2 = " "
                n3 = " "
                n4 = " "
                n5 = " "
                f1 = " "
                f2 = " "
                f3 = " "
                com = " "

                while rtext[cc:ee] == " ":                                                       #
                    cc += 1                                                                      #
                    ee = cc + 1                                                                  # ------------------------------------------
                    if ee > maxee:                                                               # Here the code will read and assign a value
                        break                                                                    # to variable 'n1'
                while not rtext[cc:ee] == " ":                                                   #
                    if rtext[cc:ee] == ".":                                                      # 
                        mvar = "mfloat"                                                          # 
                        break                                                                    #
                    elif rtext[cc:ee] == "'":                                                    #
                        mvar = "mcom"                                                            #
                        break                                                                    #
                    cc += 1                                                                      #
                    ee = cc + 1                                                                  #
                    if ee > maxee:                                                               #
                        break
                if mvar == "mint":
                    n1 = rtext[st:cc]
                    st = cc

                    while rtext[cc:ee] == " ":                                                   # 'n2'
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        if rtext[cc:ee] == ".":
                            mvar = "mfloat"
                            break
                        elif rtext[cc:ee] == "'":
                            mvar = "mcom"
                            break
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    if mvar == "mint":
                        n2 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":                                               # 'n3'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == ".":
                                mvar = "mfloat"
                                break
                            elif rtext[cc:ee] == "'":
                                mvar = "mcom"
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mint":
                            n3 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":                                           # 'n4'
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == ".":
                                    mvar = "mfloat"
                                    break
                                elif rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mint":
                                n4 = rtext[st:cc]
                                st = cc

                                while rtext[cc:ee] == " ":                                       # 'n5'
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not rtext[cc:ee] == " ":
                                    if rtext[cc:ee] == ".":
                                        mvar = "mfloat"
                                        break
                                    elif rtext[cc:ee] == "'":
                                        mvar = "mcom"
                                        break
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                if mvar == "mint":
                                    n5 = rtext[st:cc]
                                    st = cc
                                    mvar = "mfloat"

                                else:
                                    while not rtext[cc:ee] == " ":
                                        cc -= 1
                                        ee = cc + 1

                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1
                                
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    else:
                        while not rtext[cc:ee] == " ":
                            cc -= 1
                            ee = cc + 1
                            
                else:
                    while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                        cc -= 1                                                                  # the code will go back to the beginning of
                        ee = cc + 1                                                              # the variable to read again

                if mvar == "mfloat":
                    while rtext[cc:ee] == " ":                                                   # 'f1'
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        if rtext[cc:ee] == "'":
                            mvar = "mcom"
                            break
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    if mvar == "mfloat":
                        f1 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":                                               # 'f2'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == "'":
                                mvar = "mcom"
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mfloat":
                            f2 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":                                           # 'f3'
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mfloat":
                                f3 = rtext[st:cc]
                                st = cc
                                mvar = "mcom"

                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1

                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                                
                        
                    else:
                        while not rtext[cc:ee] == " ":
                            cc -= 1
                            ee = cc + 1
                if mvar == "mcom":
                    com = rtext[st:]
                textback += """Code <font color=blue>13</font>: Conservation of momentum
                                or energy.<br><br>
                                Upstream node on the source
                                channel: <font color=blue>%s</font><br><br>
                                Downstream node on the source
                                channel: <font color=blue>%s</font><br><br>
                                Number of side-inflow nodes: <font color=blue>%s</font><br><br>
                                Side nodes:<br>
                                1: <font color=blue>%s</font><br>
                                2: <font color=blue>%s</font><br><br>
                                Loss coefficient to apply to energy
                                equation: <font color=blue>%s</font><br><br>
                                Angle of water entry for side node 1: <font color=blue>%s</font>
                                <br><br>
                                Angle of water entry for side node 2: <font color=blue>%s</font>
                                <br><br>
                                Comments: <font color=blue>%s</font>
                                <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % (n1, n2, n3, n4, n5, f1, f2, f3, com)
                
            elif rcode == "MX14":
                mvar = "mint"                                                                        # ------------------------------------------
                                                                                                     # The variable type will default to integer
                maxee = len(rtext)                                                                   # 'mint'
                cc = 5                                                                              # ------------------------------------------
                ee = cc + 1                                                                          #
                st = cc

                n1 = " "
                n2 = " "
                n3 = " "
                n4 = " "
                n5 = " "
                f1 = " "
                f2 = " "
                com = " "

                while rtext[cc:ee] == " ":                                                       #
                    cc += 1                                                                      #
                    ee = cc + 1                                                                  # ------------------------------------------
                    if ee > maxee:                                                               # Here the code will read and assign a value
                        break                                                                    # to variable 'n1'
                while not rtext[cc:ee] == " ":                                                   #
                    if rtext[cc:ee] == ".":                                                      # 
                        mvar = "mfloat"                                                          # 
                        break                                                                    #
                    elif rtext[cc:ee] == "'":                                                    #
                        mvar = "mcom"                                                            #
                        break                                                                    #
                    cc += 1                                                                      #
                    ee = cc + 1                                                                  #
                    if ee > maxee:                                                               #
                        break
                if mvar == "mint":
                    n1 = rtext[st:cc]
                    st = cc

                    while rtext[cc:ee] == " ":                                                   # 'n2'
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        if rtext[cc:ee] == ".":
                            mvar = "mfloat"
                            break
                        elif rtext[cc:ee] == "'":
                            mvar = "mcom"
                            break
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    if mvar == "mint":
                        n2 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":                                               # 'n3'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == ".":
                                mvar = "mfloat"
                                break
                            elif rtext[cc:ee] == "'":
                                mvar = "mcom"
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mint":
                            n3 = rtext[st:cc]
                            st = cc

                            while rtext[cc:ee] == " ":                                           # 'n4'
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            while not rtext[cc:ee] == " ":
                                if rtext[cc:ee] == ".":
                                    mvar = "mfloat"
                                    break
                                elif rtext[cc:ee] == "'":
                                    mvar = "mcom"
                                    break
                                cc += 1
                                ee = cc + 1
                                if ee > maxee:
                                    break
                            if mvar == "mint":
                                n4 = rtext[st:cc]
                                st = cc

                                while rtext[cc:ee] == " ":                                       # 'n5'
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                while not rtext[cc:ee] == " ":
                                    if rtext[cc:ee] == ".":
                                        mvar = "mfloat"
                                        break
                                    elif rtext[cc:ee] == "'":
                                        mvar = "mcom"
                                        break
                                    cc += 1
                                    ee = cc + 1
                                    if ee > maxee:
                                        break
                                if mvar == "mint":
                                    n5 = rtext[st:cc]
                                    st = cc
                                    mvar = "mfloat"

                                else:
                                    while not rtext[cc:ee] == " ":
                                        cc -= 1
                                        ee = cc + 1

                            else:
                                while not rtext[cc:ee] == " ":
                                    cc -= 1
                                    ee = cc + 1
                                
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    else:
                        while not rtext[cc:ee] == " ":
                            cc -= 1
                            ee = cc + 1
                            
                else:
                    while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                        cc -= 1                                                                  # the code will go back to the beginning of
                        ee = cc + 1                                                              # the variable to read again

                if mvar == "mfloat":
                    while rtext[cc:ee] == " ":                                                   # 'f1'
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        if rtext[cc:ee] == "'":
                            mvar = "mcom"
                            break
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    if mvar == "mfloat":
                        f1 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":                                               # 'f2'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        while not rtext[cc:ee] == " ":
                            if rtext[cc:ee] == "'":
                                mvar = "mcom"
                                break
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mfloat":
                            f2 = rtext[st:cc]
                            st = cc
                            mvar = "mcom"

                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                                
                        
                    else:
                        while not rtext[cc:ee] == " ":
                            cc -= 1
                            ee = cc + 1
                if mvar == "mcom":
                    com = rtext[st:]
                textback += """Code <font color=blue>14</font>: Side-weir flow.<br><br>
                            Upstream node: <font color=blue>%s</font><br><br>
                            Downstream node: <font color=blue>%s</font><br><br>
                            Node used to represent the outflow
                            or inflow to the source channel: <font color=blue>%s</font><br><br>
                            Flow table of type 13 defining the
                            outflow over the side weir: <font color=blue>%s</font><br><br>
                            Flow table of type 13 representing
                            inflow over the side weir: <font color=blue>%s</font><br><br>
                            Weight coefficient used in computing
                            the average water-surface height, elevation, and flow rate into
                            the source channel: <font color=blue>%s</font><br><br>
                            Elevation from which the heads included
                            in the flow tables are measured: <font color=blue>%s</font><br><br>
                            Comments: <font color=blue>%s</font>
                            <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % (n1, n2, n3, n4, n5, f1, f2, com)

                
            elif rcode == "MX15":
                
                mvar = "mint"                                                                        # ------------------------------------------
                                                                                                     # The variable type will default to integer
                maxee = len(rtext)                                                                   # 'mint'
                cc = 5                                                                              # ------------------------------------------
                ee = cc + 1                                                                          #
                st = cc

                n1 = " "
                n2 = " "
                f1 = " "
                f2 = " "
                com = " "

                while rtext[cc:ee] == " ":                                                       #
                    cc += 1                                                                      #
                    ee = cc + 1                                                                  # ------------------------------------------
                    if ee > maxee:                                                               # Here the code will read and assign a value
                        break                                                                    # to variable 'n1'
                while not rtext[cc:ee] == " ":                                                   #
                    if rtext[cc:ee] == ".":                                                      # 
                        mvar = "mfloat"                                                          # 
                        break                                                                    #
                    elif rtext[cc:ee] == "'":                                                    #
                        mvar = "mcom"                                                            #
                        break                                                                    #
                    cc += 1                                                                      #
                    ee = cc + 1                                                                  #
                    if ee > maxee:                                                               #
                        break
                if mvar == "mint":
                    n1 = rtext[st:cc]
                    st = cc

                    while rtext[cc:ee] == " ":                                                   # 'n2'
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        if rtext[cc:ee] == ".":
                            mvar = "mfloat"
                            break
                        elif rtext[cc:ee] == "'":
                            mvar = "mcom"
                            break
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    if mvar == "mint":
                        n2 = rtext[st:cc]
                        st = cc
                        mvar = "mfloat"

                        
                    else:
                        while not rtext[cc:ee] == " ":
                            cc -= 1
                            ee = cc + 1
                            
                else:
                    while not rtext[cc:ee] == " ":                                               # If the variable is a float or a comment,
                        cc -= 1                                                                  # the code will go back to the beginning of
                        ee = cc + 1                                                              # the variable to read again

                if mvar == "mfloat":
                    while rtext[cc:ee] == " ":                                                   # 'f1'
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        if rtext[cc:ee] == "'":
                            mvar = "mcom"
                            break
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    if mvar == "mfloat":
                        f1 = rtext[st:cc]
                        st = cc

                        while rtext[cc:ee] == " ":                                               # 'f2'
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if rtext[cc:ee] == "'":
                            mvar = "mcom"
                        while not rtext[cc:ee] == " " and not rtext[cc:ee] == "'":
                            cc += 1
                            ee = cc + 1
                            if ee > maxee:
                                break
                        if mvar == "mfloat":
                            f2 = rtext[st:cc]
                            st = cc
                            mvar = "mcom"
                                
                        else:
                            while not rtext[cc:ee] == " ":
                                cc -= 1
                                ee = cc + 1
                    else:
                        while not rtext[cc:ee] == " ":
                            cc -= 1
                            ee = cc + 1
                if mvar == "mcom":
                    com = rtext[st:]
                textback += """Code <font color=blue>15</font>: Dummy branch.<br><br>
                            Upstream node: <font color=blue>%s</font><br><br>
                            Downstream node: <font color=blue>%s</font><br><br>
                            Slope factor: <font color=blue>%s</font><br><br>
                            Surface area: <font color=blue>%s</font><br><br>
                            Comments: <font color=blue>%s</font>
                            <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % (n1, n2, f1, f2, com)

            elif "-1" in rtext[:5]:
                textback += """End of network matrix<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

            elif rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment: <font color=blue>%s</font><br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext
                
        elif rcode == "MTXB":
            textback = """<b>Network Matrix Control</b><br><br>
                        Boundary node to use for
                        initializing the development of the network matrix: <font color=blue>%s</font>
                        <br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>""" % rtext[6:]


        elif rcode == "OUTL":                                               #Special Output
            textback = """<b>Special Output Locations</b><br><br>"""
            if rtext.startsWith("HOME"):
                textback += """<b>HOME</b> - Default directory for the output file: 
                            <font color=blue>%s</font>""" % rtext[5:]
            elif rtext.startsWith("UNIT"):
                textback += """<b>UNIT</b> - File used for storing the special output: <font color=blue>%s</font>""" % rtext[5:]
            elif rtext.startsWith("OUTNAM"):
                textback += """<b>OUTNAM</b> - Name for the file used for
                            storing the special output: <font color=blue>%s</font>""" % rtext[7:]
            elif rtext.startsWith("NAME"):
                textback += """<b>NAME</b> - Name for the file used for
                            storing the special output: <font color=blue>%s</font>""" % rtext[5:]
            elif "BRA" in rtext or "NODE" in rtext:
                rtext.replace(" ","<br>")
                while "<br><br>" in rtext:
                    rtext.replace("<br><br>","<br>")
                textback += """Table headers: <font color=blue>%s</font>
                            """ % rtext

            elif rtext.startsWith("   -1"):
                textback += """End of block."""

            elif rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment: <font color=blue>%s</font>""" % rtext

            else:
                maxee = len(rtext)
                global outbraL
                global outbraT
                global outnodeL
                global outnodeT
                global outhead1L
                global outhead1T
                global outhead2L
                global outhead2T
                outbraT.replace("_","")
                outbraT.replace(" ","")
                outnodeT.replace("_","")
                outnodeT.replace(" ","")
                outhead1T.replace("_","")
                outhead1T.replace(" ","")
                outhead2T.replace("_","")
                outhead2T.replace(" ","")
                outhead1D = outhead1T
                outhead2D = outhead2T
                bra = rtext[:outbraL]
                node = rtext[outbraL:outnodeL]
                head1 = rtext[outnodeL:outhead1L]
                if outhead1T == "":
                    cc = outnodeL
                    ee = cc + 1
                    while rtext[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    head1 = rtext[outnodeL:cc]
                head2 = rtext[outhead1L:]
                if outhead1T == "":
                    head2 = rtext[cc:]
                    outhead1D = "Node"
                    outhead2D = "Info"
                textback += """Branch number (if 0,
                            the node column contains an exterior node label): <font color=blue>%s</font><br><br>
                            %s: <font color=blue>%s</font><br><br>
                            %s: <font color=blue>%s</font><br><br>
                            %s: <font color=blue>%s</font><br><br>
                            """ % (bra, outnodeT, node, outhead1D, head1, outhead2D, head2)

            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_9update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""



        elif rcode == "INPF": #check update                                     #Input Files
            textback = """Input Files Block<br><br>"""
            if rtext.startsWith(" UNIT"):
                rtext.replace(" ", "<br>")
                textback += """Headers: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("HOME"):
                textback += """<b>HOME</b> - Default directory for the output file: 
                            <font color=blue>%s</font>""" % rtext[5:]
            elif rtext.startsWith("   -1"):
                textback += """End of block."""

            elif rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment: <font color=blue>%s</font>""" % rtext
            else:
                textback += """Fortran unit number
                            of the PTSF: <font color=blue>%s</font><br><br>
                            File name for PTSF file: <font color=blue>%s</font>
                            """ % (rtext[:5], rtext[5:])

            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_10update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
            


        elif rcode == "OUTF":                                                       #Output Files
            textback = """Output Files Block<br><br>"""
            if "BRA" in rtext:
                rtext.replace(" ","<br>")
                rtext.replace("<br><br>", "<br>")
                rtext.replace("<br><br>", "<br>")
                textback += """Table headers:<br><br><font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("   -1"):
                textback += """End of block."""

            elif rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment: <font color=blue>%s</font>""" % rtext

            elif rtext.startsWith("HOME"):
                textback += """Home directory: <font color=blue>%s</font>""" % rtext[5:]

            else:
                global outfunitL
                global outfbraL
                global outfnodeL
                global outfitemL
                global outftypeL
                global outfnameL
                unit = rtext[:outfunitL]
                bran = rtext[outfunitL:outfbraL]
                node = rtext[outfbraL:outfnodeL]
                item = rtext[outfnodeL:outfitemL]
                typ = rtext[outfitemL:outftypeL]
                name = rtext[outftypeL:]
                textback += """Unit: <font color=blue>%s</font> (this column is no longer
                            used by FEQ).<br><br>
                            Branch: <font color=blue>%s</font> (branch number)<br><br>
                            Node: <font color=blue>%s</font> (node number)<br><br>
                            Item: <font color=blue>%s</font><br>
                            (Item=FLOW : output of flow)<br>
                            (Item=ELEV : output of elevation)<br><br>
                            Type: <font color=blue>%s</font> (instantaneous values are to
                            be output)<br><br>
                            Name of PTSF file or path of HEC DSS
                            time series: <font color=blue>%s</font>""" % (unit, bran, node, item, typ, name)

            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_11update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
                
                            

        elif rcode.startsWith("CtrS"):                                            #Control Structures
            
            textback = """<b>Operation of Control Structures</b><br><br>
                        Block #<font color=blue>%s</font><br><br>""" % rcode[5:]
            order = rcode[5:]

            if rtext.startsWith("BLK="):
                textback += """<b>BLK</b> - Block number: <font color=blue>%s</font>""" % rtext[4:]

            elif rtext.startsWith("BLKTYPE"):
                textback += """<b>BLKTYPE</b> - Type of Structure: <font color=blue>%s</font>
                            """ % rtext[8:12]

            elif rtext.startsWith("MINDT"):
                textback += """<b>MINDT</b> - Minimum time (s) between
                            changes to the gate or pump setting: <font color=blue>%s</font>""" % rtext[6:]

            elif rtext.startsWith("PINIT"):
                textback += """<b>PINIT</b> - Initial value for the
                            opening fraction (varies between 0 - 1): <font color=blue>%s</font><br><br>
                            Example:<br>
                            0 = gate fully closed<br>
                            1 = gate fully opened""" % rtext[6:]

            elif "BRA" in rtext and "KEY" in rtext:
                rtext.replace("   "," ")
                rtext.replace("  "," ")
                rtext.replace(" ","<br>")
                rtext.replace("<br><br>","<br>")
                textback += """Table headers:<br> <font color=blue>%s</font>""" % rtext

            elif rtext.startsWith("   -1"):
                textback += """End"""

            else:
                global csBLKTYPE
                global csbranL
                global csnodeL
                global cskeyL
                global csmodeL
                global csmnrateL
                global cslrateL
                global cslowlimL
                global cshghlimL
                global cshrateL
                global cslpriL
                global csnpriL
                global cshpriL
                global csdpdtL
                global csriseL
                global csfallL
                global csonprL
                global csofprL
                    
                if csBLKTYPE[order] == "GATE":
                    cc = 0
                    ee = csbranL[order]
                    bran = rtext[cc:ee]
                    cc = ee
                    ee = csnodeL[order]
                    node = rtext[cc:ee]
                    cc = ee
                    ee = cskeyL[order]
                    key = rtext[cc:ee]
                    cc = ee
                    ee = csmodeL[order]
                    mode = rtext[cc:ee]
                    cc = ee
                    ee = csmnrateL[order]
                    mnrate = rtext[cc:ee]
                    cc = ee
                    ee = cslrateL[order]
                    lrate = rtext[cc:ee]
                    cc = ee
                    ee = cslowlimL[order]
                    lowlim = rtext[cc:ee]
                    cc = ee
                    ee = cshghlimL[order]
                    hghlim = rtext[cc:ee]
                    cc = ee
                    ee = cshrateL[order]
                    hrate = rtext[cc:ee]
                    cc = ee
                    ee = cslpriL[order]
                    lpri = rtext[cc:ee]
                    cc = ee
                    ee = csnpriL[order]
                    npri = rtext[cc:ee]
                    cc = ee
                    ee = cshpriL[order]
                    hpri = rtext[cc:ee]
                    cc = ee
                    ee = csdpdtL[order]
                    dpdt = rtext[cc:ee] #should detail
                    textback += """Branch number: <font color=blue>%s</font><br>
                                Node: <font color=blue>%s</font><br>
                                Key: <font color=blue>%s</font><br>
                                Mode: <font color=blue>%s</font><br>
                                Minimum change per hour: <font color=blue>%s</font><br>
                                Rate factor for the rate of change of opening
                                when conditions are below null zone: <font color=blue>%s</font><br>
                                Lower limit: <font color=blue>%s</font><br>
                                Upper limit: <font color=blue>%s</font><br>
                                Rate factor for the rate of change of opening
                                when conditions are above null zone: <font color=blue>%s</font><br>
                                Priority of action when below null zone: <font color=blue>%s</font><br>
                                Priority of action when in null zone: <font color=blue>%s</font><br>
                                Priority of action when above null zone: <font color=blue>%s</font><br>
                                Max. rate of change in the opening fraction: <font color=blue>%s</font><br>
                                """ % (bran, node, key, mode, mnrate, lrate, lowlim, hghlim, \
                                       hrate, lpri, npri, hpri, dpdt)

                elif csBLKTYPE[order] == "PUMP":
                    cc = 0
                    ee = csbranL[order]
                    bran = rtext[cc:ee]
                    cc = ee
                    ee = csnodeL[order]
                    node = rtext[cc:ee]
                    cc = ee
                    ee = cskeyL[order]
                    key = rtext[cc:ee]
                    cc = ee
                    ee = csmnrateL[order]
                    mnrate = rtext[cc:ee]
                    cc = ee
                    ee = csriseL[order]
                    rise = rtext[cc:ee]
                    cc = ee
                    ee = csfallL[order]
                    fall = rtext[cc:ee]
                    cc = ee
                    ee = csonprL[order]
                    onpr = rtext[cc:ee]
                    cc = ee
                    ee = csofprL[order]
                    ofpr = rtext[cc:ee]

                    textback += """Branch number: <font color=blue>%s</font><br>
                                Node: <font color=blue>%s</font><br>
                                Key: <font color=blue>%s</font><br>
                                Minimum change per hour: <font color=blue>%s</font><br>
                                Table specifying pump speed as a function of increasing
                                level: <font color=blue>%s</font><br>
                                Table specifying pump speed as a function of decreasing
                                level: <font color=blue>%s</font><br>
                                Priority assigned to the control-point when pump is on:
                                <font color=blue>%s</font><br>
                                Priority assigned to the control-point when pump is off:
                                <font color=blue>%s</font><br>
                                """ % (bran, node, key, mnrate, rise, fall, onpr, ofpr)
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_12update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
                    
                    
        elif rcode == "CtrlS":
            textback = """End of control structures block."""

            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feq98.i2h/13_12update.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
                                
                    
        elif rcode.startsWith("TAB"):                                             #Function Tables
            textback = """<b>Function Tables Block</b><br><br>"""
            if rtext.startsWith("*") or rtext.startsWith(";"):
                textback += """Comment: <font color=blue>%s</font>""" % rtext
            elif rcode == "TAB E":
                textback += """Block end."""
            elif rcode == "TAB F":
                textback += """Location of files<br><br>"""
                if "FILE=" in rtext:
                    ee = 1
                    maxee = len(rtext)
                    while not "FILE=" in rtext[:ee]:
                        ee += 1
                        if ee == maxee:
                            break
                        
                    textback += """File location: <font color=blue>%s</font>""" % rtext[ee:]
                elif "HOME=" in rtext:
                    ee = 1
                    maxee = len(rtext)
                    while not "HOME=" in rtext[:ee]:
                        ee += 1
                        if ee == maxee:
                            break

                    textback += """Default directory of files: 
                                <font color=blue>%s</font>""" % rtext[ee:]

            elif rcode == "TAB-":
                textback += """FORTRAN unit number or location or table: <font color=blue>
                            %s</font>""" % rtext[7:]

            else:
                tabno = rcode[4:]
                textback += """Table %s<br><br>""" % tabno
                if rtext.startsWith("TABLE#="):
                    textback += """Table number: <font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("TABID="):
                    textback += """Table number: <font color=blue>%s</font>""" % rtext[6:]
                elif rtext.startsWith("TYPE="):
                    textback += """Type: <font color=blue>%s</font>""" % rtext[5:]
                elif rtext.startsWith("REFL="): #ADD FAC
                    textback += """Reference level read by FEQ (not used):
                                <font color=blue>%s</font>""" % rtext[5:]
                elif "HEAD" in rtext:
                    rtext.replace(" ","<br>")
                    rtext.replace("<br><br><br>","<br>")
                    rtext.replace("<br><br>","<br>")
                    textback += """Table headers:<br><br><font color=blue>%s</font>""" % rtext
                elif rtext.startsWith("     -1"):
                    textback += """End of table."""
                else:
                    textback += """Head: <font color=blue>%s</font><br>
                                Discharge: <font color=blue>%s</font><br>
                                """ % (rtext[:10], rtext[10:])

            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_14.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
                        
            
        elif rcode == "FRND":                                                           #Free Node Blk
            textback = """<b>Free Node Initial Conditions</b><br><br>"""
            if rtext.startsWith("*") or rtext.startsWith(";"):
                textback += """Comment: <font color=blue>%s</font>""" % rtext
            elif "NODE" in rtext:
                rtext.replace(" ","<br>")
                while "<br><br>" in rtext:
                    rtext.replace("<br><br>","<br>")
                textback += """Table headers:<br><br><font color=blue>%s</font>""" % rtext
            else:
                global fnnodeL
                global fnnodeidL
                global fndepthL
                global fndischargeL
                global fnelevationL
                node = rtext[:fnnodeL]
                nodeid = rtext[fnnodeL:fnnodeidL]
                depth = rtext[fnnodeidL:fndepthL]
                discharge = rtext[fndepthL:fndischargeL]
                elev = rtext[fndischargeL:fnelevationL]

                textback += """Node parameters:<br><br>
                            Node: <font color=blue>%s</font><br>
                            Node ID: <font color=blue>%s</font><br>
                            Depth: <font color=blue>%s</font><br>
                            Discharge: <font color=blue>%s</font><br>
                            Elevation:<font color=blue>%s</font><br>""" % (node, nodeid, depth, \
                                                                           discharge, elev)

            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_15.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

        elif rcode == "BW":                                                          #Backwater

            textback = "<b>Backwater Analysis</b><br><br>"
            if rtext.startsWith("*") or rtext.startsWith(";"):
                textback += "Comment: <font color=blue>%s</font>" % rtext

            elif rtext.startsWith("BRANCH"):
                textback += "Branch number: <font color=blue>%s</font>" % rtext[14:]
            elif rtext.startsWith("DISCHARGE"):
                textback += "Discharge: <font color=blue>%s</font>" % rtext[10:]

            elif "CODE" in rtext:
                rtext.replace(" ","<br>")
                textback += "Table headers:<br><br><font color=blue>%s</font>" % rtext

            else:
                style = 1
                global bwbraL
                global bwcode1L
                global bwcode2L
                global bwelev1L
                global bwelev2L
                global bwexnL

                bra_test = rtext[:bwbraL]
                bra_test.replace(" ","")
                b = bwbraL + 1
                if bra_test == "" and not rtext[bwbraL:bwcode1L] == " ":
                    bra_test = rtext[:bwcode1L]
                    bra_test.replace(" ","")
                    b = bwbraL + 1
                if not bra_test == "":
                    while not " " in rtext[bwbraL:b]:
                        if b == bwcode1L:
                            b += 1
                            break
                        b += 1
                        
                    b -= 1
                    if b > bwbraL:
                        style = 2
                    if not " " in rtext[bwbraL:bwcode2L]:
                        b = bwbraL
                code_test = rtext[b:bwcode2L]
                code_test.replace(" ","")
                c = b
                if code_test == "" and style == 2:
                    code_test = rtext[b:bwelev1L]
                    code_test.replace(" ","")
                if not code_test == "":
                    while " " in rtext[c:c+1]:
                        c += 1
                    while not " " in rtext[c:c+1]:
                        c += 1
                        if c == bwelev1L:
                            break
                elev_test= rtext[c:bwelev2L]
                elev_test.replace(" ","")
                e = c
                if not elev_test == "":
                    while " " in rtext[e:e+1]:
                        e += 1
                    while not " " in rtext[e:e+1]:
                        e += 1
                        if e == bwexnL:
                            break

                bra = rtext[:b]
                code = rtext[b:c]
                elev = rtext[c:e]
                exn = rtext[e:]

                bra.replace(" ","")
                if bra == "0":
                    textback += """Elevation of <font color=blue>%s</font> will be the same
                                as <font color=blue>%s</font>.<br><br>""" % (code, exn)
                elif bra == "-1":
                    textback += """Block end."""
                else:
                    textback += """Branch number: <font color=blue>%s</font><br><br>""" % bra

                    code.replace(" ","")
                    if code == "0":
                        textback += """Code <font color=blue>0</font>: starting elevation
                                is the sum of the elevation of the water surface at the
                                node specified in EXN and the value specified for ELEVATION.
                                <br><br>"""
                    elif code == "1":
                        textback += """Code <font color=blue>1</font>: starting elevation
                                is used as final elevation (fixed).<br><br>"""

                    elif code == "2":
                        textback += """Code <font color=blue>2</font>: critical depth is
                                computed at the downstream end using ELEVATION as a first
                                estimate.<br><br>"""
                    elif code == "3":
                        textback += """Code <font color=blue>3</font>: water surface height is
                                computed from the stage-discharge relation specified in
                                the Network-Matrix block.<br><br>"""

                    elif code == "-3":
                        textback += """Code <font color=blue>-3</font>: water-surface height is
                                computed from a stage-discharge relation specified at the free
                                node given in EXN.<br><br>"""

                    elif code == "5":
                        textback += """Code <font color=blue>5</font>: critical depth is computed
                                at the downstream end of the branch by use of the elevation
                                in ELEVATION as a first estimate.<br><br>"""

                    elif code == "6":
                        textback += """Code <font color=blue>6</font>: upstream water-surface
                                elevation is computed from the flow and the downstream
                                water-surface elevation for a two-node control structure is
                                defined in the Network-Matrix block.<br><br>"""

                    textback += """Increment elevation: <font color=blue>%s</font><br><br>
                            Exn: <font color=blue>%s</font><br><br>""" % (elev, exn)

            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/feqdoc/chap13html/chap13_16.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""


        else:
            textback = "Cannot interpret."
        return textback


    def interpretFTL(self, rcode, rtext):

        if rcode == "TITLE":                                           #Headings
            textback = """<b></b>The first three lines of the file are no longer used but
                        required for the program to run correctly."""


        elif rcode == "COM":                                           #Comments
            textback = """Comment:<br>
                        <font color="blue">%s</font>""" % rtext[1:]

        elif rcode == "UNIT":                                          #HEADERS block
            textback = """<b>UNIT</b> - Unit system: <font color=blue>%s</font><br><Br>
                        Format: ENGLISH or METRIC""" % rtext[6:]
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_3.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
        elif rcode == "DZLI":
            textback = """<b>DZLIM</b> - Minimum water-surface height increment in output table;
                        must be &#62; 0: <font color=blue>%s</font><br><br>""" % rtext[6:]
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_3.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
            
        elif rcode == "NRZE":
            textback = """<b>NRZERO</b> - Minimum nonzero water-surface height in the table;
                        must be &#62; 0: <font color=blue>%s</font>""" % rtext[7:]
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_3.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
            
        elif rcode == "USBE":
            textback = """<b>USGSBETA</b> - Use of computation of the energy-flux correction coefficient, and the momentum
                        correction coefficient&#63;: <font color=blue>%s</font>""" % rtext[9:]
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_3.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
            
        elif rcode == "EPSA":
            textback = """<b>EPSARG</b> - Convergence criterion for CULVERT, EXPCON: <font color=blue>%s</font><br><br>""" % rtext[7:]
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_3.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
            
        elif rcode == "EPSF":
            textback = """<b>EPSF</b> - Convergence criterion for CULVERT, EXPCON: <font color=blue>%s</font><br><br>""" % rtext[5:15]
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_3.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
            
            if " EPSABS=" in rtext:
                    a = 0
                    b = 1
                    while not " EPSABS=" in rtext[a:b]:
                        b += 1
                    
                    textback += """EPSABS=<font color=blue>%s</font>:""" % rtext[b:]
            
        elif rcode == "EXTE":
            textback = """<b>EXTEND</b> - Use cross-section extension option&#63;: <font color=blue>%s</font>""" % rtext[7:]
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_3.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
            
        elif rcode == "NCMD":
            global commands
            textback = """<b>NCMD</b> - Number of Commands: <font color=blue>%i</font><br><br>""" % commands
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_3.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a><br><br>"""
            
            if rtext.startsWith("NCMD"):
                textback += """This variable specifies the number of commands present in the
                                block. The commands are identified by a name (Example: CULVERT)
                                and an internal control number (Example: 4). <br><br>
                                NOTE: The internal control number should not be changed""" 

        elif rcode.startsWith("FEQX"):                                          #FEQX block
            textback = """<b>Cross-section function tables.</b><br><br>"""
            if rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment: <font color=blue>%s</font>""" % rtext[1:]
            elif rtext.startsWith("TABLE") or rtext.startsWith("TABID") or "EXTEND" in rtext \
                 or "MONOTONE" in rtext or "BETA" in rtext or "SAVE" in rtext or "OUT" in rtext \
                 or "GISID" in rtext:
                if rtext.startsWith("TABLE#"):
                    a = 7
                    if " " in rtext[11:13]:
                        b = 12
                    else:
                        b = 13
                    tablnum = rtext[a:b]
                    textback += """Table number: <font color=blue>%s</font><br><br><u>Table options:</u><br>
                            """ % tablnum.split(' ', 1)[0]
                elif rtext.startsWith("TABID"):
                    a = 6
                    tablnum = rtext[a:]
                    textback += """Table number: <font color=blue>%s</font><br><br><u>Table options:</u><br>
                            """ % tablnum.split(' ', 1)[0]
                if "GISID" in rtext:
                    textback += """<br><br><b>GISID</b> - an identification string for
                            the cross section for a geographic information system: <font color=blue>%s</font><br>""" % rtext.split("GISID=")[-1]
                if "EXTEND" in rtext:
                    textback += """<br><font color=blue>EXTEND</font>: a vertical extension is
                                added to the first or last points to match the point of
                                maximum elevation in the cross section."""
                if "MONOTONE" in rtext:
                    textback += """<br><font color=blue>MONOTONE</font>: the offsets for the
                                cross section are examined to ensure that they are
                                increasing."""
                if " NEWBETA" in rtext or rtext.startsWith("NEWBETA"):
                    textback += """<br><font color=blue>NEWBETA</font>: the momentum-flux
                                correction coefficient and the kinetic-energy-flux correction
                                coefficient are computed by application of a method."""
                if "NEWBETAE" in rtext:
                    textback += """<br><font color=blue>NEWBETAE</font>: same as NEWBETA
                                except that the critical flow tabulated is based on the
                                energy principle."""
                if "NEWBETAM" in rtext:
                    textback += """<br><font color=blue>NEWBETAM</font>: same as NEWBETA
                                except that the critical flow tabulated is based on the
                                energy principle."""
                if "OLDBETA" in rtext:
                    textback += """<br><font color=blue>OLDBETA</font>: the kinetic-energy-flux
                                correction coefficient and the momentum-flux correction coefficient
                                for the cross section are computed from equations 7 and 8 in section
                                3.1.1."""
                if " SAVE" in rtext or rtext.startsWith("SAVE"):
                    a = 0
                    b = 1
                    if not rtext.startsWith("SAVE"):
                        while not " SAVE" in rtext[a:b]:
                            b += 1
                    else:
                        while not "SAVE" in rtext[a:b]:
                            b += 1
                    
                    textback += """<br><font color=blue>%s</font>: a copy of the resulting
                                table is saved internally in the FEQUTL computations. The table type
                                is given by the two digits next to SAVE.""" % rtext[b - 4:b + 2] 
                if "NOSAVE" in rtext:
                    textback += """<br><font color=blue>NOSAVE</font>: a copy of the table is
                                not saved internally in the FEQUTL computations."""
                if " OUT" in rtext or rtext.startsWith("OUT"):
                    a = 0
                    b = 1
                    if not rtext.startsWith("OUT"):
                        while not " OUT" in rtext[a:b]:
                            b += 1
                        c = 4
                    else:
                        while not "OUT" in rtext[a:b]:
                            b += 1
                        c = 3
                        
                    textback += """<br><font color=blue>%s</font>: a copy of the table is
                                output to the standard function-table file given by the two digits
                                after OUT.""" % rtext[b - c:b + 2] 
                if "NOOUT" in rtext:
                    textback += """<br><font color=blue>NOOUT</font>: output of the table to the
                                standard function-table file is suppressed."""
            elif rtext.startsWith("ZONE"):
                zone = rtext.split('ZONE=')[-1]
                textback +=  """<br><b>ZONE</b> - The zone designation for the horizontal grid: 
                            <font color=blue>%s</font>""" % re.split('\s+', zone)[0]
                if "HGRID" in rtext:
                    hgrid = rtext.split('HGRID=')[1]
                    textback += """<br><br><b>HGRID</b> - The name for the horizontal grid used for 
                                eastings and northings: <font color=blue>%s</font>""" % re.split('\s+', hgrid)[0]
                if "BASIS" in rtext:
                    basis = rtext.split('BASIS=')[1]
                    textback += """<br><br><b>BASIS</b> - The description of era, date, or other item to 
                                denote the data source: <font color=blue>%s</font>""" % re.split('\s+', basis)[0]
                if "VDATUM" in rtext:
                    vdatum = rtext.split('VDATUM=')[1]
                    textback += """<br><br><b>VDATUM</b> - The vertical datum: <font color=blue>%s</font>""" % re.split('\s+', vdatum)[0]
                if "UNITSYS" in rtext:
                    unitsys = rtext.split('UNITSYS=')[1]
                    textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('\s+', unitsys)[0]
            elif rtext.startsWith("EASTING"):
                    a = 8
                    while not rtext[a:a+1] == "N":
                        a += 1
                        if a > len(rtext):
                            break
                    textback += """<b>EASTING</b> - The easting or x value for the coordinate system: <font color=blue>%s</font><br><br>
                                <b>NORTHING</b> - The northing or y value for the coordinate system: 
                                <font color=blue>%s</font>""" % (rtext[8:a], rtext[a+9:])
            elif rtext.startsWith("STATION"):
                rtext.replace(" L","<br>L")
                rtext.replace(" R","<br>R")
                rtext.replace(" ","")
                rtext = rtext.split('STATION=')[-1]
                textback += """<b>STATION</b> - the station of the cross section: <font color=blue>%s</font><br><br>
                            LEFT and RIGHT are the offsets on the left and right side of the cross
                            section, respectively, where a vertical frictionless wall is added in
                            the computation.""" % rtext.split('EASTING')[0]
                if "EASTING" in rtext:
                    rtext = rtext.split('EASTING', 1)[-1]
                    a = 0
                    while not rtext[a:a+1] == "N":
                        a += 1
                        if a > len(rtext):
                            break
                    textback += """<br><br><b>EASTING</b> - The easting or x value for the coordinate system: <font color=blue>%s</font><br><br>
                                <b>NORTHING</b> - The northing or y value for the coordinate system: <font color=blue>%s</font>""" % (rtext[1:a], rtext[a+9:])
            elif rtext.startsWith("NAVM"):
                rtext = re.split('NAVM=\s*', rtext)[-1]
                textback += """<b>NAVM</b>: <font color=blue>%s</font>""" % re.split('\s*', rtext)[0]
                textback += """<br><br><b>NAVM</b> - specifies the methodology for computing
                            the effective roughness of a compound cross section and also provides optional
                            values for scaling of the offsets and shifting of the elevations. If <b>NAVM</b>=0, the
                            total conveyance is computed from the sum of the subsection conveyances (given
                            by equations 5 and 6). This is the method applied for most open channels and
                            results in the total discharge equal to the sum of the subsection
                            discharges. If <b>NAVM</b>=1, a weighted-average Manning's <i>n</i> value is computed
                            with the wetted perimeter in each subsection as the weight. The conveyance for the
                            cross section is then computed with the weighted-average <i>n</i> value. This is the
                            method usually applied for closed conduits with abrupt changes of roughness around
                            the perimeter and results in the total discharge equal to an assumed uniform flow
                            velocity times the flow area."""
                if "VSCALE" in rtext:
                    vscale = re.split('VSCALE\s*=\s*', rtext)[-1]
                    textback += """<br><br><b>VSCALE</b>: <font color=blue>%s</font>""" % re.split('\s*', vscale)[0]
                if "SCALE" in rtext:
                    scale = re.split('SCALE=\s*', rtext)[-1]
                    textback += """<br><br><b>SCALE</b>: <font color=blue>%s</font>""" % re.split('\s*', scale)[0]
                    textback += """<br><br><b>SCALE</b> - multiplied with the offsets and
                            can be applied to adjust for scaled measurements from camp. The default value is
                            1."""
                if "SHIFT" in rtext:
                    shift = re.split('SHIFT\s*=\s*', rtext)[-1]
                    textback += """<br><br><b>SHIFT</b>: <font color=blue>%s</font>""" % re.split('\s*', shift)[0]            
                    textback += """<br><br><b>SHIFT</b> - added to the elevation of each point
                            on the boundary of the cross section. The default value is 0."""
                if "EASTING" in rtext:
                    rtext = rtext.split('EASTING', 1)[-1]
                    a = 0
                    while not rtext[a:a+1] == "N":
                        a += 1
                        if a > len(rtext):
                            break
                    textback += """<br><br><b>EASTING</b> - The easting or x value for the coordinate system: <font color=blue>%s</font><br><br>
                                <b>NORTHING</b> - The northing or y value for the coordinate system: <font color=blue>%s</font>""" % (rtext[1:a], rtext[a+9:])
            elif "NSUB" in rtext:
                nsub = rtext[4:9]
                manning = rtext[9:]

                manning.replace(" ","<br>")
                while "<br><br>" in manning:
                    manning.replace("<br><br>", "<br>")

                textback += """<br><b>NSUB</b>: Number of subsections: <font color=blue>%s</font><br>
                            <br><b>N</b>: Manning's <i>n</i> for each subsection:
                            <font color=blue>%s</font>""" % (nsub, manning)
            elif rtext.startsWith(" ") and rcode == "FEQX":
                textback += """<b>Offset</b>: <font color=blue>%s</font><br><br>""" % rtext[0:10]
                textback += """<b>Elevation</b>: <font color=blue>%s</font><br><br>""" % rtext[10:20]
                textback += """<b>Subsection number</b>: <font color=blue>%s</font><br><br>""" % rtext[20:25]
                textback += """<b>Additional information</b>:<br> <font color=blue>%s</font>""" % rtext[25:]
            elif rtext.startsWith(" ") and rcode == "FEQXE":
                a = 0
                b = 1
                while " " in rtext[a:b]:
                    a += 1
                    b += 1
                    if b > len(rtext):
                        break
                while not " " in rtext[a:b]:
                    a += 1
                    b += 1
                    if b > len(rtext):
                        break
                X = a
                while " " in rtext[a:b]:
                    a += 1
                    b += 1
                    if b > len(rtext):
                        break
                while not " " in rtext[a:b]:
                    a += 1
                    b += 1
                    if b > len(rtext):
                        break
                Z = a
                while " " in rtext[a:b]:
                    a += 1
                    b += 1
                    if b > len(rtext):
                        break
                while not " " in rtext[a:b]:
                    a += 1
                    b += 1
                    if b > len(rtext):
                        break
                SB = a
                while " " in rtext[a:b]:
                    a += 1
                    b += 1
                    if b > len(rtext):
                        break
                while not " " in rtext[a:b]:
                    a += 1
                    b += 1
                    if b > len(rtext):
                        break
                N0 = a
                while " " in rtext[a:b]:
                    a += 1
                    b += 1
                    if b > len(rtext):
                        break
                while not " " in rtext[a:b]:
                    a += 1
                    b += 1
                    if b > len(rtext):
                        break
                Y1 = a
                while " " in rtext[a:b]:
                    a += 1
                    b += 1
                    if b > len(rtext):
                        break
                while not " " in rtext[a:b]:
                    a += 1
                    b += 1
                    if b > len(rtext):
                        break
                N1 = a
                textback += """<b>Offset</b>: <font color=blue>%s</font><br><br>""" % rtext[0:X]
                textback += """<b>Elevation</b>: <font color=blue>%s</font><br><br>""" % rtext[X:Z]
                textback += """<b>Subsection number</b>: <font color=blue>%s</font><br><br>""" % rtext[Z:SB]
                textback += """<b>Manning's <i>n</i> at Y=0</b>:<br> <font color=blue>%s</font><br><br>""" % rtext[SB:N0]
                textback += """<u>Variation of Manning's <i>n</i></u>:<br>
                            Y=%s n=%s""" % (rtext[N0:Y1], rtext[Y1:N1])
            else:
                if rcode == "FEQXL":
                    if "." in rtext:
                        a = 0
                        b = 1
                        while rtext[a:b] == " ":
                            a += 1
                            b += 1
                        while not rtext[a:b] == " ":
                            a += 1
                            b += 1
                        o = a
                        while rtext[a:b] == " ":
                            a += 1
                            b += 1
                        while not rtext[a:b] == " ":
                            a += 1
                            b += 1
                            if b > len(rtext):
                                break
                        e = a
                        offset = rtext[:o]
                        elev = rtext[o:e]
                        sub = rtext[e:]
                        textback += """<b>Offset</b>: <font color=blue>%s</font><br><br>""" % offset
                        textback += """<b>Elevation</b>: <font color=blue>%s</font><br><br>""" % elev
                        textback += """<b>Subsection number</b>: <font color=blue>%s</font><br><br>""" % sub                        
                    else:
                        textback += """Table headers: <br><font color=blue>%s</font>""" % rtext
                elif rcode == "FEQXE":
                    if rtext.startsWith("VARN"):
                        textback += """<b>VARN</b>- variation of manning's <i>n</i>: <font color=blue>%s</font><br><br>
                                    <u>NCON</u>: constant n<br>
                                    <u>HYDY</u>: n varies with hydraulic depth<br>
                                    <u>MAXY</u>: n varies with maximum water-surface height<br>""" % re.split('VARN\s*=', rtext)[-1]
                    else:
                        textback += """Table headers: <br><font color=blue>%s</font>""" % rtext
                else:
                    textback += """Table headers: <font color=blue>%s</font>""" % rtext
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_10.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
            

        elif rcode == "FTAB":                                          #FTAB
            textback = """<b>Function tables</b><br><br>"""
            if rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comments: <font color=blue>%s</font>""" % rtext[1:]
            elif rtext.startsWith("FTABIN"):
                textback += " "
            elif rtext.startsWith("FILE"):
                textback += """<b>FILE</b> - Location of table: <font color=blue>%s</font>""" % rtext[5:]

            elif " WEIR" in rtext or " RATIO" in rtext:
                rtext.replace(" ","<br>")
                while "<br><br>" in rtext:
                    rtext.replace("<br><br>","<br>")
                textback += "Table headers: <font color=blue>%s</font>" % rtext
                
            
            elif rtext.startsWith("TABLE"):
                tabid = rtext[7:]
                tabid.replace(" ","")
                if tabid == "-1":
                    textback += """End of block"""
                else:
                    textback += """<b>TABLE#</b> - Table number and name: <font color=blue>%s</font>
                                """ % rtext[7:]
            elif rtext.startsWith("TYPE"):
                textback += """<b>TYPE</b>: <font color=blue>%s</font>""" % rtext[5:]
            elif rtext.startsWith("REFL"):
                textback += """<b>REFL</b>: <font color=blue>%s</font>""" % rtext[5:]
            elif rtext.startsWith("TABID"):
                tabid = rtext[7:]
                tabid.replace(" ","")
                if tabid == "-1":
                    textback += """End of block"""
                else:
                    textback += """<b>TABID</b> - Table number and name: <font color=blue>%s</font>
                                """ % rtext[6:]
            elif rtext.startsWith("ZONE"):
                zone = rtext.split('ZONE=')[-1]
                textback +=  """<br><b>ZONE</b> - The zone designation for the horizontal grid: 
                            <font color=blue>%s</font>""" % re.split('\s+', zone)[0]
                if "HGRID" in rtext:
                    hgrid = rtext.split('HGRID=')[1]
                    textback += """<br><br><b>HGRID</b> - The name for the horizontal grid used for 
                                eastings and northings: <font color=blue>%s</font>""" % re.split('\s+', hgrid)[0]
                if "BASIS" in rtext:
                    basis = rtext.split('BASIS=')[1]
                    textback += """<br><br><b>BASIS</b> - The description of era, date, or other item to 
                                denote the data source: <font color=blue>%s</font>""" % re.split('\s+', basis)[0]
                if "VDATUM" in rtext:
                    vdatum = rtext.split('VDATUM=')[1]
                    textback += """<br><br><b>VDATUM</b> - The vertical datum: <font color=blue>%s</font>""" % re.split('\s+', vdatum)[0]
                if "UNITSYS" in rtext:
                    unitsys = rtext.split('UNITSYS=')[1]
                    textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('\s+', unitsys)[0]
            elif rtext.startsWith("EASTING"):
                    a = 8
                    while not rtext[a:a+1] == "N":
                        a += 1
                        if a > len(rtext):
                            break
                    textback += """<b>EASTING</b> - The easting or x value for the coordinate system: <font color=blue>%s</font><br><br>
                                <b>NORTHING</b> - The northing or y value for the coordinate system: 
                                <font color=blue>%s</font>""" % (rtext[8:a], rtext[a+9:])
            else:
                textback += """Atribute1: <font color=blue>%s</font><br>
                            Atribute2: <font color=blue>%s</font>""" % (rtext[0:10],rtext[10:])
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_15.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

        elif rcode.startsWith("CULV"):                                 # CULVERT
            textback = """<b>FLOW THROUGH CULVERT</b><br><br>"""
            if rcode.startsWith("CULVo"):
                culvert = rcode[5:]
                culvert.replace(" ","")
                culvert = int(culvert)
                global culvoffset
                global culvcrest
                global culvwidth
                global culvapproach
                global culvsurface
                if rtext.startsWith(";") or rtext.startsWith("*"):
                    textback += """Comment: <font color=blue>%s</font>""" % rtext[1:]
                elif "OFF" in rtext:
                    headers = rtext.replace(" ","<br>")
                    while "<br><br>" in headers:
                        headers.replace("<br><br>","<br>")
                    textback += """Table headers: %s""" % headers
                else:
                    offset = rtext[:culvoffset[culvert]]
                    crest = rtext[culvoffset[culvert]:culvcrest[culvert]]
                    width = rtext[culvcrest[culvert]:culvwidth[culvert]]
                    approach = rtext[culvwidth[culvert]:culvapproach[culvert]]
                    surface = rtext[culvapproach[culvert]:culvsurface[culvert]]
                    textback += """<b>Offset</b> - Horizontal offset for which geometric
                                characteristics are entered on this line: <font color=blue>%s</font><br><br>
                                <b>Crest</b> - Crest elevation: <font color=blue>%s</font><br><br>
                                <b>Width</b> - Width of the crest in the direction of
                                flow: <font color=blue>%s</font><br><br>
                                <b>Approach</b> - Elevation of the approach channel: <font color=blue>%s</font><br><br>
                                <b>Surface</b> - Type of surface: <font color=blue>%s</font><br><br>
                                """ % (offset, crest, width, approach, surface)
            elif rcode.startsWith("CULVh"):
                if rtext.startsWith(";") or rtext.startsWith("*"):
                    textback += """Comment: <font color=blue>%s</font>""" % rtext[1:]
                elif rtext.startsWith("NFRAC"):
                    textback += """<b>NFRAC</b> - Number of partial
                                free drops used in computing the table: <font color=blue>%s</font>""" % rtext[6:]
                elif rtext.startsWith("POWER"):
                    textback += """<b>POWER</b> - Power applied to
                                distribute the proportion of free drop from a value
                                of 0 to 1: <font color=blue>%s</font>""" % rtext[6:]
                elif "-1." in rtext:
                    textback += """End of block."""
                elif "." in rtext:
                    textback += """Upstream head to use in computing the 2-D table: <font color=blue>%s</font>""" % rtext
                else:
                    textback += """Header: <font color=blue>%s</font>""" % rtext
            elif rcode.startsWith("CULVt"):
                global culvnode
                global culvnodeid
                global culvxnum
                global culvstation
                global culvelev
                global culvka
                global culvkd
                global culvhtab
                culvert = rcode[5:]
                culvert.replace(" ","")
                culvert = int(culvert)
                if "-1" in rtext[:culvnode[culvert]]:
                    textback += """End of table."""
                else:
                    node = rtext[:culvnode[culvert]]
                    nodeid = rtext[culvnode[culvert]:culvnodeid[culvert]]
                    xnum = rtext[culvnodeid[culvert]:culvxnum[culvert]]
                    station = rtext[culvxnum[culvert]:culvstation[culvert]]
                    elev = rtext[culvstation[culvert]:culvelev[culvert]]
                    ka = rtext[culvelev[culvert]:culvka[culvert]]
                    kd = rtext[culvka[culvert]:culvkd[culvert]]
                    htab = rtext[culvkd[culvert]:culvhtab[culvert]]
                    textback += """Node number: <font color=blue>%s</font><br>
                                Node ID: <font color=blue>%s</font><br><br>
                                Table - number of the cross-section table: <font color=blue>%s</font><br><br>
                                Station: <font color=blue>%s</font><br>
                                Elevation: <font color=blue>%s</font><br><br>
                                KA - loss coefficient to apply to the difference in
                                velocity head when flow is accelerating: <font color=blue>%s</font><br><br>
                                KD - loss coefficient to apply to the difference in
                                velocity head when flow is decelerating: <font color=blue>%s</font><br><br>
                                HTAB: <font color=blue>%s</font><br>
                                """ % (node, nodeid, xnum, station, elev, ka, kd, htab)
            else:
                if rtext.startsWith(";") or rtext.startsWith("*"):
                    textback += """Comment:<br><font color=blue>%s</font>""" % rtext[1:]
                elif rtext.startsWith("TABLE") or rtext.startsWith("TABID"):
                    textback += """<b>%s</b> - Table number of the 2-D function table computed for the
                                flows through the culvert: <font color=blue>%s</font>
                                """ % (rtext.split('=')[0], rtext[7:])
                elif rtext.startsWith("TYPE="):
                    textback += """<b>TYPE</b> - Table type(6 and 13 only):<font color=blue>%s</font>""" % rtext[5:]
                elif rtext.startsWith("LABEL"):
                    textback += """<b>LABEL</b> - User-defined label in the table for identification purposes:<font
                                color=blue>%s</font>""" % rtext[6:]
                elif rtext.startsWith("APPTAB"):
                    textback += """<b>APPTAB#</b> - Table number for the cross-section table of the approach section
                                for the culvert:<font color=blue>%s</font>""" % rtext[8:]
                elif rtext.startsWith("APPELV"):
                    textback += """<b>APPELV</b> - Elevation of the minimum point of the cross section
                                specified in APPTAB: <font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("APPLEN"):
                    textback += """<b>APPELV</b> - Distance between the approach cross section and the entrance
                                to the culvert: <font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("APPLOS"):
                    textback += """<b>APPLOS</b> - The hydraulic-energy loss resulting from special approach conditions
                                in terms of the fraction of the velocity head in the approach cross section:
                                <font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("APPEXP"):
                    textback += """<b>APPEXP</b> - Gives a coefficient to be applied to the difference between the approach
                                -velocity head and the velocity head in the culvert entrance if the culvert
                                is an expansion in flow area instead of a contraction in flow area:
                                <font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("NODEID"):
                    textback += """<b>NODEID</b> - Indication of whether an identifying string for each node along the
                                culvert is included in the input: <font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("SFAC"):
                    textback += """<b>SFAC</b> - The multiplying factor that converts the stations in the input to
                                distances required in FEQUTL: <font color=blue>%s</font>""" % rtext[5:]
                elif rtext.startsWith("CULCLS"):
                    textback += """<b>CULCLS</b> - The general class of the culvert for selection of the discharge
                                coefficient: <font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("DEPTAB"):
                    rtext.replace("DEPTAB#=","")
                    rtext.replace("DEPTAB=","")
                    cc = 0
                    st = cc
                    ee = cc + 1
                    maxee = len(rtext)
                    while rtext[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    deptab = rtext[st:ee]
                    deptab.replace(" ","")
                    st = cc
                    while rtext[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    begtab = rtext[st:ee]
                    begtab.replace(" ","")
                    st = cc
                    while rtext[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    rmffac = rtext[st:ee]
                    rmffac.replace(" ","")
                    st = cc
                    textback += """<b>DEPTAB</b> - Table number of the cross-section table of the
                                departure section
                                for the culvert: <font color=blue>%s</font><br><br>
                                <b>BEGTAB</b> - Optional table number for the cross-section table
                                describing the
                                departure reach at the exit from the culvert: <font color=blue>%s</font><br><br>
                                <b>RMFFAC</b> - Optional entry that specifies a multiplying factor on the estimated
                                momentum flux over the roadway: <font color=blue>%s</font>""" % (deptab, begtab, rmffac)
                elif rtext.startsWith("DEPELV"): 
                    rtext.replace("DEPELV=","")
                    cc = 0
                    st = cc
                    ee = cc + 1
                    maxee = len(rtext)
                    while rtext[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    depelv = rtext[st:cc]
                    depelv.replace(" ","")
                    st = cc
                    while rtext[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    begelv = rtext[st:cc]
                    begelv.replace(" ","")
                    st = cc
                    while rtext[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    dsffac = rtext[st:cc]
                    dsffac.replace(" ","")
                    st = cc
                    while rtext[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    while not rtext[cc:ee] == " ":
                        cc += 1
                        ee = cc + 1
                        if ee > maxee:
                            break
                    widfac = rtext[st:cc]
                    widfac.replace(" ","")
                    st = cc
                    textback += """<b>DEPELV</b> - elevation of the bottom of the departure section: <font color=blue>%s</font><br><br>
                                <b>BEGELV</b> - elevation of the bottom of the beginning crosss section for the
                                departure reach: <font color=blue>%s</font><br><br>
                                <b>DSFFAC</b> - not used at the moment, default value should be 0: <font color=blue>%s</font><br><br>
                                <b>WIDFAC</b> - width factor for checking the beginning cross section of the departure
                                reach. The default value is 1.02: <font color=blue>%s</font>""" % (depelv, begelv, dsffac, widfac)
                elif rtext.startsWith("LOSOPT"):
                    textback += """<b>LOSOPT</b> - The loss option for the expansion of the flow into the departure
                                reach: <font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("KRB"):
                    textback += """<b>KRB</b> - Multiplying factor that adjust the base discharge coefficient for
                                flow types 1, 2, and 3 for the effect of rounding or beveling of the
                                entrance to the culvert:<font color=blue>%s</font>""" % rtext[4:]
                elif rtext.startsWith("KWING"):
                    textback += """<b>KWING</b> - The adjustment factor for the effect of wingwalls on the discharge
                                coefficient for flow types 1, 2, and 3 when wingwalls are present for
                                box culverts:<font color=blue>%s</font>""" % rtext[6:]
                elif rtext.startsWith("KPROJ"):
                    textback += """<b>KPROJ</b> - The adjustment factor for the effect for projecting entrances for
                                flow types 1, 2, and 3:<font color=blue>%s</font>""" % rtext[6:]
                elif rtext.startsWith("C46"):
                    textback += """<b>C46</b> - The discharge coefficient for culvert-flow types 4 and 6:<font
                                color=blue>%s</font>""" % rtext[4:]
                elif rtext.startsWith("RBVALUE"):
                    textback += """<b>RBVALUE</b> - The relative rounding/beveling for the culvert entrance:<font
                                color=blue>%s</font>""" % rtext[8:]
                elif rtext.startsWith("BVANGLE"):
                    textback += """<b>BVANGLE</b> - The angle in degrees of the level if the entrance to the culvert
                                is beveled:<font color=blue>%s</font>""" % rtext[8:]
                elif rtext.startsWith("WWANGLE"):
                    textback += """<b>WWANGLE</b> - The wingwall angle in degrees:<font color=blue>%s</font>""" % rtext[8:]
                elif rtext.startsWith("LPOVERD"):
                    textback += """<b>LPOVERD</b> - The average projection length of the culvert barrel relative to the
                                culvert maximum inside vertical dimension:<font color=blue>%s</font>""" % rtext[8:]
                elif rtext.startsWith("TYPE5SBF"):
                    textback += """<b>TYPE5SBF</b> - The value of relative water-surface height in the barrel or the barrel
                                exit that will result in full flow in the culvert barrel:<font
                                color=blue>%s</font>""" % rtext[9:]
                elif rtext.startsWith("PLCWTB"):
                    textback += """<b>PLCWTB</b> - Table number for the function table listing the low-head weir coefficient
                                for a paved surface:<font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("GLCWTB"):
                    textback += """<b>GLCWTB</b> - Table number for the function table listing the low-head weir coefficient
                                for a graveled surface:<font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("PHCWTB"):
                    textback += """<b>PHCWTB</b> - Table number for the function table listing the high-head weir coefficient
                                for a paved surface:<font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("GHCWTB"):
                    textback += """<b>GHCWTB</b> - Table number for the function table listing the high-head weir coefficient
                                for a graveled surface:<font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("PSUBTB"):
                    textback += """<b>PSUBTB</b> - Table number for the function table listing the submergence correction factor
                                for a paved surface:<font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("GSUBTB"):
                    textback += """<b>GSUBTB</b> - Table number for the function table listing the submergence correction factor
                                for a graveled surface:<font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("ZONE"):
                    zone = rtext.split('ZONE=')[-1]
                    textback +=  """<br><b>ZONE</b> - The zone designation for the horizontal grid: <font color=blue>%s</font>""" % re.split('\s+', zone)[0]
                    if "HGRID" in rtext:
                        hgrid = rtext.split('HGRID=')[1]
                        textback += """<br><br><b>HGRID</b> - The name for the horizontal grid used for 
                                    eastings and northings: <font color=blue>%s</font>""" % re.split('\s+', hgrid)[0]
                    if "BASIS" in rtext:
                        basis = rtext.split('BASIS=')[1]
                        textback += """<br><br><b>BASIS</b> - The description of era, date, or other item to 
                                    denote the data source: <font color=blue>%s</font>""" % re.split('\s+', basis)[0]
                    if "VDATUM" in rtext:
                        vdatum = rtext.split('VDATUM=')[1]
                        textback += """<br><br><b>VDATUM</b> - The vertical datum: <font color=blue>%s</font>""" % re.split('\s+', vdatum)[0]
                    if "UNITSYS" in rtext:
                        unitsys = rtext.split('UNITSYS=')[1]
                        textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('\s+', unitsys)[0]
                elif rtext.startsWith("EASTING"):
                    a = 8
                    while not rtext[a:a+1] == "N":
                        a += 1
                        if a > len(rtext):
                            break
                    textback += """<br><b>EASTING</b> - The easting or x value for the coordinate system: <font color=blue>%s</font><br><br>
                                <b>NORTHING</b> - The northing or y value for the coordinate system: 
                                <font color=blue>%s</font>""" % (rtext[8:a], rtext[a+9:])
                else:
                    textback += """Label:<br><font color=blue>%s</font>""" % rtext
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_7.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
            
        elif rcode == "CHAR":                                          #CHANRAT
            textback = """<b>FLOW THROUGH A SHORT, PRISMATIC CHANNEL THAT SIMULATES
                        OVERBANK FLOW</b><br><br>"""
            if rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment:<br><font color=blue>%s</font>""" % rtext[1:]
            elif rtext.startsWith("TABLE"):
                textback += """Table number: <font color=blue>%s</font>""" % rtext[7:]
            elif rtext.startsWith("TABID"):
                rtext.replace(" T","<br>T")
                rtext.replace(" M","<br>M")
                textback += """<b>TABID</b> - the table ID: <font color=blue>%s</font><br>""" % re.split(r'\s*=\s*', rtext)[-1]
            elif rtext.startsWith("TYPE"):
                rtext.replace(" E","<br>E")
                rtext.replace(" I","<br>I")
                rtext.replace(" N","<br>N")
                rtext.replace(" ","")
                textback += """<b>TYPE</b> - Table parameters:<br> <font color=blue>%s</font><br><br>
                            <b>TYPE</b> is the type of table (6 or 13 only)<br><br>
                            ERRKND specifies the error measure (absolute error if 0,
                            relative error if 1)<br><br>
                            INTHOW is the integration method (Simpson adaptive integration
                            if 1, no other methods available)<br><br>
                            EPSINT is the tolerance value for the adaptive integration<br><br>
                            NDDABS and NDDREL are the absolute and relative deviations from
                            normal depth, respectively, used to control the integration near the
                            singularity in the governing equation at normal depth.
                            """ % rtext
            elif rtext.startsWith("LABEL"):
                textback += """<b>Label</b>: <font color=blue>%s</font>""" % rtext[6:]
            elif rtext.startsWith("XSTAB"):
                textback += """<b>XSTAB</b> - Table number of the cross-section
                            table defining the shape of the channel: <font color=blue>%s</font>""" % rtext[7:]
            elif rtext.startsWith("BOTSLP"):
                textback += """<b>BOTSLP</b> - Bottom slope of the channel: <font color=blue>%s</font>
                            """ % rtext[7:]
            elif rtext.startsWith("LENGTH"):
                length = re.split('LENGTH\s*=\s*', rtext)[-1]
                textback += "<b>LENGTH</b> - the length of the channel: <font color=blue>%s</font><br>" % re.split('\s+', length)[0]
                if "MIDELEV" in rtext:
                    midelev = re.split('\s*MIDELEV\s*=\s*', rtext)[-1]
                    textback += "<b>MIDELEV</b> - the elevation of the midpoint: <font color=blue>%s</font>" % re.split('\s+', midelev)[0]
            elif rtext.startsWith("NFRAC"):
                textback += """<b>NFRAC</b> - Number of partial free-drop
                            fractions to use in computing tail-water heads: <font color=blue>%s</font>""" % rtext[6:]
            elif rtext.startsWith("POWER"):
                textback += """<b>POWER</b> - Power used to distribute the
                            partial free drops from 0 to 1: <font color=blue>%s</font>""" % rtext[6:]
            elif rtext.startsWith("ZONE"):
                zone = rtext.split('ZONE=')[-1]
                textback +=  """<br><b>ZONE</b> - The zone designation for the horizontal grid: 
                            <font color=blue>%s</font>""" % re.split('\s+', zone)[0]
                if "HGRID" in rtext:
                    hgrid = rtext.split('HGRID=')[1]
                    textback += """<br><br><b>HGRID</b> - The name for the horizontal grid used for 
                                eastings and northings: <font color=blue>%s</font>""" % re.split('\s+', hgrid)[0]
                if "BASIS" in rtext:
                    basis = rtext.split('BASIS=')[1]
                    textback += """<br><br><b>BASIS</b> - The description of era, date, or other item to 
                                denote the data source: <font color=blue>%s</font>""" % re.split('\s+', basis)[0]
                if "VDATUM" in rtext:
                    vdatum = rtext.split('VDATUM=')[1]
                    textback += """<br><br><b>VDATUM</b> - The vertical datum: <font color=blue>%s</font>""" % re.split('\s+', vdatum)[0]
                if "UNITSYS" in rtext:
                    unitsys = rtext.split('UNITSYS=')[1]
                    textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('\s+', unitsys)[0]
            elif "-1." in rtext:
                textback += """End of block."""
            elif "." in rtext:
                textback += """Upstream head to use in computing
                            the 2D table: <font color=blue>%s</font>""" % rtext
            else:
                textback += """Header: <font color=blue>%s</font>""" % rtext
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_5.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
            
        elif rcode.startsWith("EMBA"):                                 #EMBANKQ block
            textback = """<b>FLOW OVER EMBANKMENT-SHAPED WEIRS</b><br><br>"""
            if rcode.startsWith("EMBAo"):
                embankq = rcode[5:]
                embankq.replace(" ","")
                embankq = int(embankq)
                global embaoffset
                global embacrest
                global embawidth
                global embaapproach
                global embasurface
                if rtext.startsWith(";") or rtext.startsWith("*"):
                    textback += """Comment:<br><font color=blue>%s</font>""" % rtext[1:]
                elif "OFF" in rtext:
                    headers = rtext.replace(" ","<br>")
                    while "<br><br>" in headers:
                        headers.replace("<br><br>","<br>")
                    textback += """Table headers:<br>
                                <font color=blue>%s</font>""" % headers
                else:
                    offset = rtext[:embaoffset[embankq]]
                    crest = rtext[embaoffset[embankq]:embacrest[embankq]]
                    width = rtext[embacrest[embankq]:embawidth[embankq]]
                    approach = rtext[embawidth[embankq]:embaapproach[embankq]]
                    surface = rtext[embaapproach[embankq]:embasurface[embankq]]
                    textback += """<b>Offset</b> - Horizontal offset: <font color=blue>%s</font><br><br>
                                <b>Crest</b> - Crest elevation: <font color=blue>%s</font><br><br>
                                <b>Width</b> - Width of the crest in the direction of
                                flow: <font color=blue>%s</font><br><br>
                                <b>Approach</b> - Elevation of the approach channel: <font color=blue>%s</font><br><br>
                                <b>Surface</b> - Type of surface: <font color=blue>%s</font><br><br>
                                """ % (offset, crest, width, approach, surface)
            elif rcode.startsWith("EMBAh"):
                if rtext.startsWith("NFRAC"):
                    textback += """<b>NFRAC</b> - Number of partial
                                free drops used in computing the table: <font color=blue>%s</font>""" % rtext[6:]
                elif rtext.startsWith("POWER"):
                    textback += """<b>POWER</b> - Power applied to
                                distribute the proportion of free drop from a value
                                of 0 to 1: <font color=blue>%s</font>""" % rtext[6:]
                elif rtext.startsWith("LIPREC"):
                    textback += """<b>LIPREC</b> - Linear interpolation
                                precision specification in terms of relative
                                error: <font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("MINPFD"):
                    textback += """<b>MINPFD</b> - Minimum partial free
                                drop to be computed: <font color=blue>%s</font>""" % rtext[7:]
                elif "-1." in rtext:
                    textback += """End of block."""
                elif "." in rtext:
                    textback += """Upstream head to use in computing the 2-D table: <font color=blue>%s</font>""" % rtext
                elif rtext.startsWith(";") or rtext.startsWith("*"):
                    textback += """Comment:<br><font color=blue>%s</font>""" % rtext[1:]
                else:
                    textback += """Header: <font color=blue>%s</font>""" % rtext
            else:
                if rtext.startsWith(";") or rtext.startsWith("*"):
                    textback += """Comment:<br><font color=blue>%s</font>""" % rtext[1:]
                elif rtext.startsWith("TABLE") or rtext.startsWith("TABID"):
                    textback += "<br>"
                    if "TABLE" in rtext:
                        table = re.split('\s*TABLE\s*=\s*', rtext)[-1]
                        textback += "<b>TABLE</b> - the table number: <font color=blue>%s</font><br>" % re.split('\s+', table)[0]
                    if "TABID" in rtext:
                        tabid = re.split('\s*TABID\s*=\s*', rtext)[-1]
                        textback += "<b>TABLE</b> - the table number: <font color=blue>%s</font><br>" % re.split('\s+', tabid)[0]
                    if "HLCRIT" in rtext:
                        hlcrit = re.split('\s*HLCRIT\s*=\s*', rtext)[-1]
                        textback += """<b>HLCRIT</b> - the critical ratio between approach head and 
                                embankment width that distinguishes between low-head and high-head flow: 
                                <font color=blue>%s</font><br>""" % re.split('\s+', hlcrit)[0]
                    if "HLMAX" in rtext:
                        hlmax = re.split('\s*HLMAX\s*=\s*', rtext)[-1]
                        textback += """<b>HLMAX</b> - the maximum ratio of approach head to
                                embankment width: <font color=blue>%s</font><br>""" % re.split('\s+', hlmax)[0]
                    if "HSCALE" in rtext:
                        hscale = re.split('\s*HSCALE\s*=\s*', rtext)[-1]
                        textback += """<b>HSCALE</b> - the horizontal scale factor for the
                                offsets along the crest: <font color=blue>%s</font><br>""" % re.split('\s+', hscale)[0]
                    if "VSCALE" in rtext:
                        vscale = re.split('\s*VSCALE\s*=\s*', rtext)[-1]
                        textback += """<b>VSCALE</b> - the vertical scale factor for the
                                elevation measurements for the crest and for the
                                approach elevations: <font color=blue>%s</font><br>""" % re.split('\s+', vscale)[0]
                    if "CSHIFT" in rtext:
                        cshift = re.split('\s*CSHIFT\s*=\s*', rtext)[-1]
                        textback += """<b>CSHIFT</b> - the shift in crest elevation: 
                                <font color=blue>%s</font><br>""" % re.split('\s+', cshift)[0]
                elif rtext.startsWith("PLCWTB"):
                    textback += """<b>PLCWTB</b> - Table number for the function table listing the low-head weir coefficient
                                for a paved surface: <font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("GLCWTB"):
                    textback += """<b>GLCWTB</b> - Table number for the function table listing the low-head weir coefficient
                                for a graveled surface: <font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("PHCWTB"):
                    textback += """<b>PHCWTB</b> - Table number for the function table listing the high-head weir coefficient
                                for a paved surface: <font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("GHCWTB"):
                    textback += """<b>GHCWTB</b> - Table number for the function table listing the high-head weir coefficient
                                for a graveled surface: <font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("PSUBTB"):
                    textback += """<b>PSUBTB</b> - Table number for the function table listing the submergence correction factor
                                for a paved surface: <font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("GSUBTB"):
                    textback += """<b>GSUBTB</b> - Table number for the function table listing the submergence correction factor
                                for a graveled surface: <font color=blue>%s</font>""" % rtext[7:]
                elif rtext.startsWith("LABEL"):
                    textback += """<b>LABEL</b> - Table label: <font color=blue>%s</font>""" % rtext[6:]
                elif rtext.startsWith("ZONE"):
                    zone = rtext.split('ZONE=')[-1]
                    textback +=  """<br><b>ZONE</b> - the zone designation for the horizontal grid: <font color=blue>%s</font><br>""" % re.split('\s+', zone)[0]
                    if "HGRID" in rtext:
                        hgrid = rtext.split('HGRID=')[1]
                        textback += """<br><br><b>HGRID</b> - the name for the horizontal grid used for 
                                    eastings and northings: <font color=blue>%s</font>""" % re.split('\s+', hgrid)[0]
                    if "BASIS" in rtext:
                        basis = rtext.split('BASIS=')[1]
                        textback += """<br><br><b>BASIS</b> - the description of era, date, or other item to 
                                    denote the data source: <font color=blue>%s</font>""" % re.split('\s+', basis)[0]
                    if "VDATUM" in rtext:
                        vdatum = rtext.split('VDATUM=')[1]
                        textback += """<br><br><b>VDATUM</b> - the vertical datum: <font color=blue>%s</font>""" % re.split('\s+', vdatum)[0]
                    if "UNITSYS" in rtext:
                        unitsys = rtext.split('UNITSYS=')[1]
                        textback += """<br><br><b>UNITSYS</b> - the unit system: <font color=blue>%s</font>""" % re.split('\s+', unitsys)[0]
                elif rtext.startsWith("EASTING"):
                    a = 0
                    while rtext[a:a+1] != "=":
                        a += 1
                        if a > len(rtext):
                            break
                    e1 = a+1
                    while rtext[a:a+1] != "N":
                        a += 1
                        if a > len(rtext):
                            break
                    e2 = a
                    while rtext[a:a+1] != "=":
                        a += 1
                        if a > len(rtext):
                            break
                    n1 = a+1
                    textback += """<b>EASTING</b> - The easting or x value for the coordinate system: <font color=blue>%s</font><br><br>
                                <b>NORTHING</b> - The northing or y value for the coordinate system: 
                                <font color=blue>%s</font>""" % (rtext[e1:e2], rtext[n1:])
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_8.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
            
        elif rcode.startsWith("EXPC"):                                        #EXPCON
            textback = """<b>FLOW THROUGH A CHANNEL TRANSITION</b><br><br>"""
            if rtext.startsWith("SMOOTH"):
                textback += """<b>SMOOTH</b> - Velocity difference for smoothing the losses near the point
                            of zero difference in velocity head: <font color=blue>%s</font>""" % rtext[7:]
            elif rtext.startsWith("GMEAN"):
                textback += """<b>GMEAN</B> - Value for the alpha parameter for computing the generalized
                            mean: <font color=blue>%s</font>""" % rtext[6:]
            elif rtext.startsWith("NFRAC"):
                textback += """<b>NFRAC</b> - Number of partial free flows to use in
                            computing the 2-D table of type 14: <font color=blue>%s</font>""" % rtext[6:]
            elif rtext.startsWith("POWER"):
                textback += """<b>POWER</b> - Power used to distribute the
                            partial free-flow factors between 0 and 1: <font color=blue>%s</font>""" % rtext[6:]
            elif rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment:<br><font color=blue>%s</font>""" % rtext[1:]
            elif rtext.startsWith("ZONE"):
                zone = rtext.split('ZONE=')[-1]
                textback +=  """<br><b>ZONE</b> - The zone designation for the horizontal grid: 
                            <font color=blue>%s</font>""" % re.split('\s+', zone)[0]
                if "HGRID" in rtext:
                    hgrid = rtext.split('HGRID=')[1]
                    textback += """<br><br><b>HGRID</b> - The name for the horizontal grid used for 
                                eastings and northings: <font color=blue>%s</font>""" % re.split('\s+', hgrid)[0]
                if "BASIS" in rtext:
                    basis = rtext.split('BASIS=')[1]
                    textback += """<br><br><b>BASIS</b> - The description of era, date, or other item to 
                                denote the data source: <font color=blue>%s</font>""" % re.split('\s+', basis)[0]
                if "VDATUM" in rtext:
                    vdatum = rtext.split('VDATUM=')[1]
                    textback += """<br><br><b>VDATUM</b> - The vertical datum: <font color=blue>%s</font>""" % re.split('\s+', vdatum)[0]
                if "UNITSYS" in rtext:
                    unitsys = rtext.split('UNITSYS=')[1]
                    textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('\s+', unitsys)[0]
            else:
                linestart = rtext
                rtext = str(rtext)
                linestart = linestart.replace(" ","")
                x = rcode[4:]
                x.replace(" ","")
                x = int(x)
                if linestart.startsWith("UP") or linestart.startsWith("DN"):
                    global exploc
                    global exptab
                    global expdist
                    global expdatum
                    loc = rtext[:exploc[x]]
                    tab = rtext[exploc[x]:exptab[x]]
                    dist = rtext[exptab[x]:expdist[x]]
                    datum = rtext[expdist[x]:expdatum[x]]
                    station = " "
                    if "UP" in loc:
                        station = "upstream"
                    elif "DN" in loc:
                        station = "downstream"
                    textback += """Station - (%s cross section): <font color=blue>%s</font><br><br>
                                Table - function table number: <font color=blue>%s</font><br><br>
                                Distance: <font color=blue>%s</font><br><br>
                                Datum - bottom elevation of the cross section: <font color=blue>%s</font>
                                """ % (loc, station, tab, dist, datum)
                elif linestart.startsWith("UD") or linestart.startsWith("DU"):
                    global expdir
                    global exptab2
                    global expka
                    global expkd
                    global explabel
                    xdir = rtext[:expdir[x]]
                    tab = rtext[expdir[x]:exptab2[x]]
                    ka = rtext[exptab2[x]:expka[x]]
                    kd = rtext[expka[x]:expkd[x]]
                    label = rtext[expkd[x]:]
                    direction = " "
                    if "UD" in xdir:
                        direction = "from upstream to downstream"
                    elif "DU" in xdir:
                        direction = "from downstream to upstream"
                    textback += """<b>DIRECTION</b>: <font color=blue>%s</font>
                                (%s)<br><br>
                                <b>TABLE</b> - table number: <font color=blue>%s</font><br><br>
                                <b>KA</b> - loss coefficient to apply to the velocity-head
                                difference for accelerating flow: <font color=blue>%s</font><br><br>
                                <b>KD</b> - loss coefficient to apply to the velocity-head
                                difference for decelerating flow: <font color=blue>%s</font><br><br>
                                <b>LABEL</b>: <font color=blue>%s</font>
                                """ % (xdir, direction, tab, ka, kd, label)
                elif "-1." in rtext:
                    textback += """End of block."""
                elif "." in rtext:
                    textback += """Downstream
                                piezometric head applied in computing the
                                table: <font color=blue>%s</font>""" % rtext
                else:
                    textback += """Header:<br><font color=blue>%s</font>""" % rtext
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_9.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
            
        elif rcode == "MULC":                                                 #MULCON
            textback = """<b>Cross-section of conduits</b><br>A single cross-section function  table is computed in the MULCON command
                    to represent the hydraulic characteristics of one or more conduits.<br>"""

            if rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """<br><br>Comment:<br><font color=blue>%s</font>""" % rtext[1:]
            
            elif rtext.startsWith("TABLE") or rtext.startsWith("TABID"):
                if rtext.startsWith("TABLE"):
                    textback += """<br><br><b>TABLE</b> - Table number for the cross-section table: <font color=blue>%s</font><br>""" % rtext[7:12]
                elif rtext.startsWith("TABID"):
                    a = 6
                    while rtext[a:a+1] == " ":
                        a += 1
                        if a > len(rtext):
                            break
                    while not rtext[a:a+1] == " ":
                        a += 1
                        if a > len(rtext):
                            break
                    textback += """<br><br><b>TABID</b> - Name of the cross-section table: <font color=blue>%s</font><br>""" % rtext[6:a]
                if "EXTEND" in rtext:
                    textback += """<br><font color=blue>EXTEND</font>: a vertical extension is
                                added to the first or last points to match the point of
                                maximum elevation in the cross section."""
                if "MONOTONE" in rtext:
                    textback += """<br><font color=blue>MONOTONE</font>: the offsets for the
                                cross section are examined to ensure that they are
                                increasing."""
                if " NEWBETA" in rtext:
                    textback += """<br><font color=blue>NEWBETA</font>: the momentum-flux
                                correction coefficient and the kinetic-energy-flux correction
                                coefficient are computed by application of a method."""
                if "NEWBETAE" in rtext:
                    textback += """<br><font color=blue>NEWBETAE</font>: same as NEWBETA
                                except that the critical flow tabulated is based on the
                                energy principle."""
                if "NEWBETAM" in rtext:
                    textback += """<br><font color=blue>NEWBETAM</font>: same as NEWBETA
                                except that the critical flow tabulated is based on the
                                energy principle."""
                if "OLDBETA" in rtext:
                    textback += """<br><font color=blue>OLDBETA</font>: the kinetic-energy-flux
                                correction coefficient and the momentum-flux correction coefficient
                                for the cross section are computed from equations 7 and 8 in section
                                3.1.1."""
                if " SAVE" in rtext:
                    a = 0
                    b = 1
                    while not " SAVE" in rtext[a:b]:
                        b += 1
                    
                    textback += """<br><font color=blue>%s</font>: a copy of the resulting
                                table is saved internally in the FEQUTL computations. The table type
                                is given by the two digits next to SAVE.""" % rtext[b - 4:b + 2] 
                if "NOSAVE" in rtext:
                    textback += """<br><font color=blue>NOSAVE</font>: a copy of the table is
                                not saved internally in the FEQUTL computations."""
                if " OUT" in rtext:
                    a = 0
                    b = 1
                    while not " OUT" in rtext[a:b]:
                        b += 1
                        
                    textback += """<br><font color=blue>%s</font>: a copy of the table is
                                output to the standard function-table file given by the two digits
                                after OUT.""" % rtext[b - 3:b + 2]
                if "NOOUT" in rtext:
                    textback += """<br><font color=blue>NOOUT</font>: output of the table to the
                                standard function-table file is suppressed."""
            elif rtext.startsWith("WSLOT"):
                textback += """<br><br><b>WSLOT</b> - The width of the hypothetical slot used to maintain
                            a free surface in the conduit: <font color=blue>%s</font>""" % rtext[6:]
            elif rtext.startsWith("VDATUM"):
                vdatum = re.split("VDATUM\s*=", rtext)[-1]
                textback += """<br><br><b>VDATUM</b> - The vertical datum: <font color=blue>%s</font>""" % re.split("\s+", vdatum)[0]
                if "UNITSYS" in rtext:
                    unitsys = re.split("\s*UNITSYS\s*=\s*", rtext)[-1]
                    textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('/s+', unitsys)[0]
            elif rtext.startsWith("HSLOT"):
                textback += """<br><br><b>HSLOT</b> - The height of the hypothetical slot above the invert
                            of the conduit, which has the minimum elevation: <font color=blue>%s</font>""" % rtext[6:]
            elif rtext.startsWith("NPIPES"):
                textback += """<br><br><b>NPIPES</b> - The number of conduits present. Valid range
                            is 1 &le; NPIPES &le; 96: <font color=blue>%s</font>""" % rtext[7:]
            elif rtext.startsWith("ZONE"):
                zone = rtext.split('ZONE=')[-1]
                textback +=  """<br><b>ZONE</b> - The zone designation for the horizontal grid: 
                            <font color=blue>%s</font>""" % re.split('\s+', zone)[0]
                if "HGRID" in rtext:
                    hgrid = rtext.split('HGRID=')[1]
                    textback += """<br><br><b>HGRID</b> - The name for the horizontal grid used for 
                                eastings and northings: <font color=blue>%s</font>""" % re.split('\s+', hgrid)[0]
                if "BASIS" in rtext:
                    basis = rtext.split('BASIS=')[1]
                    textback += """<br><br><b>BASIS</b> - The description of era, date, or other item to 
                                denote the data source: <font color=blue>%s</font>""" % re.split('\s+', basis)[0]
                if "VDATUM" in rtext:
                    vdatum = rtext.split('VDATUM=')[1]
                    textback += """<br><br><b>VDATUM</b> - The vertical datum: <font color=blue>%s</font>""" % re.split('\s+', vdatum)[0]
                if "UNITSYS" in rtext:
                    unitsys = rtext.split('UNITSYS=')[1]
                    textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('\s+', unitsys)[0]
            elif rtext.startsWith("TYPE"):
                rtext.replace("TYPE:","")
                rtext.replace("TYPE=","")
                cc = 0
                st = cc
                ee = cc + 1 
                
                maxee = len(rtext)
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type1 = rtext[st:cc]
                type1.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type2 = rtext[st:cc]
                type2.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type3 = rtext[st:cc]
                type3.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type4 = rtext[st:cc]
                type4.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type5 = rtext[st:cc]
                type5.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type6 = rtext[st:cc]
                type6.replace(" ","")
                st = cc
                textback += """<br><br>CONDUIT1 = <font color=blue>%s</font><br>""" % type1
                if type2 != "":
                    textback += """CONDUIT2 = <font color=blue>%s</font><br>""" % type2
                if type3 != "":
                    textback += """CONDUIT3 = <font color=blue>%s</font><br>""" % type3
                if type4 != "":
                    textback += """CONDUIT4 = <font color=blue>%s</font><br>""" % type4
                if type5 != "":
                    textback += """CONDUIT5 = <font color=blue>%s</font><br>""" % type5
                if type6 != "":
                    textback += """CONDUIT6 = <font color=blue>%s</font><br>""" % type6
                textback += """<br><br><b>CIRC</b>: Any circular conduit.<br><br>
                            <b>NHE</b>: Nominal-elliptical conduit with major axis horizontal.<br><br>
                            <b>NVE</b>: Nominal-elliptical conduit with major axis vertical.<br><br>
                            <b>TE</b>: True-elliptical pipe.<br><br>
                            <b>RCPA</b>: Reinforced-concrete pipe-arch conduit.<br><br>
                            <b>BOX</b>: Rectangular opening.<br><br>
                            <b>CMPA</b>: Corrugated-metal pipe arch, 2 and two-thirds by one-half inch corrugation. Post-1980.<br><br>
                            <b>CMPAB</b>: Corrugated-metal pipe arch, 2 and two-thirds by one-half inch corrugation. Pre-1980.<br><br>
                            <b>CMPA1</b>: Corrugated-metal pipe arch, 3- by 1-inch corrugations. Post-1980.<br><br>
                            <b>CMPA1B</b>: Corrugated-metal pipe arch, 3- by 1-inch corrugations. Pre-1980.<br><br>
                            <b>SPPA18</b>: Structural-plate pipe arch, 6- by 2-inch corrugations. 18-inch corners<br><br>
                            <b>SPPA31</b>: Structural-plate pipe arch, 6- by 2-inch corrugations. 31-inch corners<br><br>""" 
            elif rtext.startsWith("SPAN"):
                rtext.replace("SPAN:","")
                rtext.replace("SPAN=","")
                cc = 0
                st = cc
                ee = cc + 1 
                
                maxee = len(rtext)
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type1 = rtext[st:cc]
                type1.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type2 = rtext[st:cc]
                type2.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type3 = rtext[st:cc]
                type3.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type4 = rtext[st:cc]
                type4.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type5 = rtext[st:cc]
                type5.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type6 = rtext[st:cc]
                type6.replace(" ","")
                st = cc
                
                textback += """<br><br>CONDUIT1 = <font color=blue>%s</font><br>""" % type1
                if type2 != "":
                    textback += """CONDUIT2 = <font color=blue>%s</font><br>""" % type2
                if type3 != "":
                    textback += """CONDUIT3 = <font color=blue>%s</font><br>""" % type3
                if type4 != "":
                    textback += """CONDUIT4 = <font color=blue>%s</font><br>""" % type4
                if type5 != "":
                    textback += """CONDUIT5 = <font color=blue>%s</font><br>""" % type5
                if type6 != "":
                    textback += """CONDUIT6 = <font color=blue>%s</font><br>""" % type6
                textback += """<br><br>The maximum horizontal dimension of the opening for each
                            of the conduits""" 
            elif rtext.startsWith("RISE"):
                rtext.replace("RISE:","")
                rtext.replace("RISE=","")
                cc = 0
                st = cc
                ee = cc + 1 
                
                maxee = len(rtext)
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type1 = rtext[st:cc]
                type1.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type2 = rtext[st:cc]
                type2.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type3 = rtext[st:cc]
                type3.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type4 = rtext[st:cc]
                type4.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type5 = rtext[st:cc]
                type5.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type6 = rtext[st:cc]
                type6.replace(" ","")
                st = cc
                textback += """<br><br>CONDUIT1 = <font color=blue>%s</font><br>""" % type1
                if type2 != "":
                    textback += """CONDUIT2 = <font color=blue>%s</font><br>""" % type2
                if type3 != "":
                    textback += """CONDUIT3 = <font color=blue>%s</font><br>""" % type3
                if type4 != "":
                    textback += """CONDUIT4 = <font color=blue>%s</font><br>""" % type4
                if type5 != "":
                    textback += """CONDUIT5 = <font color=blue>%s</font><br>""" % type5
                if type6 != "":
                    textback += """CONDUIT6 = <font color=blue>%s</font><br>""" % type6
                textback +="""<br><br>The maximum vertical dimension of the opening for each
                            conduit""" 
            elif rtext.startsWith("BOTT"):
                rtext.replace("BOTT:","")
                rtext.replace("BOTT=","")
                cc = 0
                st = cc
                ee = cc + 1 
                
                maxee = len(rtext)
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type1 = rtext[st:cc]
                type1.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type2 = rtext[st:cc]
                type2.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type3 = rtext[st:cc]
                type3.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type4 = rtext[st:cc]
                type4.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type5 = rtext[st:cc]
                type5.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type6 = rtext[st:cc]
                type6.replace(" ","")
                st = cc
                textback += """<br><br>CONDUIT1 = <font color=blue>%s</font><br>""" % type1
                if type2 != "":
                    textback += """CONDUIT2 = <font color=blue>%s</font><br>""" % type2
                if type3 != "":
                    textback += """CONDUIT3 = <font color=blue>%s</font><br>""" % type3
                if type4 != "":
                    textback += """CONDUIT4 = <font color=blue>%s</font><br>""" % type4
                if type5 != "":
                    textback += """CONDUIT5 = <font color=blue>%s</font><br>""" % type5
                if type6 != "":
                    textback += """CONDUIT6 = <font color=blue>%s</font><br>""" % type6
                textback += """<br><br>The height of the invert of each conduit above the invert
                            of the conduit with the smallest invert elevation""" 
            elif rtext.startsWith("ROUG:"):
                rtext.replace("ROUG:","")
                rtext.replace("ROUG=","")
                cc = 0
                st = cc
                ee = cc + 1 
                
                maxee = len(rtext)
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type1 = rtext[st:cc]
                type1.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type2 = rtext[st:cc]
                type2.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type3 = rtext[st:cc]
                type3.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type4 = rtext[st:cc]
                type4.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type5 = rtext[st:cc]
                type5.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type6 = rtext[st:cc]
                type6.replace(" ","")
                st = cc 
                textback += """<br><br>CONDUIT1 = <font color=blue>%s</font><br>""" % type1
                if type2 != "":
                    textback += """CONDUIT2 = <font color=blue>%s</font><br>""" % type2
                if type3 != "":
                    textback += """CONDUIT3 = <font color=blue>%s</font><br>""" % type3
                if type4 != "":
                    textback += """CONDUIT = <font color=blue>%s</font><br>""" % type4
                if type5 != "":
                    textback += """CONDUIT5 = <font color=blue>%s</font><br>""" % type5
                if type6 != "":
                    textback += """CONDUIT6 = <font color=blue>%s</font><br>""" % type6
                textback += """<br><br>The Manning\'s <i>n</i> for each of the conduits"""
            elif rtext.startsWith("MUDL"):
                rtext.replace("MUDL:","")
                rtext.replace("MUDL=","")
                cc = 0
                st = cc
                ee = cc + 1 
                
                maxee = len(rtext)
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type1 = rtext[st:cc]
                type1.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type2 = rtext[st:cc]
                type2.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type3 = rtext[st:cc]
                type3.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type4 = rtext[st:cc]
                type4.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type5 = rtext[st:cc]
                type5.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type6 = rtext[st:cc]
                type6.replace(" ","")
                st = cc 
                textback += """<br><br>CONDUIT1 = <font color=blue>%s</font><br>""" % type1
                if type2 != "":
                    textback += """CONDUIT2 = <font color=blue>%s</font><br>""" % type2
                if type3 != "":
                    textback += """CONDUIT3 = <font color=blue>%s</font><br>""" % type3
                if type4 != "":
                    textback += """CONDUIT = <font color=blue>%s</font><br>""" % type4
                if type5 != "":
                    textback += """CONDUIT5 = <font color=blue>%s</font><br>""" % type5
                if type6 != "":
                    textback += """CONDUIT6 = <font color=blue>%s</font><br>""" % type6
                textback += """<br><br>The thickness of the sediment measured from the invert of each conduit."""
            elif rtext.startsWith("ROUG="):
                rtext.replace("ROUG=","")
                cc = 0
                st = cc
                ee = cc + 1 
                
                maxee = len(rtext)
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type1 = rtext[st:cc]
                type1.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type2 = rtext[st:cc]
                type2.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type3 = rtext[st:cc]
                type3.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type4 = rtext[st:cc]
                type4.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type5 = rtext[st:cc]
                type5.replace(" ","")
                st = cc
                while rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                while not rtext[cc:ee] == " ":
                    cc += 1
                    ee = cc + 1
                    if ee > maxee:
                        break
                type6 = rtext[st:cc]
                type6.replace(" ","")
                st = cc 
                textback += """<br><br>CONDUIT1 = <font color=blue>%s</font><br>""" % type1
                if type2 != "":
                    textback += """CONDUIT2 = <font color=blue>%s</font><br>""" % type2
                if type3 != "":
                    textback += """CONDUIT3 = <font color=blue>%s</font><br>""" % type3
                if type4 != "":
                    textback += """CONDUIT = <font color=blue>%s</font><br>""" % type4
                if type5 != "":
                    textback += """CONDUIT5 = <font color=blue>%s</font><br>""" % type5
                if type6 != "":
                    textback += """CONDUIT6 = <font color=blue>%s</font><br>""" % type6
                textback += """<br><br>The Manning\'s <i>n</i> for the sediment in the conduit."""

            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_18.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
            
        elif rcode == "QLIM":                                           #QLIM
            textback = """<b>Free-flow limit</b><br>Estimate ofthe maximum flow of a closed
                        conduit when the conduit is flowing full.<br><br>"""
            if rtext.startsWith("TABLE"):
                textback += """<b>TABLE</b> - Table number: <font color=blue>%s</font>""" % rtext[7:]
            elif rtext.startsWith("TABID"):
                textback += """<b>TABID</b> - Table number: <font color=blue>%s</font>""" % rtext[6:]
            elif rtext.startsWith("FACTOR"):
                textback += """<b>FACTOR</b> - Multiplying factor to change value from that given by the built-in
                            extrapolation: <font color=blue>%s</font>""" % rtext[7:]
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_20.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
            
        elif rcode == "SEWR":                                          #SEWER
            textback = """<b>Cross-section of circular conduits</b><br>A cross section function table is computed in the sewer
                        command only for the barrel of a culvert or for a storm sewer.<br><br>"""
            if rtext.startsWith("TABLE#") or rtext.startsWith("TABID"):
                textback += """<b></b><b>%s</b>""" % rtext.split('=')[0] 
                textback += """ - Table number: <font color=blue>%s</font><br><br><u>Table options:</u>""" % rtext[7:12] 
                if "EXTEND" in rtext:
                    textback += """<b></b><font color=blue>EXTEND</font>: a vertical, frictionless extension is added to the
                                first or last point of the cross section, as needed, to match the point of maximum elevation
                                in the cross section."""
                if "MONOTONE" in rtext:
                    textback += """<br><font color=blue>MONOTONE</font>: the offsets for the cross section are examined to
                                ensure that they are increasing."""
                if " NEWBETA" in rtext:
                    textback += """<br><font color=blue>NEWBETA</font>: the momentum-flux
                                correction coefficient and the kinetic-energy-flux correction
                                coefficient are computed by application of a method."""
                if "NEWBETAE" in rtext:
                    textback += """<br><font color=blue>NEWBETAE</font>: same as NEWBETA
                                except that the critical flow tabulated is based on the
                                energy principle."""
                if "NEWBETAM" in rtext:
                    textback += """<br><font color=blue>NEWBETAM</font>: same as NEWBETA
                                except that the critical flow tabulated is based on the
                                energy principle."""
                if "OLDBETA" in rtext:
                    textback += """<br><font color=blue>OLDBETA</font>: the kinetic-energy-flux
                                correction coefficient and the momentum-flux correction coefficient
                                for the cross section are computed from equations 7 and 8 in section
                                3.1.1."""
                if " SAVE" in rtext:
                    a = 0
                    b = 1
                    while not " SAVE" in rtext[a:b]:
                        b += 1
                    textback += """<br><font color=blue>%s</font>: a copy of the resulting
                                table is saved internally in the FEQUTL computations. The table type
                                is given by the two digits next to SAVE.""" % rtext[b - 4:b + 2]
                if "NOSAVE" in rtext:
                    textback += """<br><font color=blue>NOSAVE</font>: a copy of the table is
                                not saved internally in the FEQUTL computations."""
                if " OUT" in rtext:
                    a = 0
                    b = 1
                    while not " OUT" in rtext[a:b]:
                        b += 1
                    textback += """<br><font color=blue>%s</font>: a copy of the table is
                                output to the standard function-table file given by the two digits
                                after OUT.""" % rtext[b - 3:b + 2]
                if "NOOUT" in rtext:
                    textback += """<br><font color=blue>NOOUT</font>: output of the table to the
                                standard function-table file is suppressed."""
                
            elif rtext.startsWith("DIAMETER"):
                textback += """<b></b><b>DIAMETER</b> - The diameter of the pipe in feet or meters: <font color=blue>%s</font>""" % rtext[9:]

            elif rtext.startsWith("NSIDES"):
                textback += """<b>NSIDES</b> - The number of sides in the polygon used to approximate
                            the circular conduit. NSIDES should be equal to or greater than 10: <font color=blue>%s</font>""" % rtext[7:]
            elif rtext.startsWith("WSLOT"):
                textback += """<b>WSLOT</b> - The width of the hypothetical slot used to maintain
                            a free surface in the conduit: <font color=blue>%s</font>""" % rtext[6:]
            elif rtext.startsWith("HSLOT"):
                textback += """<b>HSLOT</b> - The height of the hypothetical slot above the invert
                            of the conduit, which has the minimum elevation: <font color=blue>%s</font>""" % rtext[6:]
            elif rtext.startsWith("N="):
                textback += """<b>N</b> - Manning\'s <i>n</i> for the conduit: <font color=blue>%s</font>""" % rtext[2:]
            elif rtext.startsWith("MUDL"):
                textback += """<b>MUDL</b> - Thickness of the sediment measured from the invert of each conduit: <font color=blue>%s</font>""" % rtext.split("MUDL=")[-1]
            elif rtext.startsWith("MUDN"):
                textback += """<b>MUDN</b>: <font color=blue>%s</font>""" % rtext.split('MUDN=')[-1]
            elif "ZONE" in rtext :
                zone = rtext.split('ZONE=')[-1]
                textback +=  """<br><b>ZONE</b> - The zone designation for the horizontal grid: 
                            <font color=blue>%s</font>""" % re.split('\s+', zone)[0]
                if "HGRID" in rtext:
                    hgrid = rtext.split('HGRID=')[1]
                    textback += """<br><br><b>HGRID</b> - The name for the horizontal grid used for 
                                eastings and northings: <font color=blue>%s</font>""" % re.split('\s+', hgrid)[0]
                if "BASIS" in rtext:
                    basis = rtext.split('BASIS=')[1]
                    textback += """<br><br><b>BASIS</b> - The description of era, date, or other item to 
                                denote the data source: <font color=blue>%s</font>""" % re.split('\s+', basis)[0]
                if "VDATUM" in rtext:
                    vdatum = rtext.split('VDATUM=')[1]
                    textback += """<br><br><b>VDATUM</b> - The vertical datum: <font color=blue>%s</font>""" % re.split('\s+', vdatum)[0]
                if "UNITSYS" in rtext:
                    unitsys = rtext.split('UNITSYS=')[1]
                    textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('\s+', unitsys)[0]
            elif rtext.startsWith("VDATUM"):
                vdatum = re.split("VDATUM\s*=", rtext)[-1]
                textback += """<b>VDATUM</b> - The vertical datum: <font color=blue>%s</font>""" % re.split("\s+", vdatum)[0]
                if "UNITSYS" in rtext:
                    unitsys = re.split("\s*UNITSYS\s*=\s*", rtext)[-1]
                    textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('/s+', unitsys)[0]
            else:
                rtext.replace(" ","<br>")
                while "<br><br>" in rtext:
                    rtext.replace("<br><br>","<br>")
                textback += """<font color=blue>%s</font>""" % rtext
            textback += """<br><br><br>

                        <a href ="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_21.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
            
        elif rcode == "CRITQ":                                      #CRITQ
            textback = """<b>Critical flow in a constricted section</b><br> as a function of the depth of water in an approach
                        section<br><br>"""
            if rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("TABID"):
                rtext = re.split('TABID\s*=\s*', rtext)[-1]
                textback += """<br><b>TABID</b> - Gives the table number for the table to be computed in FEQUTL: 
                            <font color=blue>%s</font>""" % re.split('\s+', rtext)[0]
                if "SAVE" in rtext:
                    textback += """<br><br><b>SAVE</b> - Indicates that the resulting table is saved internally so that it can be referenced
                            for use in later commands."""
            elif rtext.startsWith("APPTAB"):
                rtext = rtext.split('APPTAB#=')[-1]
                textback += """<b>APPTAB#</b> - Table number for the cross-section table describing the shape of the channel conveying water
                            to the critical section: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("CONTAB"):
                rtext = rtext.split('CONTAB#=')[-1]
                textback += """<b>CONTAB#</b> - Table number for the cross-section table defining the cros ssection at which critical flow is
                            assumed to be present: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("DISCOEF"):
                rtext = rtext.split('DISCOEF=')[-1]
                textback += """<b>DISCOEF</b> - Discharge coefficient for the opening: <font color=blue>%s</font>""" % rtext
            elif "ZONE" in rtext :
                zone = rtext.split('ZONE=')[-1]
                textback +=  """<br><br><b>ZONE</b> - The zone designation for the horizontal grid: 
                            <font color=blue>%s</font>"""% re.split('\s+', zone)[0]
                if "HGRID" in rtext:
                    hgrid = rtext.split('HGRID=')[1]
                    textback += """<br><br><b>HGRID</b> - The name for the horizontal grid used for 
                                eastings and northings: <font color=blue>%s</font>""" % re.split('\s+', hgrid)[0]
                if "BASIS" in rtext:
                    basis = rtext.split('BASIS=')[1]
                    textback += """<br><br><b>BASIS</b> - the description of era, date, or other item to 
                                denote the data source: <font color=blue>%s</font>""" % re.split('\s+', basis)[0]
                if "VDATUM" in rtext:
                    vdatum = rtext.split('VDATUM=')[1]
                    textback += """<br><br><b>VDATUM</b> - The vertical datum: <font color=blue>%s</font>""" % re.split('\s+', vdatum)[0]
                if "UNITSYS" in rtext:
                    unitsys = rtext.split('UNITSYS=')[1]
                    textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('\s+', unitsys)[0]
            elif rtext.startsWith("EASTING"):
                    a = 8
                    while not rtext[a:a+1] == "N":
                        a += 1
                        if a > len(rtext):
                            break
                    textback += """<b>EASTING</b> - The easting or x value for the coordinate system: <font color=blue>%s</font><br><br>
                                <b>NORTHING</b> - The northing or y value for the coordinate system: 
                                <font color=blue>%s</font>""" % (rtext[8:a], rtext[a+9:])
            else:
                textback += """<font color=blue>%s</font><br><br>
                            Column headings label""" % rtext
            textback += """<br><br><br>

                        <a href="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_6.htm"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

        elif rcode == "GRIT":                                       #GRITTER
            textback = """<b>Peak outflow solution following instantaneous failure of a dam.</b><br><br>"""
            if rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("APPTAB"):
                textback += """<b>APPTAB#</b> - Table number for the approach cross section to the dam site: 
                <font color=blue>%s</font>""" % re.split('APPTAB#\s*=\s*', rtext)[-1]
            elif rtext.startsWith("CONTAB"):
                textback += """<b>CONTAB#</b> - Table number for the constricted-flow relation produced in CRITQ: 
                <font color=blue>%s</font>""" % re.split('CONTAB#\s*=\s*', rtext)[-1]
            elif "." in rtext:
                a = 0
                while " " in rtext[a:a+1]:
                    a += 1
                while not " " in rtext[a:a+1]:
                    a += 1
                    if a+1 > len(rtext):
                        break
                y = rtext[:a]
                Q = rtext[a:]
                textback += """
                            <b>DEPTH</b> - The before-failure, water-surface height in the reservoir: <font color=blue>%s</font><br><br>
                            <b>DISCHARGE</b> - Before-failure flow rate in the reservoir: <font color=blue>%s</font>""" % (y, Q)
            else:
                textback += """Table headers:<br><font color=blue>%s</font>""" % rtext
            textback += """<br><br><br>

                        <a href="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_16.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

        elif rcode == "MULP":                                       #MULPIPES
            textback = """<b>Hydraulic characteristics of circular conduits.</b><br><br>"""
            if rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment:<br><font color=blue>%s</font>""" % rtext[1:]
            elif rtext.startsWith("TABID"):
                rtext = rtext.split('TABID=')[-1]
                textback += """<b>TABID</b> - Table number of the cross-section table: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("TABLE#"):
                rtext = rtext.split('TABLE#=')[-1]
                textback += """<b>TABLE#</b> - Table number of the cross-section table: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("VDATUM"):
                vdatum = re.split("VDATUM\s*=", rtext)[-1]
                textback += """<br><br><b>VDATUM</b> -  The vertical datum: <font color=blue>%s</font>""" % re.split("\s+", vdatum)[0]
                if "UNITSYS" in rtext:
                    unitsys = re.split("\s*UNITSYS\s*=\s*", rtext)[-1]
                    textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('/s+', unitsys)[0]
            elif rtext.startsWith("NSIDES"):
                rtext = rtext.split('NSIDES=')[-1]
                textback += """<b>NSIDES</b> - Number of sides in the polygon used to approximate the multiple
                            pipes: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("WSLOT"):
                rtext = rtext.split('WSLOT=')[-1]
                textback += """<b>WSLOT</b> - Width of the hypothetical slot used to maintain a free surface in the
                            pipe: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("HSLOT"):
                rtext = rtext.split('HSLOT=')[-1]
                textback += """<b>HSLOT</b> - Height of the slot above the invert of the conduit with the lowest invert
                            elevation: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("ZONE"):
                zone = rtext.split('ZONE=')[-1]
                textback +=  """<br><b>ZONE</b> - The zone designation for the horizontal grid: 
                            <font color=blue>%s</font>""" % re.split('\s+', zone)[0]
                if "HGRID" in rtext:
                    hgrid = rtext.split('HGRID=')[1]
                    textback += """<br><br><b>HGRID</b> - The name for the horizontal grid used for 
                                eastings and northings: <font color=blue>%s</font>""" % re.split('\s+', hgrid)[0]
                if "BASIS" in rtext:
                    basis = rtext.split('BASIS=')[1]
                    textback += """<br><br><b>BASIS</b> - The description of era, date, or other item to 
                                denote the data source: <font color=blue>%s</font>""" % re.split('\s+', basis)[0]
                if "VDATUM" in rtext:
                    vdatum = rtext.split('VDATUM=')[1]
                    textback += """<br><br><b>VDATUM</b> - The vertical datum: <font color=blue>%s</font>""" % re.split('\s+', vdatum)[0]
                if "UNITSYS" in rtext:
                    unitsys = rtext.split('UNITSYS=')[1]
                    textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('\s+', unitsys)[0]
            elif rtext.startsWith("NPIPES"):
                a = 7
                while rtext[a:a+1] == " ":
                    a += 1
                    if a+1 > len(rtext):
                        break
                while not rtext[a:a+1] == " ":
                    a += 1
                    if a+1 > len(rtext):
                        break
                textback += """<b>NPIPES</b> - Number of conduits: <font color=blue>%s</font><br>
                            Difference in elev. accross a mud line: <font color=blue>%s</font>
                            """ % (rtext[7:a], rtext[a:])
            elif rtext.startsWith("DIAM"):
                rtext.replace(" ","<br>")
                while "<br><br>" in rtext:
                    rtext.replace("<br><br>","<br>")
                rtext = rtext.split('DIAM=')[-1]
                textback += """<b>DIAM</b> - Diameter of each of the pipes: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("BOTT"):
                rtext.replace(" ","<br>")
                while "<br><br>" in rtext:
                    rtext.replace("<br><br>","<br>")
                rtext = rtext.split('BOTT=')[-1]
                textback += """<b>BOTT</b> - Height of the invert of each pipe aove the invert of the
                            pipe with the smallest invert elevation: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("ROUG"):
                rtext.replace(" ","<br>")
                while "<br><br>" in rtext:
                    rtext.replace("<br><br>","<br>")
                rtext = rtext.split('ROUG=')[-1]
                textback += """<b>ROUG</b> - Manning's <i>n</i> for each of the pipes: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("MUDL"):
                rtext.replace(" ","<br>")
                while "<br><br>" in rtext:
                    rtext.replace("<br><br>","<br>")
                textback += """<b>MUDL</b> - Thickness of sediment in each conduit: <font color=blue>%s</font>""" % rtext
            textback += """<br><br><br>

                        <a href="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_19.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
            
        elif rcode == "XSIN":                                       #XSINTERP
            textback = """<b>Computation of cross section tables by interpolation.</b><br><br>"""
            if rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment:<br><font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("SFAC"):
                textback += """<b>SFAC</b> - Multiplying factor for converting the stations for the nodes given
                            in the single Branch Description Block in the FEQ input file: <font color=blue>%s</font>""" % rtext.split('SFAC=')[-1]
            elif rtext.startsWith("NODEID"):
                textback += """<b>NODEID</b>: <font color=blue>%s</font><br><br>
                            YES indicates that an id string will be given in the branch tables.<br>
                            NO indicates that no id string will be given.""" % rtext.split('NODEID=')[-1]
            elif "NODE" in rtext:
                textback += """Table headers.<br><br><font color=blue>%s</font>""" % rtext
            elif rtext == "XSINTERP":
                textback += """ """
            elif "-1" in rtext[:5]:
                textback += """End of block."""
            else:
                textback += """Table parameters.<br><br> These values are header-dependent, so they
                            are defined by the headers above. The headers are as follows:<br><br>
                            NODE is the node number.<br>
                            NAME is the optional id string for the node.<br>
                            XTAB is the number of the table giving the hydraulic characteristics.<br>
                            X is the station of the node.
                            Z is the elevation of the minimum point in the stream at the node."""
            textback += """<br><br><br>

                        <a href="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_26.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

        elif rcode == "HEC2":                                       #HEC2X
            textback = """<b>Load HEC-2 input file.</b><br><br>"""
            if rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment:<br><font color=blue>%s</font>""" % rtext[1:]
            elif rtext.startsWith("MODE"):
                textback += """<b>MODE</b>: <font color=blue>%s</font><br><br>
                            DIRECT: computes a cross-section table directly from the HEC-2 input.<br>
                            INDIRECT: computes input for the FEQX command from the HEC-2 input.<br>
                            CHANNEL: computes input for a CHANNEL command and places it in a file.""" % rtext.split('MODE=')[-1]
            elif rtext.startsWith("INFILE"):
                textback += """<b>INFILE</b> - Name of the file containing the HEC-2 input: <font color=blue>%s</font>""" % rtext[7:]
            elif rtext.startsWith("OUTFILE"):
                textback += """<b>OUTFILE</b> - File name to store FEQUTL input: <font color=blue>%s</font><br><br>
                            Only needed when MODE=INDIRECT or CHANNEL. Leave blank if MODE=DIRECT.""" % rtext[8:]
            elif rtext.startsWith("ZONE"):
                zone = rtext.split('ZONE=')[-1]
                textback +=  """<br><b>ZONE</b> - The zone designation for the horizontal grid: 
                            <font color=blue>%s</font>""" % re.split('\s+', zone)[0]
                if "HGRID" in rtext:
                    hgrid = rtext.split('HGRID=')[1]
                    textback += """<br><br><b>HGRID</b> - The name for the horizontal grid used for 
                                eastings and northings: <font color=blue>%s</font>""" % re.split('\s+', hgrid)[0]
                if "BASIS" in rtext:
                    basis = rtext.split('BASIS=')[1]
                    textback += """<br><br><b>BASIS</b> - The description of era, date, or other item to 
                                denote the data source: <font color=blue>%s</font>""" % re.split('\s+', basis)[0]
                if "VDATUM" in rtext:
                    vdatum = rtext.split('VDATUM=')[1]
                    textback += """<br><br><b>VDATUM</b> - The vertical datum: <font color=blue>%s</font>""" % re.split('\s+', vdatum)[0]
                if "UNITSYS" in rtext:
                    unitsys = rtext.split('UNITSYS=')[1]
                    textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('\s+', unitsys)[0]
            elif rtext.startsWith("OPTIONS"):
                textback += """<u>Table options:</u>"""
                if "EXTEND" in rtext:
                    textback += """<br><font color=blue>EXTEND</font>: a vertical extension is
                                added to the first or last points to match the point of
                                maximum elevation in the cross section."""
                if "MONOTONE" in rtext:
                    textback += """<br><font color=blue>MONOTONE</font>: the offsets for the
                                cross section are examined to ensure that they are
                                increasing."""
                if " NEWBETA" in rtext or rtext.startsWith("NEWBETA"):
                    textback += """<br><font color=blue>NEWBETA</font>: the momentum-flux
                                correction coefficient and the kinetic-energy-flux correction
                                coefficient are computed by application of a method."""
                if "NEWBETAE" in rtext:
                    textback += """<br><font color=blue>NEWBETAE</font>: same as NEWBETA
                                except that the critical flow tabulated is based on the
                                energy principle."""
                if "NEWBETAM" in rtext:
                    textback += """<br><font color=blue>NEWBETAM</font>: same as NEWBETA
                                except that the critical flow tabulated is based on the
                                energy principle."""
                if "OLDBETA" in rtext:
                    textback += """<br><font color=blue>OLDBETA</font>: the kinetic-energy-flux
                                correction coefficient and the momentum-flux correction coefficient
                                for the cross section are computed from equations 7 and 8 in section
                                3.1.1."""
                if " SAVE" in rtext or rtext.startsWith("SAVE"):
                    a = 0
                    b = 1
                    if not rtext.startsWith("SAVE"):
                        while not " SAVE" in rtext[a:b]:
                            b += 1
                    else:
                        while not "SAVE" in rtext[a:b]:
                            b += 1
                    
                    textback += """<br><font color=blue>%s</font>: a copy of the resulting
                                table is saved internally in the FEQUTL computations. The table type
                                is given by the two digits next to SAVE.""" % rtext[b - 4:b + 2] 
                if "NOSAVE" in rtext:
                    textback += """<br><font color=blue>NOSAVE</font>: a copy of the table is
                                not saved internally in the FEQUTL computations."""
                if " OUT" in rtext or rtext.startsWith("OUT"):
                    a = 0
                    b = 1
                    if not rtext.startsWith("OUT"):
                        while not " OUT" in rtext[a:b]:
                            b += 1
                        c = 4
                    else:
                        while not "OUT" in rtext[a:b]:
                            b += 1
                        c = 3
                        
                    textback += """<br><font color=blue>%s</font>: a copy of the table is
                                output to the standard function-table file given by the two digits
                                after OUT.""" % rtext[b - c:b + 2] 
                if "NOOUT" in rtext:
                    textback += """<br><font color=blue>NOOUT</font>: output of the table to the
                                standard function-table file is suppressed."""
                    
            elif rtext.startsWith("BEGTAB#="):
                textback += """<b>BEGTAB#</b> - Table number for the first cross section found in the HEC-2 input:
                            <font color=blue>%s</font><br><br>Table number increment added to
                            <font color=blue>
                            %s</font> resulting in the table numbers for all cross sections found in the
                            HEC-2 input: <font color=blue>%s</font>""" % (rtext[8:13], rtext[8:13], \
                                                                                 rtext[13:])
            elif rtext.startsWith("BEGSTAT"):
                textback += """<b>BEGSTAT</b> - Beggining station for the first cross section: <font color=blue>%s
                            </font><br><br>
                            The distance between cross sections in the HEC-2 input should be """ % rtext[8:18]
                if "-1" in rtext[18:23]:
                    textback += """subtracted."""
                else:
                    textback += """added."""
            elif rtext.startsWith("SFAC"):
                textback += """<b>SFAC</b> - Conversion factor from the units used in HEC-2 for the distance
                            between cross sections to the units in the stationing in the unsteady-flow
                            model: <font color=blue>%s</font><br><br>""" % rtext.split('SFAC=')[-1]
            textback += """<br><br><br>

                        <a href="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_17.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

        elif rcode == "CHAN":                                       #CHANNEL
            textback = """<b>Hydraulic properties of a cross section including the
                        correction factors for curvilinearity.</b><br><br>"""
            if rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment:<br><font color=blue>%s</font>""" % rtext[1:]
            elif rtext.startsWith("SINDEF"):
                textback += """<b>SINDEF</b> - The method to be used in computing the
                            sinuosity of each nonaxis flow line at each cross section: <font color=blue>%s</font>
                            <br><br>See manual for explanation of methods.""" % rtext[7:]
            elif rtext.startsWith("HEAD"):
                rtext.replace(" ","<br>")
                while "<br><br>" in rtext:
                    rtext.replace("<br><br>","<br>")
                textback += """Table headers:<br><br><font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("STAT"):
                rtext.replace("STAT","")
                rtext.replace(" ","<br>")
                while "<br><br>" in rtext:
                    rtext.replace("<br><br>","<br>")
                textback += """<b>STAT</b> - A station of a cross section is specified.<br><br>
                            Station values:<br><font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("LENG"):
                rtext.replace("LENG","")
                rtext.replace(" ","<br>")
                while "<br><br>" in rtext:
                    rtext.replace("<br><br>","<br>")
                textback += """<b>LENG</b> - An incremental distance from a previos section is specified.<br><br>
                            Incremental distance for each flow line: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("OFFS"):
                rtext.replace("OFFS","")
                rtext.replace(" ","<br>")
                while "<br><br>" in rtext:
                    rtext.replace("<br><br>","<br>")
                textback += """<b>OFFS</b> - Offsets of the flow lines in a cross section are specified.<br><br>
                            Offset values for each flow line: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("SINU"):
                textback += """<b>SINU</b> - Local option for computing the sinuosity."""
            elif rtext.startsWith("END"):
                textback += """End of section or block."""


            textback += """<br><br><br>

                        <a href="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_4.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""
            

        elif rcode == "UFGT":                                       #UFGATE
            textback = """<b>Underflow gate (sluice or tainter)</b><br><br>"""
            if rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment:<br><font color=blue>%s</font>""" % rtext[1:]
            elif rtext.startsWith("TABLE"):
                textback += """<b>TABLE</b> - Table number: <font color=blue>%s</font><br><br>
                            Table number to be computed (Type 15)""" % rtext.split('TABLE=')[-1]
            elif rtext.startsWith("TABID"):
                textback += """<b>TABID</b> - Table number: <font color=blue>%s</font><br><br>
                            Table number to be computed (Type 15)""" % rtext.split('TABID=')[-1]
            elif rtext.startsWith("LABEL"):
                textback += """<b>LABEL</b> - Descriptive label for the table: <font color=blue>%s</font>""" % rtext[6:]
            elif rtext.startsWith("APPTAB"):
                textback += """<b>APPTAB</b> - Table number for the approach cross-section: <font
                            color=blue>%s</font>""" % rtext[7:]
            elif rtext.startsWith("DEPTAB"):
                textback += """<b>DEPTAB</b> - Table number for the departure cross-section: <font
                            color=blue>%s</font>""" % rtext[7:]
            elif rtext.startsWith("SILLELEV"):
                textback += """<b>SILLELEV</b> - Elevation of the gate sill: <font color=blue>%s
                            </font>""" % rtext[9:]
            elif rtext.startsWith("GATEW"):
                a = 0
                while not rtext[a:a+1] == "=":
                    a += 1
                textback += """<b>GATEW</b> - Gate width: <font color=blue>%s</font>""" % rtext[a+1:]
            elif rtext.startsWith("ZONE"):
                zone = rtext.split('ZONE=')[-1]
                textback +=  """<br><b>ZONE</b> - The zone designation for the horizontal grid: 
                            <font color=blue>%s</font>""" % re.split('\s+', zone)[0]
                if "HGRID" in rtext:
                    hgrid = rtext.split('HGRID=')[1]
                    textback += """<br><br><b>HGRID</b> - The name for the horizontal grid used for 
                                eastings and northings: <font color=blue>%s</font>""" % re.split('\s+', hgrid)[0]
                if "BASIS" in rtext:
                    basis = rtext.split('BASIS=')[1]
                    textback += """<br><br><b>BASIS</b> - The description of era, date, or other item to 
                                denote the data source: <font color=blue>%s</font>""" % re.split('\s+', basis)[0]
                if "VDATUM" in rtext:
                    vdatum = rtext.split('VDATUM=')[1]
                    textback += """<br><br><b>VDATUM</b> - The vertical datum: <font color=blue>%s</font>""" % re.split('\s+', vdatum)[0]
                if "UNITSYS" in rtext:
                    unitsys = rtext.split('UNITSYS=')[1]
                    textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('\s+', unitsys)[0]
            elif rtext.startsWith("CD"):
                textback += """<b>CD</b> - Discharge coefficient: <font color=blue>%s
                            </font>""" % rtext[3:]
            elif rtext.startsWith("CCTAB"):
                textback += """<b>CCTAB</b> - Contraction coefficient table number: <font color=blue>
                            %s</font>""" % rtext[6:]
            elif rtext.startsWith("FWFOTRAN"):
                textback += """<b>FWFOTRAN</b> - Proportion of the current gate opening over which
                            a linear variation is applied to the contraction
                            coefficient from 1.0 at the upper limit of free-weir
                            flow to the value at the lower limit of standard
                            free-orifice flow: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("MAXHEAD"):
                textback += """<b>MAXHEAD</b> - Maximum upstream head
                            (at section 1) for flow through the gate: <font color=blue>%s</font>""" % rtext[8:]
            elif rtext.startsWith("MINHEAD"):
                textback += """<b>MINHEAD</b> - Minimum nonzero
                            upstream head (at section 1) for flow through the
                            gate: <font color=blue>%s</font>""" % rtext[8:]
            elif rtext.startsWith("PRECISION"):
                textback += """<b>PRECISION</b> - Linear interpolation
                            precision required in FEQUTL computations defining
                            the series of upstream heads: <font color=blue>%s</font>""" % rtext[10:]
            
            elif rtext.startsWith("MINPFD"):
                textback += """<b>MINPFD</b> - Minimum value of
                            partial fee drop to apply in computation of the
                            submerged flows for the gate: <font color=blue>%s</font>""" % rtext[7:]
            elif rtext.startsWith("BRKPFD"):
                textback += """<b>BRKPFD</b> - Value of partial
                            free drop at which variation of the submerged flows
                            changes: <font color=blue>%s</font>""" % rtext[7:]
            elif rtext.startsWith("LIMPFD"):
                textback += """<b>LIMPFD</b> - Limiting value of
                            partial free drop less than 1.0: <font color=blue>%s</font>""" % rtext[7:]
            elif rtext.startsWith("FINPOW"):
                textback += """<b>FINPOW</b> - Power to apply in
                            computation of the spacing for the partial free
                            drops from BRKPFD to LIMPFD (value must be between
                            1.0 and 3.0): <font color=blue>%s</font>""" % rtext[7:]
            elif "." in rtext:
                textback += """Gate opening: <font color=blue>%s</font><br>
                            Table number: <font color=blue>%s</font><br>
                            Optional value (overrides CCTAB): <font color=blue>
                            %s</font><br>
                            Angle: <font color=blue>%s</font>""" % (rtext[:10], \
                                                                    rtext[10:20], \
                                                                    rtext[20:30], \
                                                                    rtext[30:])
            elif rtext != "UFGATE":
                textback += """Headers:<br><font color=blue>%s</font>
                            """ % rtext

            textback += """<br><br><br>

                        <a href="http://il.water.usgs.gov/proj/feq/fequtl/chap5html/fequtl.chap5_22.html"
                        target="_blank">Manual (version FEQ 8.0 and FEQUTL 4.0)</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/proj/feq/software/release_feq.txt"
                        target="_blank">Additional Release Notes</a>
                        <br><br>
                        <a href ="http://il.water.usgs.gov/htdig/search-feq.html"
                        target="_blank">Search Tool</a>"""

        elif rcode.startsWith("ORIF"):                                       #ORIFICE
            textback = "<b>Flow through a vertical orifice</b><br><br>"""
            if rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment:<br><font color=blue>%s</font>""" % rtext[1:]
            elif rtext.startsWith("TABLE"):
                textback += """<b>TABLE</b> - Table number: <font color=blue>%s</font><br><br>
                            Table number to be computed (Type 15)""" % rtext.split('TABLE=')[-1]
            elif rtext.startsWith("TABID"):
                textback += """<b>TABID</b> - Table number: <font color=blue>%s</font><br><br>
                            Table number to be computed (Type 15)""" % rtext.split('TABID=')[-1]
            elif rtext.startsWith("ZONE"):
                zone = rtext.split('ZONE=')[-1]
                textback +=  """<br><b>ZONE</b> - The zone designation for the horizontal grid: 
                            <font color=blue>%s</font>""" % re.split('\s+', zone)[0]
                if "HGRID" in rtext:
                    hgrid = rtext.split('HGRID=')[1]
                    textback += """<br><br><b>HGRID</b> - The name for the horizontal grid used for 
                                eastings and northings: <font color=blue>%s</font>""" % re.split('\s+', hgrid)[0]
                if "BASIS" in rtext:
                    basis = rtext.split('BASIS=')[1]
                    textback += """<br><br><b>BASIS</b> - The description of era, date, or other item to 
                                denote the data source: <font color=blue>%s</font>""" % re.split('\s+', basis)[0]
                if "VDATUM" in rtext:
                    vdatum = rtext.split('VDATUM=')[1]
                    textback += """<br><br><b>VDATUM</b> - The vertical datum: <font color=blue>%s</font>""" % re.split('\s+', vdatum)[0]
                if "UNITSYS" in rtext:
                    unitsys = rtext.split('UNITSYS=')[1]
                    textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('\s+', unitsys)[0]
            elif rtext.startsWith("LABEL"):
                textback += """<b>LABEL</b>: <font color=blue>%s</font><br><br>Label for the table.""" % rtext[6:]
            elif "." in rtext and rcode == "ORIFa":
                textback += """Table values (heading dependent):<br><br>
                            <b>NUMBR</b> - number of identical barrels that are to be included in the
                            computations.<br><br>
                            <b>SHAPE</b> - shape of orifice opening<br>
                            <b>CIRCLE</b>, <b>CIRC</b>, <b>ROUND</b> - circular orifice<br>
                            RECT - rectangular orifice<br>
                            <b>INVITRI</b>, <b>TRI</b> - symmetrical triangular orifice<br>
                            <b>OTHER</b>, <b>OFF</b> - user-defined shapes<br><br>
                            <b>Edge</b> - edge shape<br>
                            <b>SHARP</b> - sharp-edged orifice<br><br>
                            <b>VertD</b> - vertical diameter for the orifice<br><br>
                            <b>HoriD</b> - horizonal diameter of the orifice<br><br>
                            <b>Invrt</b> - elevation of hte invert of the orifice<br><br>
                            <b>OrifC</b> - effective discharge coefficient for orifice flow<br><br>
                            <b>WeirC</b> - coefficient for weir flow expressed in dimensionless
                            terms."""
            elif "." in rtext and rcode == "ORIFb":
                textback += """Table values (heading dependent):<br><br>
                            <b>AppTb</b> - id for the cross section fuction table for the approach
                            channel for the orifice.<br><br>
                            <b>OriTb</b> - id for the function table that gives the relative width
                            of the opening as a function of the relative height in the opening.<br><br>
                            <b>MxZup</b> - maximum elevation that will not be exceeded by the water
                            level upstream of the orifice.<br><br>
                            <b>MnHup</b> - minimum positive head to use at the orifice for computing
                            flows.<br><br>
                            <b>MxPFD</b> - maximum partial free drop that is less than 1.0<br><br>
                            <b>MnPFD</b> - minimum positive partial free drop.<br><br>
                            <b>LIPrc</b> - linear interpolation precision factor."""
            elif not rtext == "ORIFICE":
                textback += """Table headers:<br><font color=blue>%s</font>""" % rtext

        elif rcode == "AXLP":                                       #AXIALPMP
            textback = """<b>Axial-flow pump</b><br><br>"""
            if rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment:<br><font color=blue>%s</font>""" % rtext[1:]
            elif rtext.startsWith("QUNIT"):
                textback += """Conversion factor for design flows: <font color=blue>%s</font>
                            """ % rtext[6:]
            elif "." in rtext:
                textback += """Table values (heading dependent):<br><br>
                            <b>Net Pump Table</b> - table id<br>
                            <b>Number of Pumps</b> - # of parallel pumps operating simultaneously<br>
                            <b>Inlet Conduit Length</b> - length of inlet conduit<br>
                            <b>Inlet Conduit Table</b> - table id of the cross-section function table<br>
                            <b>Outlet Conduit Length</b> - length of outlet conduit<br>
                            <b>Outlet Conduit Table</b> - table id of the cross-section function table<br>
                            <b>Inlet Loss Factor</b> - decimal fraction of the velocity head in the inlet conduit<br>
                            <b>Pump Design Head</b> - design head for the pump at point of maximum efficiency<br>
                            <b>Pump Design Q</b> - design flow for the pump<br>
                            <b>Label</b> - description (up to 50 characters)"""
            elif rtext.startsWith("AXIALPMP"):
                textback += """"""
            elif rtext.startsWith("ZONE"):
                zone = rtext.split('ZONE=')[-1]
                textback +=  """<br><b>ZONE</b> - The zone designation for the horizontal grid: 
                            <font color=blue>%s</font>""" % re.split('\s+', zone)[0]
                if "HGRID" in rtext:
                    hgrid = rtext.split('HGRID=')[1]
                    textback += """<br><br><b>HGRID</b> - The name for the horizontal grid used for 
                                eastings and northings: <font color=blue>%s</font>""" % re.split('\s+', hgrid)[0]
                if "BASIS" in rtext:
                    basis = rtext.split('BASIS=')[1]
                    textback += """<br><br><b>BASIS</b> - The description of era, date, or other item to 
                                denote the data source: <font color=blue>%s</font>""" % re.split('\s+', basis)[0]
                if "VDATUM" in rtext:
                    vdatum = rtext.split('VDATUM=')[1]
                    textback += """<br><br><b>VDATUM</b> - The vertical datum: <font color=blue>%s</font>""" % re.split('\s+', vdatum)[0]
                if "UNITSYS" in rtext:
                    unitsys = rtext.split('UNITSYS=')[1]
                    textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('\s+', unitsys)[0]
            else:
                textback += """Table headers.<br><br> Note: The headers cover up to three lines"""

        elif rcode == "PMPL":                                       #PUMPLOSS
            textback = """<b>Losses for the inlet and outlet conduits of pumps</b><br><br>"""
            if rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment:<br><font color=blue>%s</font>""" % rtext[1:]
            elif rtext.startsWith("QUNIT"):
                textback += """Conversion factor for design flows: <font color=blue>%s</font>
                            """ % rtext[6:]
            elif "." in rtext:
                textback += """Table values (heading dependent):<br><br>
                            <b>Pump Loss Table</b> - table id<br>
                            <b>Number of Pumps</b> - # of parallel pumps operating simultaneously<br>
                            <b>Inlet Conduit Length</b> - length of inlet conduit<br>
                            <b>Inlet Conduit Table</b> - table id of the cross-section function table<br>
                            <b>Outlet Conduit Length</b> - length of outlet conduit<br>
                            <b>Outlet Conduit Table</b> - table id of the cross-section function table<br>
                            <b>Inlet Loss Factor</b> - decimal fraction of the velocity head in the inlet conduit<br>
                            <b>Max Pump Flow</b> - maximum flow expected through one pump<br>
                            <b>Label</b> - description (up to 50 characters)"""
            elif rtext.startsWith("PUMPLOSS"):
                textback += """"""
            elif rtext.startsWith("ZONE"):
                zone = rtext.split('ZONE=')[-1]
                textback +=  """<br><b>ZONE</b> - The zone designation for the horizontal grid: 
                            <font color=blue>%s</font>""" % re.split('\s+', zone)[0]
                if "HGRID" in rtext:
                    hgrid = rtext.split('HGRID=')[1]
                    textback += """<br><br><b>HGRID</b> - The name for the horizontal grid used for 
                                eastings and northings: <font color=blue>%s</font>""" % re.split('\s+', hgrid)[0]
                if "BASIS" in rtext:
                    basis = rtext.split('BASIS=')[1]
                    textback += """<br><br><b>BASIS</b> - The description of era, date, or other item to 
                                denote the data source: <font color=blue>%s</font>""" % re.split('\s+', basis)[0]
                if "VDATUM" in rtext:
                    vdatum = rtext.split('VDATUM=')[1]
                    textback += """<br><br><b>VDATUM</b> - The vertical datum: <font color=blue>%s</font>""" % re.split('\s+', vdatum)[0]
                if "UNITSYS" in rtext:
                    unitsys = rtext.split('UNITSYS=')[1]
                    textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('\s+', unitsys)[0]
            else:
                textback += """Table headers.<br><br> Note: The headers cover up to three lines"""

        elif rcode == "SETS":                                       #SETSLOT
            textback = """<b>Bottom slot parameters</b><br><br>"""
            if rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment:<font color=blue>%s</font>""" % rtext[1:]
            elif rtext.startsWith("WSLOT"):
                textback += """<b>WSLOT</b> - Top width of the slot: <font color=blue>%s</font>""" % rtext[6:]
            elif rtext.startsWith("NSLOT"):
                textback += """<b>NSLOT</b> - Manning's n for the slot: <font color=blue>%s</font>""" % rtext[6:]
            elif rtext.startsWith("ESLOT"):
                textback += """<b>ESLOT</b> - Elevation of the bottom of the slot: <font color=blue>%s</font>
                            """ % rtext[6:]
            elif rtext.startsWith("YSLOT"):
                textback += """<b>YSLOT</b> - Distance from the section invert to the slot invert: <font color=blue>
                            %s</font>""" % rtext[6:]

        elif rcode == "LPRF":                                       #LPRFIT
            textback = """<b>Level-pool reservoir</b><br>
                        Estimates surface area when only storage capacity is known.<br><br>"""
            if rtext.startsWith(";") or rtext.startsWith("*"):
                textback += """Comment:<br><font color=blue>%s</font>""" % rtext[1:]
            elif rtext.startsWith("TABID"):
                rtext = rtext.split('TABID=')[-1]
                textback += """<b>TABID</b> - Table ID: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("TABLE"):
                rtext = rtext.split('TABLE=')[-1]
                textback += """<b>TABLE</b> - Table ID: <font color=blue>%s</font>""" % rtext
            elif rtext.startsWith("ZONE"):
                zone = rtext.split('ZONE=')[-1]
                textback +=  """<br><b>ZONE</b> - The zone designation for the horizontal grid: 
                            <font color=blue>%s</font>""" % re.split('\s+', zone)[0]
                if "HGRID" in rtext:
                    hgrid = rtext.split('HGRID=')[1]
                    textback += """<br><br><b>HGRID</b> - The name for the horizontal grid used for 
                                eastings and northings: <font color=blue>%s</font>""" % re.split('\s+', hgrid)[0]
                if "BASIS" in rtext:
                    basis = rtext.split('BASIS=')[1]
                    textback += """<br><br><b>BASIS</b> - The description of era, date, or other item to 
                                denote the data source: <font color=blue>%s</font>""" % re.split('\s+', basis)[0]
                if "VDATUM" in rtext:
                    vdatum = rtext.split('VDATUM=')[1]
                    textback += """<br><br><b>VDATUM</b> - The vertical datum: <font color=blue>%s</font>""" % re.split('\s+', vdatum)[0]
                if "UNITSYS" in rtext:
                    unitsys = rtext.split('UNITSYS=')[1]
                    textback += """<br><br><b>UNITSYS</b> - The unit system: <font color=blue>%s</font>""" % re.split('\s+', unitsys)[0]
            elif rtext.startsWith("EASTING"):
                    a = 8
                    while not rtext[a:a+1] == "N":
                        a += 1
                        if a > len(rtext):
                            break
                    textback += """<b>EASTING</b> - The easting or x value for the coordinate system: <font color=blue>%s</font><br><br>
                                <b>NORTHING</b> - The northing or y value for the coordinate system: 
                                <font color=blue>%s</font>""" % (rtext[8:a], rtext[a+9:])
            elif rtext.startsWith("FIT_WITH"):
                textback += """<b>FIT_WITH</b> - Fitting option: <font color=blue>%s</font>""" % rtext[10:]
            elif rtext.startsWith("CHK_OPTION"):
                textback += """<b>CHK_OPTION</b> - Result-check option: <font color=blue>%s</font>""" % rtext[12:]
            elif rtext.startsWith("LEFT_SLOPE"):
                textback += """<b>LEFT_SLOPE</b> - Initial area: <font color=blue>%s</font>""" % rtext[11:]
            elif rtext.startsWith("RIGHT_SLOPE"):
                textback += """<b>RIGHT_SLOPE</b> - Maximum elevation end area: <font color=blue>%s</font>""" % rtext[13:]
            elif rtext.startsWith("INFAC"):
                textback += """<b>INFAC</b> - Conversion factor: <font color=blue>%s</font>""" % rtext[7:].split("'")[0]
            elif rtext.startsWith("OUTFAC"):
                textback += """<b>OUTFAC</b> - External unit conversion factor: <font color=blue>%s</font>""" % rtext[8:].split("'")[0]
            elif rtext.startsWith("ARGFAC"):
                textback += """<b>ARGFAC</b> - Argument sequence conversion factor: <font color=blue>%s</font>""" % rtext[7:]
            elif "." in rtext:
                textback += """Argument and function values (Heading dependent)"""
            else:
                textback += """Table headers: <font color=blue>%s</font>""" % rtext
                
            
                
    
        elif rcode == "blank":
            textback = "blank line"

        elif rcode == "FIN":                                        #Finish
            textback = """End of file."""
        else:
            textback = "Cannot interpret."

        return textback
