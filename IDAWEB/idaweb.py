import os
import re
import sys
import getopt
import numpy as np
import PyPDF2
import datetime
import shutil
import copy
from zipfile import ZipFile


def main(argv):
    """Main function of the script

    Parameters
    ----------
    argv : dict
        Parsed set of arguments passed when script called
    """
    print(f"Starting {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    exit_code = 0
    try:
      opts, args = getopt.getopt(argv,"ihs")
    except getopt.GetoptError:
      print('idaweb.py -i|-s')
      sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            print('idaweb.py -i|')
            sys.exit(1)

        elif opt == '-i':
            print("Creating Inventory")
            createInventoryCSV()
            sys.exit(0)

    print("Manipulating Order(s)")
    exit_code = orderManipulation()
    print(f"Done {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main(sys.argv[1:])
