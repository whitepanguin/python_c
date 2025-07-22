import time
import pandas as pd
import re # 문자열가지고 정규표현식을 쓰기 위한 모듈
from selenium import webdriver
from selenium.webdriver import ActionChains # 엑션들을 이어주는 역활
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # 페이지가 열릴때까지 기다리는 것
from selenium.webdriver.support import expected_conditions as EC # 페이지가 열릴때까지 기다리는 것
from bs4 import BeautifulSoup

def fetch_starbucks():
    bana_url = 'https://www.banapresso.com/'
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(bana_url)
    time.sleep(1)

    # ActionChains(): 마우스나 키보드와 같은 복잡한 사용자 상호작용을 시뮬레이션하는 데 사용
    action = ActionChains(driver)

    first_tag = driver.find_element(By.XPATH, '/html/body/div/div/article/div[1]/div/a[1]/div')


    action.move_to_element(first_tag).perform()
    time.sleep(2)
    first_tag.click()
    time.sleep(2)

    second_tag = driver.find_element(By.CSS_SELECTOR, '#wrap > header > div > ul > li:nth-child(3) > a')
    third_tag = driver.find_element(By.CSS_SELECTOR, '#wrap > header > div > ul > li:nth-child(3) > ul > li:nth-child(1) > a')

    action.move_to_element(second_tag).move_to_element(third_tag).click().perform()

    seoul_tag = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#container > div > form > fieldset > div > section > article.find_store_cont > article > article:nth-child(4) > div.loca_step1 > div.loca_step1_cont > ul > li:nth-child(1) > a')
        )
    ) # 클릭할수 있는지 채크만 해주는 거다
    seoul_tag.click()

    # 매장정보를 담기 위한 빈 리스트
    store_list =[]
    addr_list = []
    lat_list = []
    lng_list = []

    WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME,'set_gugun_cd_btn'))) # 안에 돔 요소가 다 있는지 채크
    gu_elements = driver.find_elements(By.CLASS_NAME,'set_gugun_cd_btn')
    WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#mCSB_2_container > ul > li:nth-child(1) > a')))
    gu_elements[0].click()

    WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'quickResultLstCon')))

    req = driver.page_source
    soup = BeautifulSoup(req, 'html.parser')
    stores = soup.find('ul', 'quickSearchResultBoxSidoGugun').find_all('li')

    for store in stores:
        store_name = store.find('strong').text
        store_addr = store.find('p').text
        store_addr = re.sub(r'\d{4}-\d{4}$','',store_addr).strip()
        store_lat = store['data-lat']
        store_lng = store['data-long']
        store_list.append(store_name)
        addr_list.append(store_addr)
        lat_list.append(store_lat)
        lng_list.append(store_lng)

    df = pd.DataFrame({
        'store': store_list,
        'addr': addr_list,
        'lat': lat_list,
        'lng': lng_list
    })

    driver.quit()
    return df




starbucks_df = fetch_starbucks()
starbucks_df.to_csv('starbucks_seoul.csv', index=False, encoding='utf-8-sig')
print("데이터가 starbucks_seoul.csv 파일로 저장되었습니다.")