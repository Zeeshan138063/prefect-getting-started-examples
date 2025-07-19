from prefect import flow, task
import httpx


@task(log_prints=True, retries=2, retry_delay_seconds=2)
def get_stars(repo: str):
    """Fetch star count from GitHub API"""
    url = f"https://api.github.com/repos/{repo}"
    response = httpx.get(url, timeout=10)
    response.raise_for_status()
    stars = response.json()["stargazers_count"]
    print(f"{repo} has {stars} stars!")


@flow(name="GitHub Stars")
def github_stars(repos: list[str]):
    for repo in repos:
        get_stars(repo)


@flow
def my_workflow() -> str:
    print("Running my_workflow")
    return "Hello, world!"


if __name__ == "__main__":
    my_workflow()
    github_stars(["PrefectHQ/Prefect", "psf/requests"])
