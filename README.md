# Amazon Reviews Scraper

This Python script provides a class `AmazonReviewsScrapper` for scraping reviews for a product from an Amazon India URL. It uses Selenium WebDriver and BeautifulSoup for web scraping.

## Installation

1. Install the required libraries:
   ```bash
   pip install selenium beautifulsoup4
   ```

2. Install the Chrome WebDriver. Download the WebDriver that matches your Chrome version from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads) and add it to your system's PATH.

## Usage

1. Import the `AmazonReviewsScrapper` class from the script:

   ```python
   from amazon_reviews_scraper import AmazonReviewsScrapper
   ```

2. Create an instance of `AmazonReviewsScrapper`:

   ```python
   scraper = AmazonReviewsScrapper()
   ```

3. Use the `scrape_reviews` method to scrape reviews for a product:

   ```python
   link = 'https://www.amazon.in/product-url'
   options = {
       "sortBy": "recent",
       "reviewerType": "all_reviews",
       "filterByStar": "all_stars",
       "mediaType": "all_contents"
   }
   reviews = scraper.scrape_reviews(link, options=options, number_of_reviews=20)
   ```

## Options

The following options can be passed to the `scrape_reviews` function:

- `sortBy`: Sort the reviews by "recent" or "helpful".
- `reviewerType`: Filter reviews by "all_reviews" or "avp_only_reviews".
- `filterByStar`: Filter reviews by "all_stars", "one_star", "two_star", "three_star", "four_star", "five_star", "positive", or "critical".
- `mediaType`: Filter reviews by "all_contents" or "media_reviews_only".

## Configuration

You can configure the scraper to run in headless mode by passing `headless=False` when creating an instance of `AmazonReviewsScrapper`:

```python
scraper = AmazonReviewsScrapper(headless=False)
```

## Error Handling

The script provides error handling for invalid URLs and options. If the URL is not a valid Amazon India URL, an `InvalidUrlError` is raised. If the options provided are invalid, an `InvalidOptionError` is raised.

## Dependencies

- `selenium`: Used for automating web browsers.
- `beautifulsoup4`: Used for parsing HTML and XML documents.

## License

This script is released under the MIT License. Feel free to modify and distribute it as needed.