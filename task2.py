"""
Pixabay '자연' 키워드:
  • 1 페이지당 10장씩, 2 페이지 → 20 장 수집
  • 각 이미지 저장 후 MongoDB(pixabay_db.images)에
    {local_path, url} 문서를 기록
"""

import time, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.request import Request, urlopen
from pymongo import MongoClient

# ------------------------------------------------------------------------------
# 1) MongoDB 연결
mongo_url = 'mongodb+srv://apple:1234@cluster0.8gy1hbh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(mongo_url)
db         = client['pixabay_db']
collection = db['images']

# (선택) 기존 컬렉션 비우기
# collection.delete_many({})

# ------------------------------------------------------------------------------
# 2) 스크레이퍼 설정
SAVE_DIR        = 'images'
MAX_PAGES       = 2
PER_PAGE_LIMIT  = 10
TOTAL_LIMIT     = MAX_PAGES * PER_PAGE_LIMIT
SCROLL_CNT      = 5
WAIT_LONG       = 3
WAIT_SHORT      = 1

CONTAINER_XPATH = '/html/body/div[1]/div[1]/div/div[2]/div[3]/div/div/div'
IMG_REL_XPATH   = './div[{}]/div/a/img'
NEXT_BTN_XPATH  = '/html/body/div[1]/div[1]/div/div[2]/div[4]/div[1]/a'

os.makedirs(SAVE_DIR, exist_ok=True)
driver = webdriver.Chrome()
driver.get('https://pixabay.com/ko/images/search/자연/')
time.sleep(WAIT_LONG)

image_count = 0

# ------------------------------------------------------------------------------
# 3) 페이지 루프
for page in range(MAX_PAGES):

    # (3‑1) lazy‑loading 대응 스크롤
    for _ in range(SCROLL_CNT):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(1.5)

    # (3‑2) 이미지 컨테이너 획득
    container = driver.find_element(By.XPATH, CONTAINER_XPATH)

    page_downloaded = 0
    for i in range(1, 101):
        if page_downloaded >= PER_PAGE_LIMIT or image_count >= TOTAL_LIMIT:
            break

        try:
            img_el = container.find_element(By.XPATH, IMG_REL_XPATH.format(i))
        except:
            break  # 더 이상 div가 없으면 탈출

        # (3‑3) URL 추출: src 우선 → srcset 백업
        img_url = img_el.get_attribute('src')
        if not img_url:
            srcset = img_el.get_attribute('srcset') or ''
            if srcset:
                img_url = srcset.split(',')[-1].strip().split(' ')[0]

        if not img_url or not img_url.startswith('https://cdn.pixabay.com'):
            continue  # 유효하지 않으면 skip

        # (3‑4) 이미지 다운로드
        image_count    += 1
        page_downloaded += 1
        local_path      = f'{SAVE_DIR}/bg{image_count}.jpg'
        print(f'[{image_count}/{TOTAL_LIMIT}] {img_url}')

        try:
            req = Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
            with open(local_path, 'wb') as f:
                f.write(urlopen(req).read())
        except Exception as e:
            print('다운로드 실패:', e)
            image_count    -= 1
            page_downloaded -= 1
            continue

        # (3‑5) MongoDB에 문서 저장
        try:
            collection.insert_one({
                "local_path": local_path,
                "url": img_url
            })
        except Exception as e:
            print('MongoDB 저장 실패:', e)

        time.sleep(WAIT_SHORT)

    if image_count >= TOTAL_LIMIT:
        break  # 목표 20장 달성

    # (3‑6) 다음 페이지 이동
    if page < MAX_PAGES - 1:
        next_btn = driver.find_element(By.XPATH, NEXT_BTN_XPATH)
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(WAIT_LONG)

driver.quit()
print(f'\n✅ 최종 {image_count}장의 이미지를 저장했으며 MongoDB에도 기록했습니다.')

# DB에서 한 10개만 확인
for doc in collection.find().limit(10):
    print(doc)
