import os
import re
import sys
import getopt
import numpy as np
import PyPDF2
import datetime
from merge_csv_by_date_package import merge_csv_by_date

## Path of Scraper
scraper_path = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
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
        headerFile.write(key+";"+";".join(value)+"\n")

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
                s = ex
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

def orderManipulation():
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
            header[splitted_line[0]]=splitted_line[1]
            content[splitted_line[0]] = {}
            stations.append(splitted_line[0])
            for splitter_content in splitted_line[1].split(";"):
                content[splitted_line[0]][splitter_content] = ''
        headerFile.close()

    # Check Order files
    order_files = list(filter(lambda f: f.startswith('order_'),os.listdir(scraper_path)))
    order_data_files = list(filter(lambda f: f.startswith('order_') and f.endswith('data.txt'),os.listdir(scraper_path)))
    order_legend_files = list(filter(lambda f: f.startswith('order_') and f.endswith('legend.txt'),os.listdir(scraper_path)))
    order_files_by_id = {}
    if(len(order_files) == 0):
        print("No order file not found !")
        sys.exit(1)
    elif(len(order_files)%2!=0):
        print("Some file seems to be missing !\nMake sure you have one order_data and one order_legend for each code number")
        sys.exit(1)
    elif len(order_data_files) != len(order_legend_files):
        print("There isn't the same number of data and legend file.\nPlease make sure to have the corresponding files for each order code !")
        sys.exit(1)

    for file in order_files:
        splitted_name = file.split("_")
        if splitted_name[1] not in order_files_by_id:
            order_files_by_id[splitted_name[1]] = {}

        order_files_by_id[splitted_name[1]][splitted_name[2].replace(".txt","")] = file

    stationManipulation = False
    for key,value in order_files_by_id.items():
        legend_order_file = open(os.path.join(scraper_path,value["legend"]),'rb')
        stationDataset = {}
        for line in legend_order_file:
            firstLine = False
            decodedLine = line.decode("Windows-1252").strip()
            if("stn       Nom                                  Parameter        Source de données                                  Longitude/Latitude       Coordonnées [km] Altitude [m]" in line.decode("Windows-1252")):
                stationManipulation = True
                firstLine = True
            if("Paramètre" in line.decode("Windows-1252")):
                stationManipulation = False
            if(stationManipulation and not firstLine):
                if line.decode("Windows-1252").strip() != "":
                    splittedStation = re.split(r'\s+',decodedLine)
                    if splittedStation[0] not in stationDataset:
                        stationDataset[splittedStation[0]] = {"parameters":[]}

                    if splittedStation[1] not in stationDataset[splittedStation[0]]:
                        stationDataset[splittedStation[0]]["name"] = splittedStation[1]

                    if splittedStation[2] not in stationDataset[splittedStation[0]]["parameters"]:
                        stationDataset[splittedStation[0]]["parameters"].append(splittedStation[2])

                    if splittedStation[3] not in stationDataset[splittedStation[0]]:
                        stationDataset[splittedStation[0]]["source"] = splittedStation[3]

                    if splittedStation[4] not in stationDataset[splittedStation[0]]:
                        stationDataset[splittedStation[0]]["latlong"] = splittedStation[4]

                    if splittedStation[5] not in stationDataset[splittedStation[0]]:
                        stationDataset[splittedStation[0]]["coord"] = splittedStation[5]

                    if splittedStation[6] not in stationDataset[splittedStation[0]]:
                        stationDataset[splittedStation[0]]["altitude"] = splittedStation[6]
        legend_order_file.close()

    currentData = None
    # print(stations)
    for station in stations:
        station_name = station.replace(" / ","-")
        station_name = station_name.replace(" /","-")
        station_file = None
        try:
            station_file = open(os.path.join(transformed_media_path,station_name+".csv"),"r")
        except:
            station_file = open(os.path.join(transformed_media_path,station_name+".csv"),"x+")
        # NEED TO COMPLETE THIS FUNCTION !
        currentData = fileToData(station_file.readlines())
        station_file.close()

    if currentData == None:
        currentData = content

        # DATA ARE LOADED, NOW TO APPLY ORDER TO IT AND REWRITE IT
        # station_file = open(os.path.join(transformed_media_path,station_name+".csv"),"w")
        # station_file.write(json.dumps(currentData))
        # station_file.close()
    # print(order_files_by_id)
    dataToSave = {}
    for key,value in order_files_by_id.items():
        data_order_file = open(os.path.join(scraper_path,value["data"]),'rb')
        orderHeader = None
        for line in data_order_file:
            strippedLine = line.decode("Windows-1252").strip()
            if strippedLine != "":
                if ";" in strippedLine:
                    if strippedLine.startswith("stn"):
                        orderHeader = strippedLine.split(";")
                    else:
                        if orderHeader is not None:
                            strippedLineList = strippedLine.split(";")
                            stationName = stationDataset[strippedLineList[0]]["name"]
                            if stationName not in dataToSave:
                                dataToSave[stationName] = {}
                            orderTimeStamp = datetime.datetime.strptime(strippedLineList[1],"%Y%m%d%H%M")
                            formattedOrderTimeStamp = orderTimeStamp.strftime("%Y-%m-%d %H:%M:%S")
                            if formattedOrderTimeStamp not in dataToSave[stationName]:
                                dataToSave[stationName][formattedOrderTimeStamp] = currentData[stationName]
                            for param in dataToSave[stationName][formattedOrderTimeStamp]:
                                if param in orderHeader:
                                    index = orderHeader.index(param)
                                    dataToSave[stationName][formattedOrderTimeStamp][param] = strippedLineList[index]
                else:
                    print('Wrong Format, make sure you chose "CSV" when downloading the file from IDAWEB')
                    sys.exit(1)
        data_order_file.close()
        for key,value in dataToSave.items():
            temp = open(os.path.join(scraper_path,"temp-"+key+".csv"),"a+")
            temp.write('localtime;'+header[key]+"\n")
            str = ""
            for ke,val in value.items():
                str += ke+";"
                for k,v in val.items():
                    str += v+";"
                str += "\n"
            temp.write(str)
            temp.close()
def main(argv):
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

if __name__ == "__main__":
    main(sys.argv[1:])
