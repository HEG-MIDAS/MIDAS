#!/usr/bin/env python3
import os
from datetime import date
from datetime import timedelta
import time

def main():
    today = date.today()
    yesterday = today - timedelta(days = 1)
    print("Climacity")
    os.system('python3 /app/Climacity/climacity.py -s {yesterday} -e {yesterday}'.format(yesterday=yesterday))
    time.sleep(1 * 60 * 30)
    print("SABRA")
    os.system('python3 /app/SABRA/sabra.py -s {yesterday} -e {yesterday}'.format(yesterday=yesterday))

if __name__ == '__main__':
    main()
