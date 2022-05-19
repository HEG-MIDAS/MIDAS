import os
import re
import sys
import getopt
import numpy as np
import PyPDF2
from merge_csv_by_date_package import merge_csv_by_date

## Path of Scraper
scraper_path = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

def createInventoryCSV():
    if os.path.exists(os.path.join(scraper_path,'inventory.pdf')) == False:
        print("The inventory pdf file doesn't exist. Please place it next to this script and name it 'inventory.pdf'")
        sys.exit(1)
    inputPDF = open(os.path.join(scraper_path,'inventory.pdf'), 'rb')
    outputCSV = open(os.path.join(scraper_path,'inventory.csv'), 'w+')
    pdfReader = PyPDF2.PdfFileReader(inputPDF)
    print(str(pdfReader.numPages)+' page(s) found !')
    for i in range(0,pdfReader.numPages):
        pageObj = pdfReader.getPage(i)
        extracted = pageObj.extractText()
        extracted_list = extracted.split('\n')
        for j in range(0,len(extracted_list)):
            ex = extracted_list[j].strip()
            if(j< len(extracted_list)-1):
                next_ex = extracted_list[j+1].strip()
            if(re.match('\d*/\d*',ex) is None and ex != "" and  ex != " " and ex != 'suivant'):
                s = ex
                if(re.match('^\d*$',ex) or ( re.match('^[a-z0-9]{8}$',ex) and re.match('^[a-z0-9]{8}$',next_ex) is None)or any(x in ex for x in ['Dix minutes','Heure','Jour','Mois','Année'])):
                    s = '\t'+ex+'\t'
                elif re.match('^[a-z0-9]{8}$',next_ex):
                    s = ' '+ex
                elif(re.match('^\d{2}.\d{2}.\d{4}-\d{2}.\d{2}.\d{4}$',ex)):
                    s = ex+'\n'

                outputCSV.write(s)
    outputCSV.close()
    inputPDF.close()

def main(argv):
    try:
      opts, args = getopt.getopt(argv,"ih")
    except getopt.GetoptError:
      print('scrap.py -s <start_date> -e <end_date>')
      sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            print('idaweb.py -i|')
            sys.exit(1)
        elif opt == '-i':
            createInventoryCSV()

if __name__ == "__main__":
    main(sys.argv[1:])
