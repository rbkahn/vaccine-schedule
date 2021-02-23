from twilio.rest import Client
import csv

patients = []
with open('patient_info.csv') as f:
    for row in csv.DictReader(f, skipinitialspace=True):
        patient = {k.strip(): v for k, v in row.items()}
        patients.append(patient)

with open("twilio-credentials.txt") as fp:
    lines = fp.readlines()
    account_sid = lines[0]
    auth_token = lines[1]

def send_message(message):
    client = Client(account_sid, auth_token)
    client.messages.create(
                     body=message,
                     from_='+14159497162',
                     to='+18477103770')

def clickButtonByInnerText(browser, innerText, i=1):
    getTagByText(browser, "button", innerText, i).click()

def getTagByText(browser, tag, text, i=1):
    elements = browser.find_elements_by_tag_name(tag)
    for e in elements:
        if text in e.get_attribute("innerText"):
            if i == 1:
                return e
            else:
                i -= 1