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
        article_title = soup.find('div', class_='view_headline LoraMedium').get_text(strip=True)

        # Extract text content
        text_boxes = soup.find_all("p", class_="editor-p")
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
    Scrapes news URLs from a given section URL of "The Korea Times" news webpage and writes them to a text file.

    Args:
        url (str): The base URL of the section to scrape.
        url_filename (str): The name of the file to write the URLs to.
        contents_filename (str): The name of the file to write the contents to.
        end_date (str): The end date until which to scrape news articles in the format 'YYYY-MM-DD'.

    Returns:
        None
    """
    num_news = 0
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
    base_url = "https://www.koreatimes.co.kr/"
    current_page = 1
    proceed = True

    while proceed:
        # Construct URL for the current page
        if current_page == 1:
            url_with_page = f"{url}.html"
        else:
            url_with_page = f"{url}_{current_page}.html"
        print(url_with_page)
        # Request page content
        page = requests.get(url_with_page)
        soup = BeautifulSoup(page.text, "html.parser")

        # Find all news links on the page
        all_news_from_page = soup.find_all("div", class_="list_article_headline LoraMedium")

        # Check if there are no news links on the page
        if len(all_news_from_page) == 0:
            break

        # Iterate through each news link
        for news in all_news_from_page:
            if news.find("a").attrs["href"]:  # Check if it's a relevant news link
                full_url = f"https://www.koreatimes.co.kr{news.find('a').attrs['href']}"
                article = NewsPlease.from_url(full_url)
                publication_time = article.date_publish.replace(tzinfo=None)  # Remove timezone info for comparison
                
                # Check if the publication date is before the end date
                if publication_time.date() < end_datetime.date():
                    # Stop scraping if publication date is before end_date
                    proceed = False 
                    break

                information_collector(full_url, contents_filename)
                with open(url_filename, 'a') as file:
                    file.write(full_url + "\n")  # Write full URL to the output file
                num_news += 1
        
        current_page += 1

    print("URLs registered: ", num_news)





def main():
    # List of URLs to scrape


    urls = [

    "https://www.koreatimes.co.kr/www/sublist_129.html",  # Business
    "https://www.koreatimes.co.kr/www/sublist_602.html",  # Finance
    "https://www.koreatimes.co.kr/www/sublist_135.html",  # Lifestyle
    "https://www.koreatimes.co.kr/www/sublist_398.html",  # Entertainment & Art
    "https://www.koreatimes.co.kr/www/sublist_600.html",  # Sports
    "https://www.koreatimes.co.kr/www/sublist_501.html"  # World

    ]

    end_date = '2024-02-28'  # Desired end date

    # Output file names
    url_filename = "data/urls.txt"
    contents_filename = "data/database.txt"

    for url in urls:
        # Remove .html extension from URL
        url = url[:-5]

        # Call section_scraper function with the URL and output file names
        start_time = time.time()
        section_scraper(url, url_filename, contents_filename, end_date)
        print(f"Scraping {url} took {time.time() - start_time} seconds")

if __name__ == "__main__":
    main()
