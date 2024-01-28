from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import re
from exceptions import InvalidUrlError

class GoogleMapsReviewsScrapper:

    def __init__(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")

        self.browser = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.browser, 10)

    def scrape_reviews(self, link, number_of_reviews=20, by="newest"):
        if self.__validate_maps_url__(link) == False:
            raise InvalidUrlError(f"URL is not a valid google maps review URL: {link}")
        self.browser.get(link)
        time.sleep(10)
        self.__sort_reviews__(by)
        self.__scroll__(self.__get_total_reviews__()) if number_of_reviews == -1 else self.__scroll__(number_of_reviews)
        self.__expand_reviews__()
        self.__parse_reviews__(number_of_reviews)

    def __validate_maps_url__(self, url):
        pattern = r'^https://www\.google\.com/maps/place/.*4m8!3m7!.*$'
        return bool(re.match(pattern, url))

    def __sort_reviews__(self, by):
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
                menu_bt = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-value=\'Sort\']')))
                menu_bt.click()
                clicked = True
                time.sleep(3)

            except Exception as _:
                tries += 1
                raise RuntimeError("Unable to click sort button")

        try:
            index = menu_mapping.get(by.lower())
            rating_bt = self.browser.find_elements(By.XPATH, '//div[@role=\'menuitemradio\']')[index]
            rating_bt.click()
            time.sleep(5)
        except ValueError as _:
            raise ValueError(f"Invalid sort type. No such sort type as {by}")

    def __get_total_reviews__(self):
        review_summary_block = self.browser.find_element(By.CSS_SELECTOR, 'div.jANrlb')
        review_summary_html = self.browser.execute_script("return arguments[0].outerHTML;", review_summary_block)
        soup = BeautifulSoup(review_summary_html, "html.parser")
        reviews_text = soup.find(class_='fontBodySmall').get_text(strip=True)
        reviews_number = int(reviews_text.split()[0]) if reviews_text else None
        return reviews_number

    def __scroll__(self, num_reviews):
        scrolls = num_reviews // 10 + 2
        for _ in range(scrolls):
            scrollable_div = self.browser.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf')
            self.browser.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            time.sleep(5)

    def __expand_reviews__(self):
        more_buttons = self.browser.find_elements(By.CSS_SELECTOR, 'button.w8nwRe.kyuRq')
        for button in more_buttons:
            button.click()

    def __parse_reviews__(self, num_reviews):
        reviews_block = self.browser.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[9]')
        reviews_html = self.browser.execute_script("return arguments[0].outerHTML;", reviews_block)
        soup = BeautifulSoup(reviews_html, 'html.parser')
        print(reviews_html)

if __name__ == "__main__":
    google_reviews = GoogleMapsReviewsScrapper()
    link = "https://www.google.com/maps/place/CUMULUS+BY+SMOOR/@12.9767435,77.5981782,19z/data=!3m1!5s0x3bae167a719be543:0x1928a1b3135af4fc!4m8!3m7!1s0x3bae1784e4525fd3:0x2fa3b40e5fd70ac9!8m2!3d12.9746578!4d77.5969632!9m1!1b1!16s%2Fg%2F11v4rk996s?entry=ttu"
    google_reviews.scrape_reviews(link)