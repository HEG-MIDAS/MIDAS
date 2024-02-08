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
from merge_csv_by_date_package import merge_csv_by_date
import numpy as np

server = "vhg.ch"
page = "/io/web_service_json.php"

dossier_id = 50955

username = os.environ.get('env_username_VHG')
encrypted_password = os.environ.get('env_encrypted_password_VHG')

url = "https://"+server+":"+str(443)+page

media = {
    "TMP": 3, # Temperature. Usually expressed in Celsius degrees [°C]
    "HLM": 6, # Filling level. Usually expressed in [m] or in relative value [0:100%]
    "PLU": 7, # Pluviometry (rain). Usually expressed in [mm]
    "DEB": 16, # Flow. Instantaneous value usually expressed in [liter/sec] or [m3/h]
}

map_station_acronyme_name = {
    "AM_": "Le Foron à Ambilly",
    "AV_": "Le Nant d'Avril à Mon Désir",
    "BS_": "L'Aire à Bossenailles",
    "BU_": "Canal Le Brassu – Route Suisse",
    "CP_": "Le Chambet à Compois",
    "CS_": "L'Aire au Pont du Centenaire",
    "GC_": "La Drize à Grange-Collomb",
    "GO_": "Le Gobé à la route de Colovrex",
    "HE_": "L'Hermance à la Douane",
    "LM_": "La Seymaz au pont Ladame",
    "XPA_": "Le Canal de la Papeterie à Versoix",
    "PG_": "La Drize à Pierre-Grand",
    "PR_": "L'Aire à Pont-Rouge",
    "VI_": "La Seymaz à Villette",
    "VX_": "La Versoix à Versoix-CFF",
    "AR_": "Aïre",
    "BA_": "Bachet",
    "CE_": "Chevrier",
    "CR_": "CERN",
    "DD_": "David-Dufour",
    "ER_": "Ermitage",
    "ES_": "Essertines",
    "FO_": "Maison de la Foret",
    "GF_": "Grange-Falquet",
    "LA_": "Landecy",
    "LC_": "Laconnex",
    "SA_": "Sauverny",
    }
stations_DEB_HLM = ["AM_", "AV_", "BS_", "BU_", "CP_", "CS_", "GC_", "GO_", "HE_", "LM_", "XPA_", "PG_", "PR_", "VI_", "VX_"]
measures_DEB_HLM = ["DEB", "HLM"]
stations_PLU = ["AR_", "BA_", "CE_", "CR_", "DD_", "ER_", "ES_", "FO_", "GF_", "LA_", "LC_", "SA_"]
measures_PLU = ["PLU"]

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

path_tmp = '{}/'.format(__location__)
tmp_filename = 'tmp_data_request.csv'


def check_access() -> bool:
    challenge_txt = str(int(time.time()))
    challenge_password = sha256((encrypted_password+challenge_txt).encode('utf-8')).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "user_agent": "tetraedre/TDS",
        "method": "POST",
    }
    data = {
        "operation": "check_access",
        "username": username,
        "challenge": challenge_txt,
        "dossier_id": dossier_id,
        "challenge_password": challenge_password
    }

    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    res = ast.literal_eval(r.content.decode('utf-8'))

    print(res)

    return res["access_granted"] == 1 and res["export_data"] == '1'


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
    if r.status_code == 200:
        return r.content.decode('utf-8')

    return []

def format_data_original(data:dict, measures:str) -> list:
    array_data_formatted_original = []
    for e in data:
        val = [e]
        for m in measures:
            if m in data[e].keys():
                val.append(data[e][m])
            else:
                val.append("")
        array_data_formatted_original.append(val)
    return array_data_formatted_original


def format_data_transformed(data:dict, measures:str, start_date:str, end_date:str) -> list:
    array_data_formatted = []
    # Iterate over the data
    previous_date = start_date
    cnt_measure_DEB_HLM = 1
    for e in data:
        to_be_added = True
        # Create variable that will contain the data of the measures for a timestamp/date
        val = [datetime.datetime.fromtimestamp(int(e)).strftime('%Y-%m-%d %H') + ":00:00"]

        if (datetime.datetime.strptime(val[0], '%Y-%m-%d %H:%M:%S') <= datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')):

            # Iterate over the measures keys
            for m in measures:
                # Add value if there is one, otherwise add empty string
                if m in data[e].keys():
                    val.append(data[e][m])
                else:
                    val.append("0")

            # Check that the array is not empty as we try to access the last added value
            if array_data_formatted != []:
                previous_date = array_data_formatted[-1][0]
                # print(previous_date[:-6])
                # print(val[0][:-6])
                if ((measures[0] == "PLU") and (previous_date[:-6] == val[0][:-6])):
                    array_data_formatted[-1][1] = str(float(array_data_formatted[-1][1])+float(val[1]))
                    to_be_added = False
                elif (measures[0] == "DEB") or (measures[0] == "HLM"):          
                    if (previous_date[:-6] == val[0][:-6]):
                        array_data_formatted[-1][1] = str(float(array_data_formatted[-1][1])+float(val[1]))
                        array_data_formatted[-1][2] = str(float(array_data_formatted[-1][2])+float(val[2]))
                        to_be_added = False
                        cnt_measure_DEB_HLM+=1
                    else:
                        array_data_formatted[-1][1] = "{:.2f}".format(float(array_data_formatted[-1][1]) / cnt_measure_DEB_HLM)
                        array_data_formatted[-1][2] = "{:.2f}".format(float(array_data_formatted[-1][2]) / cnt_measure_DEB_HLM)
                        cnt_measure_DEB_HLM = 1
            else:
                if (datetime.datetime.strptime(val[0], '%Y-%m-%d %H:%M:%S') > datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')) and start_date == previous_date:
                    array_data_formatted.append([previous_date]+['0' for _ in range(len(measures))])

            # Iterate creating timestamps with empty values if there is a jump between the last and the next timestamp
            while (datetime.datetime.strptime(val[0], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(previous_date, '%Y-%m-%d %H:%M:%S')) > datetime.timedelta(hours=1):
                previous_date = ((datetime.datetime.strptime(previous_date, '%Y-%m-%d %H:%M:%S'))+datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
                array_data_formatted.append([previous_date]+['0' for _ in range(len(measures))])
            if to_be_added:
                array_data_formatted.append(val)

            previous_date = array_data_formatted[-1][0]
    # Iterate creating timestamps with empty values if there is a jump between the last and the next timestamp
    while (datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(previous_date, '%Y-%m-%d %H:%M:%S')) >= datetime.timedelta(hours=1):
        previous_date = ((datetime.datetime.strptime(previous_date, '%Y-%m-%d %H:%M:%S'))+datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        array_data_formatted.append([previous_date]+['0' for _ in range(len(measures))])

    # print(end_date)
    # print(array_data_formatted[-1])
    return array_data_formatted


def create_data_file(data:dict, tmp_filename:str, path_original_data:str, measures:list, start_date:str, end_date:str, transformed:bool=False) -> None:
    """
    Create a file with the data of the request. Will format the data (editing it or not) at some point to be able to write it into a file
    """
    data_formatted = []
     # Create header
    measures_str = ""
    first = True
    for e in measures:
        if first:
            measures_str += e
            first = False
        else:
            measures_str += ","+e

    # Open and write in file
    f = open(path_original_data+tmp_filename+"_tmp", "w")
    f.write("localtime,"+measures_str+"\n")

    if transformed:
        data_formatted = format_data_transformed(data, measures, start_date, end_date)
    else:
        data_formatted = format_data_original(data, measures)
    for line in data_formatted:
        # Make sure that the line is not empty
        if not line == []:
            f.write(','.join(line))
            f.write('\n')
    f.close()
    merge_csv_by_date.merge_csv_by_date(path_original_data+tmp_filename, path_original_data+tmp_filename+"_tmp", '%Y-%m-%d %H:%M:%S')
    os.remove(path_original_data+tmp_filename+"_tmp")


def manage_data(data: dict, metering_code: str, measures: list, start_date: str, end_date: str) -> None:
    """
    Will handle the data requested to VHG. It will first create an tmp file with the original data, in the corresponding folder, if the folder does not exists,
    it will automatically create the folder. Then it will merge the tmp original data file with the orginal data file. And repeat the same steps for the transformed datas
    transforming obviously the data if needed.
    """
    # Check if dir already exists if it's not the case, create new dir
    if(not os.path.isdir("{}/../media/original/VHG/{}".format(__location__, map_station_acronyme_name[metering_code]))):
        os.mkdir("{}/../media/original/VHG/{}".format(__location__, map_station_acronyme_name[metering_code]))
    path_original_data = '{}/../media/original/VHG/{}/'.format(__location__, map_station_acronyme_name[metering_code])
    original_data_filename = '{}_{}_original_merged.csv'.format(str(datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S').year), map_station_acronyme_name[metering_code])

    create_data_file(data, original_data_filename, path_original_data, measures, start_date, end_date)

    # Check if dir already exists if it's not the case, create new dir
    if(not os.path.isdir("{}/../media/transformed/VHG/{}".format(__location__, map_station_acronyme_name[metering_code]))):
        os.mkdir("{}/../media/transformed/VHG/{}".format(__location__, map_station_acronyme_name[metering_code]))
    path_transformed_data = '{}/../media/transformed/VHG/{}/'.format(__location__, map_station_acronyme_name[metering_code])
    transformed_data_filename = '{}_{}.csv'.format(str(datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S').year), map_station_acronyme_name[metering_code])

    create_data_file(data, transformed_data_filename, path_transformed_data, measures, start_date, end_date, True)


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

    # Test if the start date catch up the end date
    while start_date <= end_date:
        # Manually set the year working on
        year_working_on = str(datetime.datetime.strptime(start_date, '%Y-%m-%d').year)
        tmp_end_date = year_working_on + "-12-31"
        # Check if the end date generated is greater than the end date given
        if tmp_end_date > end_date:
            tmp_end_date = end_date

        print("-------------------------- " + start_date + " to " + tmp_end_date + " --------------------------")
        # Iterate over each metering code available for DEB and HLM
        for metering_code in stations_DEB_HLM:
            print(metering_code)
            data = {}
            # Iterate alternately on DEB and HLM and create a dict with the results
            for measure in measures_DEB_HLM:
                # data[measure] = request_data(start_date, end_date, metering_code, measure)
                val = []
                try:
                    val = ast.literal_eval(request_data(start_date, ((datetime.datetime.strptime(tmp_end_date, '%Y-%m-%d'))+datetime.timedelta(days=1)).strftime('%Y-%m-%d'), metering_code, measure))
                except:
                    print("There was an error...")
                    print(metering_code)
                # Iterate over the answer of the requested data
                for e in val:
                    # Add data to dict using the timestamp as key
                    if e["timestamp"] not in data.keys():
                        data[e["timestamp"]] = {
                            measure: e["value"]
                        }
                    else:
                        data[e["timestamp"]][measure] = e["value"]
            # If there was not data answered, create fake timestamp of start and end date to write in the corresponding files that no data was available
            if data == {}:
                empty_measures = {}
                for measure in measures_DEB_HLM:
                    empty_measures[measure] = '0'
                    
                data = {
                    str(int(time.mktime(datetime.datetime.strptime(start_date, "%Y-%m-%d").timetuple()))): empty_measures, 
                    str(int(time.mktime(datetime.datetime.strptime(tmp_end_date, "%Y-%m-%d").timetuple()))): empty_measures
                }

            manage_data(data, metering_code, measures_DEB_HLM, start_date+" 00:00:00", tmp_end_date+" 23:00:00")

        # Call metering code and measures for PLU and similar
        # For now it only contains PLU
        for metering_code in stations_PLU:
            print(metering_code)
            data = {}
            # Iterate alternately on DEB and HLM and create a dict with the results
            for measure in measures_PLU:
                # data[measure] = request_data(start_date, end_date, metering_code, measure)
                val = []
                try:
                    val = ast.literal_eval(request_data(start_date, ((datetime.datetime.strptime(tmp_end_date, '%Y-%m-%d'))+datetime.timedelta(days=1)).strftime('%Y-%m-%d'), metering_code, measure))
                except:
                    print("There was an error...")
                    print(metering_code)

                for e in val:
                    if e["timestamp"] not in data.keys():
                        data[e["timestamp"]] = {
                            measure: e["value"]
                        }
                    else:
                        data[e["timestamp"]][measure] = e["value"]
            if data == {}:
                empty_measures = {}
                for measure in measures_PLU:
                    empty_measures[measure] = '0'
                    
                data = {
                    str(int(time.mktime(datetime.datetime.strptime(start_date, "%Y-%m-%d").timetuple()))): empty_measures, 
                    str(int(time.mktime(datetime.datetime.strptime(tmp_end_date, "%Y-%m-%d").timetuple()))): empty_measures
                }
            manage_data(data, metering_code, measures_PLU, start_date+" 00:00:00", tmp_end_date+" 23:00:00")


        start_date = datetime.datetime.strftime(datetime.datetime.strptime(tmp_end_date, '%Y-%m-%d') + datetime.timedelta(days=1), '%Y-%m-%d')

    print("--------------- Ending requests to VHG : {} ---------------".format(time.strftime("%Y-%m-%d %H:%M:%S")))
    print(end_date)


if __name__ == '__main__':
    if check_access():
        main()
    else:
        print("Permission denied")


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

# data = {
#     "operation": "get_values",
#     "username": username,
#     "challenge": challenge_txt,
#     "dossier_id": dossier_id,
#     "challenge_password": challenge_password,
#     "metering_code": "BA_",
#     "t0": time.mktime(datetime.datetime.strptime("2023-01-08", "%Y-%m-%d").timetuple()),
#     "t1": time.mktime(datetime.datetime.strptime("2023-01-09", "%Y-%m-%d").timetuple()),
#     "limit": 0,
#     "sort": "ASC",
#     "media": media["PLU"],
# }


# r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
# print("------------------------Response------------------------")
# print(str(r)+"\n"+str(r.headers)+"\n"+str(r.content))
# print(data)
# print(r.content.decode('utf-8'))
