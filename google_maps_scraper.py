from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

filename = "data"

link = "https://www.google.com/maps/place/CUMULUS+BY+SMOOR/@12.9767435,77.5981782,19z/data=!3m1!5s0x3bae167a719be543:0x1928a1b3135af4fc!4m8!3m7!1s0x3bae1784e4525fd3:0x2fa3b40e5fd70ac9!8m2!3d12.9746578!4d77.5969632!9m1!1b1!16s%2Fg%2F11v4rk996s?entry=ttu"


chrome_options = Options()
chrome_options.add_argument("--headless")
BROWSER = webdriver.Chrome(options=chrome_options)
WAIT = WebDriverWait(BROWSER, 10)

def reviews_scraper():
    # sort the reviews
    sort_reviews()
    # scroll until desired number of reviews are loaded
    scroll(get_total_reviews())
    # expand reviews
    expand_reviews()
    # parse reviews
    parse_reviews()

    input("Press enter to close the browser...")

def sort_reviews(by="newest"):
    menu_mapping = {
        "most relevant": 0,
        "newest": 1,
        "highest rating": 2,
        "lowest rating": 3
    }
    clicked = False
    tries = 0
    while not clicked and tries < 5:
        try:
            menu_bt = WAIT.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-value=\'Sort\']')))
            menu_bt.click()
            clicked = True
            time.sleep(3)

        except Exception as _:
            tries += 1
            raise RuntimeError("Unable to click sort button")

    try:
        index = menu_mapping.get(by.lower())
        rating_bt = BROWSER.find_elements(By.XPATH, '//div[@role=\'menuitemradio\']')[index]
        rating_bt.click()
        time.sleep(5)
    except ValueError as _:
        raise ValueError(f"Invalid sort type. No such sort type as {by}")

def get_total_reviews():
    review_summary_block = BROWSER.find_element(By.CSS_SELECTOR, 'div.jANrlb')
    review_summary_html = BROWSER.execute_script("return arguments[0].outerHTML;", review_summary_block)
    soup = BeautifulSoup(review_summary_html, "html.parser")
    reviews_text = soup.find(class_='fontBodySmall').get_text(strip=True)
    reviews_number = int(reviews_text.split()[0]) if reviews_text else None
    return reviews_number

def scroll(num_reviews=20):
    scrolls = num_reviews // 10 + 2
    for _ in range(scrolls):
        scrollable_div = BROWSER.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf')
        BROWSER.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        time.sleep(5)

def expand_reviews():
    more_buttons = BROWSER.find_elements(By.CSS_SELECTOR, 'button.w8nwRe.kyuRq')
    for button in more_buttons:
        button.click()

def parse_reviews(num_reviews=20):
    reviews_block = BROWSER.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[9]')
    reviews_html = BROWSER.execute_script("return arguments[0].outerHTML;", reviews_block)
    soup = BeautifulSoup(reviews_html, 'html.parser')
    print(reviews_html)

BROWSER.get(str(link))
time.sleep(10)
reviews_scraper()