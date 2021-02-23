from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import time, winsound, random
from utils import clickButtonByInnerText, send_message, getTagByText, patients
from dateutil import parser

zips = [60613, 60641, 60077]

url = 'https://www.mhealthappointments.com/covidappt'

def welcome_screen(browser):
    browser.get(url)
    browser.implicitly_wait(5)
    time.sleep(4)
    try:
        browser.find_element_by_id('covid_vaccine_search_input').click()
    except:
        time.sleep(2)
        print("trying again")
        browser.find_element_by_id('covid_vaccine_search_input').click()
        print("succeeded")
    ActionChains(browser).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.RIGHT).send_keys(Keys.RIGHT).send_keys(Keys.RIGHT).perform()
    while True:
        browser.find_element_by_id('covid_vaccine_search_input').send_keys(random.choice(zips))
        browser.find_element_by_id('covid_vaccine_search_input').send_keys(Keys.ENTER)
        try:
            browser.find_element_by_id('attestation_1002').click()
            break
        except:
            pass

def check_for_appointments(browser, patient_zips):
    # wait for captcha
    while True:
        try:
            Select(browser.find_element_by_id("appointmentType-type")).select_by_visible_text("COVID Vaccine Dose 1 Appt")
            clickButtonByInnerText(browser, "Start Set up")
            time.sleep(4)
            browser.execute_script("window.scrollTo(0, 500)") 
            time.sleep(1)
            browser.find_element_by_xpath("//div[@id='covid19-reg-v2']/div[1]/div[2]/div[1]/div[2]/div[1]/div[4]/div[2]/div[1]/div[1]/button[1]").click()
            select = Select(browser.find_element_by_id("item-type"))
            options = select.options
            index = 0
            while True:
                select.select_by_index(index)
                time.sleep(1)
                html = browser.find_element_by_xpath("//div[@id='covid19-reg-v2']/div[1]/div[3]/div[1]/div[2]/div[1]/div[3]/div[1]").get_attribute("innerText")
                while "Loading" in html:
                    time.sleep(1)
                    html = browser.find_element_by_xpath("//div[@id='covid19-reg-v2']/div[1]/div[3]/div[1]/div[2]/div[1]/div[3]/div[1]").get_attribute("innerText")
                if "Currently, all appointments are booked in your area" in html:
                    browser.execute_script("window.scrollTo(0, 0)") 
                    browser.find_elements_by_class_name("btn-danger")[0].click()
                    try:
                        [element for element in browser.find_elements_by_class_name('btn-success') if element.get_attribute("innerText") == "Ok"][0].click()
                    except:
                        time.sleep(3)
                        [element for element in browser.find_elements_by_class_name('btn-success') if element.get_attribute("innerText") == "Ok"][0].click()
                    break
                elif "There is no availability" not in html:
                    return True
                else:
                    index = (index + 1) % len(options)
        except:
            pass

def pick_year(browser, our_year):
    lower_bound = 2020
    while (our_year < lower_bound):
        bound_string = browser.find_element_by_xpath("//table[@class='uib-yearpicker']/thead[1]/tr[1]/th[2]").get_attribute("innerText")
        lower_bound = int(bound_string.split('-')[0].strip())
        browser.find_element_by_xpath("//table[@class='uib-yearpicker']/thead[1]/tr[1]/th[1]").click()
    years = browser.find_elements_by_xpath("//table[@class='uib-yearpicker']/tbody[1]/tr/td")
    for year in years:
        if int(year.get_attribute("innerText")) == int(our_year):
            year.click()

def pick_month(browser, our_month):
    months = browser.find_elements_by_xpath("//table[@class='uib-monthpicker']/tbody[1]/tr/td")
    for month in months:
        if month.get_attribute("innerText") == our_month:
            month.click()

def pick_day(browser, our_day):
    days = browser.find_elements_by_xpath("//table[@class='uib-datepicker']/tbody[1]/tr/td")
    for day in days:
        if int(day.get_attribute("innerText")) == int(our_day):
            day.click()

def pick_date(browser, date_str):
    date = parser.parse(date_str)
    pick_year(browser, date.year)
    pick_month(browser, date.strftime('%B'))
    pick_day(browser, date.day)


def fill_form(browser):
    patient = patients[-1]
    browser.find_elements_by_class_name("time-checkbox")[0].click()
    ActionChains(browser).send_keys(Keys.TAB).send_keys(Keys.SPACE).perform()
    ActionChains(browser).send_keys(patient['First Name']).send_keys(Keys.TAB).perform()
    ActionChains(browser).send_keys(patient['Last Name']).send_keys(Keys.TAB).perform()
    ActionChains(browser).send_keys(patient['Address']).send_keys(Keys.TAB).perform()
    # Address 2
    ActionChains(browser).send_keys(Keys.TAB).perform()
    ActionChains(browser).send_keys(patient['City']).send_keys(Keys.TAB).perform()
    ActionChains(browser).send_keys('IL').send_keys(Keys.TAB).perform()
    ActionChains(browser).send_keys(patient['Zip Code']).send_keys(Keys.TAB).perform()
    #gender
    ActionChains(browser).send_keys(Keys.TAB).send_keys(Keys.SPACE).send_keys(Keys.TAB).perform()
    pick_date(browser, patients['Birthdate'])
    ActionChains(browser).send_keys(Keys.TAB).perform()
    #ethnicity
    ActionChains(browser).send_keys(Keys.DOWN).send_keys(Keys.DOWN).send_keys(Keys.DOWN).send_keys(Keys.TAB).perform()
    #race
    ActionChains(browser).send_keys(Keys.DOWN).send_keys(Keys.DOWN).send_keys(Keys.DOWN).send_keys(Keys.DOWN).send_keys(Keys.DOWN).send_keys(Keys.TAB).perform()
    ActionChains(browser).send_keys(patient['Phone']).send_keys(Keys.TAB).perform()
    ActionChains(browser).send_keys(Keys.SPACE).perform()
    ActionChains(browser).send_keys(Keys.TAB).send_keys(patient['Email']).send_keys(Keys.TAB).perform()
    ActionChains(browser).send_keys(patient['Phone']).send_keys(Keys.TAB).perform()
    ActionChains(browser).send_keys(patient['Email']).send_keys(Keys.TAB).perform()
    ActionChains(browser).send_keys(Keys.SPACE).perform()
    ActionChains(browser).send_keys(Keys.SPACE).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(patient['First Name'] + " " + patient['Last Name']).perform()
    ActionChains(browser).send_keys(Keys.TAB).send_keys(Keys.SPACE).perform()

def select_appointment(browser):
    pass

if __name__ == "__main__":
    browser = webdriver.Firefox(executable_path=r'C:\usr\local\bin\geckodriver.exe')
    while True:
        try:
            welcome_screen(browser)
            if check_for_appointments(browser, [patient['Zip Code'] for patient in patients]):
                break
        except Exception as e:
            print(e)
        time.sleep(5)
    winsound.Beep(800, 2000)
    try:
        select_appointment(browser)
        fill_form(browser)
    except Exception as e:
        print(e)
    finally:
        send_message("Found a Jewel appointment")
    