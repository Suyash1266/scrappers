from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
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

    def scrape_reviews(self, link, options:dict=None, number_of_reviews=20):
        if self.__validate_amazon_url__(link) == False:
            raise InvalidUrlError(f"URL is not a valid Amazon India URL: {link}")
        self.url = self.__create_url__(link, options)
        self.num_reviews = number_of_reviews
        self.browser.get(self.url)
        time.sleep(5)
        return {
            "Product Name": self.__get_product_name__(),
            "Product Link": self.__create_url__(link, options, type="product"),
            "Total Ratings": self.__get_total_ratings__(),
            "Average Rating": self.__get_average_rating__(),
            "Ratings": self.__get_individual_ratings__(),
            "Total Reviews": self.__get_total_reviews__(),
            "Reviews": self.__get_reviews__()
        }

    def __validate_amazon_url__(self, url):
        pattern = r'^https://www\.amazon\.in/.+$'
        return bool(re.match(pattern, url))
    
    def __create_url__(self, url, options: dict, type='reviews'):
        url_parts = str(url).split('/')
        product_id = url_parts[5].split('?')[0]
        product_name = url_parts[3]
        if type == 'product':
            return "/".join([*url_parts[:3], product_name, 'dp', product_id])
        reviews_url = "/".join([*url_parts[:3], product_name, 'product-reviews', product_id])
        options = self.__merge_default_options__(options)
        self.__validate_options__(options)
        return self.__create_final_url__(reviews_url, options)

    def __merge_default_options__(self, options):
        default_options = {
            "sortBy": "recent",
            "reviewerType": "all_reviews",
            "filterByStar": "all_stars",
            "mediaType": "all_contents"
        }

        options = {**default_options, **(options or {})}
        return options

    def __validate_options__(self, options):
        valid_options = {
            "sortBy": ["recent", "helpful"],
            "reviewerType": ["all_reviews", "avp_only_reviews"],
            "filterByStar": ["all_stars", "one_star", "two_star", "three_star", "four_star", "five_star", "positive", "critical"],
            "mediaType": ["all_contents", "media_reviews_only"]
        }

        for key, valid_values in valid_options.items():
            if options[key] not in valid_values:
                raise InvalidOptionError(f"{options[key]} is not a valid {key} option. Valid options are {valid_values}")

    def __create_final_url__(self, reviews_url, options):
        options_str = '&'.join([f"{key}={value}" for key, value in options.items()])
        return f"{reviews_url}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&{options_str}"

    def __get_total_reviews__(self):
        total_reviews_block = self.browser.find_element(By.CSS_SELECTOR, 'div#filter-info-section')
        total_reviews_html = self.browser.execute_script("return arguments[0].outerHTML;", total_reviews_block)
        soup = BeautifulSoup(total_reviews_html, 'html.parser')
        reviews_text = soup.find('div', {'data-hook': 'cr-filter-info-review-rating-count'}).get_text(strip=True)
        matches = re.findall(r'\d+', reviews_text)
        return int(matches[1])
    
    def __get_product_name__(self):
        product_name = self.browser.find_element(By.XPATH, '//*[@id="cm_cr-product_info"]/div/div[2]/div/div/div[2]/div[1]/h1/a')
        return str(product_name.get_attribute('innerHTML'))

    def __get_average_rating__(self):
        avg_rating_block = self.browser.find_element(By.XPATH, '//*[@id="cm_cr-product_info"]/div/div[1]/div[2]/div/div/div[2]/div/span')
        avg_rating_html = avg_rating_block.get_attribute('outerHTML')
        soup = BeautifulSoup(avg_rating_html, 'html.parser')
        avg_rating_text = soup.find('span', {'data-hook': 'rating-out-of-text'}).get_text(strip=True)
        match = re.search(r'(\d+(\.\d+)?) out of 5', avg_rating_text)
        return float(match[1])
    
    def __get_total_ratings__(self):
        total_ratings = self.browser.find_element(By.XPATH, '//*[@id="cm_cr-product_info"]/div/div[1]/div[3]/span')
        total_ratings = total_ratings.get_attribute('innerHTML')
        total_ratings = int(re.search(r'(\d+)', str(total_ratings))[1])
        return total_ratings
    
    def __get_individual_ratings__(self):
        histogram_block = self.browser.find_element(By.XPATH, '//*[@id="histogramTable"]/tbody')
        histogram_block_html = histogram_block.get_attribute('innerHTML')
        soup = BeautifulSoup(histogram_block_html, 'html.parser')
        stars_data = {}
        for row in soup.select('tr.a-histogram-row'):
            star_rating = (row.select_one('td.aok-nowrap span.a-size-base') or row.select_one('td.a-nowrap span.a-size-base')).get_text(strip=True)
            percentage = row.select_one('td.a-text-right span.a-size-base').get_text(strip=True)
            stars_data[star_rating] = int(percentage.rstrip('%'))
        # Calculate absolute number of ratings for each star
        stars_data = {star: round((percentage / 100) * self.__get_total_ratings__()) for star, percentage in stars_data.items()}
        return stars_data
    
    def __get_reviews_html__(self):
        def fetch_reviews():
            return [review.get_attribute('outerHTML') for review in self.browser.find_elements(By.CSS_SELECTOR, '[id^="customer_review-"]')]

        if self.num_reviews == -1:
            self.num_reviews = self.__get_total_reviews__()
        num_pages = -(-self.num_reviews // 10)
        reviews_html = []
        for i in range(1, num_pages + 1):
            if i != 1:
                self.browser.get(f"{self.url}&pageNumber={i}")
                time.sleep(5)
            reviews_html.extend(fetch_reviews())
        return reviews_html

    def __extract_country_and_date__(self, text):
        pattern = r'Reviewed in (\S+) on (\d+ \S+ \d{4})'
        match = re.search(pattern, text)
        return match.groups() if match else (None, None)
    
    def __get_reviews__(self):
        reviews_html = self.__get_reviews_html__()
        return [self.__parse_review__(review_html) for review_html in reviews_html]

    def __parse_review__(self, review_html):
        review_parser = BeautifulSoup(review_html, 'html.parser')
        review_element = review_parser.find('div', id=lambda x: x and x.startswith('customer_review-'))
        review_id = review_element.get('id').lstrip('customer_review-')
        reviewer_name = review_element.find('span', class_='a-profile-name').get_text(strip=True)
        review_location, review_date = self.__extract_country_and_date__(review_element.find('span', attrs={'data-hook': 'review-date'}).get_text(strip=True))
        rating = int(float(review_element.find('span', class_='a-icon-alt').get_text(strip=True).rstrip(" out of 5 stars")))
        review_title = review_element.find('a', attrs={'data-hook': 'review-title'}).find('span', class_=False).get_text(strip=True)
        review_body = review_element.find('span', attrs={'data-hook': 'review-body'}).find('span', class_=False, recursive=False)
        review_content = (review_body.get_text(strip=True) if review_body is not None else '')

        media = [video_block.get('data-video-url') for video_block in review_element.find_all('div', id=lambda x: x and x.startswith('review-video-'))]
        if image_block := review_element.find(
            'div', class_='review-image-tile-section'
        ):
            media.extend(img.get('src') for img in image_block.find_all('img'))

        return {
            'Review ID': review_id,
            'Reviewer Name': reviewer_name,
            'Review Date': review_date,
            'Review Location': review_location,
            'Review Title': review_title,
            'Rating': rating,
            'Review': review_content,
            **({'Media': media} if media else {}),
        }
        