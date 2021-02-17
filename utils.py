from twilio.rest import Client

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

def getButtonByInnerText(browser, innerText):
    return getTagByText(browser, "button", innerText)

def getTagByText(browser, tag, text):
    elements = browser.find_elements_by_tag_name(tag)
    for e in elements:
        if text in e.get_attribute("innerText"):
            return e