import time
from hashlib import sha256
import requests
import json
import datetime
import time
import getopt
import sys
import os
import ast
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
    # print(r.content.decode('utf-8'))
    return r.content.decode('utf-8')

def format_data_original(data:dict, measures:str) -> list:
    array_data_formatted_original = []
    print("ICIIIII")
    for e in data:
        val = [e]
        for m in measures:
            if m in data[e].keys():
                val.append(data[e][m])
            else:
                val.append("")
        array_data_formatted_original.append(val)
    print(array_data_formatted_original)
    return array_data_formatted_original


def format_data_transformed(data:dict, measures:str) -> list:
    array_data_formatted = []
    for i,e in enumerate(data):
        val = [datetime.datetime.fromtimestamp(int(e)).strftime('%Y-%m-%d %H') + ":00:00"]
        for m in measures:
            if m in data[e].keys():
                val.append(data[e][m])
            else:
                val.append("")
        if array_data_formatted != []:
            previous_date = array_data_formatted[-1][0]
            while (datetime.datetime.strptime(val[0], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(previous_date, '%Y-%m-%d %H:%M:%S')) > datetime.timedelta(hours=1):
                previous_date = ((datetime.datetime.strptime(previous_date, '%Y-%m-%d %H:%M:%S'))+datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
                array_data_formatted.append([previous_date, '', ''])
        array_data_formatted.append(val)

    return array_data_formatted


def create_original_file(data:dict, tmp_filename:str, path_original_data:str, measures:list) -> None:
    measures_str = ""
    first = True
    for e in measures:
        if first:
            measures_str += e
            first = False
        else:
            measures_str += ","+e

    f = open(path_original_data+tmp_filename, "w")
    f.write("localtime,"+measures_str+"\n")
    # format_data_original(data, measures)

    data_formatted_original = format_data_original(data, measures)
    for line in data_formatted_original:
        # Make sure that the line is not empty
        if not line == []:
            f.write(','.join(line))
            f.write('\n')
    f.close()


def create_transformed_file(data:dict, tmp_filename:str, path_original_data:str, measures:list) -> None:
    measures_str = ""
    first = True
    for e in measures:
        if first:
            measures_str += e
            first = False
        else:
            measures_str += ","+e

    f = open(path_original_data+tmp_filename, "w")
    f.write("localtime,"+measures_str+"\n")
    format_data_original(data, measures)

    data_formatted_transformed = format_data_transformed(data, measures)
    for line in data_formatted_transformed:
        # Make sure that the line is not empty
        if not line == []:
            f.write(','.join(line))
            f.write('\n')
    f.close()


def manage_data(data: dict, metering_code: str, measures: list) -> None:
    """
    Will handle the data requested to VHG. It will first create an tmp file with the original data, in the corresponding folder, if the folder does not exists,
    it will automatically create the folder. Then it will merge the tmp original data file with the orginal data file. And repeat the same steps for the transformed datas
    transforming obviously the data if needed.
    """
    # Check if dir already exists if it's not the case, create new dir
    if(not os.path.isdir("{}/../media/original/VHG/{}".format(__location__, metering_code[:-1]))):
        os.mkdir("{}/../media/original/VHG/{}".format(__location__, metering_code[:-1]))
    path_original_data = '{}/../media/original/VHG/{}/'.format(__location__, metering_code[:-1])
    original_data_filename = '{}_original_merged.csv'.format(metering_code[:-1])

    create_original_file(data, original_data_filename, path_original_data, measures)

    # Check if dir already exists if it's not the case, create new dir
    if(not os.path.isdir("{}/../media/transformed/VHG/{}".format(__location__, metering_code[:-1]))):
        os.mkdir("{}/../media/transformed/VHG/{}".format(__location__, metering_code[:-1]))
    path_transformed_data = '{}/../media/transformed/VHG/{}/'.format(__location__, metering_code[:-1])
    transformed_data_filename = '{}_transformed_merged.csv'.format(metering_code[:-1])

    create_transformed_file(data, transformed_data_filename, path_transformed_data, measures)


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
                # data[measure] = request_data(start_date, end_date, metering_code, measure)
                val = ast.literal_eval(request_data(start_date, end_date, metering_code, measure))
                for e in val:
                    if e["timestamp"] not in data.keys():
                        data[e["timestamp"]] = {
                            measure: e["value"]
                        }
                    else:
                        data[e["timestamp"]][measure] = e["value"]
            if data != {}:
                manage_data(data, metering_code, measures_DEB_HLM)


        start_date = datetime.datetime.strftime(datetime.datetime.strptime(tmp_end_date, '%Y-%m-%d') + datetime.timedelta(days=1), '%Y-%m-%d')

    print("--------------- Ending requests to VHG : {} ---------------".format(time.strftime("%Y-%m-%d %H:%M:%S")))


if __name__ == '__main__':
    main()


# challenge_txt = str(int(time.time()))
# challenge_password = sha256((encrypted_password+challenge_txt).encode('utf-8')).hexdigest()

# headers = {
#     "Content-Type": "application/json",
#     "user_agent": "tetraedre/TDS",
#     "method": "POST",
# }
# data = {
#     "operation": "check_access",
#     "username": username,
#     "challenge": challenge_txt,
#     "dossier_id": dossier_id,
#     "challenge_password": challenge_password
# }


# r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
# print("------------------------Response------------------------")
# print(str(r)+"\n"+str(r.headers)+"\n"+str(r.content))
# print(data)
# print(r.content.decode('utf-8'))
