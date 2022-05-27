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
        sys.exit(1)
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

def buildDataFromOrder():
    return {}

def fileToData(lines:dict):
    if(len(lines)<1):
        return None

    #print(lines)
    return {}

def station_sanitizer(station:str) -> str:
    return station.replace(' /',',').replace(' / ',',').replace('/',',')

def loadHeader():
    headerFile = None
    header = {}
    content = {}
    stations = []

    # Check and load header file
    if os.path.exists(os.path.join(scraper_path,'headers.csv')) == False:
        print("The headers file wasn't found. run the command with the -i option to generate it.")
        sys.exit(1)
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

def orderManipulation():

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


    for order_file in order_data_files:
        station_parameters_type = order_file.replace('.txt','').split('_')[2:]
        if(len(station_parameters_type)==4):
            station_name = station_sanitizer(order_file.replace('.txt','').split('_')[2])
            parameter = order_file.replace('.txt','').split('_')[3]
            dataset = {}
            for k,v in station_abbr.items():
                if (os.path.exists(os.path.join(transformed_media_path,f'{v}.csv'))):
                    print("File Found")
            order_station_file = open(os.path.join(temp_path,order_file),'r')
            for line in order_station_file:
                stripped_line = line.strip()
                if stripped_line != "":
                    measures = stripped_line.split(';')[1:]
                    order_header = []

                    if measures[0] != "time" and measures[0] not in dataset:
                        dataset[measures[0]] = {}
                        for param in header[station_abbr[station_name]].split(';'):
                            dataset[measures[0]][param] = ''

                        dataset[measures[0]][parameter] = measures[1]

            order_station_file.close()

    print(dataset)
    sys.exit(0)
    # # Check Order files
    # order_files = list(filter(lambda f: f.startswith('order_'),os.listdir(scraper_path)))
    # order_data_files = list(filter(lambda f: f.startswith('order_') and f.endswith('data.txt'),os.listdir(scraper_path)))
    # order_legend_files = list(filter(lambda f: f.startswith('order_') and f.endswith('legend.txt'),os.listdir(scraper_path)))
    # order_files_by_id = {}
    # if(len(order_files) == 0):
    #     print("No order file found !")
    #     sys.exit(1)
    # elif(len(order_files)%2!=0):
    #     print("Some file seems to be missing !\nMake sure you have one order_data and one order_legend for each code number")
    #     sys.exit(1)
    # elif len(order_data_files) != len(order_legend_files):
    #     print("There isn't the same number of data and legend file.\nPlease make sure to have the corresponding files for each order code !")
    #     sys.exit(1)
    #
    # for file in order_files:
    #     splitted_name = file.split("_")
    #     if splitted_name[1] not in order_files_by_id:
    #         order_files_by_id[splitted_name[1]] = {}
    #
    #     order_files_by_id[splitted_name[1]][splitted_name[2].replace(".txt","")] = file
    #
    # stationManipulation = False
    # for key,value in order_files_by_id.items():
    #     legend_order_file = open(os.path.join(scraper_path,value["legend"]),'rb')
    #     stationDataset = {}
    #     for line in legend_order_file:
    #         firstLine = False
    #         decodedLine = line.decode("Windows-1252").strip()
    #         if("stn       Nom                                  Parameter        Source de données                                  Longitude/Latitude       Coordonnées [km] Altitude [m]" in line.decode("Windows-1252")):
    #             stationManipulation = True
    #             firstLine = True
    #         if("Paramètre" in line.decode("Windows-1252")):
    #             stationManipulation = False
    #         if(stationManipulation and not firstLine):
    #             if line.decode("Windows-1252").strip() != "":
    #                 decodedLine = decodedLine.replace(" / ","/").replace(" /","/")
    #                 splittedStation = re.split(r'\s+',decodedLine)
    #                 if splittedStation[0] not in stationDataset:
    #                     stationDataset[splittedStation[0]] = {"parameters":[]}
    #
    #                 if splittedStation[1] not in stationDataset[splittedStation[0]]:
    #                     stationDataset[splittedStation[0]]["name"] = splittedStation[1]
    #
    #                 if splittedStation[2] not in stationDataset[splittedStation[0]]["parameters"]:
    #                     stationDataset[splittedStation[0]]["parameters"].append(splittedStation[2])
    #
    #                 if splittedStation[3] not in stationDataset[splittedStation[0]]:
    #                     stationDataset[splittedStation[0]]["source"] = splittedStation[3]
    #
    #                 if splittedStation[4] not in stationDataset[splittedStation[0]]:
    #                     stationDataset[splittedStation[0]]["latlong"] = splittedStation[4]
    #
    #                 if splittedStation[5] not in stationDataset[splittedStation[0]]:
    #                     stationDataset[splittedStation[0]]["coord"] = splittedStation[5]
    #
    #                 if splittedStation[6] not in stationDataset[splittedStation[0]]:
    #                     stationDataset[splittedStation[0]]["altitude"] = splittedStation[6]
    #     legend_order_file.close()
    # currentData = None
    # # print(stations)
    # for station in stations:
    #     station_name = station.replace("/","\\")
    #     station_file = None
    #     print(station_name)
    #     try:
    #         station_file = open(os.path.join(transformed_media_path,station_name+".csv"),"r+")
    #     except:
    #         station_file = open(os.path.join(transformed_media_path,station_name+".csv"),"x+")
    #     # NEED TO COMPLETE THIS FUNCTION !
    #     currentData = fileToData(station_file.readlines())
    #     station_file.close()
    #
    # if currentData == None:
    #     currentData = content
    #
    #     # DATA ARE LOADED, NOW TO APPLY ORDER TO IT AND REWRITE IT
    #     # station_file = open(os.path.join(transformed_media_path,station_name+".csv"),"w")
    #     # station_file.write(json.dumps(currentData))
    #     # station_file.close()
    # # print(order_files_by_id)
    # dataToSave = {}
    # for key,value in order_files_by_id.items():
    #     data_order_file = open(os.path.join(scraper_path,value["data"]),'rb')
    #     orderHeader = None
    #     for line in data_order_file:
    #         strippedLine = line.decode("Windows-1252").strip()
    #         if strippedLine != "":
    #             if ";" in strippedLine:
    #                 if strippedLine.startswith("stn"):
    #                     orderHeader = strippedLine.split(";")
    #                 else:
    #                     if orderHeader is not None:
    #                         strippedLineList = strippedLine.split(";")
    #                         stationName = stationDataset[strippedLineList[0]]["name"]
    #                         if stationName not in dataToSave:
    #                             dataToSave[stationName] = {}
    #                         try:
    #                             orderTimeStamp = datetime.datetime.strptime(strippedLineList[1],"%Y%m%d%H%M")
    #                         except:
    #                             try:
    #                                 orderTimeStamp = datetime.datetime.strptime(strippedLineList[1],"%Y%m%d")
    #                             except:
    #                                 orderTimeStamp = datetime.datetime.strptime(strippedLineList[1],"%Y%m")
    #                         formattedOrderTimeStamp = orderTimeStamp.strftime("%Y-%m-%d %H:%M:%S")
    #                         if formattedOrderTimeStamp not in dataToSave[stationName]:
    #                             dataToSave[stationName][formattedOrderTimeStamp] = currentData[stationName]
    #                         for param in dataToSave[stationName][formattedOrderTimeStamp]:
    #                             if param in orderHeader:
    #                                 index = orderHeader.index(param)
    #                                 dataToSave[stationName][formattedOrderTimeStamp][param] = strippedLineList[index]
    #             else:
    #                 print('Wrong Format, make sure you chose "CSV" when downloading the file from IDAWEB')
    #                 sys.exit(1)
    #     data_order_file.close()
    #     for key,value in dataToSave.items():
    #         name = r''+key.replace("/",'\\')
    #         temp = open(os.path.join(scraper_path,"temp-"+name+".csv"),"a+")
    #         temp.write('localtime;'+header[name]+"\n")
    #         str = ""
    #         for ke,val in value.items():
    #             str += ke+";"
    #             for k,v in val.items():
    #                 str += v+";"
    #             str += "\n"
    #         temp.write(str)
    #         temp.close()
def main(argv):
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
            createInventoryCSV()
            sys.exit(0)

    orderManipulation()
    sys.exit(exit_code)

if __name__ == "__main__":
    main(sys.argv[1:])
