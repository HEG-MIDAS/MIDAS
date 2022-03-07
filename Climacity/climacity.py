import requests
import time
import re
import os
from merge_csv_by_date_package import merge_csv_by_date

def add_logs():
    with open("log.txt", "a") as file:
        file.write(time.strftime("%Y-%m-%d %H:%M:%S"))


def download_data(url):
    #start_time = time.time()
    r = requests.get(url)
    #print(time.time()-start_time)
    if r.ok:
        return r
    else:
        add_logs()


def decode_request(r):
    data_lines = []
    for line in r.iter_lines():
        data_lines.append(line.decode())
    
    print(data_lines)



def extract_relevant_data(r):
    header_beggining = False
    data_beggining = False
    dict_header = {}
    for line in r.iter_lines():
        if data_beggining:
            infos_line = line.decode().split(',')
            if infos_line[1] != '':
                print(line.decode())
        elif header_beggining:
            data_beggining = True
            infos_line = line.decode().split(',')
            for i,info in enumerate(infos_line):
                dict_header[info] = i
            print(dict_header)
        elif re.match("^-+-$", line.decode()):
            header_beggining = True


def process_data(data):
    pass


def write_request_in_tmp_file(r, path):
    f = open('{}/tmp_data_request.csv'.format(path), 'a')
    for line in r.iter_lines():
        f.write(line.decode())
    f.close()


def write_data_in_folder(data):
    pass


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

today = time.strftime("%Y-%m-%d %H:%M:%S")

start_date = "2021-01-18"
end_date = "2021-01-18"

url = """http://www.climacity.org/Axis/a_data_export.gwt?fdate={}&tdate={}&h_loc=on&
    h_Tsv=on&h_Gh_Avg=on&h_Dh_Avg=on&h_Tamb_Avg=on&h_HRamb_Avg=on&h_Prec_Tot=on&h_Vv_Avg=on&h_Vv_Avg=on&
    h_Vv_Max=on&h_Dv_Avg=on&h_Baro=on&h_CS125_Vis=on&chB_PM25=on&h_PM10=on&h_Hc=on&h_Az=on""".format(today, today)

#merge_csv_by_date.my_function()
data = write_request_in_tmp_file(download_data(url), __location__)