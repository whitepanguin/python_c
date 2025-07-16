import time
from selenium import webdriver
from bs4 import BeautifulSoup

def crawl_yanolja_reviews(name, url):
    review_list = []
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)

    # 원래는 무한 루프 도는게 맞는데 학습상 이런식으로 하겠다 
    scroll_count = 3 # 3번만 내리겠다
    for i in range(scroll_count):
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)") # 여기에 자바 스크립트 문법이 먹힌다 // 0 부터 최대한 아래 까지 
        time.sleep(2)

    html = driver.page_source
    # css의 select를 쓰겠다
    soup = BeautifulSoup(html,'html.parser')

    review_containers = soup.select('#__next > section > div > div.css-1js0bc8 > div')
    # print(review_containers)
    # nth-child는 없애준다
    review_date = soup.select('#__next > section > div > div.css-1js0bc8 > div > div > div > div.css-1toaz2b > div > div.css-1ivchjf > p')

    for i in range(len(review_containers)):
        review_text = review_containers[i].find('p',class_='content-text').text
        # print(review_text)
        # print("-"*30)
        date = review_date[i].text
        review_empty_stars = review_containers[i].find_all('path',{'fill-rule':'evenodd'})
        stars=5-len(review_empty_stars)
        # print(review_empty_stars)
        # print("-"*30) 아무것도 없으면 별 5개, 한개당 빈 별개수
        review_dict = {
            'review': review_text,
            'stars': stars,
            'date': date
        }
        review_list.append(review_dict)
    return review_list



total_review = crawl_yanolja_reviews('파르나스 호텔 제주',"https://nol.yanolja.com/reviews/domestic/10045535")
print(total_review)