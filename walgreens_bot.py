from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from utils import send_message, clickButtonByInnerText, getTagByText
from itertools import cycle
import time, sys, winsound

url = 'https://www.walgreens.com/login.jsp?ru=%2Ffindcare%2Fvaccination%2Fcovid-19%2Fappointment%2Fscreening%3Fflow%3Drx'
url = 'https://www.walgreens.com/findcare/vaccination/covid-19/location-screening'
url = 'https://www.walgreens.com/findcare/vaccination/covid-19/appointment/screening'
# global variables for success
chosen_date = ""
chosen_time = ""

def get_location(browser):
    return browser.find_element_by_xpath("//section[@class='locationLeft']/section[1]/p[3]").get_attribute("innerText")

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

def get_appointment(date, argv, loc, time, second_dose=False):
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get(url)
    login(browser, argv[1], argv[2], argv[3])
    fill_out_survey(browser, argv[4], second_dose=second_dose)
    browser.find_element_by_class_name("continueBtn").click()
    time.sleep(1)
    browser.find_element_by_class_name("storeSearch").click()
    time.sleep(1)
    browser.find_elements_by_class_name("selectbtn")[0].click()
    browser.find_element_by_id("continueBtn").click()
    while get_location(browser)[-5:] != loc[-5:]:
        try: 
            browser.find_element_by_name("userStore").click()
        except:
            pass
        time.sleep(1)
        browser.find_element_by_id("search-address").clear()
        time.sleep(1)
        browser.find_element_by_id("search-address").send_keys(loc[-5:])
        time.sleep(1)
        browser.find_element_by_class_name("storeSearch").click()
        store_button = browser.find_elements_by_xpath(f"//section[@id='wag-store-info-0']/div[1]/section[3]/a[1]")
        store_button[0].click()
        time.sleep(5)
    Select(browser.find_element_by_id("select-dropdown")).select_by_value(time)


def fill_out_survey(browser, second_dose=False):
    browser.implicitly_wait(20)
    time.sleep(10)
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

def check_state_availability(browser):
    if "those eligible to receive a COVID-19" in browser.find_element_by_id("wag-body-main-container").get_attribute("innerHTML"):
        return True
    while True:
        time.sleep(2)
        browser.find_element_by_id("inputLocation").clear()
        browser.find_element_by_id("inputLocation").send_keys('Carbondale, IL')
        clickButtonByInnerText(browser, "Search")
        time.sleep(2)
        if not appointments_unavailable(browser):
            if service_unavailable(browser):
                return False
            else:
                return True
        time.sleep(5)


def confirm_eligibility(browser):
    if "those eligible to receive a COVID-19" in browser.find_element_by_id("wag-body-main-container").get_attribute("innerHTML"):
        return
    ActionChains(browser).send_keys(Keys.TAB).send_keys(Keys.ENTER).perform()
    time.sleep(5)
    browser.find_element_by_id("sq_100i_3").click()
    browser.find_element_by_id("eligibility-check").click()
    browser.find_element_by_class_name("sv_complete_btn").click()

def find_availability(browser, home_zips):
    for home_zip in cycle(home_zips):
        browser.find_element_by_id("search-address").clear()
        time.sleep(1)
        browser.find_element_by_id("search-address").send_keys(home_zip)
        time.sleep(1)
        browser.find_element_by_id("icon__search").click()
        time.sleep(1)
        if not find_p_with_text(browser, "We don't have any"):
            return True
        time.sleep(5)
        

def check_for_appointments(browser, argv, second_dose=False):
    if check_state_availability(browser):
        confirm_eligibility(browser)
        fill_out_survey(browser, second_dose=second_dose)
        if find_availability(browser, argv[4:]):
            winsound.Beep(500, 1000)
            return True
        if "Service unavailable" in browser.find_element_by_id("wag-body-main-container").get_attribute("innerHTML"):
            return False
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
            if check_for_appointments(browser, argv, second_dose=second_dose):
                try:
                    choose_appointment(browser)
                except:
                    pass
                break
        except Exception as e:
            print(e)
    message = "Found a Walgreens appointment!"
    print(message)
    try:
        send_message(message)
    except:
        pass

if __name__ == "__main__":
    login_and_check(sys.argv, second_dose=False)
        
