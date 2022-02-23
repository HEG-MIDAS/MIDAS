import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

# Set Up Paths
root_path = os.path.dirname(os.getcwd())
scraper_path = os.path.join(root_path,'SABRA')
media_path = os.path.join(root_path,'media/SABRA')

# URL to scrap
URL = "https://www.ropag-data.ch/gechairmo/i_extr.php"
def scraper(URL,urbain_input,polluants_input,time_input,timelapse_input):
    # Go to URL
    driver.get(URL)
    # Get submit button and assert its value
    submit_button = driver.find_element(By.ID,"submit_button")
    assert submit_button.get_attribute('value') == "Extraire"
    # Download with params Urbain, PM 10, <DATE>, Journalière
    urbain = driver.find_element(By.CSS_SELECTOR,urbain_input).click()
    polluants = driver.find_element(By.CSS_SELECTOR,polluants_input).click()
    time = driver.find_element(By.CSS_SELECTOR,time_input).click()
    date_from = driver.find_element(By.CSS_SELECTOR,'table input[name="date_from"]').clear()
    date_from = driver.find_element(By.CSS_SELECTOR,'table input[name="date_from"]').send_keys("19.01.2021")
    date_to = driver.find_element(By.CSS_SELECTOR,'table input[name="date_to"]').clear()
    date_to = driver.find_element(By.CSS_SELECTOR,'table input[name="date_to"]').send_keys("22.02.2022")
    timelapse = driver.find_element(By.CSS_SELECTOR,timelapse_input).click()
    # Submit Form
    submit_button.click()
    # Find the Download button and download it
    csv_button = driver.find_element(By.CSS_SELECTOR,'a[title="Télécharger les données"]').click()
# Create Firefox Options
options = webdriver.FirefoxOptions()
options.headless = True
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.viewableInternally.enabledTypes", "")
options.set_preference("browser.download.useDownloadDir", True)
options.set_preference("browser.download.dir", media_path)
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv,application/octet-stream")
options.set_preference("pdfjs.disabled", True)
options.set_preference("browser.helperApps.neverAsk.openFile", "text/csv,application/octet-stream")
# Create Service for Firefox (Gecko) Driver Location
service = Service(os.path.join(scraper_path,'geckodriver'))
# Create Driver
driver = webdriver.Firefox(options=options,service=service)
# Scrap Urbain, PM10, <DATE>, Journalier
scraper(URL,'table input[value="urbain"]','table input[value="1"]','table input[value="autre"]','table input[value="quot"]')
# Scrap Urbain, PM2.5, <DATE>, Journalier
scraper(URL,'table input[value="urbain"]','table input[value="18"]','table input[value="autre"]','table input[value="quot"]')
# Scrap Urbain, NO2, <DATE>, Journalier
scraper(URL,'table input[value="urbain"]','table input[value="2"]','table input[value="autre"]','table input[value="hor"]')
# Scrap Urbain, O3, <DATE>, Journalier
scraper(URL,'table input[value="urbain"]','table input[value="3"]','table input[value="autre"]','table input[value="hor"]')
# Close Firefox Driver
driver.close()
