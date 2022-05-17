import os
import re
import sys
import getopt
import numpy as np
import tabula.io
from merge_csv_by_date_package import merge_csv_by_date

def main(argv):
    # Read a PDF File
    df = tabula.io.read_pdf("/home/amir/Git/MIDAS/IDAWEB/inventory.pdf", pages='all')[0]
    # convert PDF into CSV
    tabula.io.convert_into("/home/amir/Git/MIDAS/IDAWEB/inventory.pdf", "/home/amir/Git/MIDAS/IDAWEB/inventory.csv", output_format="csv", pages='all')
    print(df)


if __name__ == "__main__":
    main(sys.argv[1:])
