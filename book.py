import time
import os
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

def yes24(key_word, page):
    url = 'https://www.yes24.com/Main/default.aspx'
    options = Options()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(2)

    search_input = driver.find_element(By.ID, 'query')
    search_input.click()
    time.sleep(1)
    search_input.send_keys(key_word, Keys.ENTER)
    time.sleep(3)

    # XPath로 책 목록 접근
    books_xpath = '/html/body/div/div[4]/div/div[2]/section[2]/div[3]/ul/li'
    books = driver.find_elements(By.XPATH, books_xpath)

    print(f'총 {len(books)}개의 검색 결과')

    titles, authors, companies, releases, prices, img_paths = [], [], [], [], [], []
    img_dir = 'images/yes24'
    os.makedirs(img_dir, exist_ok=True)

    for i, book in enumerate(books):
        try:
            title = book.find_element(By.XPATH, f'./div/div[2]/div[2]/a[1]').text
            author = book.find_element(By.XPATH, f'./div/div[2]/div[3]/span[1]').text
            company = book.find_element(By.XPATH, f'./div/div[2]/div[3]/span[2]/a').text
            release = book.find_element(By.XPATH, f'./div/div[2]/div[3]/span[3]').text
            price = book.find_element(By.XPATH, f'./div/div[2]/div[4]/strong/em').text

            img_tag = book.find_element(By.XPATH, f'./div/div[1]/div[1]/span/span/a/em/img')
            img_url = img_tag.get_attribute('src')

            # 이미지 저장
            img_filename = ''
            if img_url:
                img_filename = f"{img_dir}/{i+1:02d}.jpg"
                with open(img_filename, 'wb') as f:
                    f.write(requests.get(img_url).content)

            # 저장
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

    # DataFrame 저장
    df = pd.DataFrame({
        '검색어':key_word,
        '제목': titles,
        '저자': authors,
        '출판사': companies,
        '출간일': releases,
        '가격': prices,
        '이미지 경로': img_paths
    })

    df.to_excel('yes24_books.xlsx', index=False, sheet_name='Sheet1', engine='openpyxl')
    print("엑셀 저장 완료: yes24_books.xlsx")

yes24('파이썬', 1)