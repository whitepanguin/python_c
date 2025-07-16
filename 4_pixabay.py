from selenium import webdriver
from urllib.request import Request, urlopen

driver = webdriver.Chrome()
url = 'https://pixabay.com/ko/images/search/고양이/'
driver.get(url)

image_xpath = '/html/body/div[1]/div[1]/div/div[2]/div[2]/div/div/div[1]/div[5]/div/a/img'

image_url = driver.find_element('xpath', image_xpath).get_attribute('src')
print('image_url',image_url)

image_byte = Request(image_url, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

f = open('cat.jpg','wb')
f.write(urlopen(image_byte).read())
f.close()