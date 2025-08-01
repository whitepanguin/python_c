import time
import os
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote

def yes24(key_word, max_page):
    options = Options()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)

    titles, authors, companies, releases, prices, img_paths, keywords = [], [], [], [], [], [], []
    img_dir = 'images/yes24'
    os.makedirs(img_dir, exist_ok=True)

    base_url = 'https://www.yes24.com/Main/default.aspx'
    driver.get(base_url)
    time.sleep(2)

    search_input = driver.find_element(By.ID, 'query')
    search_input.click()
    time.sleep(1)
    search_input.send_keys(key_word, Keys.ENTER)
    time.sleep(3)

    books_xpath = '/html/body/div/div[4]/div/div[2]/section[2]/div[3]/ul/li'

    # ✅ STEP 1: 1페이지 수집
    print(f'\n[INFO] 1페이지 수집 시작')
    books = driver.find_elements(By.XPATH, books_xpath)

    if not books:
        print('[INFO] 1페이지에 책이 없습니다. 수집을 종료합니다.')
        driver.quit()
        return

    print(f'1페이지: {len(books)}개 책 발견')

    for i, book in enumerate(books):
        try:
            title = book.find_element(By.XPATH, './div/div[2]/div[2]/a[1]').text
            author = book.find_element(By.XPATH, './div/div[2]/div[3]/span[1]').text
            company = book.find_element(By.XPATH, './div/div[2]/div[3]/span[2]/a').text
            release = book.find_element(By.XPATH, './div/div[2]/div[3]/span[3]').text
            price = book.find_element(By.XPATH, './div/div[2]/div[4]/strong/em').text

            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", book)
            time.sleep(1)

            img_tag = book.find_element(By.XPATH, './div/div[1]/div[1]/span/span/a/em/img')
            img_url = img_tag.get_attribute('src')

            img_filename = ''
            if img_url:
                img_filename = f"{img_dir}/{key_word}_p1_{i+1:02d}.jpg"
                with open(img_filename, 'wb') as f:
                    f.write(requests.get(img_url).content)

            titles.append(title)
            authors.append(author)
            companies.append(company)
            releases.append(release)
            prices.append(price)
            img_paths.append(img_filename)
            keywords.append(key_word)

        except Exception as e:
            print(f"1페이지 {i+1}번째 항목 오류: {e}")
            continue

    # ✅ STEP 2: 2페이지부터 max_page까지 반복
    encoded_keyword = quote(key_word)
    for page in range(2, max_page + 1):
        url = f'https://www.yes24.com/Product/Search?query={encoded_keyword}&page={page}'
        print(f'\n[INFO] {page}페이지 접속 중: {url}')
        driver.get(url)
        time.sleep(3)

        books = driver.find_elements(By.XPATH, books_xpath)
        if not books:
            print(f'[INFO] {page}페이지에 책이 없습니다. 수집을 종료합니다.')
            break

        print(f'{page}페이지: {len(books)}개 책 발견')

        for i, book in enumerate(books):
            try:
                title = book.find_element(By.XPATH, './div/div[2]/div[2]/a[1]').text
                author = book.find_element(By.XPATH, './div/div[2]/div[3]/span[1]').text
                company = book.find_element(By.XPATH, './div/div[2]/div[3]/span[2]/a').text
                release = book.find_element(By.XPATH, './div/div[2]/div[3]/span[3]').text
                price = book.find_element(By.XPATH, './div/div[2]/div[4]/strong/em').text

                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", book)
                time.sleep(1)

                img_tag = book.find_element(By.XPATH, './div/div[1]/div[1]/span/span/a/em/img')
                img_url = img_tag.get_attribute('src')

                img_filename = ''
                if img_url:
                    img_filename = f"{img_dir}/{key_word}_p{page}_{i+1:02d}.jpg"
                    with open(img_filename, 'wb') as f:
                        f.write(requests.get(img_url).content)

                titles.append(title)
                authors.append(author)
                companies.append(company)
                releases.append(release)
                prices.append(price)
                img_paths.append(img_filename)
                keywords.append(key_word)

            except Exception as e:
                print(f"{page}페이지 {i+1}번째 항목 오류: {e}")
                continue

    driver.quit()

    df = pd.DataFrame({
        '검색어': keywords,
        '책제목': titles,
        '저자': authors,
        '가격': prices,
        '출판사': companies,
        '출간일': releases,
        '이미지 경로': img_paths
    })

    df.to_excel('yes24_books.xlsx', index=False, sheet_name='Sheet1', engine='openpyxl')
    print("\n✅ 엑셀 저장 완료: yes24_books.xlsx")


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


def aladin(key_word, max_page):
    options = Options()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)

    titles, authors, companies, releases, prices, img_paths, keywords = [], [], [], [], [], [], []
    img_dir = 'images/aladin'
    os.makedirs(img_dir, exist_ok=True)

    base_url = 'https://www.aladin.co.kr/home/welcome.aspx'
    driver.get(base_url)
    time.sleep(2)

    search_input = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[1]/form/div/div[2]/input[2]')
    search_input.click()
    time.sleep(1)
    search_input.send_keys(key_word, Keys.ENTER)
    time.sleep(3)

    books_xpath = '/html/body/div[3]/table/tbody/tr/td[3]/form/div[2]/div'

    print(f'\n[INFO] 1페이지 수집 시작')
    books = driver.find_elements(By.XPATH, books_xpath)

    if not books:
        print('[INFO] 1페이지에 책이 없습니다. 수집을 종료합니다.')
        driver.quit()
        return

    print(f'1페이지: {len(books)}개 책 발견')

    for i, book in enumerate(books):
        try:
            title = book.find_element(By.XPATH, './/table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/div[1]/ul/li[1]/a[1]').text
            author = book.find_element(By.XPATH, './/table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/div[1]/ul/li[2]/a[1]').text
            company = book.find_element(By.XPATH, './/table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/div[1]/ul/li[2]/a[2]').text
            release = book.find_element(By.XPATH, './/table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/div[1]/ul/li[2]').text.split('|')[-1].strip()
            price = book.find_element(By.XPATH, './/table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/div[1]/ul/li[3]/span[1]').text

            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", book)
            time.sleep(1)

            img_tag = book.find_element(By.XPATH, './/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/a/div/div/img[2]')
            img_url = img_tag.get_attribute('src')

            img_filename = ''
            if img_url:
                img_filename = f"{img_dir}/{key_word}_p1_{i+1:02d}.jpg"
                with open(img_filename, 'wb') as f:
                    f.write(requests.get(img_url).content)

            titles.append(title)
            authors.append(author)
            companies.append(company)
            releases.append(release)
            prices.append(price)
            img_paths.append(img_filename)
            keywords.append(key_word)

        except Exception as e:
            print(f"1페이지 {i+1}번째 항목 오류: {e}")
            continue

    encoded_keyword = quote(key_word)
    for page in range(2, max_page + 1):
        url = f'https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=All&SearchWord={encoded_keyword}&page={page}'
        print(f'\n[INFO] {page}페이지 접속 중: {url}')
        driver.get(url)
        time.sleep(3)

        books = driver.find_elements(By.XPATH, books_xpath)
        if not books:
            print(f'[INFO] {page}페이지에 책이 없습니다. 수집을 종료합니다.')
            break

        print(f'{page}페이지: {len(books)}개 책 발견')

        for i, book in enumerate(books):
            try:
                title = book.find_element(By.XPATH, './/table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/div[1]/ul/li[1]/a[1]').text
                author = book.find_element(By.XPATH, './/table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/div[1]/ul/li[2]/a[1]').text
                company = book.find_element(By.XPATH, './/table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/div[1]/ul/li[2]/a[2]').text
                release = book.find_element(By.XPATH, './/table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/div[1]/ul/li[2]').text.split('|')[-1].strip()
                price = book.find_element(By.XPATH, './/table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/div[1]/ul/li[3]/span[1]').text

                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", book)
                time.sleep(1)

                img_tag = book.find_element(By.XPATH, './/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/a/div/div/img[2]')
                img_url = img_tag.get_attribute('src')

                img_filename = ''
                if img_url:
                    img_filename = f"{img_dir}/{key_word}_p{page}_{i+1:02d}.jpg"
                    with open(img_filename, 'wb') as f:
                        f.write(requests.get(img_url).content)

                titles.append(title)
                authors.append(author)
                companies.append(company)
                releases.append(release)
                prices.append(price)
                img_paths.append(img_filename)
                keywords.append(key_word)

            except Exception:
                # 구조가 다른 경우 백업 XPath 사용
                try:
                    title = book.find_element(By.XPATH, './table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/div/ul/li[2]/a').text
                    author = book.find_element(By.XPATH, './table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/div/ul/li[3]').text
                    company = book.find_element(By.XPATH, './table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/div/ul/li[3]/a[2]').text
                    release = book.find_element(By.XPATH, './table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/div/ul/li[3]').text.split('|')[-1].strip()
                    price = book.find_element(By.XPATH, './table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/div/ul/li[4]/span/em').text

                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", book)
                    time.sleep(1)

                    img_tag = book.find_element(By.XPATH, './table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/a/img')
                    img_url = img_tag.get_attribute('src')

                    img_filename = ''
                    if img_url:
                        img_filename = f"{img_dir}/{key_word}_p{page}_{i+1:02d}.jpg"
                        with open(img_filename, 'wb') as f:
                            f.write(requests.get(img_url).content)

                    titles.append(title)
                    authors.append(author)
                    companies.append(company)
                    releases.append(release)
                    prices.append(price)
                    img_paths.append(img_filename)
                    keywords.append(key_word)

                except Exception as e:
                    print(f"{page}페이지 {i+1}번째 항목 [백업 XPath 사용] 오류: {e}")
                    continue


    driver.quit()

    df = pd.DataFrame({
        '검색어': keywords,
        '책제목': titles,
        '저자': authors,
        '가격': prices,
        '출판사': companies,
        '출간일': releases,
        '이미지 경로': img_paths
    })

    df.to_excel('aladin_books.xlsx', index=False, sheet_name='Sheet1', engine='openpyxl')
    print("\n✅ 엑셀 저장 완료: aladin_books.xlsx")



def crawl_start(keyword, yes24_pages, kyobo_pages, aladin_pages):
    yes24(keyword, yes24_pages)
    kyobo(keyword, kyobo_pages)
    aladin(keyword, aladin_pages)

    df_yes24 = pd.read_excel('yes24_books.xlsx', engine='openpyxl')
    df_kyobo = pd.read_excel('kyobo_books.xlsx', engine='openpyxl')
    df_aladin = pd.read_excel('aladin_books.xlsx', engine='openpyxl')

    output_file = f'{keyword}_books_combined.xlsx'
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df_yes24.to_excel(writer, index=False, sheet_name='yes24')
        df_kyobo.to_excel(writer, index=False, sheet_name='kyobo')
        df_aladin.to_excel(writer, index=False, sheet_name='aladin')

    print(f"\n✅ 통합 엑셀 저장 완료: {output_file}")

crawl_start("파이썬",2,3,2)