"""Web scraper for extracting content from websites."""

import re
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup

    HAS_WEB_DEPS = True
except ImportError:
    HAS_WEB_DEPS = False


def fetch_page(url: str) -> str:
    """Fetch a web page and return HTML"""
    if not HAS_WEB_DEPS:
        raise ImportError(
            "Install requests and beautifulsoup4: pip install requests beautifulsoup4"
        )

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def parse_html(html: str) -> BeautifulSoup:
    """Parse HTML with BeautifulSoup"""
    return BeautifulSoup(html, "html.parser")


def extract_main_content(soup: BeautifulSoup) -> str:
    """Extract main content from page"""
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()

    # Try common content selectors
    content = (
        soup.find("main") or soup.find("article") or soup.find("div", class_="content")
    )

    if content:
        return content.get_text(separator="\n", strip=True)

    return soup.get_text(separator="\n", strip=True)


def extract_title(soup: BeautifulSoup) -> str:
    """Extract page title"""
    title = soup.find("h1")
    if title:
        return title.get_text(strip=True)
    return soup.title.string if soup.title else "Untitled"


def extract_metadata(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract metadata"""
    meta = {}
    for tag in soup.find_all("meta"):
        name = tag.get("name") or tag.get("property")
        content = tag.get("content")
        if name and content:
            meta[name] = content
    return meta


def scrape_url(url: str) -> Dict[str, Any]:
    """Scrape a single URL"""
    html = fetch_page(url)
    soup = parse_html(html)

    return {
        "url": url,
        "title": extract_title(soup),
        "content": extract_main_content(soup),
        "metadata": extract_metadata(soup),
    }


def scrape_links(url: str, selector: str = "a") -> List[str]:
    """Get all links from a page"""
    html = fetch_page(url)
    soup = parse_html(html)

    links = []
    for link in soup.find_all(selector, href=True):
        href = link.get("href")
        if href:
            full_url = urljoin(url, href)
            if full_url.startswith("http"):
                links.append(full_url)

    return list(set(links))


def scrape_playbooks(base_url: str, output_dir: Path) -> List[Path]:
    """Scrape playbook articles and save as markdown"""
    if not HAS_WEB_DEPS:
        raise ImportError("Install requests and beautifulsoup4")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Get all playbook links
    links = scrape_links(base_url)

    output_files = []
    for link in links:
        try:
            print(f"Scraping: {link}")
            data = scrape_url(link)

            # Convert to markdown
            md_content = f"""# {data["title"]}

**Source:** {data["url"]}

---

{data["content"]}
"""

            # Save to file
            filename = re.sub(r"[^\w\-]", "_", data["title"][:50]) + ".md"
            output_file = output_dir / filename
            output_file.write_text(md_content)
            output_files.append(output_file)
            print(f"Saved: {filename}")

        except Exception as e:
            print(f"Error scraping {link}: {e}")

    return output_files


# Test with a URL
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        url = sys.argv[1]
        output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("raw")

        files = scrape_playbooks(url, output_dir)
        print(f"\nScraped {len(files)} pages")
    else:
        print("Usage: python -m evokb.scraper <url> [output_dir]")
