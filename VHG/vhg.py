import time
from hashlib import sha256
import requests
import json
import datetime
import time
import getopt
import sys
import os
# DO NOT FORGET TO CREATE env.py FILE WITH
# env_username = with username
# env_encrypted_password = with encrypted password
from env import *

server = "vhg.ch"
page = "/io/web_service_json.php"

dossier_id = 50955

username = env_username
encrypted_password = env_encrypted_password

url = "https://"+server+":"+str(443)+page

media = {
    "TMP": 3, # Temperature. Usually expressed in Celsius degrees [°C]
    "HLM": 6, # Filling level. Usually expressed in [m] or in relative value [0:100%]
    "PLU": 7, # Pluviometry (rain). Usually expressed in [mm]
    "DEB": 16, # Flow. Instantaneous value usually expressed in [liter/sec] or [m3/h]
}

stations_DEB_HLM = ["AM_", "AV_", "BS_", "BU_", "CP_", "CS_", "GC_", "GO_", "HE_", "LM_", "XPA_", "PG_", "PR_", "VI_", "VX_"]
measures_DEB_HLM = ["DEB", "HLM"]
stations_PLU = ["AR_", "BA_", "CE_", "CR_", "DD_", "ER_", "ES_", "FO_", "GF_", "LA_", "LC_", "SA_"]
measures_PLU = ["PLU"]

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

path_tmp = '{}/'.format(__location__)
tmp_filename = 'tmp_data_request.csv'
path_original_data = '{}/../media/original/Climacity/Prairie/'.format(__location__)
original_data_filename = 'climacity_original_merged.csv'

path_transformed_data = '{}/../media/transformed/Climacity/Prairie/'.format(__location__)
transformed_data_filename = 'Prairie.csv'


def request_data(starting_date:str, ending_date:str, metering_code: str, measure: str) -> list:
    challenge_txt = str(int(time.time()))
    challenge_password = sha256((encrypted_password+challenge_txt).encode('utf-8')).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "user_agent": "tetraedre/TDS",
        "method": "POST",
    }
    # data = {
    #     "operation": "check_access",
    #     "username": username,
    #     "challenge": challenge_txt,
    #     "dossier_id": dossier_id,
    #     "challenge_password": challenge_password
    # }

    data = {
        "operation": "get_values",
        "username": username,
        "challenge": challenge_txt,
        "dossier_id": dossier_id,
        "challenge_password": challenge_password,
        "metering_code": metering_code,
        "t0": time.mktime(datetime.datetime.strptime(starting_date, "%Y-%m-%d").timetuple()),
        "t1": time.mktime(datetime.datetime.strptime(ending_date, "%Y-%m-%d").timetuple()),
        "limit": 0,
        "sort": "ASC",
        "media": media[measure],
    }

    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    # print("------------------------Response------------------------")
    # print(str(r)+"\n"+str(r.headers)+"\n"+str(r.content))
    # print(data)
    return r.content.decode('utf-8')


def create_original_tmp_file(data:dict, tmp_filename:str, path_original_data:str, measures:list) -> None:
    measures_str = ""
    first = True
    for e in measures:
        if first:
            measures_str += e
            first = False
        else:
            measures_str += ","+e
    f = open(path_original_data+tmp_filename, "w")
    f.write("localtime,"+measures_str)
    f.close()


def manage_data(data: dict, metering_code: str, measures: list) -> None:
    """
    Will handle the data requested to VHG. It will first create an tmp file with the original data, in the corresponding folder, if the folder does not exists,
    it will automatically create the folder. Then it will merge the tmp original data file with the orginal data file. And repeat the same steps for the transformed datas
    transforming obviously the data if needed.
    """
    tmp_filename = 'tmp_data_request_{}.csv'.format(metering_code)
    # Check if dir already exists if it's not the case, create new dir
    if(not os.path.isdir("{}/../media/original/VHG/{}".format(__location__, metering_code[:-1]))):
        os.mkdir("{}/../media/original/VHG/{}".format(__location__, metering_code[:-1]))
    path_original_data = '{}/../media/original/VHG/{}/'.format(__location__, metering_code[:-1])
    original_data_filename = '{}_original_merged.csv'.format(metering_code)

    create_original_tmp_file(data, tmp_filename, path_original_data, measures)




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

    today = time.strftime("%Y-%m-%d %H:%M:%S")

    print("--------------- Starting requests to VHG : {} ---------------".format(today))

    while start_date <= end_date:
        year_working_on = str(datetime.datetime.strptime(start_date, '%Y-%m-%d').year)
        tmp_end_date = year_working_on + "-12-31"
        if tmp_end_date > end_date:
            tmp_end_date = end_date

        # Iterate over each metering code available for DEB and HLM
        for metering_code in stations_DEB_HLM:
            data = {}
            # Iterate alternately on DEB and HLM and create a dict with the results
            for measure in measures_DEB_HLM:
                data[measure] = request_data(start_date, end_date, metering_code, measure)
            manage_data(data, metering_code, measures_DEB_HLM)


        start_date = datetime.datetime.strftime(datetime.datetime.strptime(tmp_end_date, '%Y-%m-%d') + datetime.timedelta(days=1), '%Y-%m-%d')

    print("--------------- Ending requests to VHG : {} ---------------".format(time.strftime("%Y-%m-%d %H:%M:%S")))


if __name__ == '__main__':
    main()
