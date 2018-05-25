from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import os

start = "0000"


def convert(var):
    while len(var) < 4:
        var = "0" + var
    return var


for i in range(1, 3622):
    var = str(i)
    var = convert(var)
    file_name = "a" + var + ".pdf"
    fp = open(file_name, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser)
    fp.close()
    metadata = doc.info  # The "Info" metadata
    print(metadata)
    metadata = metadata[0]
    for x in metadata:
        if x == "Title":
            new_name = metadata[x] + ".pdf"
            os.rename(file_name, new_name)
