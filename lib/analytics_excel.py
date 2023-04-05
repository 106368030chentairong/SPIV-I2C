import openpyxl

class open_excel():
    def __init__(self):
        self.excel_path = None
        pass

    def read_sheet(self): 
        return openpyxl.load_workbook(self.excel_path, read_only=False).sheetnames

    def read_excel(self,filename, sheetname):
        try:
            wb = openpyxl.load_workbook(filename, read_only=False)
            ws = wb.worksheets[sheetname]
            return ws
        except Exception as e:
            print(e)
            return None
    
    def get_rowname(self,)