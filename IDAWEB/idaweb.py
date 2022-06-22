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

## Path of Scraper
scraper_path = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
## Path for temporatry unzipped files
temp_path = os.path.join(scraper_path,'temp')
## Root of Project
root_path = os.path.join(scraper_path,'..')
## Path of Media
original_media_path = os.path.join(root_path,'media/original/IDAWEB')
transformed_media_path = os.path.join(root_path,'media/transformed/IDAWEB')

def sortFileListByStation(list):
    new_array = []
    stations = []
    for elem in list:
        name = elem.split("_")[2]
        if name not in stations:
            stations.append(name)
            new_array.append([])
        new_array[stations.index(name)].append(elem)
        new_array[stations.index(name)].sort()
    new_array.sort()
    return new_array

def station_sanitizer(station:str) -> str:
    """Sanitize the station string
    """
    return station.replace(' /',',').replace(' / ',',').replace('/',',')

def orderManipulation():
    # Delete old temporary folder if still exists
    if os.path.isdir(temp_path):
        shutil.rmtree(temp_path)

    # Search for all order zip file in the folder and extract them to the temp folder
    order_files = list(filter(lambda f: f.startswith('order') and f.endswith('.zip'),os.listdir(scraper_path)))
    for order_file in order_files:
        with ZipFile(os.path.join(scraper_path,order_file), 'r') as zipObj:
           zipObj.extractall(temp_path)


    # Order Files loading
    order_data_files = list(filter(lambda f: f.startswith('order_') and f.endswith('data.txt'),os.listdir(temp_path)))
    order_legend_files = list(filter(lambda f: f.startswith('order_') and f.endswith('legend.txt'),os.listdir(temp_path)))
    order_data_files = sortFileListByStation(order_data_files)
    order_legend_files = sortFileListByStation(order_legend_files)

    station_abbr = {}
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Retrieving station abbreviation to full name")
    for file in order_legend_files:
        station_name = file[0].split('_')[2]
        if station_name not in station_abbr:
            for line in open(os.path.join(temp_path,file[0]),'rb'):
                line = line.decode('Windows-1252').strip()
                if line.startswith(station_name):
                    station_abbr[station_name] = station_sanitizer(re.split(r'\s+',line)[1])

    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Manipulating Data Files")
    for station_file in order_data_files:
        dataset = {}
        for file in station_file:
            name = file.split('_')[2]
            param = file.split('_')[3]
            open_file = open(os.path.join(temp_path,file),'r')
            data_10_minutes = []
            for line in open_file:
                measures = line.strip()
                if measures != "":
                    if measures.startswith("stn") == False:
                        measures = measures.split(';')[1:]
                        try:
                            o_timestamp = datetime.datetime.strptime(measures[0],'%Y%m%d')
                            for i in range(0,24):
                                timestamp = o_timestamp + datetime.timedelta(hours=i)
                                timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                                if timestamp not in dataset:
                                    dataset[timestamp] = []

                                dataset[timestamp].append((param,measures[1]))
                        except Exception:
                            try:
                                timestamp = datetime.datetime.strptime(measures[0],'%Y%m%d%H')
                                timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                                if timestamp not in dataset:
                                    dataset[timestamp] = []

                                dataset[timestamp] = (param,measures[1])
                            except Exception:
                                try:
                                    timestamp = datetime.datetime.strptime(measures[0],'%Y%m%d%H%M')
                                    if(timestamp.minute==0):
                                        average = ""
                                        if len(data_10_minutes) > 0:
                                            average = np.average(data_10_minutes)
                                        timestamp = timestamp - datetime.timedelta(hours=1)
                                        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                                        if timestamp not in dataset:
                                            dataset[timestamp] = []

                                        dataset[timestamp] = (param,average)
                                        if measures[1] != '-' and measures[1] != '':
                                            data_10_minutes = [float(measures[1])]
                                    else:
                                        if measures[1] != '-' and measures[1] != '':
                                            data_10_minutes.append(float(measures[1]))
                                except Exception:
                                    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {file} - \033[91mNo Matching Timestamp Found\033[0m')
                                    break
            open_file.close()
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Dataset created for {name}")
        # Write to temp file
        # merge temp file with final one if exists or write it
def main(argv):
    """Main function of the script

    Parameters
    ----------
    argv : dict
        Parsed set of arguments passed when script called
    """
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting...")
    exit_code = 0
    try:
      opts, args = getopt.getopt(argv,"h")
    except getopt.GetoptError:
      print('idaweb.py')
      sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            print('idaweb.py')
            sys.exit(1)

    exit_code = orderManipulation()
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Done!")
    sys.exit(exit_code)

if __name__ == "__main__":
    main(sys.argv[1:])
