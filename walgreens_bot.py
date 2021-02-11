from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from twilio.rest import Client
import time, sys, winsound

url = 'https://www.walgreens.com/login.jsp?ru=%2Ffindcare%2Fvaccination%2Fcovid-19%2Fappointment%2Fscreening%3Fflow%3Drx'
# global variables for success
chosen_date = ""
chosen_time = ""

def get_location(browser):
    return browser.find_element_by_xpath("//section[@class='locationLeft']/section[1]/p[3]").get_attribute("innerText")

def send_message(browser, message, account_sid, auth_token):
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


def fill_out_survey(browser, home_zip, second_dose=False):
    browser.implicitly_wait(10)
    browser.find_element_by_id('sq_100i_1').click()
    browser.find_element_by_id('sq_102i_1').click()
    browser.find_element_by_id('sq_103i_1').click()
    browser.find_element_by_id('sq_104i_1').click()
    browser.find_elements_by_class_name("sv_complete_btn")[0].click()
    
    browser.find_element_by_id("hn-startVisitBlock-gb-terms").click()
    time.sleep(2)
    
    if second_dose:
        browser.find_element_by_id("dose2").click()
        browser.find_element_by_id("datepicker0").click()
        browser.find_element_by_xpath("//div[@id='ui-datepicker-div']/table[1]/tbody[1]/tr[5]/td[5]").click()
        Select(browser.find_element_by_id("vaccination-dropdown")).select_by_visible_text("Moderna")
    else:
        browser.find_element_by_id("dose1").click()
    time.sleep(1)
    browser.find_element_by_id("continueBtn").click()

        
def select_zip(browser, zip):
    while True:
        time.sleep(1)
        #browser.find_element_by_id("search-address").clear()
        #time.sleep(2)
        #browser.find_element_by_id("search-address").send_keys(zip)
        #time.sleep(2)
        browser.find_element_by_class_name("storeSearch").click()
        time.sleep(1)
        message = browser.find_element_by_xpath("//section[@id='wag-body-main-container']/section[1]/section[1]/section[1]/p[1]").get_attribute("innerText")
        while "Checking" in message:
            time.sleep(1)
            message = browser.find_element_by_xpath("//section[@id='wag-body-main-container']/section[1]/section[1]/section[1]/p[1]").get_attribute("innerText")
        if "don't" not in message:
            winsound.Beep(2500, 4000)
            sys.exit()
            break
        time.sleep(10)

def confirm_eligibility(browser, home_zip):
    time.sleep(2)
    browser.find_element_by_id("inputLocation").clear()
    browser.find_element_by_id("inputLocation").send_keys(home_zip)
    browser.find_element_by_xpath("//section[@id='wag-body-main-container']/section[1]/section[1]/section[1]/section[1]/div[1]/span[1]/button[1]").click()
    time.sleep(3)
    browser.find_element_by_id("sq_100i_1").click()
    browser.find_element_by_id("eligibility-check").click()
    browser.find_element_by_class_name("sv_complete_btn").click()

def check_for_appointments(browser, argv, second_dose=False):
    confirm_eligibility(browser, argv[4])
    fill_out_survey(browser, argv[4], second_dose=second_dose)
    select_zip(browser, argv[4] if len(argv) > 4 else "60035")

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
            check_for_appointments(browser, argv, second_dose=second_dose)
        except Exception as e:
            print(e)
        finally:
            message = chosen_date + ' ' + chosen_time + ' ' + get_location(browser)
            print(message)
            try:
                with open("twilio-credentials.txt") as fp:
                    lines = fp.readlines()
                    account_sid = lines[0]
                    auth_token = lines[1]
                    send_message(browser, message, account_sid, auth_token)
            except:
                pass
            winsound.Beep(2500, 4000)
            get_appointment(chosen_date, argv, get_location(browser), chosen_time, second_dose=second_dose)
            break

if __name__ == "__main__":
    login_and_check(sys.argv, second_dose=False)
            
            
        
