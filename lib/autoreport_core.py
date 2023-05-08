import os, sys, time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *

# Autoreport library imports
from openpyxl import load_workbook
from docxtpl import DocxTemplate , InlineImage, RichText
from docx.shared import Mm

class Autoreport(QtCore.QThread):
    _progressBar = pyqtSignal(int)

    def __init__(self) -> None:
        super(Autoreport, self).__init__()
        self.timestemp      = None
        self.excel_path     = None
        self.Image_path     = None
        self.template_path  = None
        self.output_path    = None

        self.context = {}
    
    def EXCEL2WORD(self, sheetname):
        if self.excel_path != None :
            wb_data = load_workbook(self.excel_path, data_only=True)
            sheet_data = wb_data[sheetname]
            wb_data.close()
            self._progressBar.emit(70)
            for Tag in self.doc.get_undeclared_template_variables():
                if Tag.split('_')[0] == "CL":
                    self.context.setdefault(Tag ,sheet_data[Tag.split('_')[-1]].internal_value)
            self._progressBar.emit(80)
            self.doc.render(self.context)
            self.doc.save("%s/%s.docx" %(self.output_path, self.timestemp))
            self._progressBar.emit(100)

    def IMG2WORD(self):
        self._progressBar.emit(10)
        for index_dir, (dirPath, dirNames, fileNames) in enumerate(os.walk(self.Image_path)):
            for Tag in self.doc.get_undeclared_template_variables():
                if Tag.split('_')[0] == "image":
                    for index, f in enumerate(fileNames):
                        if f.split('_')[0] == Tag.split('_')[-1]:
                            self.context.setdefault(Tag, InlineImage(self.doc, os.path.join(dirPath, f),width=Mm(int(80))))
        self._progressBar.emit(50)
    def run(self):
        self._progressBar.emit(0)
        self.context = {}
        self.doc = DocxTemplate(self.template_path)
        self.IMG2WORD()
        self.EXCEL2WORD("Testing")
        
