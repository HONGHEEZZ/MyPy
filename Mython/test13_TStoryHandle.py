
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# element 로딩완료 대기
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ctrl+v용
from selenium.webdriver.common.action_chains import ActionChains



options = webdriver.ChromeOptions()
options.add_argument('--disable-extensions')  # 확장 프로그램 구동 정지
options.add_argument('--start-maximized')  # 최대 크기 윈도우로 시작

# options.add_argument('window-size=1200x600') #윈도우 크기 지정
# options.headless = True    #윈도우가 눈에 보이지 않게 실행

driver = webdriver.Chrome(options=options, executable_path="D:/driver/chromedriver_91.exe")

startUrl = "https://hanhonghee.tistory.com/manage/newpost/"  #TStory 글쓰기 url...
driver.get(startUrl)



