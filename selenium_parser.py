from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
import time

paths = {
    'market_data': '/html/body/header/nav/div[2]/div/div/ul/li[3]',
    'category': '/html/body/div[11]/div/section/div/div/div/div/div/div/div[2]/div[1]/div[1]/div[2]/select',
    'table_data': '/html/body/div[11]/div/section/div/div/div/div/div/div/div[3]/div/table/tbody',
    'pre-open_market': './div/div[1]/div/div[1]/ul/li[1]/a',
    'cards': '//*[@id="sitemapAccordion"]/div',
    'card_link': './div[1]/a',
    'card_cols': './div[2]/div/div/div'
}

if __name__ == '__main__':
    driver_location: str = 'C:/Users/andm2/source/repos/test_task_python_parsers/chromedriver.exe'
    current_element: WebElement = None
    driver: WebDriver = None

    def get_by_xpath(path: str = '', root: bool = False, element = None) -> WebElement:
        global current_element
        if root:
            current_element = driver.find_element(By.XPATH, path)
        else:
            if not element:
                element = current_element
            if not element:
                raise ValueError()
            current_element = element.find_element(By.XPATH, path)
        return current_element
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36')
    options.add_argument("--log-level=3")
    driver = Chrome(options=options)
    driver.get('https://www.nseindia.com')
    WebDriverWait(driver, 5)
    action = ActionChains(driver)

    action \
        .move_to_element(get_by_xpath(paths['market_data'], True)) \
        .move_to_element(get_by_xpath(paths['pre-open_market'])) \
        .click() \
        .perform()
    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, paths['category'])))
    action \
        .move_to_element(get_by_xpath(paths['category'], True)) \
        .click() \
        .perform()
    Select(current_element).select_by_index(5)
    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, paths['table_data'] + '/tr/td[7]')))
    rows = driver.find_elements(By.XPATH, paths['table_data'] + '/tr/td[7]')
    print('Data:')
    for row in rows:
        print(row.text, end=", ")
    print()
    
    action \
        .scroll_from_origin(ScrollOrigin.from_element(driver.find_element(By.ID, 'site-map')), 0, 100) \
        .perform()
    time.sleep(0.5)
    action \
        .move_to_element(driver.find_element(By.ID, 'site-map')) \
        .click() \
        .perform()
    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.ID, 'sitemapAccordion')))
    print('\n\nSitemap:')
    for card in driver.find_elements(By.XPATH, paths['cards']):
        link = card.find_element(By.XPATH, paths['card_link'])
        print(f'"{link.text}"')
        action \
            .scroll_by_amount(0, -1000) \
            .perform()
        time.sleep(0.5)
        action \
            .scroll_to_element(link) \
            .perform()
        time.sleep(0.5)
        action \
            .scroll_by_amount(0, 100) \
            .perform()
        time.sleep(0.5)
        action \
            .move_to_element(link) \
            .click() \
            .perform()
        for col in card.find_elements(By.XPATH, paths['card_cols']):
            print(f'"    {col.find_element(By.XPATH, './h3').text}"')
            for item in col.find_elements(By.XPATH, './ul/li'):
                print(f'"        {item.find_element(By.XPATH, './a').text}"')
        
