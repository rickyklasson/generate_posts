import datetime
import os.path
import pyperclip
import shutil
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


def code_to_text(folder_name, img_idx):
    path_to_code = os.path.join('./raw_material', folder_name, f'code_{img_idx}.py')
    with open(path_to_code, 'r') as file:
        code = file.read()

    if not code:
        raise FileNotFoundError("Couldn't find source code python file.")

    return code


def click_by_css_selector(driver, css_selector):
    item = driver.find_element(By.CSS_SELECTOR, css_selector)
    time.sleep(0.4)
    item.click()
    time.sleep(0.1)


def image_from_code_selenium(source_folder: str, img_idx: int):
    driver = webdriver.Firefox()
    driver.get("https://carbon.now.sh/")

    actions = ActionChains(driver)

    # Select Nord theme.
    click_by_css_selector(driver, 'div.jsx-6aef7fa683662777:nth-child(1) > span:nth-child(3)')  # Click on theme dropdown.
    click_by_css_selector(driver, '#downshift-0-item-10')  # Click on "Nord" theme.

    # Select python language.
    click_by_css_selector(driver, 'div.jsx-6aef7fa683662777:nth-child(2) > span:nth-child(3)')  # Click on theme dropdown
    click_by_css_selector(driver, '#downshift-1-item-52')  # Click on "Nord" theme

    # Remove background.
    click_by_css_selector(driver, 'div.jsx-492597142:nth-child(3)')
    click_by_css_selector(driver, '#rc-editable-input-5')
    actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()  # Mark all text
    actions.send_keys(Keys.DELETE).perform()  # Delete all text in box
    actions.send_keys('0').perform()  # Type a 0 for alpha

    # Remove boilerplate code.
    click_by_css_selector(driver, '.CodeMirror-lines > div:nth-child(1)')  # Select text box.
    actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()  # Mark all text
    actions.send_keys(Keys.DELETE).perform()  # Delete all text in box.

    # Enter my code.
    code_text = code_to_text(source_folder, img_idx)
    pyperclip.copy(code_text)  # Copy to clipboard
    actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()  # Paste from clipboard
    actions.send_keys(Keys.BACKSPACE).perform()

    # Download as png with date as name.
    image_name = f'code_{source_folder}'
    download_path = os.path.join('/home/ricky/Downloads', f'{image_name}.png')
    try:
        os.remove(download_path)
    except FileNotFoundError:
        pass

    click_by_css_selector(driver, '#export-menu')  # Open export menu
    click_by_css_selector(driver, 'button.jsx-1997739259:nth-child(3)')  # 4x quality
    click_by_css_selector(driver, '.jsx-3682524635')  # Select naming field
    actions.send_keys(image_name).perform()  # Name the image on format 'code_YYMMDD.png'
    click_by_css_selector(driver, '#export-png')
    time.sleep(2)  # Wait for download to complete
    driver.close()

    # Move to appropriate location.
    target_file = os.path.join('./raw_material', source_folder, f'code_{img_idx}.png')
    os.makedirs(target_file.rsplit('/', 1)[0], exist_ok=True)  # Make all dirs except leaf.
    shutil.move(download_path, target_file)