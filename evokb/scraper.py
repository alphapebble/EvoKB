"""Better web scraper using trafilatura (best-in-class for content extraction)."""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import trafilatura

    HAS_TRAFILATURA = True
except ImportError:
    HAS_TRAFILATURA = False


def scrape_url_trafilatura(url: str) -> Dict[str, Any]:
    """Scrape URL using trafilatura (best content extraction)."""
    if not HAS_TRAFILATURA:
        raise ImportError("Install trafilatura: pip install trafilatura")

    # Fetch and extract
    result = trafilatura.extract(
        url,
        include_comments=False,
        include_tables=True,
        include_images=False,
        output_format="json",
    )

    if result:
        import json

        data = json.loads(result)
        return {
            "url": url,
            "title": data.get("title", ""),
            "content": data.get("text", ""),
            "description": data.get("description", ""),
            "author": data.get("author", ""),
            "date": data.get("date", ""),
            "categories": data.get("categories", []),
            "tags": data.get("tags", []),
        }

    return {"url": url, "error": "No content extracted"}


def scrape_urls_trafilatura(urls: List[str]) -> List[Dict[str, Any]]:
    """Scrape multiple URLs using trafilatura."""
    results = []
    for url in urls:
        try:
            result = scrape_url_trafilatura(url)
            results.append(result)
        except Exception as e:
            results.append({"url": url, "error": str(e)})
    return results


def save_as_markdown(data: Dict[str, Any], output_dir: Path) -> Path:
    """Save scraped content as markdown."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create filename from title
    title = data.get("title", "untitled")
    filename = re.sub(r"[^\w\-]", "_", title[:50]) + ".md"
    output_file = output_dir / filename

    # Build markdown
    content = f"""# {data.get("title", "Untitled")}

**Source:** {data.get("url", "")}

"""

    if data.get("description"):
        content += f"*{data.get('description')}*\n\n"

    content += "---\n\n"
    content += data.get("content", "")

    output_file.write_text(content)
    return output_file


def scrape_and_save(urls: List[str], output_dir: Path) -> List[Path]:
    """Scrape URLs and save as markdown files."""
    results = scrape_urls_trafilatura(urls)

    output_files = []
    for data in results:
        if "error" not in data and data.get("content"):
            output_file = save_as_markdown(data, output_dir)
            output_files.append(output_file)

    return output_files


# Fallback scraper using requests + readability if trafilatura not available
def scrape_url_fallback(url: str) -> Dict[str, Any]:
    """Fallback scraper using requests + beautifulsoup."""
    import requests
    from bs4 import BeautifulSoup

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    # Remove unwanted elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Get title
    title = soup.title.string if soup.title else "Untitled"

    # Get main content
    main = soup.find("main") or soup.find("article") or soup.find("div", role="main")
    content = (
        main.get_text(separator="\n", strip=True)
        if main
        else soup.get_text(separator="\n", strip=True)
    )

    return {"url": url, "title": title, "content": content}


def scrape_url(url: str) -> Dict[str, Any]:
    """Primary scrape function - uses best available method."""
    if HAS_TRAFILATURA:
        try:
            return scrape_url_trafilatura(url)
        except:
            pass

    return scrape_url_fallback(url)
