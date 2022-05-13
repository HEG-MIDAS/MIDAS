#!/usr/bin/env python
#title           :climacity.py
#description     :Request data to climacity and update existing data on server or add a log if cannot download data
#author          :David Nogueiras Blanco & Amir Alwash
#date            :04 May 2022
#version         :0.1.0
#usage           :python3 climacity.py -h
#notes           :none
#python_version  :3.9.2

from ctypes import Array
from urllib import request, response
import requests
import time
import datetime
from dateutil.relativedelta import relativedelta
import re
import os
import getopt
import sys
import numpy as np
from merge_csv_by_date_package import merge_csv_by_date
from pathlib import Path
import shutil


def add_logs(start_date: datetime.datetime, end_date: datetime.datetime, __location__: str) -> None:
    """Add a log line to a log file in the directory. The log line is only composed of the date

    """
    with open("{}/../logs/Climacity.txt".format(__location__), "a") as file:
        file.write("-s {} -e {}\n".format(start_date, end_date))


def extract_relevant_data(r: requests.Request) -> Array:
    """Extract relevant data from the result of the request. More or less, it will skip the comments on top of the csv file
    and only take into count the header and the data

    Parameters
    ----------
    r : requests.Request
        result of the request previously done
    
    Returns
    -------
    Array
        an array containing all the relevant data that has been extracted from the lines of the requested data
    """
    header_beggining = False
    data_beggining = False
    array_data = []
    for line in r.iter_lines():
        # Get the data
        if data_beggining:
            infos_line = line.decode().split(',')
            if infos_line[1] != '':
                array_data.append(line.decode())
        # Get the data of the header
        elif header_beggining:
            data_beggining = True
            infos_line = line.decode().split(',')
            array_data.append(infos_line)
        # Find line of separation composed of "-" between comments and data with header
        elif re.match("^-+-$", line.decode()):
            header_beggining = True

    return array_data


def process_data(array_data: Array) -> Array:
    """Process the data passed in argument by doing a mean for every hour

    Parameters
    ----------
    array_data : Array
        data to be processed with the header as first element of the array
    
    Returns
    -------
    Array
        an array containing all the relevant data that has been extracted from the lines of the requested data
    """
    array_processed_data = []
    index_to_find_max = array_data[0][2:].index("Vv_Max")
    header_to_edit = {
        'PM25': 'PM2.5',
        'CS125_Vis': 'Dvis_Avg',
        'Baro': 'Pa_Avg',
    }
    array_processed_data.append([header_to_edit[h]+'*' if h in header_to_edit.keys() else h+'*' for h in array_data[0]])
    array_hour_data = []
    hour_working = datetime.datetime.now()
    hour_working_until = datetime.datetime.now()
    time_set = False
    # Winter hour gap
    hour_gap = 1
    for i in range(1, len(array_data)):
        line_data = array_data[i].split(',')
        # Check if the line of data is still in the same range of hour or that the data ended
        if datetime.datetime.strptime(line_data[0], '%Y-%m-%d %H:%M:%S') >= hour_working_until or i >= len(array_data)-1:
            #print(i >= len(array_data)-1)
            # Ignore the firsts two values (that are dates) and cast the other ones into floats
            # when possible, if not into np.nan
            casted_data = np.array([[float(k) if k != '' else np.nan for k in j[2:]] for j in array_hour_data])
            # Create a new array with mean values that starts by the hour GMT and the hour GMT+1 of the mean over the values
            array_mean_full = [str(hour_working), str(hour_working+datetime.timedelta(hours=hour_gap))]
            #print(hour_gap)
            #print(datetime.timedelta(hours=hour_gap))
            #print(hour_working+datetime.timedelta(hours=hour_gap))
            #print(array_mean_full)
            # Do the mean over all the columns of the data casted before, if there is no value for a column
            # an empty string is added
            data_mean = [str(j) if j != np.nan else '' for j in np.nanmean(casted_data, axis=0)]

            # Take the value max of the index that correspond to a header where the value max is used
            data_mean[index_to_find_max] = str(np.max(casted_data[:, index_to_find_max]))

            array_processed_data.append(array_mean_full + data_mean)
            array_hour_data = []
            time_set = False

        # Beginning of a new hour range
        if not time_set:
            # Date with hour of the start of the new hour range
            hour_working = datetime.datetime.strptime(line_data[0], '%Y-%m-%d %H:%M:%S')
            hour_gap = int((datetime.datetime.strptime(line_data[1], '%Y-%m-%d %H:%M:%S')-hour_working).seconds / 3600)
            # print((datetime.datetime.strptime(line_data[1], '%Y-%m-%d %H:%M:%S')-hour_working).seconds / 3600)
            # print(hour_gap)
            # print(hour_working)
            # End of the new hour range
            hour_working_until = (hour_working+datetime.timedelta(hours=1)).replace(microsecond=0, second=0, minute=0)
            #print(hour_working_until)
            time_set = True
        array_hour_data.append(line_data)
        
    return array_processed_data


def edit_original_header(path_original_data_file: str, path_tmp_file: str) -> None:
    header_original = ''
    with open(path_original_data_file, "r") as file:
        header_original = file.readline()

    header_original_splitted = header_original.split()

    header_tmp = ''
    with open(path_tmp_file, "r") as file:
        header_tmp = file.readline()

    header_tmp_splitted = header_tmp.split()

    if datetime.datetime.strptime(header_original_splitted[5],'%Y-%m-%d').date() > datetime.datetime.strptime(header_tmp_splitted[5],'%Y-%m-%d').date():
        header_original_splitted[5] = header_tmp_splitted[5]
        header_original_splitted[8] = header_tmp_splitted[8]
    if datetime.datetime.strptime(header_original_splitted[10],'%Y-%m-%d').date() < datetime.datetime.strptime(header_tmp_splitted[10],'%Y-%m-%d').date():
        header_original_splitted[10] = header_tmp_splitted[10]
        header_original_splitted[13] = header_tmp_splitted[13]

    header_to_write = ' '.join(header_original_splitted) + '\n'

    lines = []
    with open(path_original_data_file, "r") as file:
        for line in file:
            lines.append(line)

    lines[0] = header_to_write

    with open(path_original_data_file, "w") as file:
        for line in lines:
            file.write(line)


def write_array_in_tmp_file(array_data: Array, path_tmp_file: str) -> None:
    """Write the data contained in an array into a file which has a given path

    Parameters
    ----------
    array_data : Array
        data to be written in the file
    path_tmp_file : str
        path to the file where the data will be written
    """
    f = open(path_tmp_file, 'w')
    for line in array_data:
        f.write("{}\n".format(','.join(line)))
    f.close()


def write_request_in_tmp_file(r: requests.Request, path_tmp_file: str) -> None:
    """Write the data contained in the result of a request into a file which has a given path

    Parameters
    ----------
    r : request.Request
        result of the request to be written in the file
    path_tmp_file : str
        path to the file where the data will be written
    """
    f = open(path_tmp_file, 'w')
    for line in r.iter_lines():
        f.write("{}\n".format(line.decode()))
    f.close()


def main() -> None:
    
    # Deal with arguments
    # Get arguments
    argv = sys.argv[1:]

    start_date =  datetime.datetime.now().date()
    end_date = datetime.datetime.now().date()
    # Check arguments
    try:
      opts, _ = getopt.getopt(argv,"hs:e:",["start_date=","end_date="])
    except getopt.GetoptError:
      print('climacity.py -s <start_date> -e <end_date>')
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print('climacity.py -s <start_date> -e <end_date>')
         sys.exit()
      elif opt in ("-s", "--start_date"):
         start_date = datetime.datetime.strptime(arg,'%Y-%m-%d').date()
      elif opt in ("-e", "--end_date"):
         end_date = datetime.datetime.strptime(arg,'%Y-%m-%d').date()

    if(start_date > end_date):
        print('The end date is inferior to the start date !')
        sys.exit(1)

    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    path_tmp_file = '{}/tmp_data_request.csv'.format(__location__)
    path_original_data_file = '{}/../media/original/Climacity/climacity_original_merged.csv'.format(__location__)
    path_transformed_data_file = '{}/../media/transformed/Climacity/Prairie_Urbain.csv'.format(__location__)

    today = time.strftime("%Y-%m-%d %H:%M:%S")
    # Indicates the interval of years for a request
    gap_years = 1

    print("--------------- Starting requests to Climacity : {} ---------------".format(today))

    while start_date <= end_date:
        tmp_end_date = datetime.datetime.strftime(datetime.datetime.strptime(start_date, '%Y-%m-%d').date() + relativedelta(years=gap_years), '%Y-%m-%d')
        if tmp_end_date > end_date:
            tmp_end_date = end_date

        url = """http://www.climacity.org/Axis/a_data_export.gwt?fdate={}&tdate={}&h_loc=on&""" \
            """h_Tsv=on&h_Gh_Avg=on&h_Dh_Avg=on&h_Tamb_Avg=on&h_HRamb_Avg=on&h_Prec_Tot=on&h_Vv_Avg=on&h_Vv_Avg=on&""" \
            """h_Vv_Max=on&h_Dv_Avg=on&h_Baro=on&h_CS125_Vis=on&h_PM25=on&h_PM10=on&h_Hc=on&h_Az=on""".format(start_date, tmp_end_date)


        print("--------------- Requesting data Climacity : from {} to {} ---------------".format(start_date, tmp_end_date))

        # Request data to download
        #start_time = time.time()
        r = None
        try:
            r = requests.get(url)
        except:
            sys.exit(2)
        #print(time.time()-start_time)
        if r.ok:
            start_time = time.time()
            # Create a temporary file containing the data requested to climacity (original data)
            write_request_in_tmp_file(r, path_tmp_file)
            # Merge temporary file with the file containing all the original data
            print("--------------- Merging new data --------------")
            merge_csv_by_date.merge_csv_by_date(path_original_data_file, path_tmp_file, '%Y-%m-%d %H:%M:%S')
            if Path(path_original_data_file).is_file():
                edit_original_header(path_original_data_file, path_tmp_file)
            # Remove the temporary file created
            os.remove(path_tmp_file)

            print("--------------- Processing data ---------------")

            array_data = extract_relevant_data(r)
            array_data = process_data(array_data)
            write_array_in_tmp_file(array_data, path_tmp_file)

            print("--------------- Merging processed data ---------------")
            merge_csv_by_date.merge_csv_by_date(path_transformed_data_file, path_tmp_file, '%Y-%m-%d %H:%M:%S')
            os.remove(path_tmp_file)
            #print(time.time()-start_time)

        else:
            print("--------------- Error at request adding logs --------------")
            add_logs(start_date, tmp_end_date, __location__)
            sys.exit(3)

        print("--------------- Requesting data Climacity ended : {} ---------------".format(time.strftime("%Y-%m-%d %H:%M:%S")))

        start_date = tmp_end_date

        if start_date == end_date:
            break

    print("--------------- Ending requests to Climacity : {} ---------------".format(today))

if __name__ == '__main__':
    main()
