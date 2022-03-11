import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

# Set Up Paths
## Root of Project
root_path = os.path.dirname(os.getcwd())
## Path of Scraper
scraper_path = os.path.join(root_path,'SABRA')
## Path of Media
media_path = os.path.join(root_path,'media/SABRA')

# URL to scrap
URL = "https://www.ropag-data.ch/gechairmo/i_extr.php"

# Function to write logs.
## Needs to define how
def logs():
    with open(os.path.join(scraper_path,'log.txt'), 'a') as file:
        file.write(time.strftime('%Y-%m-%d %H:%M:%S'))

# Function to manipulate the downloaded files
def manipulate():
    # Loop through all files in the scraper folder
    for f in os.listdir(scraper_path):
        # If files is a CSV
        if f.find('.csv') >-1 and f.find('temp') < 0:
            # Merge Script Here to create original file
            # Set up variables for each files
            polluant=""
            typologie=""
            stations=[]
            tempFiles = []
            # Open File
            file = open(f)
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
                # If line has 'Date [GMT+1]' => Daily Datas
                elif x.find('Date  [GMT+1]')>-1:
                    stations = x.strip().split("Date  [GMT+1]")[1].strip().split(";")
                    stations.pop(0)
                    temp = stations
                    stations = [os.path.join(media_path,'{0}-{1}.csv'.format(element,typologie)) for element in stations]
                    tempFiles = [os.path.join(scraper_path,'temp-{0}-{1}.csv'.format(element,typologie)) for element in temp]
                    ## Need to add something to open/create/check file?!
                # If line has 'Date' => Weekly Datas
                elif x.find('Date')>-1:
                    stations = x.strip().split("Date")[1].strip().split(";")
                    stations.pop(0)
                    temp = stations
                    stations = [os.path.join(media_path,'{0}-{1}.csv'.format(element,typologie)) for element in stations]
                    tempFiles = [os.path.join(scraper_path,'temp-{0}-{1}.csv'.format(element,typologie)) for element in temp]
                    ## Need to add something to open/create/check file?!
                # Else if date isn't an empty string
                elif x != "" and x.find('Unité') < 0:
                    for tF in tempFiles:
                        if(os.path.isfile(tF) == False):
                            f = open(tF, 'w')
                            f.write("Date [GMT+1];PM2.5;PM10;NO2;03\n")
                            f.close()
                    data = x.strip().strip().split(";")
                    for i in range(1,len(data)):
                        f = open(tempFiles[i-1], 'a+')
                        f.write(data[0]+";"+data[i]+"\n")
                        f.close()
# Clean Folder Script
def clean():
    for f in os.listdir(scraper_path):
        # If files is a CSV
        if f.find('.csv') >-1 and f.find('temp') > -1:
            os.remove(f)

# Scrap website
def scraper(URL,urbain_input,polluants_input,time_input,timelapse_input):
    # Go to URL
    driver.get(URL)
    # Get submit button and assert its value
    submit_button = driver.find_element(By.ID,"submit_button")
    assert submit_button.get_attribute('value') == "Extraire"
    # Set params in Form
    driver.find_element(By.CSS_SELECTOR,'table input[value="'+urbain_input+'"]').click()
    driver.find_element(By.CSS_SELECTOR,'table input[value="'+polluants_input+'"]').click()
    driver.find_element(By.CSS_SELECTOR,'table input[value="'+time_input+'"]').click()
    driver.find_element(By.CSS_SELECTOR,'table input[name="date_from"]').clear()
    driver.find_element(By.CSS_SELECTOR,'table input[name="date_from"]').send_keys("19.01.2021")
    driver.find_element(By.CSS_SELECTOR,'table input[name="date_to"]').clear()
    driver.find_element(By.CSS_SELECTOR,'table input[name="date_to"]').send_keys("22.02.2022")
    driver.find_element(By.CSS_SELECTOR,'table input[value="'+timelapse_input+'"]').click()
    # Submit Form
    driver.find_element(By.ID,"submit_button").click()
    # Find the Download button and download it
    csv_button = driver.find_element(By.CSS_SELECTOR,'a[title="Télécharger les données"]').click()
    # Print Debug for download
    print("Downloaded "+urbain_input+" "+polluants_input)
    # Need to wait of website can crash
    time.sleep(2)

# Setup the headless browser (Using Firefox/Gecko)
def download():
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
    service = Service(os.path.join(scraper_path,'geckodriver'))
    # Create Driver
    driver = webdriver.Firefox(options=options,service=service)
    # Array of params
    urbanArea = ['urbain','suburbain','rural']
    pollTimeStep = {'1':'quot','18':'quot','2':'hor','3':'hor'}
    # Loop through both array to get all files
    for u in urbanArea:
        for k, v in pollTimeStep.items():
            scraper(URL,u,k,'autre',v)
    # Close Firefox Driver
    driver.close()
# Debug Start
print("Starting "+time.strftime("%Y-%m-%d %H:%M:%S"))
# Download Function
# download()
# Manipulating
manipulate()
# Clean folder
# clean()
# Print Debug for End
print("Done "+time.strftime("%Y-%m-%d %H:%M:%S"))
