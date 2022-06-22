import os
import re
import sys
import getopt
import numpy as np
import PyPDF2
import datetime
import shutil
from zipfile import ZipFile
from merge_csv_by_date_package import merge_csv_by_date
import gc

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

def createHeaders():
    """Take the inventory csv file and create a headers file from it
    """
    inventoryCSV = open(os.path.join(scraper_path,'inventory.csv'))
    inventoryCSVLength = len(inventoryCSV.readlines())
    inventoryCSV.close()
    inventoryCSV = open(os.path.join(scraper_path,'inventory.csv'))
    inventoryCSV.readline()
    stations = {}
    count = 1
    for csvLine in inventoryCSV:
        print(str(count)+"/"+str(inventoryCSVLength),end="\r")
        lineList = csvLine.split('\t')
        if lineList[0] not in stations:
            stations[lineList[0]] = []
        if lineList[3] not in stations[lineList[0]]:
            stations[lineList[0]].append(lineList[3])
        count+=1

    headerFile = open(os.path.join(scraper_path,'headers.csv'),'w+')
    for key,value in stations.items():
        headerFile.write(key.replace(" / ","/").replace(" /","/")+";"+";".join(value)+"\n")

    headerFile.close()
    inventoryCSV.close()
    print("Created headers csv file !")

def createInventoryCSV():
    """Take an iventory pdf file from idaweb and transform it to csv
    """
    if os.path.exists(os.path.join(scraper_path,'inventory.pdf')) == False:
        print("The inventory pdf file doesn't exist. Please place it next to this script and name it 'inventory.pdf'")
        return 1
    inputPDF = open(os.path.join(scraper_path,'inventory.pdf'), 'rb')
    outputCSV = open(os.path.join(scraper_path,'inventory.csv'), 'w+')
    pdfReader = PyPDF2.PdfFileReader(inputPDF)
    print(str(pdfReader.numPages)+' page(s) found !')
    outputCSV.write('Station\tAltitude\tDescription du paramètre\tParamètre\tUnité\tTemporalité\tDate de service\n')
    for i in range(0,pdfReader.numPages):
        print(str(i)+"/"+str(pdfReader.numPages),end="\r")
        sys.stdout.flush()
        pageObj = pdfReader.getPage(i)
        extracted = pageObj.extractText()
        extracted_list = extracted.split('\n')
        for j in range(0,len(extracted_list)):
            ex = extracted_list[j].strip()
            if(j< len(extracted_list)-1):
                next_ex = extracted_list[j+1].strip()
            if(re.match('\d*/\d*',ex) is None and ex != "" and  ex != " " and ex != 'suivant'):
                s = ex.replace(" / ","/").replace(" /","/")
                if(re.match('^\d*$',ex) or ( re.match('^[a-z0-9]{8}$',ex) and re.match('^[a-z0-9]{8}$',next_ex) is None)or any(x in ex for x in ['Dix minutes','Heure','Jour','Mois','Année'])):
                    s = '\t'+ex+'\t'
                elif re.match('^[a-z0-9]{8}$',next_ex):
                    s = ' '+ex
                elif(re.match('^\d{2}.\d{2}.\d{4}-\d{2}.\d{2}.\d{4}$',ex)):
                    s = ex+'\n'

                outputCSV.write(s)
    outputCSV.close()
    inputPDF.close()
    print("Created inventory csv file !")
    createHeaders()

def dataToFile(dataset: dict, header:dict) -> int:
    """Write dataset to files

    Parameters
    ----------
    dataset : dict
        Dictionary to write
    header: dict
        Dictionary of the headers to get the correct order

    Returns
    -------
    int
        The System Exit Code
    """
    try:
        for station, timestamps in dataset.items():
            station_file = open(os.path.join(transformed_media_path,station)+'.csv',"w+")
            station_file.write(f'localtime;{header[station]}\n')
            splitted_header = header[station].split(";")
            for timestamp, parameters in timestamps.items():
                station_file.write(f'{timestamp};')
                # To be more safe, loop through header and assign parameter value
                for param_header in splitted_header:
                    station_file.write(f'{parameters[param_header]};')
                station_file.write('\n')
            station_file.close()
        print("Done creating or editing the station files")
        return 0
    except Exception:
        return 1

def station_sanitizer(station:str) -> str:
    """Sanitize the station string
    """
    return station.replace(' /',',').replace(' / ',',').replace('/',',')

def loadHeader():
    """Loop through an existing header.csv to load header, content and stations
    """
    headerFile = None
    header = {}
    content = {}
    stations = []

    # Check and load header file
    if os.path.exists(os.path.join(scraper_path,'headers.csv')) == False:
        print("The headers file wasn't found. run the command with the -i option to generate it.")
        return 1
    else:
        headerFile = open(os.path.join(scraper_path,'headers.csv'))
        for line in headerFile:
            line = line.strip()
            splitted_line = line.split(";",1)
            sanitized_station = station_sanitizer(splitted_line[0])
            header[sanitized_station]=splitted_line[1]
            content[sanitized_station] = {}
            stations.append(sanitized_station)
            for splitter_content in splitted_line[1].split(";"):
                content[sanitized_station][splitter_content] = ''
        headerFile.close()

    return header, content, stations

def datasetManiulation():
    return {}

def orderManipulation() -> int:
    """Manipulate order file to create the station output file

    Returns
    -------
    int
        the system exit code
    """
    # Load Header
    header, content, stations = loadHeader()

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

    # Get Station Abbreviation to Station Name transformation
    station_abbr = {}
    print("Start looping through legend file(s)")
    for order_file in order_legend_files:
        station_parameters_type = order_file.replace('.txt','').split('_')[2:]
        if(len(station_parameters_type)==4):
            station_name = order_file.replace('.txt','').split('_')[2]
            if station_name not in station_abbr:
                legend_order_file = open(os.path.join(temp_path,order_file),'rb')
                for line in legend_order_file:
                    stripped_line = line.decode('Windows-1252').strip()
                    if stripped_line.startswith(station_name):
                        station_abbr[station_name] = station_sanitizer(re.split(r'\s+',stripped_line)[1])
                legend_order_file.close()

    # Init Dataset
    dataset = {}
    for k,v in station_abbr.items():
        if v not in dataset:
            dataset[v] = {}
        # Load existing station file data
        if (os.path.exists(os.path.join(transformed_media_path,f'{v}.csv'))):
            print(f"File Found for {v}")
            # Load file if exist and fill dataset
            station_found_file = open(os.path.join(transformed_media_path,f'{v}.csv'))
            header_found_file = station_found_file.readline().strip().split(";")
            for line in station_found_file:
                stripped_line = line.strip().split(";")
                if stripped_line[0] not in dataset[v]:
                    dataset[v][stripped_line[0]] = {}
                for i in range(1,len(stripped_line)-1):
                    dataset[v][stripped_line[0]][header_found_file[i]] = stripped_line[i]
            station_found_file.close()

    # Add Order files datas to Dataset
    print("Start lopping through data file(s)")
    for order_file in order_data_files:
        station_parameters_type = order_file.replace('.txt','').split('_')[2:]
        # Check to exclude orders that are not divided
        if(len(station_parameters_type)==4):
            station_name = station_sanitizer(order_file.replace('.txt','').split('_')[2])
            parameter = order_file.replace('.txt','').split('_')[3]

            order_station_file = open(os.path.join(temp_path,order_file),'r')
            data_10_minutes = []
            # cnt = 0
            #file = order_station_file.readlines()
            for line in order_station_file:
                stripped_line = line.strip()
                # cnt+=1
                if stripped_line != "":
                    measures = stripped_line.split(';')[1:]

                    # Ignore header lineimport gc
                    if measures[0] != "time":
                        try:
                            o_timestamp = datetime.datetime.strptime(measures[0],'%Y%m%d')
                            for i in range(0,24):
                                timestamp = o_timestamp + datetime.timedelta(hours=i)
                                timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                                if timestamp not in dataset[station_abbr[station_name]]:
                                    dataset[station_abbr[station_name]][timestamp] = {}
                                    for param in header[station_abbr[station_name]].split(';'):
                                        dataset[station_abbr[station_name]][timestamp][param] = ''

                                dataset[station_abbr[station_name]][timestamp][parameter] = measures[1]
                                # del timestamp
                                # gc.collect()
                        except Exception:
                            try:
                                timestamp = datetime.datetime.strptime(measures[0],'%Y%m%d%H')
                                timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                                if timestamp not in dataset[station_abbr[station_name]]:
                                    dataset[station_abbr[station_name]][timestamp] = {}
                                    for param in header[station_abbr[station_name]].split(';'):
                                        dataset[station_abbr[station_name]][timestamp][param] = ''

                                dataset[station_abbr[station_name]][timestamp][parameter] = measures[1]
                            except Exception:
                                try:
                                    timestamp = datetime.datetime.strptime(measures[0],'%Y%m%d%H%M')
                                    if(timestamp.minute==0):
                                        average = ""
                                        if len(data_10_minutes) > 0:
                                            average = np.average(data_10_minutes)
                                        timestamp = timestamp - datetime.timedelta(hours=1)
                                        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                                        if timestamp not in dataset[station_abbr[station_name]]:
                                            dataset[station_abbr[station_name]][timestamp] = {}
                                            for param in header[station_abbr[station_name]].split(';'):
                                                dataset[station_abbr[station_name]][timestamp][param] = ''
                                        dataset[station_abbr[station_name]][timestamp][parameter] = average
                                        if measures[1] != '-' and measures[1] != '':
                                            data_10_minutes = [float(measures[1])]
                                    else:
                                        if measures[1] != '-' and measures[1] != '':
                                            data_10_minutes.append(float(measures[1]))
                                except Exception:
                                    print("No Matching Timestamp Found")
                                    break

            order_station_file.close()
            print(f'{order_file}...done')
    print("Dataset created")
    return dataToFile(dataset,header)

def main(argv):
    """Main function of the script

    Parameters
    ----------
    argv : dict
        Parsed set of arguments passed when script called
    """
    print(f"Starting {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    exit_code = 0
    try:
      opts, args = getopt.getopt(argv,"ihs")
    except getopt.GetoptError:
      print('idaweb.py -i|-s')
      sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            print('idaweb.py -i|')
            sys.exit(1)

        elif opt == '-i':
            print("Creating Inventory")
            createInventoryCSV()
            sys.exit(0)

    print("Manipulating Order(s)")
    exit_code = orderManipulation()
    print(f"Done {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main(sys.argv[1:])
