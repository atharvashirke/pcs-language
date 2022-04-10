"""
A script to scrape all bill text off of the California Legislation. Stores 
all bills as their bill ID in files within data/raw.
"""

import requests
import os
from pathlib import Path
from bs4 import BeautifulSoup
import time 

def clean_data(result_set: list) -> str:
    """ 
        Cleans inputted strings of all html/css and other markup text.

        Arguments: 
            (list) result_set : Set of strings to clean from soup
        Returns 
            (string) output: output string cleaned of all html/css formatting
    """
    output = []

    for item in result_set:
        bill_text = item.get_text()
        bill_text = bill_text[bill_text.index("#DOCUMENTBill Start") + len("#DOCUMENTBill Start"):]
        output.append(bill_text.strip())

    return ''.join(output)

def scrape_urls(directory_url: str) -> list:
    """
        Returns a list with all urls from a "directory page": a page on 
        CA legislator that lists all bills in a given year.

        Arguments: 
            (str) directory_url: the url of a "directory page"
        Returns:
            (list) urls: urls to all bills on a directory page
    """
    page = requests.get(directory_url)
    soup = BeautifulSoup(page.content, "html.parser")

    urls = []

    for item in soup.find_all('a', href=True):
        urls.append(item['href'])
    
    return urls

for i in range(1999, 2022):
    year_id = str(i) + str(i + 1)

    os.mkdir(Path() / 'data' / 'raw' / year_id)
    directory_url = "https://leginfo.legislature.ca.gov/faces/billSearchClient.xhtml?session_year=" + year_id + "&house=Both&author=All&lawCode=All"

    urls = scrape_urls(directory_url)

    url_start = "https://leginfo.legislature.ca.gov"
    count = 0

    for bill_url in urls:
        if "bill_id=" in bill_url:
            bill_id = bill_url[bill_url.index("bill_id=") + len("bill_id="):] + ".txt"
            bill_page = requests.get(url_start + bill_url)
            bill_soup = BeautifulSoup(bill_page.content, "html.parser")

            with open(Path() / 'data' / 'raw' / year_id / bill_id, 'w') as df:
                df.write(clean_data(bill_soup.find_all(id="content_main")))

            count = count + 1

            if count % 100 == 0:
                print(str(count) + " files have been scraped so far...")
            time.sleep(1)

    print("Finished " + year_id + " directory.")
 



print("Completed Scraping " + count + " Bills!")