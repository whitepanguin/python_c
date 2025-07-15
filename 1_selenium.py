# 구글 검색
import time
from selenium import webdriver # 웹 접속
from selenium.webdriver.common.keys import Keys # 키 입력


driver = webdriver.Chrome()
driver.get('https://www.google.com') # 실행이 끝나면 꺼진다
search = driver.find_element("name","q")
search.send_keys("날씨")
search.send_keys(Keys.RETURN)

#계속 보고 싶다면
# time.sleep(5)
