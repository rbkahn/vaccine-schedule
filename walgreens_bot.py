from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from twilio.rest import Client

import time, sys, winsound

home_zip = "60035"
account_sid = 'AC99bf6aa4ea27b5b4ac6711c30bb0ddc2' #twilio
auth_token = '984a666cb60039b199575eec091a4203' #twilio

def get_location(browser):
    return browser.find_element_by_xpath("//section[@class='locationLeft']/section[1]/p[3]").get_attribute("innerText")

def send_message(browser, message):
    client = Client(account_sid, auth_token)
    client.messages.create(
                     body=message,
                     from_='+14159497162',
                     to='+18477103770')

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

def get_appointment(date, loc, time):
    browser = webdriver.Chrome(ChromeDriverManager().install())
    url = 'https://www.walgreens.com/findcare/vaccination/covid-19/appointment/screening'
    browser.get(url)
    login(browser, username, password, security_answer)
    fill_out_survey(browser)
    browser.find_element_by_class_name("selectStorebtn").click()
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
    select_date(browser, date, "datepicker")
    Select(browser.find_element_by_id("select-dropdown")).select_by_value(time)

def check_times(browser, date):
    dropdown = Select(browser.find_element_by_id("select-dropdown"))
    for time in ["Before 8 am", "8 am - 12 pm", "12 pm - 3 pm", "3 pm - 6 pm", "6 pm - 9 pm", "After 9 pm"]:
        dropdown.select_by_value(time)
        slots = browser.find_element_by_class_name("slotssection")
        if "sorry" not in slots.find_elements_by_css_selector("*")[1].get_attribute("innerText"):
            message = str(date) + ' ' + time + ' ' + get_location(browser)
            print(message)
            send_message(browser, message)
            winsound.Beep(2500, 5000)
            get_appointment(date, get_location(browser), time)
            sys.exit()

def fill_out_survey(browser, second_dose=False):
    browser.implicitly_wait(10)
    browser.find_element_by_id('sq_101i_0').click()
    browser.find_element_by_id('sq_102i_1').click()
    browser.find_element_by_id('sq_104i_1').click()
    browser.find_element_by_id('sq_105i_1').click()
    browser.find_element_by_id('sq_106i_1').click()
    browser.find_elements_by_class_name("sv_complete_btn")[0].click()
    
    browser.find_element_by_id("hn-startVisitBlock-gb-terms").click()
    time.sleep(2)
    
    browser.find_element_by_id("insurance-yes").click()
    if second_dose:
        browser.find_element_by_id("dose2").click()
        browser.find_element_by_id("datepicker0").click()
        browser.find_element_by_xpath("//div[@id='ui-datepicker-div']/table[1]/tbody[1]/tr[4]/td[4]").click()
        Select(browser.find_element_by_id("vaccination-dropdown")).select_by_visible_text("Moderna")
    else:
        browser.find_element_by_id("dose1").click()
    browser.find_element_by_class_name("selectStorebtn").click()
    time.sleep(1)
    browser.find_element_by_class_name("storeSearch").click()
    time.sleep(1)
    browser.find_elements_by_class_name("selectbtn")[0].click()
    browser.find_element_by_id("continueBtn").click()

def select_date(browser, date, datepicker):
    browser.find_element_by_id(datepicker).click()
    try:
        cells = browser.find_elements_by_class_name("ui-state-default")
        for cell in cells:
            if cell.get_attribute("href") == "https://www.walgreens.com/findcare/vaccination/covid-19/appointment/date-time#" and cell.get_attribute("innerText") == str(date):
                cell.click()
                break
    except:
        print(date)
        print(get_location(browser))

def check_dates(browser):
    for date in range(time.localtime().tm_mday + 6, 24, -1):
        select_date(browser, date, "datepicker")
        check_times(browser, date)

def check_cities(browser):
    for city in range(0, 40):
            browser.find_element_by_name("userStore").click()
            for _ in range(5):
                browser.find_element_by_class_name("storeSearch").send_keys(Keys.DOWN)
            store_button = browser.find_elements_by_xpath(f"//section[@id='wag-store-info-{city}']/div[1]/section[3]/a[1]")
            store_button[0].click()
            check_dates(browser)

def select_zip(browser, zip):
    while get_location(browser)[-5:-2] != str(zip)[-5:-2]:
        try: 
            browser.find_element_by_name("userStore").click()
        except:
            pass
        time.sleep(1)
        browser.find_element_by_id("search-address").clear()
        time.sleep(1)
        browser.find_element_by_id("search-address").send_keys(zip)
        time.sleep(1)
        browser.find_element_by_class_name("storeSearch").click()
        store_button = browser.find_elements_by_xpath(f"//section[@id='wag-store-info-0']/div[1]/section[3]/a[1]")
        store_button[0].click()
        time.sleep(5)

def check_for_appointments(browser):
    fill_out_survey(browser)
    select_zip(browser, home_zip)
    while (True):
        check_cities(browser)

if __name__ == "__main__":
    username = sys.argv[1]
    password = sys.argv[2]
    security_answer = sys.argv[3]
    browser = webdriver.Firefox(executable_path=r'C:\usr\local\bin\geckodriver.exe')
    url = 'https://www.walgreens.com/findcare/vaccination/covid-19/appointment/screening'

    while True:
        browser.get(url)
        try:
            login(browser, username, password, security_answer)
        except:
            pass
        try:
            check_for_appointments(browser)
        except Exception as e:
            #winsound.Beep(1500, 500)
            print(e)
            time.sleep(5)
            
            
        
