from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time, sys, winsound
from utils import clickButtonByInnerText, send_message

url = 'https://www.marianos.com/rx/covid-eligibility'

def check_for_appointments(browser, zip):
    browser.find_element_by_xpath("//div[@class='LocationDatePicker-formFields']/div[1]/div[1]/input[1]").send_keys(zip)
    Select(browser.find_element_by_xpath("//div[@class='LocationDatePicker-formFields']/div[2]/div[1]/select[1]")).select_by_visible_text("20 miles")
    badges = browser.find_elements_by_class_name("kds-Badge-wrapper")
    for badge in badges:
        if badge.get_attribute("innerText") != "0":
            return True
    return False

n = 3
def fill_out_survey(browser):
    browser.get(url)
    browser.implicitly_wait(5)
    time.sleep(4)
    clickButtonByInnerText(browser, "I Agree")
    time.sleep(n)
    clickButtonByInnerText(browser, "No")
    ActionChains(browser).send_keys(Keys.TAB).perform()
    Select(browser.find_element_by_class_name("kds-Select")).select_by_visible_text("IL")
    time.sleep(n)
    ActionChains(browser).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.SPACE).perform()
    time.sleep(n)
    ActionChains(browser).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.SPACE).perform()
    #clickButtonByInnerText(browser, "No", 3)
    time.sleep(n)
    #browser.find_elements_by_class_name("kds-Input")[1].click()
    ActionChains(browser).send_keys(Keys.TAB).send_keys("08141945").send_keys(Keys.TAB).send_keys(Keys.ENTER).perform()
    time.sleep(n)
    ActionChains(browser).send_keys(Keys.TAB).send_keys(Keys.SPACE).perform()



if __name__ == "__main__":
    browser = webdriver.Firefox(executable_path=r'C:\usr\local\bin\geckodriver.exe')
    while True:
        try:
            fill_out_survey(browser)
            if check_for_appointments(browser, sys.argv[4]):
                winsound.Beep(500, 1000)
                send_message("Found a Jewel appointment")
        except Exception as e:
            print(e)
        time.sleep(30)