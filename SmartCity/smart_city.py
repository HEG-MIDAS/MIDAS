import requests
import time
from merge_package import merge 

def add_logs():
    with open("log.txt", "a") as file:
        file.write(time.strftime("%Y-%m-%d %H:%M:%S"))


def extract_data(url):
    start_time = time.time()
    r = requests.get(url)
    #print(r.content)
    print(time.time()-start_time)
    if r.ok:
        return r
    else:
        add_logs()


def process_data(data):
    pass


def write_data_in_folder(data):
    pass


today = time.strftime("%Y-%m-%d")

start_date = "2021-01-18"
end_date = "2021-01-18"

url = """http://www.climacity.org/Axis/a_data_export.gwt?fdate={}&tdate={}&h_loc=on&
    h_Tsv=on&h_Gh_Avg=on&h_Dh_Avg=on&h_Tamb_Avg=on&h_HRamb_Avg=on&h_Prec_Tot=on&h_Vv_Avg=on&h_Vv_Avg=on&
    h_Vv_Max=on&h_Dv_Avg=on&h_Baro=on&h_CS125_Vis=on&chB_PM25=on&h_PM10=on&h_Hc=on&h_Az=on""".format(today, today)

merge.my_function()
#extract_data(url)