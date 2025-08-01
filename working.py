import time
import os
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

def kyobo(key_word, max_page):
    base_url = 'https://www.kyobobook.co.kr/'
    options = Options()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)

    driver.get(base_url)
    time.sleep(2)

    # 1페이지: 검색창 통해 진입
    search_input = driver.find_element(By.XPATH, '/html/body/div[2]/header/div[3]/div[1]/section/section[2]/form/input')
    search_input.click()
    time.sleep(1)
    search_input.send_keys(key_word, Keys.ENTER)
    time.sleep(3)

    titles, authors, companies, releases, prices, img_paths = [], [], [], [], [], []
    img_dir = 'images/kyobo'
    os.makedirs(img_dir, exist_ok=True)

    def extract_books_from_page(use_special_xpath=False):
        # 기본 XPath (1페이지용)
        xpath_base = '/html/body/div[3]/main/section/div/div/div[3]/div[2]/div/div[2]/div[3]/ul/li' if use_special_xpath else '/html/body/div[3]/main/section/div/div/div[4]/div[2]/div/div[2]/div[3]/ul/li'
        books = driver.find_elements(By.XPATH, xpath_base)
        print(f'총 {len(books)}개의 검색 결과')

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
                    img_filename = f"{img_dir}/{len(titles)+1:02d}.jpg"
                    with open(img_filename, 'wb') as f:
                        f.write(requests.get(img_url).content)

                titles.append(title)
                authors.append(author)
                companies.append(company)
                releases.append(release)
                prices.append(price)
                img_paths.append(img_filename)

            except Exception as e:
                print(f"{len(titles)+1}번째 항목 처리 중 오류 발생: {e}")
                continue

    # 1페이지 추출 (검색 후 진입)
    extract_books_from_page()

    # 2페이지부터 직접 URL로 접근
    for page in range(2, max_page + 1):
        print(f"\n--- {page}페이지 크롤링 중 ---")
        search_url = f"https://search.kyobobook.co.kr/search?gbCode=TOT&target=total&keyword={key_word}&page={page}"
        driver.get(search_url)
        time.sleep(5)
        extract_books_from_page(use_special_xpath=True)

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

    df.to_excel('kyobo_books.xlsx', index=False, sheet_name='Sheet1', engine='openpyxl')
    print("엑셀 저장 완료: kyobo_books.xlsx")

# 사용 예시
kyobo('파이썬', 3)
