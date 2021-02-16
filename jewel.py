from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time, sys, winsound

url = 'https://www.mhealthappointments.com/covidappt'

def getButtonByInnerText(browser, innerText):
    buttons = browser.find_elements_by_tag_name('button')
    for button in buttons:
        if button.get_attribute("innerText") == innerText:
            return button

if __name__ == "__main__":
    browser = webdriver.Firefox(executable_path=r'C:\usr\local\bin\geckodriver.exe')
    browser.get(url)
    browser.implicitly_wait(5)
    time.sleep(6)
    browser.find_element_by_id('thirtyMile-covid_vaccine_search').click()
    browser.find_element_by_id('covid_vaccine_search_input').send_keys("60657")
    while True:
        browser.find_element_by_id('covid_vaccine_search_input').send_keys(Keys.ENTER)
        try:
            browser.find_element_by_id('attestation_1002').click()
            browser.find_element_by_xpath('//div[@id="covid_vaccine_search_questions_content"]/div[2]/button[1]').click()
            break
        except:
            pass
    Select(browser.find_element_by_id("appointmentType-type")).select_by_visible_text("COVID Vaccine Dose 1 Appt")
    getButtonByInnerText(browser, "Start Set up").click()
    time.sleep(4)
    getButtonByInnerText(browser, "Next").click()
    pass