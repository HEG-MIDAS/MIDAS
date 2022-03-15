from ctypes import Array
import requests
import time
import datetime
import re
import os
import numpy as np
from merge_csv_by_date_package import merge_csv_by_date


def add_logs() -> None:
    with open("log.txt", "a") as file:
        file.write(time.strftime("%Y-%m-%d %H:%M:%S"))


def download_data(url: str) -> requests.Request:
    #start_time = time.time()
    r = requests.get(url)
    #print(time.time()-start_time)
    if r.ok:
        return r
    else:
        add_logs()


def decode_request(r: requests.Request) -> None:
    data_lines = []
    for line in r.iter_lines():
        data_lines.append(line.decode())
    
    print(data_lines)



def extract_relevant_data(r: requests.Request) -> Array:
    header_beggining = False
    data_beggining = False
    array_data = []
    dict_header = {}
    for line in r.iter_lines():
        if data_beggining:
            infos_line = line.decode().split(',')
            if infos_line[1] != '':
                array_data.append(line.decode())
        elif header_beggining:
            data_beggining = True
            infos_line = line.decode().split(',')
            array_data.append(infos_line)
        elif re.match("^-+-$", line.decode()):
            header_beggining = True

    return array_data


def process_data(array_data: Array) -> Array:
    array_processed_data = []
    array_processed_data.append(array_data[0])
    array_hour_data = []
    hour_working = datetime.datetime.now()
    hour_working_until = datetime.datetime.now()
    time_set = False
    for i in range(1, len(array_data)):
        line_data = array_data[i].split(',')
        if merge_csv_by_date.string_to_date(line_data[0]) >= hour_working_until:
            casted_data = np.array([[float(k) if k != '' else np.nan for k in j[2:]] for j in array_hour_data])
            array_mean_full = [str(hour_working), str(hour_working_until)]
            array_processed_data.append(array_mean_full + ([str(j) if j != np.nan else '' for j in np.nanmean(casted_data, axis=0)]))
            array_hour_data = []
            time_set = False

        if not time_set:
            hour_working = merge_csv_by_date.string_to_date(line_data[0])
            hour_working_until = (hour_working+datetime.timedelta(hours=1)).replace(microsecond=0, second=0, minute=0)
            time_set = True
        array_hour_data.append(line_data)
        
    return array_processed_data


def write_array_in_tmp_file(array_data: Array, path_tmp_file: str) -> None:
    f = open(path_tmp_file, 'w')
    for line in array_data:
        f.write("{}\n".format(','.join(line)))
    f.close()


def write_request_in_tmp_file(r: requests.Request, path_tmp_file: str) -> None:
    f = open(path_tmp_file, 'w')
    for line in r.iter_lines():
        f.write("{}\n".format(line.decode()))
    f.close()



__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
path_tmp_file = '{}/tmp_data_request.csv'.format(__location__)
path_original_data_file = '{}/../media/original/Climacity/climacity_original_merged.csv'.format(__location__)
path_transformed_data_file = '{}/../media/transformed/Climacity/climacity_transformed_merged.csv'.format(__location__)

start_date = "2021-02-18"
end_date = "2021-02-18"

url = """http://www.climacity.org/Axis/a_data_export.gwt?fdate={}&tdate={}&h_loc=on&
    h_Tsv=on&h_Gh_Avg=on&h_Dh_Avg=on&h_Tamb_Avg=on&h_HRamb_Avg=on&h_Prec_Tot=on&h_Vv_Avg=on&h_Vv_Avg=on&
    h_Vv_Max=on&h_Dv_Avg=on&h_Baro=on&h_CS125_Vis=on&chB_PM25=on&h_PM10=on&h_Hc=on&h_Az=on""".format(start_date, end_date)

today = time.strftime("%Y-%m-%d %H:%M:%S")

print("--------------- Requesting data Climacity : {} ---------------".format(today))

# Request data to download
r = download_data(url)
start_time = time.time()
# Create a temporary file containing the data requested to climacity (original data)
write_request_in_tmp_file(r, path_tmp_file)
# Merge temporary file with the file containing all the original data
print("--------------- Merging new data --------------")
merge_csv_by_date.merge_csv_by_date(path_original_data_file, path_tmp_file)
# Remove the temporary file created
os.remove(path_tmp_file)

print("-------------- Processing data --------------")

array_data = extract_relevant_data(r)
array_data = process_data(array_data)
write_array_in_tmp_file(array_data, path_tmp_file)

print("-------------- Merging processed data --------------")
merge_csv_by_date.merge_csv_by_date(path_transformed_data_file, path_tmp_file)
os.remove(path_tmp_file)
print(time.time()-start_time)

print("--------------- Requesting data Climacity ended : {} ---------------".format(today))
