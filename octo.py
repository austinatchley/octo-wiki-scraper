import requests
from bs4 import BeautifulSoup, PageElement, ResultSet
from urllib.parse import urljoin, urlparse
import os

BASE_URL = 'https://en.wikipedia.org/wiki/'
START_URL = 'Web_scraping'
OUTPUT_FOLDER = 'out/' # TODO: Make this a relative path
MAX_DEPTH = 3

# Function to download HTML content of a Wikipedia page
def download_wikipedia_html(relative_url: str, depth: int, visited: set[str]):
    if relative_url in visited:
        return

    visited.add(relative_url)
    
    full_url = BASE_URL + relative_url
    print(f"Requesting {full_url}")
    
    # Send a GET request to the Wikipedia page
    response = requests.get(full_url)
    
    # Check if the request was successful (status code 200)
    if response.status_code != 200:
        print("Failed to retrieve the webpage.")
        return
    
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    # print(soup.text)
    
    # Save the HTML content to a file
    filename = relative_url.replace("/", "_")
    path = os.path.join(OUTPUT_FOLDER, filename)
    print(f"Path={path}")
    with open(path, 'w', encoding='utf-8') as file:
        file.write(response.text)
    print(f"HTML content saved to '{filename}'")
    
    # Extract all links from the page
    if depth >= MAX_DEPTH:
        print("Reached max depth")
        return

    for link in extract_links(soup):
        process_link(link, depth, visited)
    
# Function to check if a URL is a valid Wikipedia article link
def is_valid_wikipedia_link(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme in ('http', 'https') and 'wikipedia.org' in parsed_url.netloc

def extract_links(soup: BeautifulSoup) -> ResultSet[PageElement]:
    return soup.find_all('a', href=True)
    
def process_link(link: PageElement, depth: int, visited: set[str]) -> None:
    relative_link = link.get('href')

    if not relative_link.startswith('/wiki/'):
        return
    relative_link = relative_link.replace('/wiki/', '')

    # Construct absolute URL
    absolute_link = urljoin(BASE_URL, relative_link)
    
    # Ensure it's a Wikipedia article link and not a special page
    if is_valid_wikipedia_link(absolute_link):
        print(f"Visiting linked page: {relative_link}")

        # Recursively download HTML of linked article
        download_wikipedia_html(relative_link, depth + 1, visited)



if __name__ == "__main__": 
    # Create output folder if it doesn't exist
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    
    download_wikipedia_html(relative_url=START_URL, 
                            depth=0, 
                            visited=set())
