import os
import re
import sys
import getopt
import numpy as np
import PyPDF2
import datetime
import shutil
import copy
from zipfile import ZipFile

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

def is_string_date(date_string: str, format_date: str) -> bool:
    """Test if a string is a date and return a boolean

    Parameters
    ----------
    date_string : str
        string to be cast
    format_date: str
        The format of the date that will be used

    Returns
    -------
    bool
        indicate if the string is a date or not
    """

    try:
        datetime.datetime.strptime(date_string, format_date)
    except:
        return False
    return True


def station_sanitizer(station:str) -> str:
    """Sanitize the station string
    """
    return station.replace(' /',',').replace(' / ',',').replace('/',',')

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
        print(str(count)+"/"+str(inventoryCSVLength)+" lines",end="\r")
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
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Created headers csv file")

def createInventoryCSV():
    """Take an iventory pdf file from idaweb and transform it to csv
    """
    if os.path.exists(os.path.join(scraper_path,'inventory.pdf')) == False:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] The inventory pdf file doesn't exist. Please place it next to this script and name it 'inventory.pdf'")
        return 1
    inputPDF = open(os.path.join(scraper_path,'inventory.pdf'), 'rb')
    outputCSV = open(os.path.join(scraper_path,'inventory.csv'), 'w+')
    pdfReader = PyPDF2.PdfFileReader(inputPDF)
    outputCSV.write('Station\tAltitude\tDescription du paramètre\tParamètre\tUnité\tTemporalité\tDate de service\n')
    for i in range(0,pdfReader.numPages):
        print(str(i)+"/"+str(pdfReader.numPages)+" page(s)",end="\r")
        sys.stdout.flush()
        pageObj = pdfReader.getPage(i)
        extracted = pageObj.extractText()
        extracted_list = extracted.split('\n')
        for j in range(0,len(extracted_list)):
            ex = extracted_list[j].strip()
            if(j< len(extracted_list)-1):
                next_ex = extracted_list[j+1].strip()
            if(re.match('\d*/\d*',ex) is None and ex != "" and  ex != " " and ex != 'suivant'):
                s = station_sanitizer(ex)
                if(re.match('^\d*$',ex) or ( re.match('^[a-z0-9]{8}$',ex) and re.match('^[a-z0-9]{8}$',next_ex) is None)or any(x in ex for x in ['Dix minutes','Heure','Jour','Mois','Année'])):
                    s = '\t'+ex+'\t'
                elif re.match('^[a-z0-9]{8}$',next_ex):
                    s = ' '+ex
                elif(re.match('^\d{2}.\d{2}.\d{4}-\d{2}.\d{2}.\d{4}$',ex)):
                    s = ex+'\n'

                outputCSV.write(s)
    outputCSV.close()
    inputPDF.close()
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Created inventory csv file")
    createHeaders()

def sortFileListByStation(list):
    new_array = []
    stations = []
    for elem in list:
        name = elem.split("_")[2]
        if name not in stations:
            stations.append(name)
            new_array.append([])
        new_array[stations.index(name)].append(elem)
        new_array[stations.index(name)].sort()
    new_array.sort()
    return new_array

def mergeFile(final_filename,temp_filename):
    if(os.path.exists(os.path.join(transformed_media_path,final_filename))):
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Final file exists, proceed to merge",end="\r")
        old_data_file = open(os.path.join(transformed_media_path,final_filename), 'r')
        new_data_file = open(os.path.join(temp_path,temp_filename), 'r')
        old_data_file_array = old_data_file.read().splitlines()
        new_data_file_array = new_data_file.read().splitlines()
        old_data_file.close()
        new_data_file.close()
        merged_data_file_array = []
        format_date = '%Y-%m-%d %H:%M:%S'

        pos_old = 0
        pos_new = 0

        new_stopped = False
        old_stopped = False

        while pos_old != len(old_data_file_array) or pos_new != len(new_data_file_array):

            if pos_old == len(old_data_file_array):
                old_stopped = True
            if pos_new == len(new_data_file_array):
                new_stopped = True

            new_splitted_line = [''] if new_stopped else re.split('[,;]', new_data_file_array[pos_new])
            old_splitted_line = [''] if old_stopped else re.split('[,;]', old_data_file_array[pos_old])

            if (is_string_date(new_splitted_line[0], format_date) and is_string_date(old_splitted_line[0], format_date)) or (is_string_date(new_splitted_line[0], format_date) and old_stopped) or (new_stopped and is_string_date(old_splitted_line[0], format_date)):
                if (not old_stopped) and ((new_stopped and is_string_date(old_splitted_line[0], format_date)) or (datetime.datetime.strptime(new_splitted_line[0], format_date) > datetime.datetime.strptime(old_splitted_line[0], format_date))):
                    merged_data_file_array.append(old_data_file_array[pos_old])
                    pos_old += 1
                elif (not new_stopped) and ((is_string_date(new_splitted_line[0], format_date) and old_stopped) or (datetime.datetime.strptime(new_splitted_line[0], format_date) < datetime.datetime.strptime(old_splitted_line[0], format_date))):
                    merged_data_file_array.append(new_data_file_array[pos_new])
                    pos_new += 1
                elif datetime.datetime.strptime(new_splitted_line[0], format_date) == datetime.datetime.strptime(new_splitted_line[0], format_date):
                    # Here the timestamp exists on both files
                    if len(new_splitted_line) != len(old_splitted_line):
                        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Content length doesn't match. Exiting...")
                        sys.exit(1)

                    for j in range(1, len(old_splitted_line)):
                        if old_splitted_line[j] != '':
                            new_splitted_line[j] = old_splitted_line[j]

                    merged_data_file_array.append(';'.join(new_splitted_line))
                    pos_new += 1
                    pos_old += 1
            else:
                # Move indexes until it reaches the first line with a date at position 0

                if (not is_string_date(new_splitted_line[0], format_date)) and not new_stopped:
                    # Write comments and header of the new file
                    if len(new_data_file_array[pos_new]) != len(old_data_file_array[pos_new]):
                        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Header length doesn't match. New:({len(new_data_file_array[pos_new])} Old:{len(old_data_file_array[pos_new])}) Exiting...")
                        sys.exit(1)
                    merged_data_file_array.append(new_data_file_array[pos_new])
                    pos_new += 1
                if (not is_string_date(old_splitted_line[0], format_date)) and not old_stopped:
                    pos_old += 1


        merged_data_file = open(os.path.join(transformed_media_path,final_filename), 'w')
        for line in merged_data_file_array:
            merged_data_file.write("{}\n".format(line))
        merged_data_file.close()
        return os.path.join(transformed_media_path,final_filename)
    else:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Moving temp file",end="\r")
        shutil.move(os.path.join(temp_path,temp_filename),os.path.join(transformed_media_path,final_filename))

    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Final file {final_filename} written")

def writeTempfile(dataset,headers,station_name):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Writing temp file for {station_name}",end="\r")
    open_file = open(os.path.join(temp_path,f'temp-{station_name}.csv'),'w')
    open_file.write(f'localtime;{headers}\n')
    headers = headers.split(";")
    for timestamp,array in dataset.items():
        tuple_array = [""] * len(headers)
        for tuple in array:
            tuple_array[headers.index(tuple[0])] = tuple[1]
        line = ';'.join(tuple_array)
        open_file.write(timestamp+";"+line+"\n")
    open_file.close()
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Written temp file for {station_name}")
    mergeFile(f'{station_name}.csv',f'temp-{station_name}.csv')

def orderManipulation():
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
    order_data_files = sortFileListByStation(order_data_files)
    order_legend_files = sortFileListByStation(order_legend_files)

    station_abbr = {}
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Retrieving station abbreviation to full name")
    for file in order_legend_files:
        station_name = file[0].split('_')[2]
        if station_name not in station_abbr:
            open_file = open(os.path.join(temp_path,file[0]),'rb')
            for line in open_file:
                line = line.decode('Windows-1252').strip()
                if line.startswith(station_name):
                    station_abbr[station_name] = station_sanitizer(re.split(r'\s{2,}',line)[1])
            open_file.close()
    headers = {}
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Loading Headers")
    open_file = open(os.path.join(scraper_path,'headers.csv'),'r')
    for line in open_file:
        line = line.split(";",1)
        if line[0] in list(station_abbr.values()):
            headers[line[0]] = line[1].strip()
    open_file.close()

    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Manipulating Data Files")
    for station_file in order_data_files:
        dataset = {}
        for file in station_file:
            name = file.split('_')[2]
            param = file.split('_')[3]
            open_file = open(os.path.join(temp_path,file),'r')
            data_10_minutes = []
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Creating dataset for {name}",end="\r")
            for line in open_file:
                measures = line.strip()
                if measures != "":
                    if measures.startswith("stn") == False:
                        measures = measures.split(';')[1:]
                        try:
                            o_timestamp = datetime.datetime.strptime(measures[0],'%Y%m%d')
                            for i in range(0,24):
                                timestamp = o_timestamp + datetime.timedelta(hours=i)
                                timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                                if timestamp not in dataset:
                                    dataset[timestamp] = []

                                dataset[timestamp].append((param,measures[1]))
                        except Exception:
                            try:
                                timestamp = datetime.datetime.strptime(measures[0],'%Y%m%d%H')
                                timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                                if timestamp not in dataset:
                                    dataset[timestamp] = []

                                dataset[timestamp] = (param,measures[1])
                            except Exception:
                                try:
                                    timestamp = datetime.datetime.strptime(measures[0],'%Y%m%d%H%M')
                                    if(timestamp.minute==0):
                                        average = ""
                                        if len(data_10_minutes) > 0:
                                            average = np.average(data_10_minutes)
                                        timestamp = timestamp - datetime.timedelta(hours=1)
                                        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                                        if timestamp not in dataset:
                                            dataset[timestamp] = []

                                        dataset[timestamp] = (param,average)
                                        if measures[1] != '-' and measures[1] != '':
                                            data_10_minutes = [float(measures[1])]
                                    else:
                                        if measures[1] != '-' and measures[1] != '':
                                            data_10_minutes.append(float(measures[1]))
                                except Exception:
                                    print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}][{file}] \033[91mNo Matching Timestamp Found\033[0m (Timestamp = {measures[0]})')
                                    break
            open_file.close()
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Created dataset for {name} ")
        # Write to temp file
        writeTempfile(dataset,headers[station_abbr[name]],station_abbr[name])
        # merge temp file with final one if exists or write it
def main(argv):
    """Main function of the script

    Parameters
    ----------
    argv : dict
        Parsed set of arguments passed when script called
    """
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting...")
    exit_code = 0
    inventory = False
    try:
      opts, args = getopt.getopt(argv,"ih")
    except getopt.GetoptError:
      print('idaweb.py')
      sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            print('idaweb.py')
            sys.exit(1)
        elif opt == '-i':
            createInventoryCSV()
            inventory = True

    if inventory == False:
        if os.path.exists(os.path.join(scraper_path,'headers.csv')) == True:
            exit_code = orderManipulation()
        else:
            exit_code = 1
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] The headers file doesn't exist. Please launch this script with the -i option to create it")

    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Done")
    sys.exit(exit_code)

if __name__ == "__main__":
    main(sys.argv[1:])
    
