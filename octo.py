import requests
from bs4 import BeautifulSoup, PageElement, ResultSet
from urllib.parse import ParseResult, urljoin, urlparse
import os
from markdownify import markdownify

BASE_URL = "https://en.wikipedia.org/wiki/"
START_URL = "Opera"
OUTPUT_FOLDER = "out/" # TODO: Make this a relative path
WIKI_PREFIX = "/wiki/"
MAX_DEPTH = 1
MAX_ARTICLES = 300


# TODO: Move into a new file
class ArticleCounter:
    def __init__(self, max: int) -> None:
        self.count: int = 0
        self.max_count: int = max
        self.visited: set[str] = set()

    def visit(self, link: str):
        self.visited.add(link)
        self.increment()

    def increment(self):
        self.count += 1

    def reached_max_articles(self):
        return self.count >= self.max_count

    def seen(self, link: str):
        return link in self.visited

    def num_visited(self):
        return len(self.visited)


# Function to download HTML content of a Wikipedia page
def download_wikipedia_html(relative_url: str, depth: int, counter: ArticleCounter):    
    if counter.seen(relative_url):
        return

    counter.visit(relative_url)
    
    full_url = BASE_URL + relative_url
    print(f"Requesting '{full_url}'")
    
    # Send a GET request to the Wikipedia page
    response: requests.Response = requests.get(full_url)
    if response.status_code != 200:
        print("Failed to retrieve the webpage.")
        return 
    
    # Save the HTML content to a file
    filename = relative_url.replace("/", "_") + ".html"
    filetext = preprocess_text(response.text)
    save_file(filename, filetext)
    
    if depth >= MAX_DEPTH:
        return

    # Extract and process all links from the page
    for link in extract_links(response):
        if counter.reached_max_articles():
            return

        process_link(link, depth, counter)


def save_file(filename: str, filetext: str):
    path = os.path.join(OUTPUT_FOLDER, filename)

    with open(path, "w", encoding="utf-8") as file:
        file.write(filetext)

    # print(f"HTML content saved to '{filename}'")
    

def preprocess_text(html: str) -> str:
    return html
    # return markdownify(html) # TODO

# Function to check if a URL is a valid Wikipedia article link
def is_valid_wikipedia_link(url: str) -> bool:
    parsed_url: ParseResult = urlparse(url)
    return parsed_url.scheme in ("http", "https") and "wikipedia.org" in parsed_url.netloc


def extract_links(response: requests.Response) -> list[PageElement]:
    soup = BeautifulSoup(response.content, "html.parser")

    # print(soup.text)
    links: ResultSet[PageElement] = soup.find_all("a", href=True)

    # TODO: Impl filtering logic here. Link ranking, enforce a max from each page, etc.

    return links
    

def process_link(link: PageElement, depth: int, visited: set[str]) -> None:
    relative_link = link.get("href")

    if relative_link is None or not relative_link.startswith(WIKI_PREFIX):
        return

    relative_link = relative_link.replace(WIKI_PREFIX, "")
    absolute_link = urljoin(BASE_URL, relative_link)
    
    # Ensure it's a Wikipedia article link and not a special page
    if is_valid_wikipedia_link(absolute_link):
        # print(f"Visiting linked page: {relative_link}")

        # Recursively download HTML of linked article
        download_wikipedia_html(relative_link, depth + 1, visited)

if __name__ == "__main__": 
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    
    article_counter = ArticleCounter(MAX_ARTICLES)

    download_wikipedia_html(relative_url=START_URL, 
                            depth=0, 
                            counter=article_counter)

    print(f"\nFinished successfully with {article_counter.num_visited()} pages visited!")
