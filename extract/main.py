import re
import os
import datetime
import requests
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from html.parser import HTMLParser


HTTP_URL_PATTERN = r"^http[s]{0,1}://.+$"

# Define root domain to crawl
domain = "learn.microsoft.com/en-us/cli/azure"
full_url = (
    "https://learn.microsoft.com/en-us/cli/azure/reference-index?view=azure-cli-latest"
)


# Create a class to parse the HTML and get the hyperlinks
class HyperlinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        # Create a list to store the hyperlinks
        self.hyperlinks = []

    # Override the HTMLParser's handle_starttag method to get the hyperlinks
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # If the tag is an anchor tag and it has an href attribute, add the href attribute to the list of hyperlinks
        if tag == "a" and "href" in attrs:
            self.hyperlinks.append(attrs["href"])


# Function to get the hyperlinks from a URL
def get_hyperlinks(url):
    # Try to open the URL and read the HTML
    try:
        # Open the URL and read the HTML
        with urllib.request.urlopen(url) as response:
            # If the response is not HTML, return an empty list
            if not response.info().get("Content-Type").startswith("text/html"):
                return []

            # Decode the HTML
            html = response.read().decode("utf-8")
    except Exception as e:
        print(e)
        return []

    # Create the HTML Parser and then Parse the HTML to get hyperlinks
    parser = HyperlinkParser()
    parser.feed(html)

    return parser.hyperlinks


# Function to get the hyperlinks from a URL that are within the same domain
def get_domain_hyperlinks(local_domain, url):
    clean_links = []
    for link in set(get_hyperlinks(url)):
        clean_link = None

        # If the link is a URL, check if it is within the same domain
        if re.search(HTTP_URL_PATTERN, link):
            # Parse the URL and check if the domain is the same
            url_obj = urlparse(link)
            if url_obj.netloc == local_domain:
                clean_link = link

        # If the link is not a URL, check if it is a relative link
        else:
            if link.startswith("/"):
                link = link[1:]
            elif (
                link.startswith("#")
                or link.startswith("mailto:")
                or link.startswith("tel:")
            ):
                continue
            clean_link = "https://" + local_domain + "/" + link

        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)

    # Return the list of hyperlinks that are within the same domain
    return list(set(clean_links))


def extract_content(url):
    response = requests.get(url)
    content = response.content
    soup = BeautifulSoup(content, features="html.parser")

    for data in soup(["table"]):
        data.decompose()

    title = soup.find("title").text
    body = soup.find("div", {"class": "content"})

    if body is None:
        return None, None

    lines = (line.strip() for line in body.get_text().splitlines())
    lines = "\n".join(
        line for line in lines
            if line and
            line != "Reference" and
            line != "Feedback" and
            line != "In this article" and
            line != "Edit" and
            line != "Note" and
            line != "This command group has commands that are defined in both Azure CLI and at least one extension. Install each extension to benefit from its extended capabilities. Learn more about extensions." # noqa
    )

    return title, lines


if __name__ == "__main__":
    now = datetime.date.today()

    isExist = os.path.exists("extract/docs")

    if not isExist:
        os.makedirs("extract/docs")

    print(f"Getting links from {domain} and {full_url}")
    links = get_domain_hyperlinks(domain, full_url)

    print(f"Found {len(links)} links")

    for url in links:
        print(f"Extracting text from {url}")
        title, copy = extract_content(url)

        if title is None or copy is None:
            continue

        if title.startswith("404 - Content Not Found"):
            continue

        title = title.replace(" | Microsoft Learn", "")
        f = open(f"extract/docs/{title}.txt", "w")

        print(f"Writing file {title}.txt")

        f.write(copy)
        f.close()
