import requests
from bs4 import BeautifulSoup
import time
from newsplease import NewsPlease
from datetime import datetime, timedelta

def information_collector(url, contents_filename):
    """
    Extracts information from a news article URL and appends it to a file.

    Args:
        url (str): The URL of the news article.
        contents_filename (str): The name of the file to write the contents to.

    Returns:
        None
    """
    try:
        # Remove leading/trailing whitespace and newline characters
        url = url.strip()
            
        # Send a GET request to the URL
        page = requests.get(url)
        page.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

        # Parse the HTML content
        soup = BeautifulSoup(page.text, "html.parser")

        # Extract title
        article_title = soup.find('h1', class_='news_title').get_text(strip=True)

        # Extract text content
        text_boxes = soup.find_all("div", class_="text_box")
        article_content = '\n'.join(text_box.get_text(strip=True) for text_box in text_boxes)

        # Extract publication time
        article = NewsPlease.from_url(url)
        publication_time = article.date_publish

        # Append the extracted information to the file
        with open(contents_filename, 'a', encoding='utf-8') as file:
            file.write(article_title + "\n")
            file.write(article_content + "\n")
            file.write(str(publication_time) + "\n")
            file.write(url + "\n")
            file.write("==========================================\n")
        
    except Exception as e:
        print(f"Error processing URL: {url}. Skipping. Error message: {str(e)}")

def section_scraper(url, url_filename, contents_filename, end_date):
    """
    Scrapes news URLs from a given section URL of "The Korean Herald" news webpage and writes them to a text file.

    Args:
        url (str): The URL of the section to scrape.
        url_filename (str): The name of the file to write the URLs to.
        contents_filename (str): The name of the file to write the contents to.
        end_date (str): The end date until which to scrape news articles in the format 'YYYY-MM-DD'.

    Returns:
        None
    """
    current_page = 1
    num_news = 0
    proceed = True
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
    while proceed:
        # Construct URL for the current page
        url_with_page = f"{url}&np={current_page}"
        print(url_with_page)
        # Request page content
        page = requests.get(url_with_page)
        soup = BeautifulSoup(page.text, "html.parser")

        # Find all news links on the page
        all_news_from_page = soup.find_all("a", class_="news_link")

        # Iterate through each news link
        for news in all_news_from_page:
            if news.get("href")[0] == "v":  # Check if it's a relevant news link
                full_url = f"https://www.koreaherald.com/{news.get('href')}"
                article = NewsPlease.from_url(full_url)
                publication_time = article.date_publish.replace(tzinfo=None)  # Remove timezone info for comparison
                if publication_time.date() < end_datetime.date():
                    proceed = False  # Stop scraping if publication date is before end_date
                    break
                information_collector(full_url, contents_filename)
                with open(url_filename, 'a') as file:
                    file.write(full_url + "\n")  # Write full URL to the output file
                num_news += 1

        # Check if there are no more relevant news links or if reached end_date
        if len(all_news_from_page) < 10:  # Assuming less than 10 non-relevant news links per page
            proceed = False
        
        current_page += 1
    print("URLs registered: ", num_news)

def main():
    # List of URLs to scrape
    urls = [
        "https://www.koreaherald.com/list.php?ct=020100000000",  # national
        "https://www.koreaherald.com/list.php?ct=020200000000",  # business
        "https://www.koreaherald.com/list.php?ct=020300000000",  # life&culture
        "https://www.koreaherald.com/list.php?ct=020500000000&np=1",  # sports
        "https://www.koreaherald.com/list.php?ct=021200000000",  # world
        "https://www.koreaherald.com/list.php?ct=020409000000"  # k-pop (entertainment)
    ]

    start_date = datetime.now().strftime('%Y-%m-%d')  # Current date
    end_date = '2024-02-28'  # Desired end date

    # Output file names
    url_filename = "data/urls.txt"
    contents_filename = "data/database.txt"

    # Iterate over each URL and call section_scraper function
    for url in urls:
        start_time = time.time()
        section_scraper(url, url_filename, contents_filename, end_date)
        print(f"Scraping {url} took {time.time() - start_time} seconds")

if __name__ == "__main__":
    main()