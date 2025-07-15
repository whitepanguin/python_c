import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys # 키 입력
from selenium.webdriver.common.action_chains import ActionChains

driver = webdriver.Chrome()
driver.get('https://www.instagram.com/')
# soup = BeautifulSoup(driver.page_source, "html.parser")
time.sleep(5)
print('** 로그인 시도 **')
xpath = '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/article/div[2]/div[1]/div[2]/div/form'
insta_loginbox = driver.find_element(By.XPATH, xpath)

try:
    insta_id = insta_loginbox.find_element(By.XPATH, './div[1]/div[1]/div/label/input')
    insta_id.send_keys("kimapple10042")
    time.sleep(6)
    insta_pw = insta_loginbox.find_element(By.XPATH, './div[1]/div[2]/div/label/input')
    insta_pw.send_keys("Apple1004")
    time.sleep(7)
    insta_enter = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/article/div[2]/div[1]/div[2]/div/form/div[1]/div[3]/button").click()
    time.sleep(20)
    driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div/div/div").click()
    time.sleep(8)
    driver.get('https://www.instagram.com/explore/search/keyword/?q=%23%EC%97%AC%ED%96%89')
    time.sleep(10)
    blog = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div/div/div[1]/div[1]/div/a"
    insta_blog = driver.find_element(By.XPATH, blog)

    # 썸네일 클릭 전 href 가져오기
    post_url = insta_blog.get_attribute("href")
    print("게시물 URL:", post_url)

    # 해당 게시물로 직접 이동
    driver.get(post_url)
    time.sleep(9)


    actions = ActionChains(driver)
    heart_xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div/div[3]/section[1]/div[1]/span[1]/div/div/div"
    heart_element = driver.find_element(By.XPATH, heart_xpath)
    actions.move_to_element(heart_element).perform()
    time.sleep(1)
    heart_element.click()

    comment_icon_xpath = '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div/div[3]/section[1]/div[1]/span[2]/div/div'
    comment_icon = driver.find_element(By.XPATH, comment_icon_xpath)
    actions.move_to_element(comment_icon).perform()
    time.sleep(2) 
    comment_icon.click()
    time.sleep(5)   
    # 댓글 입력창 (textarea) 찾기
    textarea_xpath = '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div/div[4]/section/div/form/div/textarea'
    comment_input = driver.find_element(By.XPATH, textarea_xpath)

    comment_input.click()  # 입력창 클릭
    comment_input.clear()  # 혹시 남아있는 내용 클리어
    comment_input.send_keys("와! 축하드립니다", Keys.ENTER)

    print("댓글 입력 완료")
    time.sleep(30)

# //*[@id="mount_0_0_mY"]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div/div[4]/section/div/form/div/textarea
except Exception as e:
    print("오류:", e)

