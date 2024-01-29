from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import re
from exceptions import InvalidUrlError, InvalidOptionError

class AmazonReviewsScrapper:

    def __init__(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")

        self.browser = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.browser, 10)

    def scrape_reviews(self, link, number_of_reviews=20, options:dict=None):
        if self.__validate_amazon_url__(link) == False:
            raise InvalidUrlError(f"URL is not a valid Amazon India URL: {link}")
        self.url = self.__create_reviews_url__(link, options)
        # self.browser.get(self.url)
        # time.sleep(10)
        # self.__scroll__(self.__get_total_reviews__()) if number_of_reviews == -1 else self.__scroll__(number_of_reviews)
        # self.__expand_reviews__()
        # self.__parse_reviews__(number_of_reviews)

    def __validate_amazon_url__(self, url):
        pattern = r'^https://www\.amazon\.in/.+$'
        return bool(re.match(pattern, url))
    
    def __create_reviews_url__(self, url, options:dict):
        url_parts = str(url).split('/')
        product_id = url_parts[5]
        product_name = url_parts[3]
        reviews_url = "/".join([*url_parts[:3], product_name, 'product-reviews', product_id])
        
        # check for validity of options
        
        # default options
        default_options = {
            "sortBy": "recent",
            "reviewerType": "all_reviews",
            "filterByStar": "all_stars",
            "mediaType": "all_contents"
        }

        if options == None:
            options = default_options.copy()

        valid_sort_options = ["recent", "helpful"]
        valid_reviewer_type = ["all_reviews", "avp_only_reviews"]
        valid_star_filters = ["all_stars", "one_star", "two_star", "three_star", "four_star", "five_star", "positive", "critical"]
        valid_media_types = ["all_contents", "media_reviews_only"]

        if options.get("sortBy") != None and options.get("sortBy") not in valid_sort_options:
            raise InvalidOptionError(f"{options.get('sortBy')} is not a valid sortBy option. Valid options are {valid_sort_options}")
        if options.get("filterByStar") != None and options.get("filterByStar") not in valid_star_filters:
            raise InvalidOptionError(f"{options.get('filterByStar')} is not a valid filterByStar option. Valid options are {valid_star_filters}")
        if options.get("reviewerType") != None and options.get("reviewerType") not in valid_reviewer_type:
            raise InvalidOptionError(f"{options.get('reviewerType')} is not a valid reviewerType option. Valid options are {valid_reviewer_type}")
        if options.get("mediaType") != None and options.get("mediaType") not in valid_media_types:
            raise InvalidOptionError(f"{options.get('mediaType')} is not a valid mediaType option. Valid options are {valid_media_types}")

        default_options.update(options)

        # final url
        options_str = '&'.join([f"{key}={value}" for key, value in options.items()])
        modified_url = f"{reviews_url}?{options_str}"
        return(modified_url)

        

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
    amazon_scraper = AmazonReviewsScrapper()
    amazon_scraper.scrape_reviews("https://www.amazon.in/SMOOR-Mothera-Festive-Chocolate-Christmas/product-reviews/B08KV4W7PX/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&pageNumber=1&sortBy=recent&mediaType=all_contents&filterByStar=all_stars")