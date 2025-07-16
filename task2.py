import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys # 키 입력
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

# https://pixabay.com/ko/images/search/자연/

driver = webdriver.Chrome()
url = 'https://pixabay.com/ko/images/search/자연/'
driver.get(url)
time.sleep(2)
driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
time.sleep(2)

image_xpath = '/html/body/div[1]/div[1]/div/div[2]/div[3]/div/div/div'

img1 = './div[1]/div/a/img'
img2 = './div[2]/div/a/img'
imgl = './div[100]/div/a/img'

for i in range(1,101):
    image_url = image_xpath.find_element('xpath', './div[i]/div/a/img').get_attribute('src')
    print('image_url',image_url)

    image_byte = Request(image_url, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

f = open('bg[i].jpg','wb')
f.write(urlopen(image_byte).read())
f.close()