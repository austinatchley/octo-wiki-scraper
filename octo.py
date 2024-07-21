import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

BASE_URL = 'https://en.wikipedia.org/wiki/'
START_URL = 'Web_scraping'
OUTPUT_FOLDER = 'out/' # TODO: Make this a relative path

# Function to download HTML content of a Wikipedia page
def download_wikipedia_html(relative_url: str, visited: set[str]):
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
    filename = relative_url
    path = os.path.join(OUTPUT_FOLDER, filename)
    print(f"Path={path}")
    with open(path, 'w', encoding='utf-8') as file:
        file.write(response.text)
    print(f"HTML content saved to '{filename}'")
    
    # Extract all links from the page
    links = soup.find_all('a', href=True)
    for link in links:
        relative_link = link.get('href')
        if relative_link.startswith('/wiki/'):
            relative_link = relative_link.replace('/wiki/', '')

            # Construct absolute URL
            absolute_link = urljoin(BASE_URL, relative_link)
            print(f"Relative link: {relative_link}")
            print(f"Absolute link: {absolute_link}")
            
            # Ensure it's a Wikipedia article link and not a special page
            if is_valid_wikipedia_link(absolute_link):
                # Recursively download HTML of linked article
                download_wikipedia_html(relative_link, visited)


# Function to check if a URL is a valid Wikipedia article link
def is_valid_wikipedia_link(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme in ('http', 'https') and 'wikipedia.org' in parsed_url.netloc

if __name__ == "__main__": 
    # Create output folder if it doesn't exist
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    
    download_wikipedia_html(START_URL, set())
