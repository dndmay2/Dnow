from dnow.Spreadsheet.ReadSpreadsheet import ReadSpreadsheet


def readSpreadsheet():
    print('in here')
    ss = ReadSpreadsheet()
    ss.readStudents()
    ss.readHosts()
