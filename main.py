import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import lxml
import time
from dotenv import load_dotenv
load_dotenv()

email = os.environ.get('email')
password = os.environ.get('psw')

# _____________________BS4 gathering data______________________________________
links_list = []
prices_list = []
addresses_list = []
for i in range(3):
    url = f'https://www.zillow.com/boston-ma/rentals/{i}_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage' \
          f'%22%3A2%7D%2C%22mapBounds%22%3A%7B%22north%22%3A42.46329459372928%2C%22south%22%3A42.16321084340145%2C' \
          f'%22east%22%3A-70.81176226806642%2C%22west%22%3A-71.2834877319336%7D%2C%22regionSelection%22%3A%5B%7B' \
          f'%22regionId%22%3A44269%2C%22regionType%22%3A6%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B' \
          f'%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value' \
          f'%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore' \
          f'%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22mf%22%3A%7B%22value%22%3Afalse' \
          f'%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B' \
          f'%22max%22%3A3000%7D%2C%22price%22%3A%7B%22max%22%3A588141%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom' \
          f'%22%3A11%7D '

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}

    response = requests.get(url, headers=headers)
    html_page = response.text

    soup = BeautifulSoup(html_page, 'lxml')
    find_prices = soup.find_all(name='div', class_='StyledPropertyCardDataArea-c11n-8-69-2__sc-yipmu-0 kJFQQX')
    prices = [prices_list.append(x.text) for x in find_prices]

    find_addresses = soup.find_all(name='div', class_='StyledPropertyCardDataWrapper-c11n-8-69-2__'
                                                      'sc-1omp4c3-0 KzAaq property-card-data')
    addresses = [addresses_list.append(x.address.text) for x in find_addresses]

    find_links = soup.find_all(name='div', class_='StyledPropertyCardDataWrapper-c11n-8-69-2__'
                                                  'sc-1omp4c3-0 KzAaq property-card-data')
    links_plain = [x.a['href'] for x in find_addresses]

    for links in links_plain:
        if "https://" not in links:
            new_links = f"https://zillow.com/{links}"
            links_list.append(new_links)
        else:
            links_list.append(links)

# _____________________Using selenium filling up the form______________________________________#
chrome_driver_path = os.environ.get("path") # the path for the chromedriver
s = Service(chrome_driver_path)
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=s, options=chrome_options)

form_link = 'https://docs.google.com' \
            '/forms/d/e/1FAIpQLSfeXIDoak51-snVz1HyQ-aDYcX-ZbsJOwN3CS1otkTKZ6JdkA/viewform?usp=sf_link'

driver.get(form_link)
time.sleep(5)
#
# # _____________________Filling up the form______________________________________#
for i in range(len(addresses_list)):
    address_input = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/'
                                                  'div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input')
    address_input.send_keys(addresses_list[i])

    price_input = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/'
                                                'div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input')
    price_input.send_keys(prices_list[i])

    link_input = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/'
                                               'div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input')
    link_input.send_keys(links_list[i])

    driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div/span/span').click()
    time.sleep(5)

    driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div/div[4]/a').click()

# # _____________________Signing in a Google account and converting form to spreadsheet________________________________#
driver.get("https://accounts.google.com/v3/signin/identifier?dsh=S-837988882%3A1664707453790393&continue=https%3A%2F"
           "%2Fdocs.google.com%2Fforms%2Fu%2F0%2F%3Ftgif%3Dd&followup=https%3A%2F%2Fdocs.google.com%2Fforms%2Fu%2F0"
           "%2F%3Ftgif%3Dd&ltmpl=forms&osid=1&passive=1209600&service=wise&flowName=GlifWebSignIn&flowEntry"
           "=ServiceLogin&ifkv=AQDHYWqz4WPKaWdABDEdLFft6UZsg0_RvqKbC31M8L4wjfhWgLMh2LOrcbTiCYzxE-9N3ROSV8tjqg")

email_fill = driver.find_element(By.XPATH, '//*[@id="identifierId"]')
time.sleep(3)
email_fill.send_keys(email)
time.sleep(3)

driver.find_element(By.XPATH, '//*[@id="identifierNext"]/div/button/span').click()
time.sleep(5)

password_fill = driver.find_element(By.NAME, 'Passwd')
password_fill.send_keys(password)
time.sleep(3)

driver.find_element(By.XPATH, '//*[@id="passwordNext"]/div/button/span').click()
time.sleep(10)

driver.find_element(By.CLASS_NAME, 'docs-homescreen-grid-item').click()

driver.find_element(By.CLASS_NAME, 'a6yTpb').click()
time.sleep(10)

driver.find_element(By.XPATH, '//*[@id="ResponsesView"]/div/div[1]/div[1]/div[2]/div[1]/div/div/span/span').click()
time.sleep(5)
driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/div[13]/div/div[2]/div[3]/div[2]/span/span').click()