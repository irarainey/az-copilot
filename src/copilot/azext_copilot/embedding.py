import json
from azext_copilot.constants import AZ_CLI_DOCUMENTATION
import requests
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import urlparse
from html.parser import HTMLParser
import re
import chromadb


HTTP_URL_PATTERN = r'^http[s]{0,1}://.+$'

# Define root domain to crawl
domain = "learn.microsoft.com/en-us/cli/azure"
full_url = AZ_CLI_DOCUMENTATION


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
            if not response.info().get('Content-Type').startswith("text/html"):
                return []

            # Decode the HTML
            html = response.read().decode('utf-8')
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


def extract_text_from(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, features="html.parser")
    text = soup.get_text()

    lines = (line.strip() for line in text.splitlines())
    return '\n'.join(line for line in lines if line)


if __name__ == "__main__":

    # pages = []
    # print(f"Getting links from {domain} and {full_url}")
    # links = get_domain_hyperlinks(domain, full_url)
    # print(f"Found {len(links)} links")
    # for url in links:
    #     copy = extract_text_from(url)
    #     copy = copy.replace('Microsoft Learn\nSkip to main content\nThis browser is no longer supported.\nUpgrade to Microsoft Edge to take advantage of the latest features, security updates, and technical support.\nDownload Microsoft Edge\nMore info about Internet Explorer and Microsoft Edge\nTable of contents\nExit focus mode\nRead in English\nSave\nTable of contents\nRead in English\nSave\nPrint\nTwitter\nLinkedIn\nFacebook\nEmail', '')
    #     copy = copy.replace('\nFeedback\nSubmit and view feedback for\nThis page\nView all page feedback\nTheme\nLight\nDark\nHigh contrast\nPrevious Versions\nBlog\nContribute\nPrivacy\nTerms of Use\nTrademarks\n\u00a9 Microsoft 2023\nAdditional resources\nIn this article\nTheme\nLight\nDark\nHigh contrast\nPrevious Versions\nBlog\nContribute\nPrivacy\nTerms of Use\nTrademarks\n\u00a9 Microsoft 2023', '')
    #     copy = copy.replace('\n', '. ')
    #     copy = copy.replace('Table of contents.', '')
    #     copy = copy.replace('..', '.')
    #     pages.append({'text': copy, 'source': url})
    #     print(f"Extracting text from {url}")

    # with open("output.json", "w") as f:
    #     json.dump(pages, f, indent=4)

    chroma_client = chromadb.PersistentClient(path="/home/ira/.az-copilot")
    # chroma_client = chromadb.Client()
    collection = chroma_client.get_or_create_collection(name="az-cli-documentation")

    # coll_list = chroma_client.list_collections()
    # print(coll_list)

    # settings = chroma_client.get_settings()
    # print(settings)

    # print("\n\nIndexing documents")

    # docs, metadatas = [], []
    # for page in pages:
    #     collection.add(
    #         documents=[page['text']],
    #         metadatas=[{"source": page['source']}],
    #         ids=[page['source']]
    #     )

    # print("\n\nSearching documents")

    results = collection.query(
        query_texts=["load testing"],
        n_results=1
    )

    print(results)
