from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from twilio.rest import Client
import time, sys, winsound

home_zip = "60035"
with open("twilio-credentials.txt") as fp:
    lines = fp.readlines()
    account_sid = lines[0]
    auth_token = lines[1]

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

def get_appointment(date, argv, loc, time, second_dose=False):
    browser = webdriver.Chrome(ChromeDriverManager().install())
    url = 'https://www.walgreens.com/findcare/vaccination/covid-19/appointment/screening'
    browser.get(url)
    login(browser, argv[1], argv[2], argv[3])
    fill_out_survey(browser, argv[4], second_dose=second_dose)
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

def check_times(browser, argv, second_dose=False):
    dropdown = Select(browser.find_element_by_id("select-dropdown"))
    for time in ["Before 8 am", "8 am - 12 pm", "12 pm - 3 pm", "3 pm - 6 pm", "6 pm - 9 pm", "After 9 pm"]:
        dropdown.select_by_value(time)
        slots = browser.find_element_by_class_name("slotssection")
        if "sorry" not in slots.find_elements_by_css_selector("*")[1].get_attribute("innerText"):
            date = browser.find_element_by_id("datepicker").get_attribute("value")
            message = date + ' ' + time + ' ' + get_location(browser)
            print(message)
            send_message(browser, message)
            winsound.Beep(2500, 5000)
            get_appointment(date, argv, get_location(browser), time, second_dose=second_dose)
            sys.exit()

def fill_out_survey(browser, home_zip, second_dose=False):
    browser.implicitly_wait(10)
    browser.find_element_by_id('sq_101i_0').click()
    browser.find_element_by_id('sq_102i_1').click()
    browser.find_element_by_id('sq_104i_1').click()
    browser.find_element_by_id('sq_105i_1').click()
    browser.find_element_by_id('sq_106i_1').click()
    browser.find_elements_by_class_name("sv_complete_btn")[0].click()
    
    browser.find_element_by_id("hn-startVisitBlock-gb-terms").click()
    time.sleep(2)
    
    try:
        browser.find_element_by_id("insurance-yes").click()
    except:
        time.sleep(5)
        try:
            browser.find_element_by_id("insurance-yes").click()
        except:
            pass
    if second_dose:
        browser.find_element_by_id("dose2").click()
        browser.find_element_by_id("datepicker0").click()
        browser.find_element_by_xpath("//div[@id='ui-datepicker-div']/table[1]/tbody[1]/tr[4]/td[4]").click()
        Select(browser.find_element_by_id("vaccination-dropdown")).select_by_visible_text("Moderna")
    else:
        browser.find_element_by_id("dose1").click()
    browser.find_element_by_class_name("selectStorebtn").click()
    
    time.sleep(1)
    if len(browser.find_element_by_id("search-address").get_attribute("value").strip()) == 0:
        browser.find_element_by_id("search-address").send_keys(home_zip)
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

def check_dates(browser, argv, second_dose=False, recursing=False):
    dates_xpath = "//div[@id='ui-datepicker-div']/table[1]/tbody[1]/tr/td/a"
    cells = browser.find_elements_by_xpath(dates_xpath)
    if recursing:
        cells[0].click()
    else:
        browser.find_element_by_class_name("ui-datepicker-current-day").click()
    check_times(browser, argv, second_dose=second_dose)
    for i in range(1, len(cells)):
        browser.find_element_by_id("datepicker").click()
        try:
            browser.find_elements_by_xpath(dates_xpath)[i].click()
        except:
            time.sleep(1)
            browser.find_elements_by_xpath(dates_xpath)[i].click()
        check_times(browser, argv, second_dose=second_dose)
    browser.find_element_by_id("datepicker").click()
    right_button = browser.find_element_by_xpath("//div[@id='ui-datepicker-div']/div[1]/a[2]")
    if ("disabled" in right_button.get_attribute("class")):
        browser.find_element_by_xpath("//div[@id='ui-datepicker-div']/div[1]/a[1]").click()
        cells = browser.find_elements_by_xpath(dates_xpath)
        cells[0].click()
        return
    right_button.click()
    check_dates(browser, argv, second_dose=second_dose, recursing=True)


def check_cities(browser, argv, second_dose=False):
    for city in range(100):
        browser.find_element_by_name("userStore").click()
        store_button = browser.find_elements_by_xpath(f"//section[@id='wag-store-info-{city}']/div[1]/section[3]/a[1]")
        store_button[0].click()
        limit = float(argv[5]) if len(argv) > 5 else 30
        if float(browser.find_element_by_class_name("locationright").get_attribute("innerText").split(' ')[0]) > limit:
            break
        browser.find_element_by_id("datepicker").click()
        check_dates(browser, argv, second_dose=second_dose)
        
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
        time.sleep(2)

def check_for_appointments(browser, argv, second_dose=False):
    fill_out_survey(browser, argv[4], second_dose=second_dose)
    select_zip(browser, argv[4] if len(argv) > 4 else "60035")
    while (True):
        check_cities(browser, argv, second_dose=second_dose)

def login_and_check(argv, second_dose=False):
    username = argv[1]
    password = argv[2]
    security_answer = argv[3]
    browser = webdriver.Firefox(executable_path=r'C:\usr\local\bin\geckodriver.exe')
    url = 'https://www.walgreens.com/findcare/vaccination/covid-19/appointment/screening'
    while True:
        browser.get(url)
        try:
            login(browser, username, password, security_answer)
        except:
            pass
        try:
            check_for_appointments(browser, argv, second_dose=second_dose)
        except Exception as e:
            #winsound.Beep(1500, 500)
            print(e)
            time.sleep(5)
    
            
            
        
