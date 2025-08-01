import time
import os
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

def kyobo(key_word, page):
    from urllib.parse import quote

    base_url = f"https://www.kyobobook.co.kr/search?keyword={quote(key_word)}&page={page}"
    options = Options()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)

    driver.get(base_url)
    time.sleep(3)

    books_xpath = '/html/body/div[3]/main/section/div/div/div[4]/div[2]/div/div[2]/div[3]/ul/li'
    books = driver.find_elements(By.XPATH, books_xpath)

    print(f'총 {len(books)}개의 검색 결과 (페이지 {page})')

    titles, authors, companies, releases, prices, img_paths = [], [], [], [], [], []
    img_dir = 'images/kyobo'
    os.makedirs(img_dir, exist_ok=True)

    for i, book in enumerate(books):
        try:
            title = book.find_element(By.XPATH, './div[1]/div[2]/div[2]/div[1]/div/a').text
            author = book.find_element(By.XPATH, './div[1]/div[2]/div[4]/div[1]/div[1]/div').text
            company = book.find_element(By.XPATH, './div[1]/div[2]/div[4]/div[2]/a').text
            release = book.find_element(By.XPATH, './div[1]/div[2]/div[4]/div[2]/span[2]').text
            price = book.find_element(By.CLASS_NAME, 'price').text

            img_tag = book.find_element(By.XPATH, './div[1]/div[1]/a/span/img')
            img_url = img_tag.get_attribute('src')

            img_filename = ''
            if img_url:
                img_filename = f"{img_dir}/{(page-1)*len(books)+i+1:03d}.jpg"
                with open(img_filename, 'wb') as f:
                    f.write(requests.get(img_url).content)

            titles.append(title)
            authors.append(author)
            companies.append(company)
            releases.append(release)
            prices.append(price)
            img_paths.append(img_filename)

        except Exception as e:
            print(f"{i+1}번째 항목 처리 중 오류 발생: {e}")
            continue

    driver.quit()

    df = pd.DataFrame({
        '검색어': key_word,
        '제목': titles,
        '저자': authors,
        '출판사': companies,
        '출간일': releases,
        '가격': prices,
        '이미지 경로': img_paths
    })

    filename = f'kyobo_books_p{page}.xlsx'
    df.to_excel(filename, index=False, sheet_name='Sheet1', engine='openpyxl')
    print(f"엑셀 저장 완료: {filename}")

# 사용 예시
kyobo('파이썬', 2)
