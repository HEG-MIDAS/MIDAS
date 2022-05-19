import os
import time
import re
import sys
import getopt
import numpy as np
from sys import platform
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.chrome.service import Service as sv
from selenium.webdriver.support import expected_conditions as EC
from merge_csv_by_date_package import merge_csv_by_date
from collections import OrderedDict
from datetime import datetime, timedelta

# Set Up Paths
## Path of Scraper
scraper_path = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
## Root of Project
root_path = os.path.join(scraper_path,'..')
## Path of Media
media_path = os.path.join(root_path,'media')

# URL to scrap
URL = "https://www.ropag-data.ch/gechairmo/i_extr.php"

# Function to write logs.
## Needs to define how
def logs(str = ''):
    """Add a log line to a log file in the directory. The log line is only composed of the date

    """
    print(os.path.join(root_path,'logs/SABRA.txt'))
    with open(os.path.join(root_path,'logs/SABRA.txt'), 'a') as file:
        if str == '':
            file.write(time.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            file.write(str)

# Sort data by date
def sortByDate(data: dict) -> OrderedDict:
    """Sort a Dictionary by date

    Parameters
    ----------
    data : dict
        Dictionary to sort

    Returns
    -------
    OrderedDict
        the sorted Dictionary as a OrderedDict
    """
    # Create a sorted list and transform it as an OrderedDict
    ordered_data = OrderedDict(sorted(data.items(), key = lambda x:time.strptime(x[0], '%Y-%m-%d %H:%M:%S'), reverse=False))
    return ordered_data

# Function to write files
def dataToFiles(data: dict):
    """Write a Dictionary into files

    Parameters
    ----------
    data : dict
        Dictionary to write
    """
    for k in data:
        # Sort the datas by Date (Not correctly sorted by default)
        data[k] = sortByDate(data[k])
        # Open temp file
        f = open(os.path.join(scraper_path,"temp-"+k+".csv"), 'a+')
        # Write header (HardCoded)
        f.write("localtime,PM2.5*,PM10*,NO2,O3\n")
        # Loop datas
        for e in data[k]:
            # Write Date
            text = str(e)+","
            # If value for polluant 1, add it
            if 1 in data[k][e]:
                if(data[k][e] == ''):
                    text += np.NaN
                else:
                    text += data[k][e][1]
            # Always add the  , to separate
            text += ","
            # If value for polluant 2, add it
            if 2 in data[k][e]:
                if(data[k][e] == ''):
                    text += np.NaN
                else:
                    text += data[k][e][2]
            # Always add the  , to separate
            text += ","
            # If value for polluant 3, add it
            if 3 in data[k][e]:
                if(data[k][e] == ''):
                    text += np.NaN
                else:
                    text += data[k][e][3]
            # Always add the  , to separate
            text += ","
            # If value for polluant 4, add it
            if 4 in data[k][e]:
                if(data[k][e] == ''):
                    text += np.NaN
                else:
                    text += data[k][e][4]
            # Add a newline or else everything is on the same line
            text += "\n"
            # Write the line on the file
            f.write(text)
        # Close file
        f.close()
        # Logs in terminal
        print("Written "+os.path.join(scraper_path,"temp-"+k+".csv"))
        # At the end, use merge to create final file
        merge_csv_by_date.merge_csv_by_date(os.path.join(media_path,'transformed/SABRA/{0}.csv'.format(k)),os.path.join(scraper_path,"temp-{0}.csv".format(k)), '%Y-%m-%d %H:%M:%S')
        print('Written {0}\n'.format(os.path.join(media_path,'transformed/SABRA/{0}.csv'.format(k))))
# Function to manipulate the downloaded files
def manipulate():
    """Take the downloaded file and apply and sort it into a Dictionary

    """
    headerOrder = {'Date':0,'PM2.5':1,'PM10':2,'NO2':3,"O3":4}
    dataTable = {}
    # Loop through all files in the scraper folder
    for f in os.listdir(scraper_path):
        # If files is a CSV
        if f.find('.csv') >-1 and f.find('temp') < 0:
            # Set up variables for each files
            polluant=""
            typologie=""
            stations=[]
            duplicate = False
            # Open File
            file = open(os.path.join(scraper_path,f))
            # Loop each line of file
            for x in file:
                # Strip whitespaces
                x = x.strip()
                # If the line has 'Typologie'
                if x.find('Typologie')>-1:
                    typologie = x.strip().split("Typologie:  ")[1]
                # If line has 'Polluant'
                elif x.find('Polluant')>-1:
                    polluant = re.search("\((.*?)\)",x.strip().split("Polluant:  ")[1]).group(1)
                # If line has 'Date'
                elif x.find('Date')>-1:
                    # Do it for Hourly
                    stations = x.strip().split("Date  [GMT+1]")
                    # Then Daily if Hourly didn't split
                    if(len(stations) == 1):
                        stations = x.strip().split("Date")
                        duplicate = True
                    # Remove whitespace and split
                    stations = stations[1].strip().split(";")
                    # Pop first element which is the date
                    stations.pop(0)
                    # Format it with the 'Typologie'
                    stations = ['{0}_{1}'.format(element,typologie) for element in stations]
                    # Set the dataTable
                    for i in range(0,len(stations)):
                        if stations[i] not in dataTable:
                            dataTable[stations[i]] = {}
                # Else if date isn't an empty string (And we skip the unit one)
                elif x != "" and x.find('Unité') < 0:
                    # Split the datas
                    data = x.strip().strip().split(";")
                    # Loop through them
                    for i in range(1,len(data)):
                        # If the data are hourly to begin with
                        if(duplicate == False):
                            d = '{0}:00'.format(data[0].strip())
                            if d not in dataTable[stations[i-1]]:
                                dataTable[stations[i-1]][d] = {}
                            dataTable[stations[i-1]][d][headerOrder[polluant]] = data[i]
                        # Otherwise need to create them by duplication
                        else:
                            for h in range(0,24):
                                # Ternary condition
                                d = '{0}  0{1}:00:00'.format(data[0],h) if h < 10 else '{0}  {1}:00:00'.format(data[0],h)
                                if d not in dataTable[stations[i-1]]:
                                    dataTable[stations[i-1]][d] = {}
                                dataTable[stations[i-1]][d][headerOrder[polluant]] = data[i]
            format_date = ' %Y-%m-%d %H:%M '
            print(polluant)
            if polluant in ['PM10', 'PM2.5']:
                format_date = '%Y-%m-%d'

            # Write the data in the original files
            merge_csv_by_date.merge_csv_by_date(os.path.join(media_path,'original/SABRA/{0}_{1}.csv'.format(typologie,polluant)),os.path.join(scraper_path,f), format_date)
            print('Written {0}'.format(os.path.join(media_path,'original/SABRA/{0}_{1}.csv'.format(typologie,polluant))))
    print('')
    dataToFiles(dataTable)
# Clean Folder Script
def clean():
    """Clean folders

    """
    for f in os.listdir(scraper_path):
        # If files is a CSV
        if f.find('.csv') >-1:
            os.remove(os.path.join(scraper_path,f))

# Scrap website
def scraper(URL:str,driver,urbain_input:str,polluants_input:str,time_input:str,start_date:str,end_date:str,timelapse_input:str):
    """Download SABRA data with selenium

    Parameters
    ----------
    URL : str
        link to the webpage
    driver: webdriver.Firefox or webdriver.Chrome
        firefox webbrowser driver options
    urbain_input:str
        Value for typologie imput
    polluants_input:str
        Value for polluant imput
    time_input:str
        Value for time imput
    start_date:str
        Starting Date (%d.%m.%Y)
    end_date:str
        Ending Date (%d.%m.%Y)
    timelapse_input:str
        Value for time interval
    """
    # Go to URL
    driver.get(URL)
    # Get submit button and assert its value
    submit_button = driver.find_element(By.ID,"submit_button")
    assert submit_button.get_attribute('value') == "Extraire"
    # Set params in Form
    arr = ['table input[value="'+urbain_input+'"]','table input[value="'+polluants_input+'"]','table input[value="'+time_input+'"]',start_date,end_date,'table input[value="'+timelapse_input+'"]']
    # Typologie
    for el in arr:
        if(el != start_date and el != end_date):
            try:
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,el))).location_once_scrolled_into_view
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,el))).click()
            except ElementClickInterceptedException:
                fnd = driver.find_element(By.CSS_SELECTOR,el)
                driver.execute_script ("arguments[0].click();",fnd)
        elif ((el == start_date or el == end_date) and start_date == end_date):
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'table input[name="date_from"]'))).location_once_scrolled_into_view
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'table input[name="date_from"]'))).clear()
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'table input[name="date_from"]'))).send_keys(start_date)
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'table input[name="date_to"]'))).location_once_scrolled_into_view
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'table input[name="date_to"]'))).clear()
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'table input[name="date_to"]'))).send_keys(end_date)
        elif el == start_date:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'table input[name="date_from"]'))).location_once_scrolled_into_view
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'table input[name="date_from"]'))).clear()
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'table input[name="date_from"]'))).send_keys(start_date)
        elif el == end_date:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'table input[name="date_to"]'))).location_once_scrolled_into_view
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'table input[name="date_to"]'))).clear()
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'table input[name="date_to"]'))).send_keys(end_date)

    # Submit Form
    driver.find_element(By.ID,"submit_button").click()
    # Find the Download button and download it
    csv_button = driver.find_element(By.CSS_SELECTOR,'a[title="Télécharger les données"]').click()
    # Print Debug for download
    print("Downloaded "+urbain_input+" "+polluants_input)
    # Need to wait of website can crash
    time.sleep(2)

def firefoxDriver():
    """Create and return a driver
       Returns
       -------
       webdriver.Firefox
          the driver using Firefox
    """
    # Create Firefox Options needed to autodownload
    options = webdriver.FirefoxOptions()
    options.headless = True
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.viewableInternally.enabledTypes", "")
    options.set_preference("browser.download.useDownloadDir", True)
    options.set_preference("browser.download.dir", scraper_path)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv,application/octet-stream")
    options.set_preference("pdfjs.disabled", True)
    options.set_preference("browser.helperApps.neverAsk.openFile", "text/csv,application/octet-stream")
    # Create Service for Firefox (Gecko) Driver Location
    service = None
    if platform == "darwin":
        service = Service(os.path.join(scraper_path,'geckodriver_osx'))
    elif platform == "linux" or platform == "linux2":
        service = Service(os.path.join(scraper_path,'geckodriver_linux'))
    # Create Driver
    return webdriver.Firefox(options=options,service=service)

def chromeDriver():
    """Create and return a driver
       Returns
       -------
       webdriver.Chrome
          the driver using Chrome
    """
    options = webdriver.ChromeOptions()
    options.headless = True
    # Specify Download folder
    prefs = {"download.default_directory" : scraper_path}
    options.add_experimental_option("prefs",prefs)
    service = None
    if platform == "darwin":
        service = sv(os.path.join(scraper_path,'chromedriver_osx'))
    elif platform == "linux" or platform == "linux2":
        service = sv(os.path.join(scraper_path,'chromedriver_linux'))
    # Create Driver
    return webdriver.Chrome(options=options,service=service)
# Setup the headless browser (Using Firefox/Gecko)
def download(s:str,e:str,b:str):
    """Download Wrapper Function

    Parameters
    ----------
    s : str
        Starting Date (%d.%m.%Y)
    e: str
        Ending Date (%d.%m.%Y)
    b: str
        Browser Value (firefox or chrome)
    """
    if b == 'firefox':
        driver = firefoxDriver()
    elif b == 'chrome':
        driver = chromeDriver()
    else:
        print("No browser defined")
        try:
            print("Trying Firefox")
            driver = firefoxDriver()
        except:
            print("Couldn't download with Firefox trying Chrome")
            driver = chromeDriver()
    # Array of params
    urbanArea = ['urbain','suburbain','rural']
    pollTimeStep = {'1':'quot','18':'quot','2':'hor','3':'hor'}
    # Loop through both array to get all files
    for u in urbanArea:
        for k, v in pollTimeStep.items():
            scraper(URL,driver,u,k,'autre',s,e,v)
    # Close Firefox Driver
    driver.close()

def operation(sD:str,eD:str,b:str):
    """Wrapper Function

    Parameters
    ----------
    sD : str
        Starting Date (%d.%m.%Y)
    eD: str
        Ending Date (%d.%m.%Y)
    b: str
        Browser Value (firefox or chrome)
    """
    # Download for current time diff
    download(sD,eD,b)
    # Manipulating
    manipulate()
    # Clean folder
    clean()

def main(argv):
    """Main Function

    Parameters
    ----------
    argv: sys.argv
        Parameters given to the script
    """
    exit_code = 0
    # Print Debug for Start
    print("Starting "+time.strftime("%Y-%m-%d %H:%M:%S"))
    start_date =  datetime.now().date()
    end_date = datetime.now().date()
    browser = None
    try:
      opts, args = getopt.getopt(argv,"cfhs:e:",["start_date=","end_date=","chrome","firefox"])
    except getopt.GetoptError:
      print('sabra.py -s <start_date> -e <end_date>')
      sys.exit(1)
    for opt, arg in opts:
      if opt == '-h':
         print('sabra.py -s <start_date> -e <end_date>')
         sys.exit(1)
      elif opt in ("-s", "--start_date"):
         start_date = datetime.strptime(arg,'%Y-%m-%d').date()
      elif opt in ("-e", "--end_date"):
         end_date = datetime.strptime(arg,'%Y-%m-%d').date()
      elif opt in ("-c","--chrome"):
         browser = 'chrome'
      elif opt in ("-f","--firefox"):
         browser = 'firefox'

    if(start_date > end_date):
        print('The end date is inferior to the start date !')
        exit(1)

    if(end_date - start_date > timedelta(days=365)):
        print('The time difference is greater than 365 days !')
        timeDiff = (end_date - start_date)
        reducedDiff = np.intc(np.ceil(timeDiff/timedelta(days=365)))
        tempStartDate = start_date
        tempEndDate = start_date + timedelta(days=365)
        for x in range(0,reducedDiff):
            str_start_date = tempStartDate.strftime('%d.%m.%Y')
            str_end_date = tempEndDate.strftime('%d.%m.%Y')
            print('Getting Datas from '+str_start_date+' to '+str_end_date)
            try:
                operation(str_start_date,str_end_date,browser)
            except:
                print('An error occured for '+tempStartDate.strftime('%Y-%m-%d')+'/'+tempEndDate.strftime('%Y-%m-%d'))
                exit_code += 1
                logs('-s '+tempStartDate.strftime('%Y-%m-%d')+' -e '+tempEndDate.strftime('%Y-%m-%d')+'\n')
            tempStartDate = tempEndDate
            tempEndDate = tempStartDate + timedelta(days=365)
            if(end_date < tempEndDate):
                tempEndDate = end_date
    else:
        start_date_edit = start_date.strftime('%d.%m.%Y')
        end_date_edit = end_date.strftime('%d.%m.%Y')
        try:
            operation(start_date_edit,end_date_edit,browser)
        except:
            print('An error occured for '+start_date.strftime('%Y-%m-%d')+'/'+end_date.strftime('%Y-%m-%d'))
            exit_code += 1
            logs('-s '+start_date.strftime('%Y-%m-%d')+' -e '+end_date.strftime('%Y-%m-%d')+'\n')
    # Clean folder (in case of)
    clean()
    # Print Debug for End
    print("Done "+time.strftime("%Y-%m-%d %H:%M:%S"))
    exit(exit_code)

if __name__ == "__main__":
    main(sys.argv[1:])
