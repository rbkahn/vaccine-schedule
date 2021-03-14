from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from utils import send_message, clickButtonByInnerText, getTagByText
from itertools import cycle
import time, sys, winsound

url = 'https://www.walgreens.com/login.jsp?ru=%2Ffindcare%2Fvaccination%2Fcovid-19%2Fappointment%2Fscreening%3Fflow%3Drx'
url = 'https://www.walgreens.com/findcare/vaccination/covid-19/location-screening'
url = 'https://www.walgreens.com/findcare/vaccination/covid-19/appointment/screening'
# global variables for success
chosen_date = ""
chosen_time = ""

def login(browser, username, password, security_answer):
    browser.find_element_by_name("username").send_keys(username)
    browser.find_element_by_name("password").send_keys(password)
    browser.find_element_by_id("submit_btn").click()
    try:
        time.sleep(3)
        browser.find_element_by_id("radio-security").click()
        browser.find_element_by_id("optionContinue").click()     
        browser.find_element_by_name("SecurityAnswer").send_keys(security_answer)
        browser.find_element_by_id("validate_security_answer").click()
    except:
        pass

def fill_out_survey(browser, second_dose=False):
    browser.implicitly_wait(20)
    time.sleep(5)
    browser.find_element_by_id('sq_100i_1').click()
    browser.find_element_by_id('sq_102i_1').click()
    browser.find_element_by_id('sq_103i_1').click()
    browser.find_element_by_id('sq_104i_1').click()
    browser.find_elements_by_class_name("sv_complete_btn")[0].click()
    browser.find_element_by_id("hn-startVisitBlock-gb-terms").click()
    time.sleep(2)
    Select(browser.find_element_by_id("race-dropdown")).select_by_visible_text("White")
    Select(browser.find_element_by_id("ethnicity-dropdown")).select_by_visible_text("Decline to answer")
    if second_dose:
        browser.find_element_by_id("dose2").click()
        browser.find_element_by_id("datepicker0").click()
        browser.find_element_by_xpath("//div[@id='ui-datepicker-div']/table[1]/tbody[1]/tr[5]/td[5]").click()
        Select(browser.find_element_by_id("vaccination-dropdown")).select_by_visible_text("Moderna")
    else:
        browser.find_element_by_id("dose1").click()
    clickButtonByInnerText(browser, "Schedule Now")

def find_p_with_text(browser, text):
    return getTagByText(browser, "p", text)

def service_unavailable(browser):
    return appointments_unavailable(browser) or find_p_with_text(browser, "Service temporarily unavailable")

def appointments_unavailable(browser):
    return find_p_with_text(browser, "Appointments unavailable")

def check_state_availability(browser, locations):
    if "those eligible to receive a COVID-19" in browser.find_element_by_id("wag-body-main-container").get_attribute("innerHTML"):
        return True
    for location in cycle(locations):
        time.sleep(2)
        browser.find_element_by_id("inputLocation").clear()
        browser.find_element_by_id("inputLocation").send_keys(location)
        clickButtonByInnerText(browser, "Search")
        time.sleep(2)
        if not appointments_unavailable(browser):
            if service_unavailable(browser):
                return False
            else:
                print(f"Found availability in {location}")
                return True
        time.sleep(3)


def confirm_eligibility(browser):
    if "those eligible to receive a COVID-19" in browser.find_element_by_id("wag-body-main-container").get_attribute("innerHTML"):
        return
    ActionChains(browser).send_keys(Keys.TAB).send_keys(Keys.ENTER).perform()
    time.sleep(5)
    browser.find_element_by_id("sq_100i_3").click()
    browser.find_element_by_id("eligibility-check").click()
    browser.find_element_by_class_name("sv_complete_btn").click()

def enter_zip(browser, zip):
    browser.find_element_by_id("search-address").clear()
    time.sleep(1)
    browser.find_element_by_id("search-address").send_keys(zip)
    time.sleep(1)
    browser.find_element_by_id("icon__search").click()
    time.sleep(1)

def find_availability(browser, home_zips):
    for zip in cycle(home_zips):
        enter_zip(browser, zip)
        if not find_p_with_text(browser, "We don't have any"):
            time.sleep(1)
            if find_p_with_text(browser, "Service unavailable"):
                return False
            time.sleep(2)
            enter_zip(browser, zip)
            if not find_p_with_text(browser, "We don't have any"):
                winsound.Beep(500, 1000)
                return zip
        time.sleep(5)

def check_for_appointments(browser, argv, second_dose=False):
    if check_state_availability(browser, ['Carbondale, IL', 'Springfield, IL'] + argv[4:]):
        confirm_eligibility(browser)
        fill_out_survey(browser, second_dose=second_dose)
        return find_availability(browser, argv[4:])
    else:
        return False

def choose_appointment(browser, second_dose=False):
    browser.find_elements_by_class_name('timeSlot')[0].click()
    buttons = browser.find_elements_by_class_name("confirmDoseTimeslots")  
    for button in buttons:
        if not "btn__disabled" in button.get_attribute("className"):
            button.click()
    if not second_dose:
        browser.find_elements_by_class_name('timeSlot')[0].click()
    buttons = browser.find_elements_by_class_name("confirmDoseTimeslots")  
    for button in buttons:
        if not "btn__disabled" in button.get_attribute("className"):
            button.click()    

def login_and_check(argv, second_dose=False):
    username = argv[1]
    password = argv[2]
    security_answer = argv[3]
    browser = webdriver.Firefox(executable_path=r'C:\usr\local\bin\geckodriver.exe')
    while True:
        browser.get(url)
        try:
            login(browser, username, password, security_answer)
        except:
            pass
        try:
            zip = check_for_appointments(browser, argv, second_dose=second_dose)
            if zip:
                try:
                    choose_appointment(browser)
                except:
                    pass
                break
        except Exception as e:
            print(e)
    message = f"Found a Walgreens appointment in {zip}!"
    print(message)
    try:
        send_message(message)
    except:
        pass

if __name__ == "__main__":
    login_and_check(sys.argv, second_dose=False)
        
