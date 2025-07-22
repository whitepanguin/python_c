import time
import pandas as pd
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def get_lat_lng_from_address(address, api_key):
    url = 'https://dapi.kakao.com/v2/local/search/address.json'
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": address}

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        result = response.json()
        if not result['documents']:
            print(f"❌ 지오코딩 실패 → '{address}'")
        else:
            location = result['documents'][0]['address']
            return location['y'], location['x']
    else:
        print(f"❌ API 오류 ({response.status_code}): {response.text}")
    return None, None


# 바나프레소 크롤링 함수
def fetch_bana(api_key):
    bana_url = 'https://www.banapresso.com/'
    driver = webdriver.Chrome()
    driver.get(bana_url)
    time.sleep(1)

    # 매장찾기 메뉴 클릭
    driver.find_element(By.XPATH, '/html/body/div/div/article/div[1]/div/a[1]/div').click()
    time.sleep(2)

    # 메뉴 > 매장찾기 이동
    # ✅ hover → click 구조
    action = ActionChains(driver)

    store_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#wrap > header > div > ul > li:nth-child(3) > a'))
    )

    store_search_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#wrap > header > div > ul > li:nth-child(3) > ul > li:nth-child(1) > a'))
    )

    action.move_to_element(store_menu).move_to_element(store_search_menu).click().perform()
    time.sleep(2)


    # 매장 리스트 로딩 대기
    scrollable_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.store_shop_list'))
    )
    time.sleep(1)

    # 스크롤 반복
    for _ in range(20):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(1)

    # HTML 파싱
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    store_items = soup.select('.store_shop_list > ul > li')

    print(f"📦 총 매장 수: {len(store_items)}")

    results = []
    for item in store_items:
        name_tag = item.select_one('a > span > i')
        addr_tag = item.select_one('a > span > span')

        store_name = name_tag.text.strip() if name_tag else ''
        store_addr = addr_tag.text.strip() if addr_tag else ''

        lat, lng = get_lat_lng_from_address(store_addr, api_key)

        print(f"📍 {store_name} - {store_addr} → 위도: {lat}, 경도: {lng}")

        results.append({
            '매장명': store_name,
            '주소': store_addr,
            '위도': lat,
            '경도': lng
        })

    driver.quit()

    # DataFrame 저장
    df = pd.DataFrame(results)
    csv_path = os.path.join(os.getcwd(), 'banapresso_stores.csv')
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"\n✅ CSV 저장 완료!\n📁 파일 위치: {csv_path}\n📄 총 매장 수: {len(df)}개")
fetch_bana('9cda7248ae6173da152c629e811dad49')