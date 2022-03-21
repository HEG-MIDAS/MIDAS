from ctypes import Array
import requests
import time
import datetime
import re
import os
import getopt
import sys
import numpy as np
from merge_csv_by_date_package import merge_csv_by_date


def add_logs() -> None:
    """Add a log line to a log file in the directory. The log line is only composed of the date

    """
    with open("log.txt", "a") as file:
        file.write(time.strftime("%Y-%m-%d %H:%M:%S"))


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
    array_processed_data.append(array_data[0])
    array_hour_data = []
    hour_working = datetime.datetime.now()
    hour_working_until = datetime.datetime.now()
    time_set = False
    for i in range(1, len(array_data)):
        line_data = array_data[i].split(',')
        # Check if the line of data is still in the same range of hour or that the data ended
        if datetime.datetime.strptime(line_data[0], '%Y-%m-%d %H:%M:%S') >= hour_working_until or i >= len(array_data)-1:
            # Ignore the firsts two values (that are dates) and cast the other ones into floats
            # when possible, if not into np.nan
            casted_data = np.array([[float(k) if k != '' else np.nan for k in j[2:]] for j in array_hour_data])
            # Create a new array with mean values that starts by the hour GMT and the hour GMT+1 of the mean over the values
            array_mean_full = [str(hour_working), str(hour_working_until)]
            # Do the mean over all the columns of the data casted before, if there is no value for a column
            # an empty string is added
            array_processed_data.append(array_mean_full + ([str(j) if j != np.nan else '' for j in np.nanmean(casted_data, axis=0)]))
            array_hour_data = []
            time_set = False

        # Beginning of a new hour range
        if not time_set:
            # Date with hour of the start of the new hour range
            hour_working = datetime.datetime.strptime(line_data[0], '%Y-%m-%d %H:%M:%S')
            # End of the new hour range
            hour_working_until = (hour_working+datetime.timedelta(hours=1)).replace(microsecond=0, second=0, minute=0)
            time_set = True
        array_hour_data.append(line_data)
        
    return array_processed_data


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
        exit(1)

    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    path_tmp_file = '{}/tmp_data_request.csv'.format(__location__)
    path_original_data_file = '{}/../media/original/Climacity/climacity_original_merged.csv'.format(__location__)
    path_transformed_data_file = '{}/../media/transformed/Climacity/climacity_transformed_merged.csv'.format(__location__)

    url = """http://www.climacity.org/Axis/a_data_export.gwt?fdate={}&tdate={}&h_loc=on&
        h_Tsv=on&h_Gh_Avg=on&h_Dh_Avg=on&h_Tamb_Avg=on&h_HRamb_Avg=on&h_Prec_Tot=on&h_Vv_Avg=on&h_Vv_Avg=on&
        h_Vv_Max=on&h_Dv_Avg=on&h_Baro=on&h_CS125_Vis=on&chB_PM25=on&h_PM10=on&h_Hc=on&h_Az=on""".format(start_date, end_date)

    today = time.strftime("%Y-%m-%d %H:%M:%S")

    print("--------------- Requesting data Climacity : {} ---------------".format(today))

    # Request data to download
    #start_time = time.time()
    r = requests.get(url)
    #print(time.time()-start_time)
    if r.ok:
        start_time = time.time()
        # Create a temporary file containing the data requested to climacity (original data)
        write_request_in_tmp_file(r, path_tmp_file)
        # Merge temporary file with the file containing all the original data
        print("--------------- Merging new data --------------")
        merge_csv_by_date.merge_csv_by_date(path_original_data_file, path_tmp_file, '%Y-%m-%d %H:%M:%S')
        # Remove the temporary file created
        os.remove(path_tmp_file)

        print("--------------- Processing data ---------------")

        array_data = extract_relevant_data(r)
        array_data = process_data(array_data)
        write_array_in_tmp_file(array_data, path_tmp_file)

        print("--------------- Merging processed data ---------------")
        merge_csv_by_date.merge_csv_by_date(path_transformed_data_file, path_tmp_file, '%Y-%m-%d %H:%M:%S')
        os.remove(path_tmp_file)
        print(time.time()-start_time)

    else:
        print("--------------- Error at request adding logs --------------")
        add_logs()

    print("--------------- Requesting data Climacity ended : {} ---------------".format(today))


if __name__ == '__main__':
    main()
