import datetime
import os.path
import pyperclip
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

driver = webdriver.Firefox()
driver.get("https://carbon.now.sh/")

def get_code_as_text():
    today = datetime.datetime.today()
    today_str = f'{today:%Y%m%d}'

    path_to_code = os.path.join('./raw_material', today_str, 'code.py')
    with open(path_to_code, 'r') as file:
        code = file.read()

    if not code:
        raise FileNotFoundError("Couldn't find source code python file.")

    return code

def click_by_css_selector(css_selector):
    item = driver.find_element(By.CSS_SELECTOR, css_selector)
    time.sleep(0.4)
    item.click()
    time.sleep(0.1)

# Select Nord theme.
click_by_css_selector('div.jsx-6aef7fa683662777:nth-child(1) > span:nth-child(3)')  # Click on theme dropdown.
click_by_css_selector('#downshift-0-item-14')  # Click on "Nord" theme.

# Select python language.
click_by_css_selector('div.jsx-6aef7fa683662777:nth-child(2) > span:nth-child(3)')  # Click on theme dropdown.
click_by_css_selector('#downshift-1-item-52')  # Click on "Nord" theme.

# Remove background. CONTINUE

click_by_css_selector('.CodeMirror-lines > div:nth-child(1)') # Select text box.
actions = ActionChains(driver)
actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()  # Mark all text
actions.send_keys(Keys.DELETE).perform()  # Delete all text in box.

code_text = get_code_as_text()
pyperclip.copy(code_text)  # Copy to clipboard
actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()  # Paste from clipboard
actions.send_keys(Keys.BACKSPACE).perform()

