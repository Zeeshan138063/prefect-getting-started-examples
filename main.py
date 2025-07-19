# from prefect import flow, task
# import httpx
#
#
# @task(log_prints=True)
# def get_stars(repo: str):
#     url = f"https://api.github.com/repos/{repo}"
#     count = httpx.get(url).json()["stargazers_count"]
#     print(f"{repo} has {count} stars!")
#
#
# @flow(name="GitHub Stars")
# def github_stars(repos: list[str]):
#     for repo in repos:
#         get_stars(repo)
#
# from prefect import flow
#
#
# @flow
# def my_workflow() -> str:
#     return "Hello, world!"
# # run the flow!
# if __name__=="__main__":
#     my_workflow()
#     github_stars(["PrefectHQ/Prefect"])



from __future__ import annotations

import re
from typing import List

import requests
from bs4 import BeautifulSoup
from prefect import flow, task

@task(retries=2, retry_delay_seconds=2)
def fetch_html(url: str) -> str:
    """Download page HTML (with retries).

    This is just a regular requests call - Prefect adds retry logic
    without changing how we write the code."""
    print(f"Fetching {url} …")
    response = requests.get(f"{url}", timeout=10)
    response.raise_for_status()
    return response.text

@task
def parse_article(html: str) -> str:
    """Extract article text, skipping code blocks.

    Regular BeautifulSoup parsing with standard Python string operations.
    Prefect adds observability without changing the logic."""
    soup = BeautifulSoup(html, "html.parser")

    # Find main content - just regular BeautifulSoup
    article = soup.find("article") or soup.find("main")
    if not article:
        return ""

    # Standard Python all the way
    for code in article.find_all(["pre", "code"]):
        code.decompose()

    content = []
    for elem in article.find_all(["h1", "h2", "h3", "p", "ul", "ol", "li"]):
        text = elem.get_text().strip()
        if not text:
            continue

        if elem.name.startswith('h'):
            content.extend([
                "\n" + "=" * 80,
                text.upper(),
                "=" * 80 + "\n"
            ])
        else:
            content.extend([text, ""])

    return "\n".join(content)


@flow(log_prints=True)
def scrape(urls: List[str] | None = None) -> None:
    """Scrape and print article content from URLs.

    A regular Python function that composes our tasks together.
    Prefect adds logging and dependency management automatically."""

    if urls:
        for url in urls:
            content = parse_article(fetch_html(url))
            print(content if content else "No article content found.")




if __name__ == "__main__":
    urls = [
        "https://www.prefect.io/blog/airflow-to-prefect-why-modern-teams-choose-prefect",
        "https://www.prefect.io/blog/airflow-to-prefect-why-modern-teams-choose-prefect/8",
        "https://www.prefect.io/blog/airflow-to-prefect-why-modern-teams-choose-prefect"
    ]
    scrape(urls=urls)