from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time, sys, winsound
from utils import clickButtonByInnerText, send_message

url = 'https://www.mhealthappointments.com/covidappt'

def check_for_appointments(browser, zip):
    browser.get(url)
    browser.implicitly_wait(5)
    time.sleep(4)
    browser.find_element_by_id('fiftyMile-covid_vaccine_search').click()
    browser.find_element_by_id('covid_vaccine_search_input').send_keys(zip)
    while True:
        browser.find_element_by_id('covid_vaccine_search_input').send_keys(Keys.ENTER)
        try:
            browser.find_element_by_id('attestation_1002').click()
            browser.find_element_by_xpath('//div[@id="covid_vaccine_search_questions_content"]/div[2]/button[1]').click()
            break
        except:
            pass
    Select(browser.find_element_by_id("appointmentType-type")).select_by_visible_text("COVID Vaccine Dose 1 Appt")
    clickButtonByInnerText(browser, "Start Set up")
    time.sleep(4)
    browser.execute_script("window.scrollTo(0, 500)") 
    browser.find_element_by_xpath("//div[@id='covid19-reg-v2']/div[1]/div[2]/div[1]/div[2]/div[1]/div[4]/div[2]/div[1]/div[1]/button[1]").click()
    Select(browser.find_element_by_id('item-type'))
    select = Select(browser.find_element_by_id("item-type"))
    options = select.options
    while True:
        for index in range(0, len(options) - 1):
            select.select_by_index(index)
            time.sleep(1)
            html = browser.find_element_by_xpath("//div[@id='covid19-reg-v2']/div[1]/div[3]/div[1]/div[2]/div[1]/div[3]/div[1]").get_attribute("innerText")
            while "Loading" in html:
                time.sleep(1)
                html = browser.find_element_by_xpath("//div[@id='covid19-reg-v2']/div[1]/div[3]/div[1]/div[2]/div[1]/div[3]/div[1]").get_attribute("innerText")
            if "Currently, all appointments are booked in your area" in html:
                return False
            if "There is no availability" not in html:
                return True

if __name__ == "__main__":
    browser = webdriver.Firefox(executable_path=r'C:\usr\local\bin\geckodriver.exe')
    while True:
        try:
            if check_for_appointments(browser, sys.argv[4]):
                break
        except Exception as e:
            print(e)
        time.sleep(30)
    winsound.Beep(500, 1000)
    send_message("Found a Jewel appointment")
    